from garden_lighting.web.web import new_group, new_device

root_display_name = "Alle"

port = 5000
token = ""
secret = ""

mcp23017_address_a = 0x20
mcp23017_address_b = 0x21
mcp23017_reset_a = 4
mcp23017_reset_b = 17


def register_devices(devices):
    south = new_group("Süden", "south", devices)

    west = new_group("Westen", "west", devices)
    hall = new_group("Halle", "hall", devices)

    south.register_device(new_device(5, "Pavilion", "1", south))
    hall.register_device(new_device(0, "Halle", "2", hall))

    south.register_device(new_device(4, "Brunnen", "3", south))
    west.register_device(new_device(1, "Wohnzimmer", "4", west))

    devices.register_device(south)
    devices.register_device(west)
    devices.register_device(hall)
