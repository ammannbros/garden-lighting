from flask import Blueprint, render_template, abort
from smbus import smbus
from garden_lighting.web.web import app

temperature = Blueprint('temperature', __name__, url_prefix='/temperature')
bus = smbus.SMBus(1)

HEADER = 6
TEMP_SIZE = 2
BUS = 0x10


@temperature.route('/')
def get_temperature():
    try:
        id = read_byte(0)

        millis = read_byte(1) | read_byte(2) << 8 | read_byte(4) << 16 | read_byte(5) << 32

        amount = read_byte(5)

        temperatures = []

        for i in range(HEADER, HEADER + amount * TEMP_SIZE, TEMP_SIZE):
            temperatures.append(read_byte(i) | read_byte(i + 1) << 8)

        return render_template("temperature.html", id=id, millis=millis, temperatures=temperatures)
    except Exception as e:
        app.logger.exception(e)
        return abort(500)


def read_byte(cmd):
    bus.write_byte(BUS, cmd)
    return bus.read_byte(BUS)
