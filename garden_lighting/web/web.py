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
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.wsgi import WSGIContainer

from garden_lighting.web.auth import Auth, fucked_auth
from garden_lighting.web.devices import DeviceGroup, DefaultDevice

app = Flask(__name__)
app.debug = True

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
    logger.handlers = []

    logger.setLevel(level)
    formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')

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


def run():
    while running:
        try:
            scheduler.run()
            control.run()
        except Exception as e:
            app.logger.exception(e)
        sleep(2)


# noinspection PyBroadException
@manager.option('-p', '--port', dest='port_opt', help='The port', default=None)
@manager.option('-c', '--config', dest='config', help='The config', default="config.py")
@manager.option('-t', '--token', dest='token_opt', help='The token', default=None)
@manager.option('-s', '--secret', dest='secret_opt', help='The secret key', default=None)
@manager.option('-r', '--rules', dest='rules_opt', help='The rules save file', default=None)
def runserver(port_opt, config, token_opt, secret_opt, rules_opt):
    logger = app.logger
    setup_logging(logger, logging.INFO)

    # Start configuration

    port = 5000
    token = ""
    secret = ""
    rules = "rules.bin"
    root_display_name = "root"
    mcp23017_addresses = []
    mcp23017_reset_pins = []

    register_devices = None

    # Loading config
    if os.path.isfile(config):
        with open(config) as f:
            code = compile(f.read(), config, 'exec')

            lcl = {}

            exec(code, globals(), lcl)

            port = lcl['port']
            token = lcl['token']
            secret = lcl['secret']
            register_devices = lcl['register_devices']
            root_display_name = lcl['root_display_name']
            mcp23017_addresses = lcl['mcp23017_addresses']
            mcp23017_reset_pins = lcl['mcp23017_reset_pins']

    if port_opt:
        port = port_opt

    if token_opt:
        token = token_opt

    if secret_opt:
        secret = secret_opt

    if rules_opt:
        rules = rules_opt

    logger.info("Configuration %s" % {'port': port,
                                      'config': config,
                                      'token': token,
                                      'secret': secret,
                                      'rules': rules,
                                      'mcp23017_addresses': mcp23017_addresses,
                                      'mcp23017_reset_pins': mcp23017_reset_pins})

    # Start initialising

    logger.info("Initialising hardware interface")
    global control
    try:
        from garden_lighting.light_control import LightControl
    except Exception:
        from garden_lighting.light_control_dummy import LightControl

        # from garden_lighting.temperature_receiver import TemperatureReceiver
        # global temperature_receiver
        # temperature_receiver = TemperatureReceiver(14, 2000)
        # threading.Thread(target=temperature_receiver.start).start()

    control = LightControl(timedelta(seconds=3), 1, logger,
                           mcp23017_addresses[0], mcp23017_reset_pins[0],
                           mcp23017_addresses[1], mcp23017_reset_pins[1])
    control.init()

    global devices
    devices = new_group(root_display_name, "root")

    logger.info("Initialising scheduling thread")
    global scheduler
    from garden_lighting.web.scheduler import DeviceScheduler

    scheduler = DeviceScheduler(0.5, devices, control, logger)

    if register_devices:
        register_devices(devices)

    # Start web stuff

    global auth
    auth = Auth(token, logger)

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

    logger.info("Starting scheduling thread")
    thread = Thread(target=run)
    thread.start()

    http_server = HTTPServer(WSGIContainer(app))
    http_server.listen(port)
    try:
        IOLoop.instance().start()
    except KeyboardInterrupt:
        IOLoop.instance().stop()

    shutdown(thread)


def new_group(display_name, short_name):
    return DeviceGroup(display_name, short_name, control)


def new_device(slot, display_name, short_name):
    return DefaultDevice(slot, display_name, short_name, control)
