from time import sleep
from threading import Thread
from enum import Enum, unique
from datetime import datetime, timedelta
from flask import json
from uuid import UUID
import uuid
from garden_lighting.web.devices import Action, action_from_string
from garden_lighting.web.web import app


@unique
class Weekday(Enum):
    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6


def now_rule(unique_uid, devices, action, time_delta=0):
    current = datetime.now() + timedelta(seconds=time_delta)
    return Rule(unique_uid, Weekday(current.weekday()), devices, to_timedelta(current), action)


def to_timedelta(time):
    return timedelta(seconds=time.hour * 60 * 60 + time.minute * 60 + time.second)


class Rule:
    def __init__(self, unique_uid, weekday, devices, time, action):
        self.uuid = unique_uid
        self.action = action
        self.weekday = weekday
        self.devices = devices
        self.time = time

    def is_overdue(self):
        current = datetime.now()

        if Weekday(current.weekday()) is not self.weekday:
            return False

        return self.time.total_seconds() < to_timedelta(current).total_seconds()


def process_super_rule(rule, device, actions):
    if rule.action == Action.ON:
        device.control_manually()
    elif rule.action == Action.OFF:
        device.control_automatically()

    actions[device.slot] = rule.action


class DeviceScheduler:
    def __init__(self, delay, devices):
        self.devices = devices
        self.lastTime = datetime.today()
        self.running = False
        self.delay = delay
        self.rules = []
        self.super_rules = []
        self.manual_devices = []

    def run(self):
        actions = {}

        for rule in self.rules:

            if rule.is_overdue():

                for device in rule.devices:

                    if device.is_control_automatically():  # Don't control while it's controlled by a super
                        actions[device.slot] = rule.action  # rule or is in manual mode

        # Super rules
        for device in self.devices.get_real_devices_recursive():

            start = device.get_super_start()
            stop = device.get_super_stop()
            if start is not None and start.is_overdue():
                process_super_rule(start, device, actions)
                device.clear_super_start()

            if stop is not None and stop.is_overdue():
                process_super_rule(stop, device, actions)
                device.clear_super_stop()

        # Print current settings
        if len(actions) > 0:
            app.logger.info(actions)

    def get_next_action_date(self, device):
        rules = [rule for rule in self.rules if device in rule.devices]

        rule = device.get_super_stop()
        if rule is not None:

            if rules:
                if rule.weekday.value < rules[0].weekday.value or rule.weekday.value == rules[0].weekday.value and rule.time < rules[0].time:
                    return rule.time, rule.action
            else:
                return rule.time, rule.action

        return None if not rules else (rules[0].time, rules[0].action)

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

    # def remove_super_rule_for_device(self, device):
    # # Find rules
    # for_device = self.get_super_rules_for_device(device)
    # for rule in for_device:
    # for dev in rule.devices:
    # dev.control_automatically()
    #
    # # Remove rules
    # previous = len(self.super_rules)
    # self.super_rules = [rule for rule in self.super_rules if rule not in for_device]
    # return previous != len(self.super_rules)

    # def get_super_rules_for_device(self, device):
    # devices = [device] if type(device) == DefaultDevice else device.devices.values()
    #
    # return [rule for rule in self.super_rules if devices == set(rule.devices)]

    # def add_super_rule(self, rule):
    #     self.super_rules.append(rule)
    #     self.super_rules.sort(key=lambda r: r.time)
    #
    # def remove_rule(self, unique_uid):
    #     previous = len(self.rules)
    #     self.rules = [rule for rule in self.rules if rule.uuid != unique_uid]
    #     return previous != len(self.rules)

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
                    action_from_string(json_rule['action'])
                )
                self.add_rule(rule)
                pass

            rules_file.close()
            return True
        except ValueError:
            return False


