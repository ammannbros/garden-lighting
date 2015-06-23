from flask import Blueprint, render_template
from smbus import smbus

temperature = Blueprint('temperature', __name__, url_prefix='/temperature')
bus = smbus.SMBus(1)

@temperature.route('/')
def get_temperature():
    data = bus.read_i2c_block_data(0x04, 0, 16)

    id = data[0]
    amount = data[1]
    temperatures = []

    for i in range(2, 2 + amount):
        temperatures.append(data[i])
    return render_template("temperature.html", temperature=temperatures[0])
