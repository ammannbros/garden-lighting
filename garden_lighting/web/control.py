from flask import Blueprint, render_template
from markupsafe import Markup
from garden_lighting.web.web import scheduler, devices, log

control = Blueprint('control', __name__, url_prefix='/control')


@control.route('/')
def controls():
    return render_template("control.html", rules=scheduler.rules, devices=devices.get_all_devices_recursive())

@control.route('/log/')
def logs():
    message = Markup(log.getvalue().replace('\n', '</br>'))
    return render_template("log.html", log=message)

