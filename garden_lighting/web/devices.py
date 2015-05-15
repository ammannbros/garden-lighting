from abc import abstractmethod
from enum import Enum
import collections


class Action(Enum):
    OFF = 0,
    ON = 1,


class Device:
    def __init__(self, name, short_name, light_control, scheduler):
        self.scheduler = scheduler
        self.light_control = light_control
        self.short_name = short_name
        self.name = name

    @abstractmethod
    def is_on(self):
        pass

    @abstractmethod
    def is_off(self):
        pass

    @abstractmethod
    def is_group(self):
        pass

    def set(self, action):
        batch = []
        self.collect_batch(batch)

        slots = [device.slot for device in batch]

        if action == Action.ON:
            self.light_control.set_multiple_lights(True, slots)
            return batch
        elif action == Action.OFF:
            self.light_control.set_multiple_lights(False, slots)
            return batch
        else:
            raise ()

    @abstractmethod
    def collect_batch(self, batch):
        pass


class DeviceGroup(Device):
    def is_group(self):
        return True

    def __init__(self, name, short_name, light_control, scheduler):
        super().__init__(name, short_name, light_control, scheduler)
        self.light_control = light_control
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

    def collect_batch(self, batch):
        for key in self.devices:
            device = self.devices[key]
            device.collect_batch(batch)

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
    def is_group(self):
        return False

    def __init__(self, slot, name, short_name, light_control, scheduler):
        super().__init__(name, short_name, light_control, scheduler)
        self.slot = slot
        self.manually = False

    def is_off(self):
        return not self.is_on()

    def is_on(self):
        return self.light_control.read_light(self.slot)

    def collect_batch(self, batch):
        batch.append(self)

    def is_controlled_manually(self):
        return self.manually

    def is_controlled_automatically(self):
        return not self.manually

    def control_manually(self):
        self.manually = True

    def control_automatically(self):
        self.manually = False
