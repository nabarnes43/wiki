from flaskr import pages
from .backend import Backend
from flask import Flask
from flask_login import LoginManager
import logging

logging.basicConfig(level=logging.DEBUG)


def create_app(test_config=None):
    # Create and configure the app.
    app = Flask(__name__, instance_relative_config=True)
    login_manager = LoginManager(app)
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    # This is the default secret key used for login sessions
    # By default the dev environment uses the key 'dev'
    app.config.from_mapping(SECRET_KEY='dev',)

    if test_config is None:
        # Load the instance config, if it exists, when not testing.
        # This file is not committed. Place it in production deployments.
        app.config.from_pyfile('config.py', silent=True)
    else:
        # Load the test config if passed in.
        app.config.from_mapping(test_config)

    # TODO(Project 1): Make additional modifications here for logging in, backends
    # and additional endpoints.
    backend = Backend()
    pages.make_endpoints(app, login_manager, backend)
    login_manager.init_app(app)
    app.config['WTF_CSRF_ENABLED'] = False
    return app
