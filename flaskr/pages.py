
# ---- YOUR APP STARTS HERE ----
# -- Import section --
from flask import Flask, flash
from flask import render_template
from flask_login import login_user, current_user, logout_user, login_required
from flask import request
from .backend import Backend
from .user import User
from .form import LoginForm
from base64 import b64encode

def make_endpoints(app, login_manager):
    # Flask uses the "app.route" decorator to call methods when users
    @app.route("/")
    def home():
        backend =  Backend()
        if current_user.is_authenticated:  
            return render_template("main.html", name = current_user.name)
        return render_template("main.html")

    # TODO(Project 1): Implement additional routes according to the project requirements.
    #Allowing users to login, users are directed back to the home page after successful logins
    @app.route("/login", methods=['GET', 'POST'])
    def sign_in():
        backend = Backend()
 
        form = LoginForm()
        if form.validate_on_submit():
            user = User(form.username.data)
            username = form.username.data
            status = backend.sign_in(form.username.data, form.password.data)
            if status == 'Sign In Successful':
                login_user(user, remember = True)
                return render_template('main.html', name = current_user.name)
            elif status == 'Incorrect Password':
                return "An incorrect password was entered"
            else:
                return "The username is incorrect"
        return render_template('login.html', form=form, user=current_user)

    #Loads the user (used by flask login)
    @login_manager.user_loader
    def load_user(user_id):
        return User(user_id)
    
    #Allowing users to logout, login is required before this can be used
    @app.route("/logout", methods =['POST', 'GET'])
    @login_required
    def logout(): 
        logout_user()
        return render_template('main.html')
     # About page
    @app.route("/about")
    def about():
        backend = Backend()
        nasir_img = backend.get_image("Nasir.Barnes.Headshot.JPG")
        elei_img = backend.get_image("Mary.Elei.Nkata.jpeg")
        dimitri_img = backend.get_image("Dimitri.Pierre-Louis.JPG")
        
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

        try:
            backend.sign_up(username, password)
            return render_template("createaccount.html", username=username)
            
        except Exception as e:
            return f"Account creation failed: {e}"

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
            upload_status = backend.upload(data, destination_blob)

            return upload_status

        return render_template('upload.html')
