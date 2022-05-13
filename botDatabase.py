from pomo_logic import Timer, Pomo, Task
from typing import MutableSequence, Union
import json
import glob
import os
try:
    from replit import db
    outputToFile = False
except:
    from threading import Thread
    import time
    outputToFile = True
    fileDir = "./"
    filenameSuffix = "pomoboard.txt"


def getChannels():
    if (outputToFile):
        files = glob.glob(fileDir + '*' + filenameSuffix)
        channels = [
            file.replace(fileDir, '', 1).replace(filenameSuffix, '', 1)
            for file in files
        ]
        return channels
    else:
        return list(db.keys())


def getTimers(channel: str) -> dict:
    if (outputToFile):
        return None
    else:
        return db[channel].value


def removeChannel(channel):
    channel = channel.lower()
    if (outputToFile):
        os.remove(fileDir + channel + filenameSuffix)
    else:
        try:
            del db[channel]
        except KeyError:
            return


def writeTimer(channel: str, timer: Union[Timer, Task]):
    channel = channel.lower()
    if (outputToFile):
        if (not timer is None):
            edited = False
            with open(fileDir + channel + filenameSuffix, 'r') as pomo:
                lines = pomo.readlines()
            lines.sort()
        with open(fileDir + channel + filenameSuffix, 'w') as pomo:
            for line in lines:
                if (not timer is None):
                    if (line.lower().startswith(timer.user + ' ')):
                        edited = True
                        line = str(timer)
                pomo.writeline(line)
            if (not edited):
                pomo.writeline(str(timer))
    else:
        if (not (channel in db.keys())):
            db[channel] = {}
        if (not timer is None):
            db[channel][timer.user] = json.dumps(timer.__dict__, default=str)


def removeTimer(channel: str, user: str):
    channel = channel.lower()
    if (outputToFile):
        with open(fileDir + channel + filenameSuffix, 'r') as pomo:
            lines = pomo.readlines()
        lines.sort()
        with open(fileDir + channel + filenameSuffix, 'w') as pomo:
            for line in lines:
                if (line.lower().startswith(user + ' ')):
                    continue
                pomo.writeline(line)
    else:
        db[channel].pop(user)


def updateAllTimers(channel: str, timers: MutableSequence[Timer]):
    channel = channel.lower()
    if (outputToFile):
        with open(fileDir + channel + filenameSuffix, 'w') as pomo:
            for timer in timers:
                pomo.writeline(str(timer))
    else:
        db[channel] = {}
        for timer in timers:
            db[channel][timer.user] = json.dumps(timer.__dict__, default=str)


def keepOutputtingToFile(pomo: Pomo, pomoTasks: dict, interval: float):
    while True:
        for channel, timersDict in pomo.active_timers.items():
            updateAllTimers(
                channel,
                list(timersDict.values()) + list(pomoTasks[channel].values()))
        time.sleep(interval)


def runFileOutputThread(pomo, pomoTasks=dict(), interval=5):
    t = Thread(target=keepOutputtingToFile, args=(
        pomo,
        pomoTasks,
        interval,
    ))
    t.start()
