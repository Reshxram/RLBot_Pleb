import logging
import math
import time
from threading import Thread
import carball
import compress_json
import gzip
import numpy as np
import queue
import asyncio
import json
import os
import sys
import createTrainingData as ctd

from calendar import monthrange
from datetime import datetime
from tqdm import tqdm

# Disable all logger of carball
for name in logging.root.manager.loggerDict:
    if "carball" in name:
        logger = logging.getLogger(name)
        logger.disabled = True


# Build custom json encoder to handle all bool_
class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.bool_):
            return obj.tolist()
        '''if isinstance(obj, (np.floating, np.complexfloating)):
            return float(obj)
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, np.string_):
            return str(obj)'''
        return super(NpEncoder, self).default(obj)


def encode_json(replay_files):
    for x in tqdm(replay_files, total=len(replay_files), file=sys.stdout, leave=True, position=0):
        x = x.replace("downloads/replays", "").replace(".replay", "")

        data = ctd.creating_data(f"downloads/replays/{x}.replay")

        with gzip.open(f'analysis/environment/{x}.json.gz', 'wb') as f:
            f.write(json.dumps(data, cls=NpEncoder).encode("utf-8"))


def split(list_a, chunk_size):
    for i in range(0, len(list_a), chunk_size):
        yield list_a[i:i + chunk_size]


playlists = ["ranked-duels", "ranked-doubles", "ranked-standard"]

# read status.txt
status = {}
with open("analysis/status.txt", "r") as f:
    for line in f:
        key, value = line.strip().split(': ')
        status[key] = int(value)

year = status["Year"]
month = status["Month"]
day = status["Day"]
replay_links = []
for x in range(3):
    replay_links.append(f"{year}/{playlists[x]}/{month}/{day}")

    path = f"analysis/environment/{replay_links[x]}"
    if not os.path.exists(path):
        os.makedirs(path)

replay_files = []
for x in range(3):
    for path, subdirs, files in os.walk(f"downloads\\replays\\{replay_links[x]}"):
        for name in files:
            name = f"downloads/replays/{replay_links[x]}/" + name
            replay_files.append(name)

if len(replay_files) > 0:
    print(f"Processing {len(replay_files)} replays...")
    loop = asyncio.get_event_loop()

    chucked_replay_files = list(split(replay_files, math.ceil(len(replay_files) / 2)))


# bz to json | reading
'''with gzip.open(f'analysis/environment/{link}/{files[0].split(".")[0]}.json.bz', 'r') as fin:
    gzip_data = json.loads(fin.read().decode('utf-8'))'''

'''"how decompile a .replay file into .json format, save it locally(optional) returns extracted game frames data and controls"
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
print(gameData[500]["PlayerData"][0])'''

# update status.txt
status["Day"] += 1
if status["Day"] > monthrange(status["Year"], status["Month"])[1]:
    status["Day"] = 1
    status["Month"] += 1
if status["Month"] > 12:
    status["Month"] = 1
    status["Year"] += 1
if f'{status["Day"]}-{status["Month"]}-{status["Year"]}' == datetime.today().strftime('%d-%m-%Y'):
    exit(0)

new_status = ""
for key, value in status.items():
    # add key-value pair to output string
    new_status += f"{key}: {value}\n"

with open("analysis/status.txt", "w") as f:
    f.write(new_status)
