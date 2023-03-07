from flask import render_template
from .backend import Backend


def make_endpoints(app):

    # Flask uses the "app.route" decorator to call methods when users
    # go to a specific route on the project's website.
    @app.route("/")
    def home():
        return render_template("main.html")

    # TODO(Project 1): Implement additional routes according to the project requirements.

    @app.route("/pages", methods=['GET'])
    def pages():
        backend = Backend()
        all_pages = backend.get_all_page_names()

        return render_template('main.html', page_titles = all_pages)

    @app.route("/pages/<page_title>", methods=['GET'])
    def page_details(page_title):
        backend = Backend()
        page = backend.get_wiki_page(page_title)

        return render_template('main.html', page=page)

    
