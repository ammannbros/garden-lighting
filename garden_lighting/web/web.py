from datetime import timedelta
from flask import Flask, render_template, jsonify, request
from flask.ext.libsass import Sass
from flask.ext.bower import Bower

import pkg_resources

from garden_lighting.web.devices import Action
from garden_lighting.web.config import get_all_devices
from garden_lighting.web.json import ComplexEncoder
from garden_lighting.web.scheduler import DeviceScheduler, Rule


app = Flask(__name__)
app.json_encoder = ComplexEncoder
Bower(app)

Sass(
    {'layout': 'static/sass/layout.scss',
     'lights': 'static/sass/lights.scss',
     'controls': 'static/sass/controls.scss'}, app,
    url_path='/static/sass/',
    include_paths=[
        pkg_resources.resource_filename('garden_lighting.web', 'static/sass'),
    ]
)

devices = get_all_devices()

scheduler = DeviceScheduler(0.5)


@app.route('/')
def lights():
    return overview()


@app.route('/areas/')
def overview():
    return render_template("lights.html", name="Bereiche", devices=devices.get_all_devices())


@app.route('/all_lights/')
def all_lights():
    return render_template("lights.html", name="Alle Lichter", devices=devices.get_all_devices_recursive())


@app.route('/controls/')
def controls():
    return render_template("controls.html", rules=scheduler.rules, devices=devices.get_all_devices_recursive())


@app.route('/about/')
def about():
    return render_template("about.html")


@app.route('/api/<slot>/on/')
def on(slot):
    app.logger.info("Turning " + slot + " on!")
    return handle_state(slot, Action.ON)


@app.route('/api/<slot>/off/')
def off(slot):
    app.logger.info("Turning " + slot + " off!")
    return handle_state(slot, Action.OFF)


@app.route('/api/<slot>/toggle/')
def toggle(slot):
    return handle_state(slot, Action.TOGGLE)


@app.route('/api/add_rules/', methods=['POST'])
def add_rules():
    json = request.get_json()

    if json is None:
        return jsonify(rules=scheduler.rules, success=False)

    for json_rule in json:
        rule_devices = []

        for device in json_rule['devices']:
            get_device = devices.get_device(device)
            if get_device is None:
                continue
            rule_devices.append(get_device)

        rule = Rule(json_rule['weekday'], rule_devices, timedelta(seconds=json_rule['time']), json_rule['action'])
        scheduler.rules.append(rule)

    return jsonify(rules=scheduler.rules, success=True)


def handle_state(slot, action):
    if action == "on":
        action = Action.ON
    elif action == "off":
        action = Action.OFF
    elif action == "toggle":
        action = Action.TOGGLE

    if slot == "all":
        success = devices.set(action)
    else:

        device = devices.get_device(slot)
        if device is not None:
            success = device.set(action)
        else:
            success = False

    return jsonify(success=success)


def start_web():
    app.run(host='0.0.0.0', debug=True)


