import os

from flask import Flask, g
from flask_pymongo import PyMongo

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        MONGO_URI='mongodb://localhost:27017/cars4sale',
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    mongo = PyMongo(app)
    @app.before_request
    def before_request():
        g.db = mongo.db

    from . import api
    app.register_blueprint(api.bp)

    return app
