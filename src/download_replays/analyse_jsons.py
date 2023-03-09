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



replays_analysed = []
for path, subdirs, files in os.walk(f"analysis\\"):
    for name in files:
        if name != "queue.txt" and os.stat(os.path.join(path, name)).st_size != 0:
            replays_analysed.append(os.path.join(path, name))


gzip_data = []
# bz to json | reading
with gzip.open(replays_analysed[0], 'r') as f:
    gzip_data = json.loads(f.read().decode('utf-8'))

print(gzip_data[0])

for info in gzip_data:
    del info["GameState"]["time"]
    del info["GameState"]["seconds_remaining"]
    del info["GameState"]["deltatime"]
    print(info["GameState"].keys())
    print(info["PlayerData"][1].keys())
    break

