import RattletrapPython.rattletrap as rat
import carball
import json
import os
import createTrainingData as ctd

from calendar import monthrange
from tqdm import tqdm

replay_path = "downloads/replays"

playlists = ["ranked-duels", "ranked-doubles", "ranked-standard"]

# read status.txt
status = {}
with open("analysis/status.txt", "r") as f:
    for line in f:
        key, value = line.strip().split(': ')
        status[key] = int(value)

playlist = playlists[status["Playlist"]]
year = status["Year"]
month = 2  # status["Month"]
day = 15  # status["Day"]
link = f"{year}/{playlist}/{month}/{day}"

# create folders if not existing
path = f"downloads/meta/{link}"
if not os.path.exists(path):
    os.makedirs(path)

path = f"analysis/environment/{link}"
if not os.path.exists(path):
    os.makedirs(path)

path = f"analysis/inputs/{link}"
if not os.path.exists(path):
    os.makedirs(path)

files = os.listdir(f"downloads/replays/{link}")

for x in files:
    _json = carball.decompile_replay(f"downloads/replays/{link}/" + x)
    with open(f'analysis/environment/{link}/{x.split(".")[0]}.json', "w", encoding='utf-8') as f:
        json.dump(_json, f, ensure_ascii=False)

exit(0)

"how decompile a .replay file into .json format, save it locally(optional) returns extracted game frames data and controls"
extractedGameStatesAndControls = ctd.convert_replay_to_game_frames(
    "rocket league replays/00C878424939F13B2E9643B905A5E833.replay", "test.json", save_json=True)

"how to extract game frames data and controls from a previously decompiled .json file"
x = ctd.convert_json_to_game_frames("PreviouslyUnpackedJson.json")

"how to load the data from a previously saved .pbz2 file"
gameData = ctd.loadSavedTrainingData("exampleSavedTrainingData.pbz2")

"uncomment below code and replace dummy arg with the path to a valid previously saved training data file. Run to see frame data format"
gameData = ctd.loadSavedTrainingData("insert valid path to saved training data")
print(f"This variable contains data for {len(gameData)} game frames in addition to controller input data")
print(gameData[500]["GameState"])
print(gameData[500]["PlayerData"][0])

exit(0)

# update status.txt
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
