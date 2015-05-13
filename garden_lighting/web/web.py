import os

from flask import Flask

from flask.ext.libsass import Sass

from flask.ext.bower import Bower
from flask.ext.script import Manager
import pkg_resources

from garden_lighting.lightControl import LightControlDummy

from garden_lighting.web.devices import DeviceGroup, DefaultDevice
from garden_lighting.web.scheduler import DeviceScheduler

from garden_lighting.web.json import ComplexEncoder

app = Flask(__name__)
app.json_encoder = ComplexEncoder

manager = Manager(app)

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
control = LightControlDummy()
control.init()

scheduler = DeviceScheduler(0.5)
devices = DeviceGroup("root", "root", control)

token = ""


@manager.option('-p', '--port', help='The port', default=80)
@manager.option('-c', '--config', help='The config', default="config.py")
@manager.option('-t', '--token', dest="token_", help='The token', default="")
@manager.option('-s', '--secret', help='The secret key', default="")
def runserver(port, config, token_, secret):
    if os.path.isfile(config):
        with open(config) as f:
            code = compile(f.read(), config, 'exec')
            exec(code)

    global token
    token = token_

    # Init routes
    # noinspection PyUnresolvedReferences
    from garden_lighting.web import routes

    if not scheduler.read(devices):
        app.logger.warn("Failed to load rules!")

    app.secret_key = secret

    app.run(host='0.0.0.0', port=int(port), debug=True)


def new_group(display_name, short_name):
    return DeviceGroup(display_name, short_name, control)


def new_device(slot, display_name, short_name):
    return DefaultDevice(slot, display_name, short_name, control)