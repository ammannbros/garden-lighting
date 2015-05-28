from flask import Blueprint, jsonify
from garden_lighting.web.web import temperature_receiver

temperatures = Blueprint('temperatures', __name__)




@temperatures.route('/temperatures/')
def overview():
    return jsonify(temp=temperature_receiver.get_sender(1).get_temperature(0))