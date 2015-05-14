from time import sleep
from threading import Thread
from enum import Enum, unique
from datetime import datetime, timedelta
from flask import json
from uuid import UUID
from garden_lighting.web.devices import Action


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
        current = datetime.now()

        if Weekday(current.weekday()) is not self.weekday:
            return False

        second_of_day = current.hour * 60 * 60 + current.minute * 60 + current.second
        return self.time.total_seconds() < second_of_day


class DeviceScheduler:
    def __init__(self, delay, rules=None):
        self.lastTime = datetime.today()
        self.running = False
        self.delay = delay
        if rules is None:
            self.rules = []
        else:
            self.rules = rules
        self.super_rules = []
        self.manual_devices = []

    def run(self):
        actions = {}

        for rule in self.rules:

            if rule.is_overdue():

                for device in rule.devices:

                    if not self.is_controlled_manually(device):  # Don't control while it's controlled by a super
                        actions[device.slot] = rule.action  # rule or is in manual mode

        # Super rules
        for rule in self.super_rules[:]:

            if rule.is_overdue():

                for device in rule.devices:
                    self.control_manually(rule.action, device.slot)

                    actions[device.slot] = rule.action
                self.super_rules.remove(rule)

        # Print current settings
        if len(actions) > 0:
            print(actions)

    def is_controlled_manually(self, device):
        return device.slot in self.manual_devices

    def control_manually(self, action, slot):
        if action == Action.ON and slot not in self.manual_devices:
            self.manual_devices.append(slot)  # Disable
        elif action == Action.OFF and slot in self.manual_devices:
            self.manual_devices.remove(slot)  # Enable

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

    def remove_super_rule(self, uuid):
        previous = len(self.super_rules)
        self.super_rules = [rule for rule in self.super_rules if rule.uuid != uuid]
        return previous != len(self.super_rules)

    def add_super_rule(self, rule):
        self.super_rules.append(rule)
        self.super_rules.sort(key=lambda r: r.time)

    def remove_rule(self, uuid):
        previous = len(self.rules)
        self.rules = [rule for rule in self.rules if rule.uuid != uuid]
        return previous != len(self.rules)

    def add_rule(self, rule):
        self.rules.append(rule)
        self.rules.sort(key=lambda r: r.time)

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
                    Weekday(json_rule['weekday']),
                    rule_devices,
                    timedelta(seconds=json_rule['time']),
                    json_rule['action']
                )
                self.add_rule(rule)
                pass

            rules_file.close()
            return True
        except ValueError:
            return False


