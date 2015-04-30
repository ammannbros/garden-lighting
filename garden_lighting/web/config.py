from garden_lighting.web.devices import DefaultDevice, DeviceGroup


def get_all_devices():
    devices = DeviceGroup("root", "root")
    group1 = DeviceGroup("Bereich #1", "area1")
    group2 = DeviceGroup("Bereich #2", "area2")
    group3 = DeviceGroup("Bereich #3", "area3")

    group1.register_device(DefaultDevice(0, "Garten #1", "1"))
    group1.register_device(DefaultDevice(1, "Garten #2", "2"))
    group1.register_device(DefaultDevice(2, "Garten #3", "3"))
    group2.register_device(DefaultDevice(3, "Garten #4", "4"))
    group2.register_device(DefaultDevice(4, "Garten #5", "5"))
    group2.register_device(DefaultDevice(5, "Garten #6", "6"))
    group3.register_device(DefaultDevice(6, "Garten #7", "7"))
    group3.register_device(DefaultDevice(7, "Garten #8", "8"))
    group3.register_device(DefaultDevice(8, "Garten #9", "9"))
    group3.register_device(DefaultDevice(8, "Garten #9", "9"))

    devices.register_device(group1)
    devices.register_device(group2)
    devices.register_device(group3)

    return devices

