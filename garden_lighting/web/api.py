from datetime import timedelta
from flask import Blueprint, jsonify, request
import uuid
from garden_lighting.web.devices import Action, action_from_string, DefaultDevice
from garden_lighting.web.scheduler import Rule, Weekday, now_rule

from garden_lighting.web.web import app, devices, scheduler, auth, control

api = Blueprint('api', __name__, url_prefix="/api")


def get_device(slot):
    if slot == "all":
        return devices
    else:
        return devices.get_device(slot)


def handle_state(slot, action, duration):
    success = True

    device = get_device(slot)

    if device is not None:
        if duration == 0:
            controlled = device.set(action)
            success = len(controlled) > 0
            for device in controlled:
                device.control_manually()

                # Forget about the super rule, we're real manual now!
                device.clear_super_rule()

        else:
            device_list = device.get_real_devices_recursive()

            unique_uid = uuid.uuid1()

            for device in device_list:
                device.super_rule_start = now_rule(unique_uid, device_list, action)
                device.super_rule_stop = now_rule(unique_uid, device_list, action.opposite(), time_delta=duration)
    else:
        success = False

    return jsonify(success=success)


@api.route('/<slot>/on/', defaults={'duration': 0})
@api.route('/<slot>/on/<int:duration>')
def on(slot, duration):
    if not auth.auth():
        return auth.fucked_auth()

    app.logger.info("Turning " + slot + " on!")
    return handle_state(slot, Action.ON, duration)


def collect_device_info(device, ons):
    state = device.__getstate__()
    state['group'] = type(device) != DefaultDevice
    state['manual'] = device.is_controlled_manually()

    next_action = scheduler.get_next_action_date(device)

    if next_action:
        state['next_time'] = next_action[0].total_seconds()
        state['next_action'] = str(next_action[1])

    if not state['group']:
        state['state'] = device.slot in ons
    return state


@api.route('/devices')
def get_devices():
    if not auth.auth():
        return auth.fucked_auth()

    ons = control.get_lights(True)

    result = [collect_device_info(device, ons) for device in devices.get_all_devices_recursive()]

    return jsonify(devices=result)


@api.route('/rules')
def get_rules():
    if not auth.auth():
        return auth.fucked_auth()

    result = [rule.__getjsonifystate__() for rule in scheduler.rules]

    return jsonify(rules=result)


@api.route('/<slot>/off/', defaults={'duration': 0})
@api.route('/<slot>/off/<int:duration>')
def off(slot, duration):
    if not auth.auth():
        return auth.fucked_auth()

    app.logger.info("Turning " + slot + " off!")
    return handle_state(slot, Action.OFF, duration)


@api.route('/<slot>/manual/')
def control_manually(slot):
    if not auth.auth():
        return auth.fucked_auth()

    device = get_device(slot)
    for dev in device.get_real_devices_recursive():
        dev.control_manually()

    return jsonify(success=True)


@api.route('/<slot>/automatic/')
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


@api.route('/add_rules/', methods=['POST'])
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
            Weekday(json_rule['weekday']),
            rule_devices,
            timedelta(seconds=json_rule['time']),
            action_from_string(json_rule['action'])
        )

        scheduler.add_rule(rule)

    success = scheduler.write()

    return jsonify(success=success)


@api.route('/delete_rule/<rule>', methods=['GET'])
def delete_rule(rule):
    if not auth.auth():
        return auth.fucked_auth()

    if scheduler.remove_rule(uuid.UUID("{" + rule + "}")):
        success = scheduler.write()
        return jsonify(success=success)
    else:
        return jsonify(success=False)
