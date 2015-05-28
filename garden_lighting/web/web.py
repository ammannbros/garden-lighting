import os
from datetime import timedelta
import threading
from time import sleep
from threading import Thread
import sys
import logging
from logging.handlers import RotatingFileHandler

from flask import Flask
from flask.ext.libsass import Sass
from flask.ext.bower import Bower
from flask.ext.script import Manager
import pkg_resources


from garden_lighting.web.auth import Auth, fucked_auth
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

auth = None
rules_path = None
log = None

running = True
control = None
scheduler = None
devices = None
# temperature_receiver = None


def setup_logging(logger, level):
    logger.setLevel(level)
    formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s ' \
                                  '[in %(pathname)s:%(lineno)d]')

    console = logging.StreamHandler(sys.stderr)
    console.setLevel(level)
    console.setFormatter(formatter)
    logger.addHandler(console)

    file_handler = RotatingFileHandler("lighting.log")
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)


@app.before_request
def before_request():
    if not auth.auth():
        return fucked_auth()


def shutdown(thread):
    app.logger.info('Shutting down!')
    global running
    running = False
    thread.join()
    sys.exit(0)


def run():
    while running:
        try:
            scheduler.run()
            control.run()
        except Exception as e:
            app.logger.exception(e)
        sleep(2)


@manager.option('-p', '--port', help='The port', default=80)
@manager.option('-c', '--config', help='The config', default="config.py")
@manager.option('-t', '--token', help='The token', default="")
@manager.option('-s', '--secret', help='The secret key', default="")
@manager.option('-r', '--rules', help='The rules save file', default="rules.bin")
def runserver(port, config, token, secret, rules):
    setup_logging(app.logger, logging.INFO)

    app.logger.info("Initialising hardware interface")
    global control
    try:
        from garden_lighting.light_control import LightControl

        control = LightControl(timedelta(seconds=3), 1, app.logger)
        control.init()

        # from garden_lighting.temperature_receiver import TemperatureReceiver
        # global temperature_receiver
        # temperature_receiver = TemperatureReceiver(14, 2000)
        # threading.Thread(target=temperature_receiver.start).start()
    except:
        from garden_lighting.light_control_dummy import LightControl

        control = LightControl(timedelta(seconds=3), 1, app.logger)
        control.init()

    global devices
    devices = new_group("root", "root")

    app.logger.info("Initialising scheduling thread")
    global scheduler
    from garden_lighting.web.scheduler import DeviceScheduler

    scheduler = DeviceScheduler(0.5, devices, control, app.logger)

    app.logger.info("Configuration %s" % {'port': port,
                                          'config': config,
                                          'token': token,
                                          'secret': secret,
                                          'rules': rules})

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
    auth = Auth(token, app.logger)

    global rules_path
    rules_path = rules

    scheduler.read(rules, devices)

    app.secret_key = secret

    from garden_lighting.web.api import api

    app.register_blueprint(api)

    from garden_lighting.web.control import control as controls

    app.register_blueprint(controls)

    from garden_lighting.web.lights import lights

    app.register_blueprint(lights)

    # from garden_lighting.temperatures import temperatures
    #
    # app.register_blueprint(temperatures)

    app.logger.info("Starting scheduling thread")
    thread = Thread(target=run)
    thread.start()

    app.run(host='0.0.0.0', port=int(port), debug=False, use_reloader=False)
    shutdown(thread)


def new_group(display_name, short_name):
    return DeviceGroup(display_name, short_name, control)


def new_device(slot, display_name, short_name):
    return DefaultDevice(slot, display_name, short_name, control)
