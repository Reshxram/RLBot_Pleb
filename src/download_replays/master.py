import sys
import requests
import time
import json
import os

from calendar import monthrange
from tqdm import tqdm


with open("token.txt", "r") as f:
    token = f.read()


url = "https://ballchasing.com/api/replays/"

name_request = 16  # per second
download_request = 2  # per second

playlists = ["ranked-duels", "ranked-doubles", "ranked-standard"]

while True:
    with open("weiter.txt", "r") as f:
        if f.read() != "1":
            exit(0)

    print("-----------------------------------------------------------------------------------------------------")

    # gets total previous progress of download -> [Mode, Year, Month, Day]
    status = {}
    with open("downloads/status.txt", "r") as f:
        for line in f:
            key, value = line.strip().split(': ')
            status[key] = int(value)

    playlist = playlists[status["Playlist"]]
    year = status["Year"]
    month = status["Month"]
    day = status["Day"]
    hour_interval = 1

    replay_names = []

    path = f"downloads/meta/{year}/{playlist}/{month}/{day}"
    if not os.path.exists(path):
        os.makedirs(path)

    path = f"downloads/replays/{year}/{playlist}/{month}/{day}"
    if not os.path.exists(path):
        os.makedirs(path)

    # Get names of replays of one day
    print(f"Getting names of {day}.{month}.{year} in {playlist}")
    for hour in tqdm(range(0, 24, hour_interval), file=sys.stdout):
        filter = f"?playlist={playlist}&min-rank=supersonic-legend&pro=1&count=200&replay-date-after={year}-{month:02d}-{day:02d}T{hour:02d}:00:00Z&replay-date-before={year}-{month:02d}-{day:02d}T{hour + hour_interval - 1:02d}:59:59Z"
        r = requests.get(url + filter, headers={'Authorization': token})
        if r.status_code == 200:
            body = json.loads(r.content)
            for x in body["list"]:
                replay_names.append(x["link"])
                name = x["id"] + ".json"
                with open(f"downloads/meta/{year}/{playlist}/{month}/{day}/{name}", "w", encoding='utf-8') as f:
                    json.dump(x, f, ensure_ascii=False, indent=4)
        else:
            print("Status code: ", r.status_code)
            print("Fetch error: ", r.json()["error"])
            exit(0)
        time.sleep(1 / name_request)

    print(f"Got {len(replay_names)} replays")

    # Download replays of set day
    print("Starting Downloads")
    for x in tqdm(range(len(replay_names)), file=sys.stdout):
        time.sleep(1 / download_request)
        name = replay_names[x].split("/")[-1] + ".replay"
        r = requests.get(replay_names[x] + "/file", headers={'Authorization': token})
        if r.status_code == 200:
            with open(f"downloads/replays/{year}/{playlist}/{month}/{day}/{name}", "wb") as f:
                f.write(r.content)
        else:
            print()
            print("Download error")
            print("Replay name: ", replay_names[x])
            print("Status code: ", r.status_code)
            print("Error message: ", r.json()["error"])
            if r.status_code == 404:
                with open("downloads/404.txt", "a") as f:
                    f.write(f"{day}.{month}.{year} in {playlist}\n" + replay_names[x] + "\n\n")
                continue
            else:
                exit(0)

    status["Day"] += 1
    if status["Day"] > monthrange(status["Year"], status["Month"])[1]:
        status["Day"] = 1
        status["Month"] += 1
        if status["Month"] > 12:
            status["Month"] = 1
            status["Year"] += 1
            if status["Year"] > 2022:
                status["Year"] = 2021
                status["Playlist"] += 1
                if status["Playlist"] > 2:
                    exit(0)

    new_status = ""
    for key, value in status.items():
        # add key-value pair to output string
        new_status += f"{key}: {value}\n"

    with open("downloads/status.txt", "w") as f:
        f.write(new_status)
