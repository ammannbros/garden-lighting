from flask import Blueprint, render_template
from garden_lighting.web.web import auth, scheduler, devices

control = Blueprint('control', __name__, url_prefix='/control')


@control.route('/')
def controls():
    if not auth.auth():
        return auth.fucked_auth()
    return render_template("control.html", rules=scheduler.rules, devices=devices.get_all_devices_recursive())

