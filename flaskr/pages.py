
# ---- YOUR APP STARTS HERE ----
# -- Import section --
from flask import Flask
from flask import render_template
from flask import request
from .backend import Backend
from base64 import b64encode



def make_endpoints(app):
    # Flask uses the "app.route" decorator to call methods when users
    # go to a specific route on the project's website.
    @app.route("/")
    def home():
        backend = Backend()
        image = b64encode(backend.get_image("cat.jpg")).decode("utf-8")

        return render_template("main.html", image = image)

    # TODO(Project 1): Implement additional routes according to the project requirements.

     # About page
    @app.route("/about")
    def about():
        backend = Backend()
        nasir_img = b64encode(backend.get_image("Nasir.Barnes.Headshot.JPG")).decode("utf-8")
        elei_img = b64encode(backend.get_image("Mary.Elei.Nkata.jpeg")).decode("utf-8")
        dimitri_img = b64encode(backend.get_image("cat.jpg")).decode("utf-8")

        return render_template("about.html", nasir_img = nasir_img, elei_img = elei_img, dimitri_img = dimitri_img)

    @app.route("/signup")
    def signup():
        return render_template("signup.html")

    @app.route("/createaccount",  methods=['GET', 'POST'])
    def createaccount():
        backend = Backend()

        if request.method != 'POST':
            return "Please go back and use the form!"

        username = str(request.form['Username'])
        password = str(request.form['Password'])

        if  username == '' or  password == '':
            return "Please enter a username and password."

        print(username)
        print(password)

        backend.sign_up(username, password)

        return render_template("createaccount.html")

    @app.route("/pages", methods=['GET'])
    def pages():
        backend = Backend()
        all_pages = backend.get_all_page_names()

        return render_template('pages.html', page_titles = all_pages)

    @app.route("/pages/<page_title>", methods=['GET'])
    def page_details(page_title):
        backend = Backend()
        page = backend.get_wiki_page(page_title)

        return render_template('pages.html', page=page)

    @app.route("/upload", methods = ['GET', 'POST'])
    def uploads():
        if request.method == 'POST':
            backend = Backend()
            destination_blob = str(request.form['destination_blob'])
            data_file = request.files['data_file']

            data = data_file.read()
            result = backend.upload(data, destination_blob)
            return result

        return render_template('upload.html')
