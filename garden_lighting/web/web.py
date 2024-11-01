import atexit
import os
from datetime import timedelta
from time import sleep
from threading import Thread
import sys
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask
from garden_lighting.web.auth import Auth, fucked_auth
from garden_lighting.web.devices import DeviceGroup, DefaultDevice

app = Flask(__name__)
app.debug = True

auth = None
rules_path = None
temperature_path = None
log = None

running = True
control = None
scheduler = None
devices = None


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


def run_control(control):
    while running:
        try:
            control.run()
        except Exception as e:
            app.logger.exception(e)
        sleep(2)


@app.cli.command("test_lights")
def test_lights():
    # from garden_lighting.light_control_dummy import LightControl
    from garden_lighting.light_control import LightControl

    control = LightControl(
        timedelta(seconds=3), app.logger,
        0x20, 4,
        0x21, 17
    )

    thread = Thread(target=run_control, args=[control])
    thread.start()

    print("Press ENTER to switch though the lights")

    for i in range(0, 16):
        input()
        control.set_lights(0, range(0, 16))
        control.set_lights(1, [i])
        print("Switched light %d on" % i)

    print("Testing finished")
    pass


def create_app():
    dry = False
    config = "config.py"
    logger = app.logger
    setup_logging(logger, logging.INFO)

    # Start configuration

    port = 5000
    token = ""
    secret = ""
    rules_path_tmp = "rules.bin"
    temperature_path_tmp = "temperature.json"
    root_display_name = "root"
    mcp23017_address_a = 0
    mcp23017_address_b = 0
    mcp23017_reset_a = 0
    mcp23017_reset_b = 0

    register_devices = None

    # Loading config
    if os.path.isfile(config):
        with open(config, encoding="utf-8") as f:
            code = compile(f.read(), config, 'exec')

            lcl = {}

            exec(code, globals(), lcl)

            port = lcl['port']
            token = lcl['token']
            secret = lcl['secret']
            register_devices = lcl['register_devices']
            root_display_name = lcl['root_display_name']
            mcp23017_address_a = lcl['mcp23017_address_a']
            mcp23017_address_b = lcl['mcp23017_address_b']
            mcp23017_reset_a = lcl['mcp23017_reset_a']
            mcp23017_reset_b = lcl['mcp23017_reset_b']

    logger.info("Configuration %s" % {'port': port,
                                      'config': config,
                                      'token': token,
                                      'secret': secret,
                                      'rules_path': rules_path_tmp,
                                      'mcp23017_address_a': mcp23017_address_a,
                                      'mcp23017_address_b': mcp23017_address_b,
                                      'mcp23017_reset_a': mcp23017_reset_a,
                                      'mcp23017_reset_b': mcp23017_reset_b})

    # Start initialising

    logger.info("Initialising hardware interface")
    global control

    if dry:
        from garden_lighting.light_control_dummy import LightControl
    else:
        from garden_lighting.light_control import LightControl

    control = LightControl(timedelta(seconds=3), logger,
                           mcp23017_address_a, mcp23017_reset_a,
                           mcp23017_address_b, mcp23017_reset_b
                           )

    try:
        control.init()
    except Exception as e:
        logger.exception(e)
        logger.error("Failed to initialise hardware!")
        return

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
    rules_path = rules_path_tmp

    global temperature_path
    temperature_path = temperature_path_tmp

    scheduler.read(rules_path, devices)

    app.secret_key = secret

    from garden_lighting.web.api import api

    app.register_blueprint(api)

    from garden_lighting.web.control import control as controls

    app.register_blueprint(controls)

    from garden_lighting.web.lights import lights

    app.register_blueprint(lights)

    from garden_lighting.web.temperature import temperature

    app.register_blueprint(temperature)

    logger.info("Starting scheduling thread")
    thread = Thread(target=run)
    thread.start()

    atexit.register(lambda: shutdown(thread))

    return app


def new_group(display_name, short_name, parent=None):
    return DeviceGroup(display_name, short_name, control, parent)


def new_device(slot, display_name, short_name, parent=None):
    return DefaultDevice(slot, display_name, short_name, control, parent)
