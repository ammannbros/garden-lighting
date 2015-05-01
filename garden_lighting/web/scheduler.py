from time import sleep
from threading import Thread
from enum import Enum, unique
from datetime import datetime

@unique
class Weekday(Enum):
    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6


class Rule:
    def __init__(self, weekday, devices, time, action):
        self.action = action
        self.weekday = weekday
        self.devices = devices
        self.time = time

    def is_overdue(self):
        current = datetime.utcnow()

        if Weekday(current.weekday()) is not self.weekday:
            return False

        second_of_day = current.hour * 60 * 60 + current.minute * 60 + current.second
        return self.time.total_seconds() > second_of_day


class DeviceScheduler:
    def __init__(self, delay, rules=None):
        self.finished = []
        self.lastTime = datetime.today()
        self.running = False
        self.delay = delay
        if rules is None:
            self.rules = []
        else:
            self.rules = rules

    def run(self):
        for rule in self.rules:
            if rule not in self.finished and rule.is_overdue():
                for device in rule.devices:
                    device.set(rule.action)
                self.finished.append(rule)

        current = datetime.today()

        if self.lastTime.hour == 23 and current.hour == 0:
            self.finished.clear()

        self.lastTime = current

    def start_scheduler(self):
        while self.running:
            self.run()
            sleep(self.delay)

    def stop_scheduler(self):
        self.running = False

    def start_scheduler_thread(self):
        self.running = True
        thread = Thread(target=self.start_scheduler)
        thread.start()


