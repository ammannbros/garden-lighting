from garden_lighting.web.devices import DefaultDevice, DeviceGroup


def get_all_devices():
    devices = DeviceGroup("root", "root")

    south = DeviceGroup("Süden", "south")
    west = DeviceGroup("Westen", "west")
    hall = DeviceGroup("Halle", "hall")

    south.register_device(DefaultDevice(0, "Pavilion", "1"))
    hall.register_device(DefaultDevice(1, "Halle", "2"))

    south.register_device(DefaultDevice(4, "Brunnen", "3"))
    west.register_device(DefaultDevice(5, "Wohnzimmer", "4"))

    devices.register_device(south)
    devices.register_device(west)
    devices.register_device(hall)

    return devices

