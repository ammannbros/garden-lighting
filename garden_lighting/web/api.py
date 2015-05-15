from datetime import timedelta
from flask import Blueprint, jsonify, request
import uuid
from garden_lighting.web.devices import Action
from garden_lighting.web.scheduler import Rule, Weekday, now_rule

from garden_lighting.web.web import app, devices, scheduler, auth

api = Blueprint('api', __name__)


def get_device(slot):
    if slot == "all":
        return devices
    else:
        return devices.get_device(slot)


def handle_state(slot, action, duration):
    success = True

    if action == "on":
        action = Action.ON
    elif action == "off":
        action = Action.OFF

    device = get_device(slot)

    if device is not None:
        if duration == 0:
            controlled = device.set(action)
            success = len(controlled) > 0
            for device in controlled:
                device.control_manually()
        else:
            device_list = device.get_real_devices_recursive()

            unique_uid = uuid.uuid1()

            for device in device_list:
                device.super_rule_start = now_rule(unique_uid, device_list, action)
                device.super_rule_stop = now_rule(unique_uid, device_list, action.opposite(), time_delta=duration)
    else:
        success = False

    return jsonify(success=success)


@api.route('/api/<slot>/on/', defaults={'duration': 0})
@api.route('/api/<slot>/on/<int:duration>')
def on(slot, duration):
    if not auth.auth():
        return auth.fucked_auth()

    app.logger.info("Turning " + slot + " on!")
    return handle_state(slot, Action.ON, duration)


@api.route('/api/<slot>/off/', defaults={'duration': 0})
@api.route('/api/<slot>/off/<int:duration>')
def off(slot, duration):
    if not auth.auth():
        return auth.fucked_auth()

    app.logger.info("Turning " + slot + " off!")
    return handle_state(slot, Action.OFF, duration)


@api.route('/api/<slot>/manual/')
def control_manually(slot):
    if not auth.auth():
        return auth.fucked_auth()

    device = get_device(slot)
    for dev in device.get_real_devices_recursive():
        dev.control_manually()

    return jsonify(success=True)


@api.route('/api/<slot>/automatic/')
def control_automatically(slot):
    if not auth.auth():
        return auth.fucked_auth()

    device = get_device(slot)
    for dev in device.get_real_devices_recursive():
        dev.control_automatically()
        # Automatic devices do not have super rules!
        dev.super_rule_start = None
        dev.super_rule_stop = None

    return jsonify(success=True)


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
            rule_devices.add(get_device)

        rule = Rule(
            uuid.uuid1(),
            Weekday(json_rule['weekday']),
            rule_devices,
            timedelta(seconds=json_rule['time']),
            json_rule['action']
        )

        scheduler.add_rule(rule)

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
