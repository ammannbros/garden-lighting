from flask import Blueprint, request, render_template, jsonify
import time
from tinydb import TinyDB
import statsd

from garden_lighting.web.web import temperature_path

temperature = Blueprint('temperature', __name__, url_prefix='/temperature')

db = TinyDB(temperature_path)
temperature_db = db.table('temperature')


@temperature.route('/update', methods=['POST'])
def get_temperature():
    content_type = request.headers.get('Content-Type')
    if content_type == 'application/json':
        json = request.json

        temp_c = json["temp"]
        temperature_db.insert({'temp': temp_c, 'date': round(time.time())})

        client = statsd.StatsClient('localhost', 8125)
        client.gauge('temp', temp_c)

        return jsonify(message="OK"), 400
    else:
        return jsonify(message="Invalid content type"), 400


@temperature.route('/')
def temperature_home():
    return render_template("temperature.html")


@temperature.route('/frame')
def temperature_frame():
    return render_template("temperature_frame.html")
