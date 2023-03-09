from flaskr import create_app

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

# TODO(Checkpoint (groups of 4 only) Requirement 4): Change test to
# match the changes made in the other Checkpoint Requirements.
def test_home_page(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert b"<title>Wikipedia!</title>" in resp.data
    assert b"<h1>Wikipedia!</h1>" in resp.data
    assert b"<a href=\"/about\">About</a>" in resp.data
    assert b"<a href=\"/signup\">Sign Up</a>" in resp.data
    assert b"Hey there, thanks for using Wikipedia!" in resp.data

# TODO(Project 1): Write tests for other routes.

def test_about_page(client):
    resp = client.get("/about")
    assert resp.status_code == 200
    assert b"<h1>About This Wiki</h1>" in resp.data
    assert b"<h3>Your Authors</h3>" in resp.data


def signup






