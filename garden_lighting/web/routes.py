from datetime import timedelta
from flask import jsonify, session, request, render_template
import uuid

from garden_lighting.web.devices import Action
from garden_lighting.web.scheduler import Rule

from garden_lighting.web.web import devices, token
from garden_lighting.web.web import control, scheduler, app


def auth():
    if token == "":
        return True

    if 'token' in request.args and request.args.get('token') == token:
        session['auth'] = True
        return True
    else:
        return 'auth' in session and session['auth']


def fucked_auth():
    return jsonify(result="Fuck off!")


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


@app.route('/')
def lights():
    if not auth():
        return fucked_auth()
    return overview()


@app.route('/areas/')
def overview():
    if not auth():
        return fucked_auth()
    all_devices = devices.get_all_devices()
    return render_template("lights.html", name="Bereiche", areas=True, devices=all_devices)


@app.route('/all_lights/')
def all_lights():
    if not auth():
        return fucked_auth()
    all_devices = devices.get_all_devices_recursive()
    batch = []
    devices.collect_batch(batch)

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
    if not auth():
        return fucked_auth()
    return render_template("controls.html", rules=scheduler.rules, devices=devices.get_all_devices_recursive())


@app.route('/api/<slot>/on/')
def on(slot):
    if not auth():
        return fucked_auth()
    app.logger.info("Turning " + slot + " on!")
    return handle_state(slot, Action.ON)


@app.route('/api/<slot>/off/')
def off(slot):
    if not auth():
        return fucked_auth()
    app.logger.info("Turning " + slot + " off!")
    return handle_state(slot, Action.OFF)


@app.route('/api/add_rules/', methods=['POST'])
def add_rules():
    if not auth():
        return fucked_auth()

    json_text = request.get_json()

    if json_text is None:
        return jsonify(rules=scheduler.rules, success=False)

    for json_rule in json_text:
        rule_devices = []

        for device in json_rule['devices']:
            get_device = devices.get_device(device)
            if get_device is None:
                continue
            rule_devices.append(get_device)

        rule = Rule(
            uuid.uuid1(),
            json_rule['weekday'],
            rule_devices,
            timedelta(seconds=json_rule['time']),
            json_rule['action']

        )
        scheduler.rules.append(rule)

    success = scheduler.write()

    return jsonify(rules=scheduler.rules, success=success)


@app.route('/api/delete_rule/<rule>', methods=['GET'])
def delete_rule(rule):
    if not auth():
        return fucked_auth()

    if scheduler.remove_rule(uuid.UUID("{" + rule + "}")):
        success = scheduler.write()
        return jsonify(rules=scheduler.rules, success=success)
    else:
        return jsonify(rules=scheduler.rules, success=False)
