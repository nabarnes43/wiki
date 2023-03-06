from flask import render_template
from flask_login import LoginManager
from flaskr.backend import Backend

def make_endpoints(app):

    # Flask uses the "app.route" decorator to call methods when users
    @app.route("/")
    def home():
        return render_template("main.html")

    # TODO(Project 1): Implement additional routes according to the project requirements.
    @app.route("/login", methods=['GET', 'POST'])
    def login():
        