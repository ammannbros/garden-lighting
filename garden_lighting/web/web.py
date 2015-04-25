from flask import Flask, render_template, jsonify
from flask.ext.libsass import Sass
from flask.ext.bower import Bower

import pkg_resources

from garden_lighting.web.devices import DeviceGroup, Action
from garden_lighting.web.scheduler import DeviceScheduler


app = Flask(__name__)
Bower(app)

Sass(
    {'layout': 'static/sass/layout.scss',
     'lights': 'static/sass/lights.scss'}, app,
    url_path='/static/sass/',
    include_paths=[
        pkg_resources.resource_filename('garden_lighting.web', 'static/sass'),
    ]
)

devices = DeviceGroup()
scheduler = DeviceScheduler(devices, 0.5)


@app.route('/')
def lights():
    return render_template("lights.html")


@app.route('/overview/')
def overview():
    return render_template("lights.html", amount=6)


@app.route('/all_lights/')
def all_lights():
    return render_template("lights.html", amount=20)


@app.route('/controls/')
def controls():
    return render_template("controls.html")


@app.route('/about/')
def about():
    return render_template("about.html")


@app.route('/api/<slot>/on/')
def on(slot):
    return handle_state(slot, Action.ON)


@app.route('/api/<slot>/off/')
def off(slot):
    return handle_state(slot, Action.OFF)


@app.route('/api/<slot>/toggle/')
def toggle(slot):
    return handle_state(slot, Action.TOGGLE)


def handle_state(slot, action):
    if slot == "all":
        success = devices.set(action)
    else:
        try:
            device = devices.get_device(slot)
            success = device.set(action)
        except KeyError:
            success = False

    return jsonify(success=success)


def start_web():
    app.run(host='0.0.0.0', debug=True)


