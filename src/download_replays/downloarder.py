import requests
import time
import json


tokens = ["inqMrVdG2lvHCkuAaPKqQ2oLXx621Uup3CmWKvBs",  # Nico
          "LDpvHkjIEuTWn3iSdQlMhkbpFQ71MqEyfNqFzCQ6",  # Tobi
          "x8StnZIZyNCYq9GJppwRgFyLvpybYaN1MsSJob7z",  # Tobi2
          "fNkY4Hqatayd1cY8WwmCttrAIG6KkWFW5QV3iUOE",  # Tobi3
          "viBbgGt9PKgeBKANplsqkB9dlXXkERTN5aVhvaYb"]  # Marvin

url = "https://ballchasing.com/api/replays/"


year = 2021
playlist = "ranked-duels"

while True:
    with open("links/{}/{}.txt".format(year, playlist), 'r') as links:  # Default w+
        all_links = []
        line_count = 0
        for x in links:
            all_links.append(x[:-1])
            line_count += 1
        line_count -= 1
        progress = int(all_links[0])
        all_links = all_links[progress:]

    token_index = 0
    current_index = progress
    for x in range(len(all_links)):
        time.sleep(1)
        name = all_links[x].split("/")[-1] + ".replay"
        r = requests.get(all_links[x] + "/file", headers={'Authorization': tokens[token_index]})
        print("Current index: {}/{}".format(current_index, line_count))
        print("Name:", name)
        print("Status code:", r.status_code)
        print("Token index:", token_index)
        print("------------------------------------------------------------------------------------------------")
        if r.status_code == 200:
            with open("downloads/{}/{}/{}".format(year, playlist, name), "wb") as f:
                f.write(r.content)
            current_index += 1
        else:
            token_index += 1
            if token_index == len(tokens):
                break

    with open("links/{}/{}.txt".format(year, playlist), 'r+') as f:
        index = f.readline()
        f.seek(0)
        f.write(str(current_index) + "\n")

    if line_count <= current_index:
        exit(0)

    time.sleep(600)
