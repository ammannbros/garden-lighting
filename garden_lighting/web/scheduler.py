from time import sleep
from threading import Thread
from enum import Enum, unique
from datetime import datetime, timedelta
from flask import json
from uuid import UUID


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
    def __init__(self, uuid, weekday, devices, time, action):
        self.uuid = uuid
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

    def remove_rule(self, uuid):
        previous = len(self.rules)
        self.rules = [rule for rule in self.rules if rule.uuid != uuid]
        return previous != len(self.rules)

    def run(self):
        for rule in self.rules:
            if rule not in self.finished and rule.is_overdue():
                for device in rule.devices:
                    device.set(rule.action)
                self.finished.append(rule)

        # Reset after a day
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

    def add_rule(self, rule):
        self.rules.append(rule)

    def write(self):
        try:
            rules_file = open("rules.json", "w")
            rules_file.write(json.dumps(self.rules))
            rules_file.close()
            return True
        except EnvironmentError:
            return False

    def read(self, devices):
        try:
            rules_file = open("rules.json", "r")
            rules = json.load(rules_file)

            for json_rule in rules:
                rule_devices = []

                for device in json_rule['devices']:
                    device = devices.get_device(device['short_name'])
                    if device is None:
                        continue

                    rule_devices.append(device)

                rule = Rule(
                    UUID('{' + json_rule['uuid'] + '}'),
                    json_rule['weekday'],
                    rule_devices,
                    timedelta(seconds=json_rule['time']),
                    json_rule['action']
                )
                self.rules.append(rule)
                pass

            rules_file.close()
            return True
        except ValueError:
            return False


