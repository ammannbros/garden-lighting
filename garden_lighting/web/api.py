from datetime import timedelta
from flask import Blueprint, jsonify, request
import uuid
from garden_lighting.web.devices import Action
from garden_lighting.web.scheduler import Rule

from garden_lighting.web.web import app, devices, scheduler, auth

api = Blueprint('api', __name__)


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


@api.route('/api/<slot>/on/')
def on(slot):
    if not auth.auth():
        return auth.fucked_auth()

    app.logger.info("Turning " + slot + " on!")
    return handle_state(slot, Action.ON)


@api.route('/api/<slot>/off/')
def off(slot):
    if not auth.auth():
        return auth.fucked_auth()

    app.logger.info("Turning " + slot + " off!")
    return handle_state(slot, Action.OFF)


@api.route('/api/add_rules/', methods=['POST'])
def add_rules():
    if not auth.auth():
        return auth.fucked_auth()

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


@api.route('/api/delete_rule/<rule>', methods=['GET'])
def delete_rule(rule):
    if not auth.auth():
        return auth.fucked_auth()

    if scheduler.remove_rule(uuid.UUID("{" + rule + "}")):
        success = scheduler.write()
        return jsonify(rules=scheduler.rules, success=success)
    else:
        return jsonify(rules=scheduler.rules, success=False)
