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

def test_about_page(client):
    resp = client.get("/about")
    assert resp.status_code == 200
    assert b"<h1>About This Wiki</h1>" in resp.data
    assert b"<h3>Your Authors</h3>" in resp.data

def test_signup_page(client):
    resp = client.get('/signup')
    assert resp.status_code == 200
    assert b'<h1>Sign Up</h1>' in resp.data
    assert b'<input type="text" name= "Username" placeholder="Enter a username"/>' in resp.data
    assert b'<input type="text" name="Password" placeholder="Enter a password"/>' in resp.data
    assert b'<input type="submit" value="Signup"/>' in resp.data

def test_create_account_succesful_page(client):
    response = client.post('/createaccount', data=dict(
        Username='testuser',
        Password='testpassword'
    ))
    assert response.status_code == 200
    assert b'testuser' in response.data

def test_create_account_missing_fields(client):
    # test missing username field
    response = client.post('/createaccount', data=dict(Username = '',
        Password='testpassword'
    ))
    assert response.status_code == 200
    assert b'Please enter a username and password.' in response.data
    
    # test missing password field
    response = client.post('/createaccount', data=dict(
        Username='testuser', Password = ''
    ))
    assert response.status_code == 200
    assert b'Please enter a username and password.' in response.data
    
    # test missing username and password fields
    response = client.post('/createaccount', data=dict(
        Username='',
        Password=''
    ))
    assert response.status_code == 200
    assert b'Please enter a username and password.' in response.data

def test_create_account_get_page(client):
    response = client.get('/createaccount')
    assert response.status_code == 200
    assert b'Please go back and use the form!' in response.data

def test_create_account_exception(client, monkeypatch):
    def mock_sign_up(self, username, password):
        raise Exception('Test exception')
    monkeypatch.setattr(Backend, 'sign_up', mock_sign_up)
    
    response = client.post('/createaccount', data=dict(
        Username='testuser',
        Password='testpassword'
    ))
    
    assert response.status_code == 200
    assert b'Account creation failed: Test exception' in response.data

def test_pages_list(client):
    resp = client.get("/pages")
    assert resp.status_code == 200

def test_specific_page(client):
    resp = client.get("/pages/testing uploads.txt")
    assert resp.status_code == 200

def test_upload(client):
    resp = client.get("/upload")
    assert resp.status_code == 200

#Testing that users are seeing the correct login page
def test_login_page(client):
    resp = client.get('/login')
    assert resp.status_code == 200
    assert b'<h1>Sign In</h1>' in resp.data
    assert b'Username' in resp.data
    assert b'Password' in resp.data
    assert b'value="Submit"' in resp.data

#Testing that users see the correct page when wrong username is entered
def test_login_wrong_username(client):
    resp = client.post('/login', data = {
        'username': 'sdf',
        'password': 'testing123', 
    })
    assert resp.status_code == 200
    assert b'The username is incorrect' in resp.data

#Testing that users are sent to the right page when the wrong password is entered
def test_login_wrong_password(client):
    resp = client.post('/login', data = {
        'username': 'Dimitripl5',
        'password': 'testing76576', 
    })
    assert resp.status_code == 200
    assert b'An incorrect password was entered' in resp.data

#Testing that users are able to login and logout successfully
def test_login_and_logout_successful(client):
    resp = client.post('/login', data=dict(
        username='Dimitripl5',
        password='testing123', 
    ))
    assert resp.status_code == 200
    assert b'Hey there Dimitripl5' in resp.data
    assert b'Log Out' in resp.data
    resp = client.get("/logout")
    assert b'Log In' in resp.data