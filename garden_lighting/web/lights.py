from flask import render_template, Blueprint
from garden_lighting.web.web import auth, scheduler

from garden_lighting.web.web import control, devices

lights = Blueprint('lights', __name__)


@lights.route('/')
def start():
    if not auth.auth():
        return auth.fucked_auth()
    return overview()


@lights.route('/areas/')
def overview():
    if not auth.auth():
        return auth.fucked_auth()
    all_devices = devices.get_all_devices()
    return render_template("lights.html", name="Bereiche", areas=True, devices=all_devices)


@lights.route('/all_lights/')
def all_lights():
    if not auth.auth():
        return auth.fucked_auth()
    all_devices = devices.get_all_devices_recursive()
    # batch = []
    # devices.collect_batch(batch)

    lights_pattern = control.read_multiple_lights(0) | control.read_multiple_lights(1) << 8

    ons = []

    for i in range(0, 16):
        is_on = ((lights_pattern & (1 << i)) != 0)
        if is_on:
            ons.append(i)

    return render_template("lights.html", name="Alle Lichter",
                           areas=False,
                           scheduler=scheduler,
                           ons=ons,
                           devices=all_devices)