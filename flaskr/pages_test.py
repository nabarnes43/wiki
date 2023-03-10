from flaskr import create_app
from .backend import Backend
import pytest

# See https://flask.palletsprojects.com/en/2.2.x/testing/ 
# for more info on testing
@pytest.fixture
def app():
    app = create_app({
        'TESTING': True,
    })
    return app

@pytest.fixture
def client(app):
    return app.test_client()


def test_home_page(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert b"<title>Wikipedia!</title>" in resp.data
    # assert b"<h1>Wikipedia!</h1>" in resp.data
    # assert b"<a href=\"/about\">About</a>" in resp.data
    # assert b"<a href=\"/signup\">Sign Up</a>" in resp.data
    # assert b"Hey there, thanks for using Wikipedia!" in resp.data

# TODO(Project 1): Write tests for other routes.

def test_about_page(client):
    resp = client.get("/about")
    assert resp.status_code == 200
    assert b"<h1>About This Wiki</h1>" in resp.data
    assert b"<h3>Your Authors</h3>" in resp.data

def test_pages_list(client):
    resp = client.get("/pages")
    assert resp.status_code == 200

def test_specific_page(client):
    resp = client.get("/pages/testing uploads.txt")
    assert resp.status_code == 200

def test_upload(client):
    resp = client.get("/upload")
    assert resp.status_code == 200







