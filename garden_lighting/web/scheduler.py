from enum import Enum, unique
from datetime import datetime, timedelta
from uuid import UUID
import pickle

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


def now_rule(unique_uid, devices, action, time_delta=0):
    current = datetime.now() + timedelta(seconds=time_delta)
    return Rule(unique_uid, Weekday(current.weekday()), devices, to_timedelta(current), action)


def to_timedelta(time):
    return timedelta(seconds=time.hour * 60 * 60 + time.minute * 60 + time.second)


class Rule(object):
    def __getstate__(self):
        state = dict(self.__dict__)
        state['uuid'] = str(state['uuid'])
        return state

    def __getjsonifystate__(rule):
        state = rule.__getstate__()
        state['action'] = str(state['action'])
        state['time'] = state['time'].total_seconds()
        state['weekday'] = state['weekday'].value
        state['devices'] = [device.__getstate__() for device in state['devices']]
        return state

    def __setstate__(self, dict):
        dict['uuid'] = UUID('{' + dict['uuid'] + '}')
        self.__dict__.update(dict)

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

    def __lt__(self, other):
        return not self.__gt__(other)

    def __gt__(self, other):
        return self.weekday.value < other.weekday.value or self.weekday.value == other.weekday.value and self.time < other.time


def process_super_rule(rule, device, actions):
    if rule.action == Action.ON:
        device.control_manually()
    elif rule.action == Action.OFF:
        device.control_automatically()

    actions[device.slot] = rule.action


class DeviceScheduler:
    def __init__(self, delay, devices, control, logger):
        self.logger = logger
        self.control = control
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

                    if device.is_controlled_automatically():  # Don't control while it's controlled by a super
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

        on = [light for light, value in actions.items() if value == Action.ON]
        off = [light for light, value in actions.items() if value == Action.OFF]

        self.control.set_lights(1, on)
        self.control.set_lights(0, off)

    def get_next_action_date(self, device):
        rules = [rule for rule in self.rules if device in rule.devices]

        rule = device.get_super_stop()
        if rule is not None:

            if rules:
                if rule < rules[0]:
                    return rule.time, rule.action
            else:
                return rule.time, rule.action

        return None if not rules else (rules[0].time, rules[0].action)

    def add_rule(self, rule):
        self.rules.append(rule)
        self.rules.sort(key=lambda r: r.time)

    def remove_rule(self, uuid):
        previous = len(self.rules)
        self.rules = [rule for rule in self.rules if rule.uuid != uuid]
        return previous != len(self.rules)

    def write(self):
        try:
            rules_file = open("rules.json", "wb")
            pickle.dump(self.rules, rules_file)
            rules_file.flush()
            rules_file.close()
            return True
        except EnvironmentError:
            return False

    def read(self, devices):
        try:
            with open("rules.json", "rb") as rules_file:
                try:
                    rules = pickle.load(rules_file)
                except ValueError as e:
                    self.logger.warning("Invalid rules file")
                    self.logger.exception(e)
                    return

                for rule in rules:
                    rule_devices = rule.devices[:]
                    rule.devices = []
                    for device in rule_devices:
                        rule.devices.append(devices.get_device(device.short_name))

                rules_file.close()
                return True
        except FileNotFoundError:
            pass
        except IOError as e:
            self.logger.exception(e)



