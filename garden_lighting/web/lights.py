from flask import render_template, Blueprint
from garden_lighting.web.web import scheduler

from garden_lighting.web.web import control, devices

lights = Blueprint('lights', __name__)


@lights.route('/')
def start():
    return overview()


@lights.route('/areas/')
def overview():
    all_devices = devices.get_devices()
    return render_template("lights.html", name="Bereiche",
                           areas=True,
                           scheduler=scheduler,
                           devices=all_devices)


@lights.route('/all_lights/')
def all_lights():
    all_devices = devices.get_real_devices_recursive()

    return render_template("lights.html", name="Alle Lichter",
                           areas=False,
                           scheduler=scheduler,
                           ons=control.get_lights(True),
                           devices=all_devices)