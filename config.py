from garden_lighting.web.web import new_group, new_device, devices

port = 5000
token = ""
secret = ""

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