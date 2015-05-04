from datetime import timedelta
from flask import Flask, render_template, jsonify, request
from flask.ext.libsass import Sass
from flask.ext.bower import Bower

import pkg_resources
from garden_lighting.lightControl import LightControl
import uuid

app = Flask(__name__)

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

app.logger.info("Initialising hardware interface!")
control = None
control = LightControl()
control.init()

from garden_lighting.web.devices import Action
from garden_lighting.web.config import get_all_devices
from garden_lighting.web.scheduler import DeviceScheduler, Rule

devices = get_all_devices()
scheduler = DeviceScheduler(0.5)

from garden_lighting.web.json import ComplexEncoder

app.json_encoder = ComplexEncoder


@app.route('/')
def lights():
    return overview()


@app.route('/areas/')
def overview():
    all_devices = devices.get_all_devices()
    return render_template("lights.html", name="Bereiche", areas=True, devices=all_devices)


@app.route('/all_lights/')
def all_lights():
    all_devices = devices.get_all_devices_recursive()
    batch = []
    devices.collect_batch(batch)

    lights_pattern = 0xFFFF
    lights_pattern = control.read_multiple_lights(0) | control.read_multiple_lights(1) << 8

    ons = []

    for i in range(0, 16):
        is_on = ((lights_pattern & (1 << i)) != 0)
        if is_on:
            ons.append(i)

    return render_template("lights.html", name="Alle Lichter",
                           areas=False,
                           ons=ons,
                           devices=all_devices)


@app.route('/controls/')
def controls():
    return render_template("controls.html", rules=scheduler.rules, devices=devices.get_all_devices_recursive())


@app.route('/api/<slot>/on/')
def on(slot):
    app.logger.info("Turning " + slot + " on!")
    return handle_state(slot, Action.ON)


@app.route('/api/<slot>/off/')
def off(slot):
    app.logger.info("Turning " + slot + " off!")
    return handle_state(slot, Action.OFF)


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

        rule = Rule(uuid.uuid1(), json_rule['weekday'], rule_devices, timedelta(seconds=json_rule['time']),
            json_rule['action'])
        scheduler.rules.append(rule)

    return jsonify(rules=scheduler.rules, success=True)


@app.route('/api/delete_rule/<rule>', methods=['GET'])
def delete_rule(rule):
    if scheduler.remove_rule(uuid.UUID("{" + rule + "}")):
        return jsonify(rules=scheduler.rules, success=True)
    else:
        return jsonify(rules=scheduler.rules, success=False)


def handle_state(slot, action):
    if action == "on":
        action = Action.ON
    elif action == "off":
        action = Action.OFF

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


