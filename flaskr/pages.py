from flask import Flask, flash
from flask import render_template
from flask_login import login_user, current_user, logout_user, login_required
from flask import request
from .backend import Backend
from .user import User
from .form import LoginForm
from base64 import b64encode

#Constants

#How many characters of difference are allowed in search
MAX_CHAR_DIST = 1


def make_endpoints(app, login_manager, backend):

    @app.route("/")
    def home():
        """
        Renders the home page.
        
        Args:
            None

        Returns:
            If the user is authenticated, renders the main page with the user's name.
            Otherwise, renders the main page.
        """
        if current_user.is_authenticated:
            return render_template("main.html", name=current_user.get_id())
        return render_template("main.html")

    # Allowing users to login, users are directed back to the home page after successful logins
    @app.route("/login", methods=['GET', 'POST'])
    def sign_in():

        form = LoginForm()
        if form.validate_on_submit():
            user = User(form.username.data)
            status = backend.sign_in(form.username.data, form.password.data)
            if status:
                login_user(user, remember=True)
                return render_template('main.html', name=current_user.get_id())
            elif not status:
                err = "Incorrect password or username"
                return render_template('login.html',
                                       form=form,
                                       user=current_user,
                                       err=err)
        return render_template('login.html', form=form, user=current_user)

    # Loads the user (used by flask login)
    @login_manager.user_loader
    def load_user(user_id):
        return User(user_id)

    # Allowing users to logout, login is required before this can be used
    @app.route("/logout", methods=['POST', 'GET'])
    @login_required
    def logout():
        logout_user()
        return render_template('main.html')

    # About page
    @app.route("/about")
    def about():
        """Renders the about page with headshots of the team members.

        Returns:
            The rendered about page with headshot images of the team members.
        """
        nasir_img = b64encode(
            backend.get_image("Nasir.Barnes.Headshot.JPG")).decode("utf-8")
        elei_img = b64encode(
            backend.get_image("Mary.Elei.Nkata.jpeg")).decode("utf-8")
        dimitri_img = b64encode(
            backend.get_image("Dimitri.Pierre-Louis.JPG")).decode("utf-8")
        return render_template("about.html",
                               nasir_img=nasir_img,
                               elei_img=elei_img,
                               dimitri_img=dimitri_img,
                               name=current_user.get_id())

    @app.route("/signup")
    def signup():
        """
        Renders the signup page for the user to enter their information.

        Returns:
            A rendered HTML template for the signup page.
        """
        return render_template("signup.html")

    @app.route("/createaccount", methods=['GET', 'POST'])
    def createaccount():
        """Handles user account creation requests.

        Returns:
            If the request is GET, the rendered create account page is returned.
            If the request is POST, a new user account is created and the user is redirected to the create account confirmation page.
            If there is an error, an error message is displayed.
        """

        if request.method != 'POST':
            error = "Please go back and use the form!"
            return render_template("signup.html", err=error)

        username = str(request.form['Username'])
        password = str(request.form['Password'])

        if username == '' or password == '':
            error = "Please enter a username and password."
            return render_template("signup.html", err=error)

        try:
            backend.sign_up(username, password)
            return render_template("createaccount.html", username=username)

        except Exception as e:
            return f"Account creation failed: {e}"

    @app.route("/pages", methods=['GET'])
    def pages():
        '''
        Displayes a list of all the pages in the wiki.
        '''
        all_pages = backend.get_all_page_names()

        return render_template('pages.html',
                               page_titles=all_pages,
                               name=current_user.get_id())

    @app.route("/pages/<page_title>", methods=['GET'])
    def page_details(page_title):
        '''
        displays the details of the specific wiki page selected.
        '''
        page = backend.get_wiki_page(page_title)
        author = backend.check_page_author(page_title)
        if current_user.is_authenticated:
            name = str(current_user.get_id())
            existing_pages = backend.get_all_page_names()
            all_bookmarks = backend.get_bookmarks(name, existing_pages)
            bookmarked = page_title in all_bookmarks
            isAuthor = name == author
            return render_template('pageDetails.html',
                                   isAuthor=isAuthor,
                                   title=page_title,
                                   page=page,
                                   name=name,
                                   author=author,
                                   bookmarked=bookmarked)

        return render_template('pageDetails.html',
                               isAuthor=False,
                               title=page_title,
                               page=page,
                               author=author)

    @app.route("/search", methods=['GET', 'POST'])
    def search():
        """Handle the search page GET and POST requests.

        Returns:
            The rendered HTML template with search results or an error message.
        """

        backend = Backend()

        if request.method == 'POST':
            search_content = str(request.form['name'])

            if len(search_content) < 1:
                err = "Please enter a title or content"
                return render_template('search.html',
                                       page_titles=[],
                                       num_results=-1,
                                       search_content=search_content,
                                       err=err)

            all_pages = backend.search_pages(search_content, MAX_CHAR_DIST)

            num_results = len(all_pages)

            return render_template('search.html',
                                   page_titles=all_pages,
                                   num_results=num_results,
                                   search_content=search_content)

        else:
            return render_template('search.html',
                                   page_titles=[],
                                   num_results=-1,
                                   search_content="")


    @app.route("/upload", methods=['GET', 'POST'])
    def uploads():
        '''
        Renders the upload page where form is displayed to enable users to upload a page. 

        Returns:
            If method is GET: The page to fill out the form specifying what you want to upload
            If method is POST: The status message stating if the upload was successful or not. If the upload was unsuccessful, it states the reason why.

        '''

        if request.method == 'POST':
            destination_blob = str(request.form['destination_blob'])
            data_file = request.files['data_file']

            data = data_file.read()
            upload_status = backend.upload(data, destination_blob,
                                           current_user.get_id())

            return render_template('result.html',
                                   upload_status=upload_status,
                                   page_title=destination_blob,
                                   name=current_user.get_id())

        return render_template('upload.html', name=current_user.get_id())

    @app.route("/edit/<title>", methods=['GET'])
    def make_edit(title):
        '''
        Renders the edit page where form is displayed to enable users make their edit to a page. 
        '''
        content = backend.get_wiki_page(title)
        return render_template('edit.html',
                               page_title=title,
                               content=content,
                               name=current_user.get_id())

    @app.route("/save_edit/<page_title>", methods=['POST'])
    def save_edit(page_title):
        '''
        Renders the result page where the result of the users edit is displayed.
        '''
        content = str(request.form['content'])
        upload_status = backend.upload(content, page_title,
                                       current_user.get_id(), True)

        return render_template('result.html',
                               upload_status=upload_status,
                               edit=True,
                               name=current_user.get_id(),
                               page_title=page_title)

    @app.route("/delete/<page_title>", methods=['GET'])
    def delete_page(page_title):
        deleted = backend.delete_page(page_title)
        return render_template('delete.html',
                               page_title=page_title,
                               name=current_user.get_id(),
                               deleted=deleted)

    @app.route("/report/<page_title>", methods=['GET'])
    def report(page_title):
        return render_template('report.html',
                               page_title=page_title,
                               name=current_user.get_id())

    @app.route("/save_report/<page_title>", methods=['POST'])
    def save_report(page_title):
        message = str(request.form['report'])
        report_result = backend.report(page_title, message)
        return render_template('result.html',
                               report=True,
                               upload_status=report_result,
                               name=current_user.get_id())

    @app.route("/bookmark/<page_title>/<name>", methods=['GET'])
    def bookmark(page_title, name):
        '''
        Allows users to bookmark a page. 

        Args:
            isAuthor = bool value showing if the author matches the current user
            page_title = The name of the page to bookmark
            name = name of current user
            author = author of the selected wiki page

        Returns:
            Render pageDetails template with bookmark added message.
        '''

        backend.bookmark(page_title, name)
        author = backend.check_page_author(page_title)
        isAuthor = name == author
        page = backend.get_wiki_page(page_title)

        return render_template('pageDetails.html',
                               isAuthor=isAuthor,
                               title=page_title,
                               page=page,
                               name=name,
                               author=author,
                               bookmarked=True,
                               result='Bookmark added!')

    @app.route("/bookmarks", methods=['GET'])
    def view_bookmarks():
        '''
        Allows a user to view their bookmarks. 

        Returns:
            return bookmarks template with 'no bookmarks added' if there are no bookmarks, or displays list of bookmarks
        '''

        existing_pages = backend.get_all_page_names()
        all_bookmarks = backend.get_bookmarks(current_user.get_id(),
                                              existing_pages)
        current_user.bookmarks = all_bookmarks
        if not all_bookmarks:
            return render_template('bookmark.html',
                                   result="No bookmarks added",
                                   name=current_user.get_id())

        return render_template('bookmark.html',
                               page_titles=all_bookmarks,
                               name=current_user.get_id())

    @app.route("/remove_bookmark/<page_title>/<name>", methods=['GET'])
    def remove_bookmark(page_title, name):
        '''
        Allows a user to remove a bookmark. 

        Args:
            page_title = The name of the page to bookmark
            name = name of current user

        Returns:
            pageDetails template with bookmark removed message
        '''
        backend.remove_bookmark(page_title, name)
        author = backend.check_page_author(page_title)
        isAuthor = name == author
        page = backend.get_wiki_page(page_title)

        return render_template('pageDetails.html',
                               isAuthor=isAuthor,
                               title=page_title,
                               page=page,
                               name=name,
                               author=author,
                               bookmarked=False,
                               result='Bookmark deleted!')
