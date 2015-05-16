from json import JSONEncoder
from garden_lighting.web.devices import Device
from garden_lighting.web.scheduler import Rule


class ComplexEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Rule):
            rule = {'weekday': obj.weekday.value,
                    'time': obj.time.total_seconds(),
                    'action': str(obj.action),
                    'uuid': str(obj.uuid)}

            devices = []

            for device in obj.devices:
                devices.append(self.default(device))

            rule['devices'] = devices

            return rule
        elif isinstance(obj, Device):
            return {"name": obj.display_name, "short_name": obj.short_name};

        return JSONEncoder.default(self, obj)