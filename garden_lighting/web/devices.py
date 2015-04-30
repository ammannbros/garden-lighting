from abc import abstractmethod
from enum import Enum
import collections


class Action(Enum):
    OFF = 0,
    ON = 1,
    TOGGLE = 3


class Device:
    def __init__(self, name, short_name):
        self.short_name = short_name
        self.name = name

    @abstractmethod
    def is_on(self):
        pass

    @abstractmethod
    def on(self):
        pass

    @abstractmethod
    def is_off(self):
        pass

    @abstractmethod
    def off(self):
        pass

    def toggle(self):
        self.set(Action.TOGGLE)

    def set(self, action):
        if action == Action.ON:
            return self.on()
        elif action == Action.OFF:
            return self.off()
        elif action == Action.TOGGLE:
            return self.on() if self.is_on() else self.off()
        else:
            raise ()

    def is_overdue(self):
        pass

    def run_action(self):
        pass


class DeviceGroup(Device):
    def __init__(self, name, short_name):
        super().__init__(name, short_name)
        self.devices = collections.OrderedDict()

    def is_floating(self):
        return self.is_off() and self.is_on()

    def is_off(self):
        for device in self.devices:
            if device.is_on():
                return False
        return True

    def is_on(self):
        for device in self.devices:
            if device.is_off():
                return False
        return True

    def register_device(self, device):
        self.devices[device.name] = device

    def has_device(self, name):
        return name in self.devices

    def get_device(self, name):
        return self.devices[name]

    def on(self):
        return set(Action.ON)

    def off(self):
        return set(Action.OFF)

    def set(self, action):
        success = True
        for device in self.devices:
            if not device.set(action):
                if success:
                    success = False
        return success

    def get_all_devices(self):
        all_devices = []
        for key in self.devices:
            device = self.devices[key]
            all_devices.append(device)

        return all_devices

    def get_all_devices_recursive(self):
        all_devices = []
        self._get_all_devices_recursive(all_devices)
        return all_devices

    def _get_all_devices_recursive(self, all_devices):
        for key in self.devices:
            device = self.devices[key]

            all_devices.append(device)

            if type(device) is DeviceGroup:
                device._get_all_devices_recursive(all_devices)


class DefaultDevice(Device):
    def __init__(self, slot, name, short_name):
        super().__init__(name, short_name)
        self.slot = slot

    def is_off(self):
        return True

    def is_on(self):
        return False

    def on(self):
        return True

    def off(self):
        return True
