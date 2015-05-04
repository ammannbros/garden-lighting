from garden_lighting.web.devices import DefaultDevice, DeviceGroup


def get_all_devices():
    devices = DeviceGroup("root", "root")

    left = DeviceGroup("Links", "left")
    right = DeviceGroup("Rechts", "tight")

    left.register_device(DefaultDevice(0, "Pavilion", "1"))
    right.register_device(DefaultDevice(1, "Halle", "2"))
    right.register_device(DefaultDevice(2, "Brunnen", "3"))
    right.register_device(DefaultDevice(3, "Wohnzimmer", "4"))

    devices.register_device(left)
    devices.register_device(right)

    return devices

