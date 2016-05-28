import struct

import binascii
import time
from flask import Blueprint, request
from tinydb import TinyDB

from garden_lighting.web.web import temperature_path

temperature = Blueprint('temperature', __name__, url_prefix='/temperature')

db = TinyDB(temperature_path)
temperature_db = db.table('temperature')
BAT_EMPTY = 3.4 / 4.3 * 1024
BAT_FULL = 1024 - BAT_EMPTY

BAT_LENGTH = 2
UUID_LENGTH = 8
TEMP_LENGTH = 2
PACKET_LENGTH = UUID_LENGTH + TEMP_LENGTH


@temperature.route('/update', methods=['POST'])
def get_temperature():
    data = request.data
    length = len(data)

    if length < BAT_LENGTH:
        return "You need to specify at least the battery power!", 400

    battery_raw = struct.unpack_from("h", data, length - BAT_LENGTH)[0]
    battery = ((battery_raw - BAT_EMPTY) / BAT_FULL)

    for i in range(0, int(length / PACKET_LENGTH)):
        temp_raw = struct.unpack_from("h", data, i * PACKET_LENGTH + UUID_LENGTH)[0]
        temp = temp_raw / 128.0

        uuid_raw = data[i * PACKET_LENGTH:((i + 1) * PACKET_LENGTH) - TEMP_LENGTH]
        uuid = binascii.hexlify(uuid_raw).decode("utf-8")

        temperature_db.insert({'uuid': uuid, 'temp': temp, 'battery': round(battery, 2), 'date': round(time.time())})

    return "", 200
