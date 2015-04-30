from flask import Flask, render_template, jsonify
from flask.ext.libsass import Sass
from flask.ext.bower import Bower

import pkg_resources

from garden_lighting.web.devices import DefaultDevice, DeviceGroup, Action
# from garden_lighting.web.scheduler import DeviceScheduler


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

devices = DeviceGroup("root", "root")

group1 = DeviceGroup("Bereich #1", "area1")
group2 = DeviceGroup("Bereich #2", "area2")
group3 = DeviceGroup("Bereich #3", "area3")

group1.register_device(DefaultDevice(0, "Garten #1", "1"))
group1.register_device(DefaultDevice(1, "Garten #2", "2"))
group1.register_device(DefaultDevice(2, "Garten #3", "3"))
group2.register_device(DefaultDevice(3, "Garten #4", "4"))
group2.register_device(DefaultDevice(4, "Garten #5", "5"))
group2.register_device(DefaultDevice(5, "Garten #6", "6"))
group3.register_device(DefaultDevice(6, "Garten #7", "7"))
group3.register_device(DefaultDevice(7, "Garten #8", "8"))
group3.register_device(DefaultDevice(8, "Garten #9", "9"))
group3.register_device(DefaultDevice(8, "Garten #9", "9"))

devices.register_device(group1)
devices.register_device(group2)
devices.register_device(group3)

# scheduler = DeviceScheduler(devices, 0.5)

@app.route('/')
def lights():
    return overview()


@app.route('/overview/')
def overview():
    return render_template("lights.html", devices=devices.get_all_devices())


@app.route('/all_lights/')
def all_lights():
    return render_template("lights.html", devices=devices.get_all_devices_recursive())


@app.route('/controls/')
def controls():
    return render_template("controls.html", devices=devices.get_all_devices_recursive())


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


