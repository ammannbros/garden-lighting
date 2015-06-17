from flask import Blueprint, render_template
from markupsafe import Markup
from garden_lighting.web.web import scheduler, devices, log

control = Blueprint('control', __name__, url_prefix='/control')


@control.route('/')
def controls():
    return render_template("control.html", rules=scheduler.rules, devices=devices.get_all_devices_recursive())


@control.route('/log/')
def logs():
    try:
        with open("lighting.log", "r") as log_file:
            message = Markup('</br>'.join(reversed(log_file.readlines())))
    except FileNotFoundError:
        message = "No log"
    return render_template("log.html", log=message)
