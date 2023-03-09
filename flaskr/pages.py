
# ---- YOUR APP STARTS HERE ----
# -- Import section --
from flask import Flask, redirect, url_for, flash
from flask import render_template
from flask_login import login_user, current_user, logout_user, login_required
from flask import request
from .backend import Backend
from .user import User
from .form import LoginForm

def make_endpoints(app, login_manager):
    # Flask uses the "app.route" decorator to call methods when users
    @app.route("/")
    def home():
        backend =  Backend()
        return render_template("main.html")

    # TODO(Project 1): Implement additional routes according to the project requirements.
    @app.route("/login", methods=['GET', 'POST'])
    def sign_in():
        backend = Backend()
 
        form = LoginForm()
        if form.validate_on_submit():
            user = User(form.username.data)
            status = backend.sign_in(form.username.data, form.password.data)
            if status:
                login_user(user, remember = True)
                return redirect(url_for('home'))
            elif status == False:
                flash("An incorrect password was entered")
            else:
                flash("The username is incorrect")
        return render_template('login.html', form=form, user=current_user)

    @login_manager.user_loader
    def load_user(user_id):
        return User(user_id)
    
    @app.route("/logout", methods =['POST', 'GET'])
    @login_required
    def logout(): 
        logout_user()
        return redirect(url_for('home'))

     # About page
    @app.route("/about")
    def about():
        return render_template("about.html")

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
