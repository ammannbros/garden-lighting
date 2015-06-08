from garden_lighting.web.web import new_group, new_device

root_display_name = "Alle"

port = 5000
token = ""
secret = ""

mcp23017_addresses = [0x20, 0x21]
mcp23017_reset_pins = [4, 17]


def register_devices(devices):
    south = new_group("Süden", "south")

    west = new_group("Westen", "west")
    hall = new_group("Halle", "hall")

    south.register_device(new_device(0, "Pavilion", "1"))
    hall.register_device(new_device(1, "Halle", "2"))

    south.register_device(new_device(4, "Brunnen", "3"))
    west.register_device(new_device(5, "Wohnzimmer", "4"))

    devices.register_device(south)
    devices.register_device(west)
    devices.register_device(hall)
