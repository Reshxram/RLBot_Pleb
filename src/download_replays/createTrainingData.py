import logging

from carball.json_parser.game import Game
from carball.analysis.analysis_manager import AnalysisManager
from carball.controls.controls import ControlsCreator
import math
import os
import json
import carball
import pickle
import bz2
import sys

from tqdm import tqdm


def convert_replay_to_game_frames(inputName, JSONpath, save_json=True):
    _json = carball.decompile_replay(inputName)

    game = Game()
    game.initialize(loaded_json=_json)

    analysis_manager = AnalysisManager(game)
    analysis_manager.create_analysis()

    json_object = analysis_manager.get_json_data()
    with open(JSONpath, 'w+') as j_file:
        json.dump(json_object, j_file)

    result = convert_json_to_game_frames(JSONpath)
    if not save_json:
        os.remove(JSONpath)
    return result
    # return None


def duplicateFrameCheck(frame1, frame2):
    if frame1["GameState"]["ball"]["position"] != frame2["GameState"]["ball"]["position"]:
        return False
    if frame1["GameState"]["ball"]["velocity"] != frame2["GameState"]["ball"]["velocity"]:
        return False
    if frame1["GameState"]["ball"]["rotation"] != frame2["GameState"]["ball"]["rotation"]:
        return False
    for i in range(len(frame1["PlayerData"])):
        if frame1["PlayerData"][i]["position"] != frame2["PlayerData"][i]["position"]:
            return False
        if frame1["PlayerData"][i]["velocity"] != frame2["PlayerData"][i]["velocity"]:
            return False
        if frame1["PlayerData"][i]["angular_velocity"] != frame2["PlayerData"][i]["angular_velocity"]:
            return False
        if frame1["PlayerData"][i]["rotation"] != frame2["PlayerData"][i]["rotation"]:
            return False
    return True


def velocity_scaler(vel):
    if vel != 0:
        vel = vel / 10
    return vel


def angular_vecloty_scaler(a_vel):
    if a_vel != 0:
        a_vel = a_vel / 1000
    return a_vel


def creating_data(replay_location="", json_path=""):
    _json = carball.decompile_replay(replay_location)

    game = Game()
    game.initialize(loaded_json=_json)

    analysis_manager = AnalysisManager(game)
    analysis_manager.create_analysis()

    x = ControlsCreator()
    x.get_controls(game)
    frames = []
    total = 0
    duplicates = 0
    previous_frame = None
    for col, row in tqdm(analysis_manager.data_frame.iterrows(), total=sum(1 for dummy in analysis_manager.data_frame.iterrows()), file=sys.stdout, leave=True, position=0):
        frame = {}
        frame["GameState"] = {}
        frame["GameState"]["time"] = NaN_fixer(row["game"]["time"])
        frame["GameState"]["seconds_remaining"] = NaN_fixer(row["game"]["seconds_remaining"])
        frame["GameState"]["deltatime"] = NaN_fixer(row["game"]["delta"])
        frame["GameState"]["ball"] = {}
        frame["GameState"]["ball"]["position"] = [NaN_fixer(row["ball"]["pos_x"]), NaN_fixer(row["ball"]["pos_y"]),
                                                  NaN_fixer(row["ball"]["pos_z"])]
        frame["GameState"]["ball"]["velocity"] = [velocity_scaler(NaN_fixer(row["ball"]["vel_x"])),
                                                  velocity_scaler(NaN_fixer(row["ball"]["vel_y"])),
                                                  velocity_scaler(NaN_fixer(row["ball"]["vel_z"]))]
        frame["GameState"]["ball"]["rotation"] = [NaN_fixer(row["ball"]["rot_x"]), NaN_fixer(row["ball"]["rot_y"]),
                                                  NaN_fixer(row["ball"]["rot_z"])]
        frame["PlayerData"] = []
        for i in range(len(game.players)):
            frame["PlayerData"].append(getPlayerFrame(game.players[i], i, col, row))

        if previous_frame != None:
            if duplicateFrameCheck(frame, previous_frame):
                total += 1
                duplicates += 1
                continue

        previous_frame = frame
        frames.append(frame)
        total += 1

    return frames


def convert_json_to_game_frames(filename):
    with open(filename, encoding='utf-8', errors='ignore') as json_file:
        _json = json.load(json_file)

    game = Game()
    game.initialize(loaded_json=_json)

    analysis = AnalysisManager(game)
    analysis.create_analysis()

    x = ControlsCreator()
    x.get_controls(game)
    frames = []
    total = 0
    duplicates = 0
    previous_frame = None
    for col, row in analysis.data_frame.iterrows():
        frame = {}
        frame["GameState"] = {}
        frame["GameState"]["time"] = NaN_fixer(row["game"]["time"])
        frame["GameState"]["seconds_remaining"] = NaN_fixer(row["game"]["seconds_remaining"])
        frame["GameState"]["deltatime"] = NaN_fixer(row["game"]["delta"])
        frame["GameState"]["ball"] = {}
        frame["GameState"]["ball"]["position"] = [NaN_fixer(row["ball"]["pos_x"]), NaN_fixer(row["ball"]["pos_y"]),
                                                  NaN_fixer(row["ball"]["pos_z"])]
        frame["GameState"]["ball"]["velocity"] = [velocity_scaler(NaN_fixer(row["ball"]["vel_x"])),
                                                  velocity_scaler(NaN_fixer(row["ball"]["vel_y"])),
                                                  velocity_scaler(NaN_fixer(row["ball"]["vel_z"]))]
        frame["GameState"]["ball"]["rotation"] = [NaN_fixer(row["ball"]["rot_x"]), NaN_fixer(row["ball"]["rot_y"]),
                                                  NaN_fixer(row["ball"]["rot_z"])]
        frame["PlayerData"] = []
        for i in range(len(game.players)):
            frame["PlayerData"].append(getPlayerFrame(game.players[i], i, col, row))

        if previous_frame != None:
            if duplicateFrameCheck(frame, previous_frame):
                total += 1
                duplicates += 1
                continue

        previous_frame = frame
        frames.append(frame)
        total += 1

    return frames


def getPlayerFrame(player, playerIndex, frameIndex, row):
    controls = ["throttle", "steer", "pitch", "yaw", "roll", "jump", "handbrake"]
    playerData = {}
    playerData["index"] = playerIndex
    playerData["name"] = player.name
    if player.team.is_orange:
        playerData["team"] = 1
    else:
        playerData["team"] = 0

    playerData["position"] = [NaN_fixer(row[player.name]["pos_x"]), NaN_fixer(row[player.name]["pos_y"]),
                              NaN_fixer(row[player.name]["pos_z"])]
    playerData["rotation"] = [NaN_fixer(row[player.name]["rot_x"]), NaN_fixer(row[player.name]["rot_y"]),
                              NaN_fixer(row[player.name]["rot_z"])]
    playerData["velocity"] = [velocity_scaler(NaN_fixer(row[player.name]["vel_x"])),
                              velocity_scaler(NaN_fixer(row[player.name]["vel_y"])),
                              velocity_scaler(NaN_fixer(row[player.name]["vel_z"]))]
    playerData["angular_velocity"] = [angular_vecloty_scaler(NaN_fixer(row[player.name]["ang_vel_x"])),
                                      angular_vecloty_scaler(NaN_fixer(row[player.name]["ang_vel_y"])),
                                      angular_vecloty_scaler(NaN_fixer(row[player.name]["ang_vel_z"]))]
    playerData["boosting"] = NaN_fixer(row[player.name]["boost_active"])
    boost = NaN_fixer(row[player.name]["boost"])
    if boost > 0:
        boost = math.ceil((boost / 255) * 100)
    playerData["boost_level"] = int(boost)

    for c in controls:
        temp = NaN_fixer(player.controls.loc[frameIndex, c])
        if temp == None:
            temp = False
        playerData[c] = temp

    return playerData


def createAndSaveReplayTrainingDataFromJSON(replayPath, outputFileName=None):
    replayData = convert_json_to_game_frames(replayPath)

    if outputFileName != None:
        outputName = outputFileName
    else:
        outputName = replayPath + ".pbz2"

    with bz2.BZ2File(outputName, 'w') as f:
        pickle.dump(replayData, f)


def createAndSaveReplayTrainingData(replayPath, outputName, jsonPath, save_json=True):
    replayData = convert_replay_to_game_frames(replayPath, jsonPath, save_json=save_json)
    with bz2.BZ2File(outputName, 'w') as f:
        pickle.dump(replayData, f)


def loadSavedTrainingData(dataPath):
    with bz2.BZ2File(dataPath, 'r') as f:
        result = pickle.load(f)

    return result


def createDataFromReplay(filepath, outputPath, jsonPath, save_json=True):
    carball.decompile_replay(filepath)
    createAndSaveReplayTrainingDataFromJSON(jsonPath, outputFileName=outputPath)
    if not save_json:
        os.remove(jsonPath)


def NaN_fixer(value):
    if value is None or math.isnan(value):
        return 0
    else:
        return value
