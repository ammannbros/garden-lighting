from abc import abstractmethod
from enum import Enum
import collections


class Action(Enum):
    OFF = 0,
    ON = 1,

    def __str__(self):
        return "on" if self == Action.ON else "off" if self == Action.OFF else None

    def opposite(self):
        return Action.OFF if self == Action.ON else Action.ON


def action_from_string(name):
    return Action.ON if name == "on" else Action.OFF if name == "off" else None


class Device(object):

    def __getstate__(self):
        state = dict(self.__dict__)
        result = {'display_name': state['display_name'], 'short_name': state['short_name']}
        return result

    def __init__(self, display_name, short_name, light_control):
        self.light_control = light_control
        self.short_name = short_name
        self.display_name = display_name

    @abstractmethod
    def is_group(self):
        pass

    def set(self, action):
        batch = []
        self.collect_real(batch)

        slots = [device.slot for device in batch]

        if action == Action.ON:
            self.light_control.set_lights(True, slots)
            return batch
        elif action == Action.OFF:
            self.light_control.set_lights(False, slots)
            return batch
        else:
            raise ()

    @abstractmethod
    def collect_real(self, batch):
        pass

    @abstractmethod
    def collect_all(self, batch):
        pass

    @abstractmethod
    def is_controlled_manually(self):
        pass

    @abstractmethod
    def is_controlled_automatically(self):
        pass

    @abstractmethod
    def get_real_devices_recursive(self):
        pass

    @abstractmethod
    def get_all_devices_recursive(self):
        pass

    @abstractmethod
    def get_super_start(self):
        pass

    @abstractmethod
    def get_super_stop(self):
        pass


class DeviceGroup(Device):

    def is_group(self):
        return True

    def __init__(self, display_name, short_name, light_control):
        super().__init__(display_name, short_name, light_control)
        self.light_control = light_control
        self.devices = collections.OrderedDict()

    def register_device(self, device):
        self.devices[device.short_name] = device

    def has_device(self, name):
        return name in self.devices

    def get_device(self, name):
        ret = None

        try:
            ret = self.devices[name]
        except KeyError:
            for key in self.devices:
                device = self.devices[key]
                if type(device) is DeviceGroup:
                    found = device.get_device(name)
                    if found is not None:
                        return found

        return ret

    def collect_real(self, batch):
        for key in self.devices:
            device = self.devices[key]
            device.collect_real(batch)

    def get_real_devices_recursive(self):
        batch = []
        self.collect_real(batch)
        return batch

    def collect_all(self, batch):
        batch.append(self)
        for key in self.devices:
            device = self.devices[key]
            device.collect_all(batch)
        pass

    def get_all_devices_recursive(self):
        batch = []
        self.collect_all(batch)
        return batch

    def get_devices(self):
        all_devices = []
        for key in self.devices:
            device = self.devices[key]
            all_devices.append(device)

        return all_devices

    def is_controlled_manually(self):
        for device in self.get_real_devices_recursive():
            if not device.is_controlled_manually():
                return False
        return True

    def is_controlled_automatically(self):
        for device in self.get_real_devices_recursive():
            if not device.is_controlled_manually():
                return False
        return True

    def get_super_start(self):
        devices = self.get_real_devices_recursive()
        rules = [device.super_rule_start for device in devices]

        if rules.count(rules[0]) == len(rules):
            return rules[0]

        return None

    def get_super_stop(self):
        devices = self.get_real_devices_recursive()
        rules = [device.super_rule_stop for device in devices if device.super_rule_stop is not None]
        uuids = [rule.uuid for rule in rules]

        if rules and len(devices) == len(rules) and equal(uuids):
            return rules[0]
        pass


def equal(iterator):
    try:
        iterator = iter(iterator)
        first = next(iterator)
        return all(first == rest for rest in iterator)
    except StopIteration:
        return True


class DefaultDevice(Device):

    def is_group(self):
        return False

    def __init__(self, slot, display_name, short_name, light_control):
        super().__init__(display_name, short_name, light_control)
        self.slot = slot
        self.manually = False
        self.super_rule_start = None
        self.super_rule_stop = None

    def collect_real(self, batch):
        batch.append(self)

    def collect_all(self, batch):
        self.collect_real(batch)

    def is_controlled_manually(self):
        return self.manually

    def is_controlled_automatically(self):
        return not self.manually

    def control_manually(self):
        self.manually = True

    def control_automatically(self):
        self.manually = False

    def get_real_devices_recursive(self):
        return [self]

    def get_all_devices_recursive(self):
        self.get_real_devices_recursive()

    def get_super_start(self):
        return self.super_rule_start

    def clear_super_rule(self):
        self.super_rule_start = None
        self.super_rule_stop = None

    def clear_super_start(self):
        self.super_rule_start = None

    def clear_super_stop(self):
        self.super_rule_stop = None

    def get_super_stop(self):
        return self.super_rule_stop
