import os

from flask import Flask
from flask.ext.libsass import Sass
from flask.ext.bower import Bower
from flask.ext.script import Manager
import pkg_resources

from garden_lighting.light_control_dummy import LightControl
from garden_lighting.web.auth import Auth
from garden_lighting.web.devices import DeviceGroup, DefaultDevice



app = Flask(__name__)

manager = Manager(app)

Bower(app)

Sass(
    {'layout': 'static/sass/layout.scss',
     'lights': 'static/sass/lights.scss',
     'control': 'static/sass/control.scss'}, app,
    url_path='/static/sass/',
    include_paths=[
        pkg_resources.resource_filename('garden_lighting.web', 'static/sass'),
    ]
)

app.logger.info("Initialising hardware interface!")
control = LightControl()
control.init()


def new_group(display_name, short_name):
    return DeviceGroup(display_name, short_name, control, scheduler)


def new_device(slot, display_name, short_name):
    return DefaultDevice(slot, display_name, short_name, control, scheduler)

from garden_lighting.web.json import ComplexEncoder
from garden_lighting.web.scheduler import DeviceScheduler
scheduler = DeviceScheduler(0.5, None)
devices = new_group("root", "root")
scheduler.devices = devices

auth = None

app.json_encoder = ComplexEncoder


@manager.option('-p', '--port', help='The port', default=80)
@manager.option('-c', '--config', help='The config', default="config.py")
@manager.option('-t', '--token', help='The token', default="")
@manager.option('-s', '--secret', help='The secret key', default="")
def runserver(port, config, token, secret):
    # Loading config
    if os.path.isfile(config):
        with open(config) as f:
            code = compile(f.read(), config, 'exec')

            lcl = {}

            exec(code, globals(), lcl)

            port = lcl['port']
            token = lcl['token']
            secret = lcl['secret']

    global auth
    auth = Auth(token)

    if not scheduler.read(devices):
        app.logger.warn("Failed to load rules!")
        return

    app.secret_key = secret

    from garden_lighting.web.api import api

    app.register_blueprint(api)

    from garden_lighting.web.control import control

    app.register_blueprint(control)

    from garden_lighting.web.lights import lights

    app.register_blueprint(lights)

    app.run(host='0.0.0.0', port=int(port), debug=True)
