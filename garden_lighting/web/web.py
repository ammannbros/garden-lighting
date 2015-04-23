import os


from flask import Flask, render_template, jsonify
from flask.ext.assets import Environment, Bundle

from garden_lighting.web.devices import DeviceGroup, Action
from garden_lighting.web.scheduler import DeviceScheduler


app = Flask(__name__)

env = Environment(app)
env.load_path = [
    os.path.join(os.path.dirname(__file__), 'sass')
]

env.register(
    'css_all',
    Bundle(
        'lights.scss',
        filters='pyscss',
        output='css_all.css'
    )
)

devices = DeviceGroup()
scheduler = DeviceScheduler(devices, 0.5)


@app.route('/')
def lights():
    return render_template("lights.html")


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


