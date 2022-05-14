import datetime
from typing import Union, Dict
from dateutil import parser


class Task():
    def __init__(
        self,
        user: str,
        userDisplayName: str = None,
        work: str = "Work",
        done: bool = False,
        startTime: datetime.datetime = None,
    ):
        self.user = user
        self.userDisplayName = userDisplayName if userDisplayName else user
        self.work = work
        self.done = done
        if (startTime is None):
            self.startTime = datetime.datetime.now()
        elif (type(startTime) is str):
            self.startTime = parser.parse(startTime)
        else:
            self.startTime = startTime

    @property
    def timeTaken(self) -> datetime.timedelta:
        return datetime.datetime.now() - self.startTime

    @property
    def timeTakenM(self) -> int:
        return round(self.timeTaken.total_seconds() / 60)

    def __str__(self) -> str:
        text = f"{self.userDisplayName}: {self.work}"
        return text



class Timer():
    def __init__(
        self,
        user: str,
        studyPeriod: int,
        breakPeriod: int,
        iterations: int,
        iterStartTime: Union[datetime.datetime, str],
        work: str = "work",
        userDisplayName: str = None,
        currentIteration: int = 1,
        study_mode: bool = True,
        iterEndTime: str = None,
        pausedAtTimeLeft: str = None,
        chat_mode=False,
    ):
        self.user: str = user
        self.userDisplayName: str = userDisplayName if userDisplayName else user
        self.studyPeriod: float = studyPeriod
        self.breakPeriod: float = breakPeriod
        self.iterations: int = iterations
        self.iterStartTime: datetime.datetime = parser.parse(
            iterStartTime) if (type(iterStartTime) is str) else iterStartTime
        self.work: str = work
        self.currentIteration: int = currentIteration
        self.study_mode: bool = study_mode
        self.iterEndTime: datetime.datetime = parser.parse(
            iterEndTime) if iterEndTime else (
                self.iterStartTime +
                datetime.timedelta(minutes=self.studyPeriod))
        if(pausedAtTimeLeft):
            t = datetime.strptime(pausedAtTimeLeft,"%H:%M:%S")
            self.pausedAtTimeLeft: datetime.timedelta = datetime.timedelta(hours=t.hour, minutes=t.minute, seconds=t.second)
        else:
            self.pausedAtTimeLeft: datetime.timedelta = None
        self.chat_mode: bool = chat_mode

    def nextIter(self) -> bool:
        if(self.paused):
            self.resume()
            return True

        self.iterStartTime = datetime.datetime.now()

        if (self.study_mode and self.breakPeriod != 0):
            self.study_mode = False
            self.iterEndTime = self.iterStartTime + datetime.timedelta(
                minutes=self.breakPeriod)

        elif (not (self.study_mode)
              and self.currentIteration + 1 <= self.iterations):
            self.study_mode = True
            self.currentIteration += 1
            self.iterEndTime = self.iterStartTime + datetime.timedelta(
                minutes=self.studyPeriod)

        else:
            return False

        return True

    def addTime(self, minutes: float):
        self.iterEndTime += datetime.timedelta(minutes=minutes)

    def triggerChatMode(self, set=True):
        self.chat_mode = set

    def pause(self, pausePeriod):
        self.iterStartTime = datetime.datetime.now()
        self.pausedAtTimeLeft = self.timeLeft
        self.iterEndTime = self.iterStartTime + datetime.timedelta(
                minutes=self.studyPeriod)

    def resume(self):
        self.iterStartTime = datetime.datetime.now()
        self.iterEndTime = self.iterStartTime + self.pausedAtTimeLeft
        self.pausedAtTimeLeft = None

    @property
    def paused(self,) -> bool:
        return not(self.pausedAtTimeLeft is None)

    @property
    def timeLeft(self) -> datetime.timedelta:
        return self.iterEndTime - datetime.datetime.now()

    def __str__(self) -> str:
        text = f"{self.userDisplayName}: {self.work} {round(self.timeLeft.total_seconds() / 60)}"
        if (self.iterations):
            text += f" ({self.currentIteration} of {self.iterations})"
        return text


class Pomo():
    def __init__(self):
        self.active_timers: Dict[str, Dict[str, Timer]] = dict()

    def get_timer(self, channel: str, user: str) -> Union[Timer, None]:
        channel, user = channel.lower(), user.lower()
        try:
            return self.active_timers[channel][user]
        except KeyError:
            return None

    def add_timer(self, channel: str, user: str, timer: Timer) -> Timer:
        channel, user = channel.lower(), user.lower()
        try:
            self.active_timers[channel][user] = timer
        except KeyError:
            self.active_timers[channel] = dict()
            self.active_timers[channel][user] = timer
        return timer

    def set_timer(self,
                  channel: str,
                  user: str,
                  studyPeriod: int,
                  breakPeriod: int = 0,
                  iterations: int = 1,
                  work: str = "work",
                  **kwargs) -> Timer:
        channel, user = channel.lower(), user.lower()
        current_time = datetime.datetime.now()
        timer = Timer(
            user,
            studyPeriod,
            breakPeriod,
            iterations,
            current_time,
            work,
            **kwargs,
        )
        try:
            self.active_timers[channel][user] = timer
        except KeyError:
            self.active_timers[channel] = dict()
            self.active_timers[channel][user] = timer
        return timer

    def time_left(self, channel: str, username: str) -> int:
        channel, username = channel.lower(), username.lower()
        user = self.get_timer(channel, username)
        if user is not None:
            time = user.timeLeft
            return round(time.total_seconds() / 60)

    def cancel_timer(self, channel: str, username: str):
        channel, username = channel.lower(), username.lower()
        user = self.get_timer(channel, username)
        if user is not None:
            self.active_timers[channel].pop(username)
            return True
        return False
