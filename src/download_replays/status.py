import os

from calendar import monthrange

replays_downloaded = []

for path, subdirs, files in os.walk(f"downloads\\replays\\"):
    for name in files:
        replays_downloaded.append(os.path.join(path, name))

replays_analysed = []

for path, subdirs, files in os.walk(f"analysis\\"):
    for name in files:
        if name != "queue.txt" and os.stat(os.path.join(path, name)).st_size != 0:
            replays_analysed.append(os.path.join(path, name))

replays = [item for item in replays_downloaded if "analysis\\" + "\\".join(item.split("\\")[2:]).replace(".replay", "") + ".json.gz" not in replays_analysed and item.split("\\")[2] == "2022"]
print("Total replays: ", len(replays_downloaded))
print("Replays analysed: ", len(replays_analysed))
print("Replays to go: ", len(replays))

with open("analysis/queue.txt", "w") as f:
    for replay in replays:
        f.write(replay + "\n")

