import requests
import time
import json


tokens = ["inqMrVdG2lvHCkuAaPKqQ2oLXx621Uup3CmWKvBs",  # Nico
          "LDpvHkjIEuTWn3iSdQlMhkbpFQ71MqEyfNqFzCQ6",  # Tobi
          "x8StnZIZyNCYq9GJppwRgFyLvpybYaN1MsSJob7z",  # Tobi2
          "fNkY4Hqatayd1cY8WwmCttrAIG6KkWFW5QV3iUOE",  # Tobi3
          "viBbgGt9PKgeBKANplsqkB9dlXXkERTN5aVhvaYb"]  # Marvin

url = "https://ballchasing.com/api/replays/"

# ----------------------------------------------------------------------------------------------------------------------
# Get filenames of replays based on playlist and season

links = []
request_count = 0
token_index = 0
hour_interval = 8
playlist = "ranked-standard"  # ranked-duels, ranked-doubles, ranked-standard
year = "2022"
for month in range(1, 13):       # Default: 1 - 13
    for day in range(1, 32):    # Default: 1 - 32
        for hour in range(0, 25 - hour_interval, hour_interval):
            if request_count >= 480:
                request_count = 0
                token_index += 1
                print("Request count exceeded, changed API-Token to index", token_index)
                if token_index >= 5:
                    print("Token index out of bounds at {}.{}.{} {}:00:00-{}:00:00".format(day, month, year, hour, hour + 2))
                    exit(0)
            time.sleep(0.5)
            filter = "?playlist={}&min-rank={}&pro=1&count={}&replay-date-after={}&replay-date-before={}".format(playlist, "supersonic-legend", "200", "{}-{}-{}T{}:00:00Z".format(year, str(month).zfill(2), str(day).zfill(2), hour), "{}-{}-{}T{}:59:59Z".format(year, str(month).zfill(2), str(day).zfill(2), hour+hour_interval-1))
            r = requests.get(url + filter, headers={'Authorization': tokens[token_index]})
            request_count += 1
            if r.status_code == 200:
                body = json.loads(r.content)
                print("{}.{}.{} {}:00:00-{}:59:59".format(day, month, year, hour, hour + hour_interval - 1), "- Replays found:", len(body["list"]))
                for x in body["list"]:
                    links.append(x["link"])
            else:
                print(r.json()["error"])
                break

with open("links/{}/{}.txt".format(year, playlist), 'a') as f:  # Default w+
    for x in links:
        f.write(x + "\n")

# Request file from ballchasing api
# ----------------------------------------------------------------------------------------------------------------------
# r = requests.get(url + name + "/file", headers={'Authorization': token})
# open(name + ".replay", 'wb').write(r.content)
