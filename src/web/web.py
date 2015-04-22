import os
from flask import Flask, render_template
from flask.ext.assets import Environment, Bundle


app = Flask(__name__)

env = Environment(app)
env.load_path = [
    os.path.join(os.path.dirname(__file__), 'sass')
]

env.register(
    'css_all',
    Bundle(
        'lights.scss',
        filters='pyscss',
        output='css_all.css'
    )
)


@app.route('/')
def hello_world():
    return render_template("lights.html")


def start_web():
    app.run(host='0.0.0.0', debug=True)