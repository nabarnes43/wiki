from flaskr import create_app
from .backend import Backend
from unittest.mock import patch
from .user import User
from unittest.mock import MagicMock
from unittest import mock
import pytest
import io


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
    """
    Test that the home page loads successfully and contains the expected content.
    """
    resp = client.get("/")
    assert resp.status_code == 200
    assert b"<title>People To Know In Computer Science</title>" in resp.data
    assert b"This wiki is dedicated to providing information and insight into the lives and works of the most influential and notable people in the field of computer science. From pioneers of computer programming and artificial intelligence to modern-day innovators in cybersecurity and machine learning, this wiki seeks to showcase the incredible contributions made by these individuals to the world of computer science." in resp.data


def test_about_page(client, monkeypatch):
    nasir_image_data = b"nasir image data"
    elei_image_data = b"elei image data"
    dimitri_image_data = b"dimitri image data"

    def mock_get_image(self, name):
        return b''

    monkeypatch.setattr(Backend, 'get_image', mock_get_image)

    response = client.get("/about")
    assert response.status_code == 200
    assert b"<h1>About This Wiki</h1>" in response.data
    assert b"<h3>Your Authors</h3>" in response.data
    assert b'' in response.data


def test_signup_page(client):
    """
    Test that the signup page loads successfully and contains the expected content.
    """
    resp = client.get('/signup')
    assert resp.status_code == 200
    assert b'<h1>Sign Up</h1>' in resp.data
    assert b'<input type="text" name= "Username" placeholder="Enter a username"/>' in resp.data
    assert b'<input type="text" name="Password" placeholder="Enter a password"/>' in resp.data
    assert b'<input type="submit" value="Signup"/>' in resp.data


def test_create_account_succesful_page(client, monkeypatch):
    """
    GIVEN a Flask application
    WHEN the '/createaccount' page is posted with username and password
    THEN check that the response is successful and the username is displayed
    """

    def mock_sign_up(self, username, password):
        return 'User successfuly created!'

    monkeypatch.setattr(Backend, 'sign_up', mock_sign_up)

    response = client.post('/createaccount',
                           data=dict(Username='testuser',
                                     Password='testpassword'))
    assert response.status_code == 200
    assert b'testuser' in response.data


def test_create_account_missing_fields(client):
    """
    GIVEN a Flask application
    WHEN the '/createaccount' page is posted with missing username or password fields
    THEN check that the response is successful and the appropriate error message is displayed
    """
    # test missing username field
    response = client.post('/createaccount',
                           data=dict(Username='', Password='testpassword'))
    assert response.status_code == 200
    assert b'Please enter a username and password.' in response.data

    # test missing password field
    response = client.post('/createaccount',
                           data=dict(Username='testuser', Password=''))
    assert response.status_code == 200
    assert b'Please enter a username and password.' in response.data

    # test missing username and password fields
    response = client.post('/createaccount',
                           data=dict(Username='', Password=''))
    assert response.status_code == 200
    assert b'Please enter a username and password.' in response.data


def test_create_account_get_page(client):
    """
    GIVEN a Flask application
    WHEN the '/createaccount' page is accessed with GET method
    THEN check that the response is successful and the appropriate error message is displayed
    """
    response = client.get('/createaccount')
    assert response.status_code == 200
    assert b'Please go back and use the form!' in response.data


def test_create_account_exception(client, monkeypatch):
    """
    GIVEN a Flask application and a monkeypatched Backend class
    WHEN the '/createaccount' page is posted with username and password
    THEN check that the response is successful and the appropriate error message is displayed
    """

    def mock_sign_up(self, username, password):
        raise Exception('Test exception')

    monkeypatch.setattr(Backend, 'sign_up', mock_sign_up)

    response = client.post('/createaccount',
                           data=dict(Username='testuser',
                                     Password='testpassword'))

    assert response.status_code == 200
    assert b'Account creation failed: Test exception' in response.data


@patch("flaskr.backend.Backend.get_all_page_names",
       return_value=['Trial page 1', 'Trial page 2'])
def test_pages_list(mock_get_all_page_names, client):
    '''
    Test that it displays all the pagas available for view on the wiki.
    '''
    resp = client.get("/pages")
    assert resp.status_code == 200
    assert b'Pages contained in this Wiki' in resp.data


@patch("flaskr.backend.Backend.get_wiki_page",
       return_value=b"sample page content")
@patch("flaskr.backend.Backend.check_page_author", return_value=b"fake author")
@patch("flaskr.user.User.get_id", return_value=b'Dimitripl5')
@patch('flaskr.backend.Backend.get_all_page_names', return_value=['page_test'])
@patch('flaskr.backend.Backend.get_bookmarks', return_value=[])
def test_specific_page(mock_get_wiki_page, mock_check_page_author, mock_get_id,
                       mock_get_all_page_names, mock_get_bookmarks, client):
    '''
    Test that specific page can be called to display.
    '''
    resp = client.get("/pages/page_test")
    assert resp.status_code == 200
    assert b'page_test' in resp.data
    assert b'fake author' in resp.data


@patch("flaskr.backend.Backend.upload", return_value=b"upload sucessful")
@patch("flask_login.utils._get_user", return_value=MagicMock())
def test_upload_page(mock_upload, mock_logged_in, client):
    '''
    Test that the upload page displays correctly when called.
    '''
    resp = client.get("/upload")

    assert resp.status_code == 200
    assert b'Upload a doc to the Wiki' in resp.data


#Testing that users are seeing the correct login page
def test_login_page(client):
    resp = client.get('/login')
    assert resp.status_code == 200
    assert b'<h1>Sign In</h1>' in resp.data
    assert b'Username' in resp.data
    assert b'Password' in resp.data
    assert b'value="Submit"' in resp.data


#Testing that users see the correct page when wrong username is entered
def test_login_wrong_username(client, monkeypatch):

    def mock_sign_in(self, username, password):
        return False

    monkeypatch.setattr(Backend, 'sign_in', mock_sign_in)
    resp = client.post('/login',
                       data={
                           'username': 'sdf',
                           'password': 'testing123',
                       })
    assert resp.status_code == 200
    assert b"Incorrect password or username" in resp.data


#Testing that users are sent to the right page when the wrong password is entered
def test_login_wrong_password(client, monkeypatch):

    def mock_sign_in(self, username, password):
        return False

    monkeypatch.setattr(Backend, 'sign_in', mock_sign_in)
    resp = client.post('/login',
                       data={
                           'username': 'Dimitripl5',
                           'password': 'testing76576',
                       })
    assert resp.status_code == 200
    assert b"Incorrect password or username" in resp.data


#Testing that users are able to login and logout successfully
def test_login_and_logout_successful(client, monkeypatch):

    def mock_sign_in(self, username, password):
        return True

    monkeypatch.setattr(Backend, 'sign_in', mock_sign_in)
    resp = client.post('/login',
                       data=dict(
                           username='Dimitripl5',
                           password='testing123',
                       ))
    assert resp.status_code == 200
    assert b'Welcome Dimitripl5' in resp.data
    assert b'Log Out' in resp.data
    #Test logout
    resp = client.get("/logout")
    assert b'Log In' in resp.data


def test_bookmark(client, monkeypatch):
    '''
    Test that bookmark button is working properly and that log in is required. .
    '''

    #Setting mock objects
    def mock_bookmark(self, page_title, name):
        return True

    def mock_sign_in(self, username, password):
        return 'Sign In Successful'

    def mock_get_wiki_page(self, name):
        return "This is a test page"

    def mock_check_page_author(self, page_title):
        return None

    monkeypatch.setattr(Backend, 'bookmark', mock_bookmark)
    monkeypatch.setattr(Backend, 'sign_in', mock_sign_in)
    monkeypatch.setattr(Backend, 'get_wiki_page', mock_get_wiki_page)
    monkeypatch.setattr(Backend, 'check_page_author', mock_check_page_author)

    #Log in and going to bookmark route
    resp = client.post('/login',
                       data=dict(
                           username='Dimitripl5',
                           password='testing123',
                       ))
    resp = client.get('/bookmark/test/Dimitripl5')

    #Ensuring bookmark was successful
    assert resp.status_code == 200
    assert b'Bookmark added!' in resp.data


def test_view_bookmarks(client, monkeypatch):
    '''
    Test that bookmarks are able to properly be viewed.
    '''

    #mocking

    def mock_get_id(self):
        return 'Dimitripl5'

    def mock_get_bookmarks(self, name, existing_pages):
        return ['Test Page', 'Hello World']

    def mock_get_all_page_names(self):
        return ['Test Page', 'Hello World']

    def mock_sign_in(self, username, password):
        return 'Sign In Successful'

    monkeypatch.setattr(User, 'get_id', mock_get_id)
    monkeypatch.setattr(Backend, 'get_bookmarks', mock_get_bookmarks)
    monkeypatch.setattr(Backend, 'sign_in', mock_sign_in)
    monkeypatch.setattr(Backend, 'get_all_page_names', mock_get_all_page_names)

    #login then go to bookmarks route
    resp = client.post('/login',
                       data=dict(
                           username='Dimitripl5',
                           password='testing123',
                       ))
    resp = client.get('/bookmarks')

    #Ensure bookmarks are pulled up properly
    assert resp.status_code == 200
    assert b'Bookmarks' in resp.data
    assert b'Test Page' in resp.data
    assert b'Hello World' in resp.data


def test_remove_bookmark(client, monkeypatch):
    '''
    Test that remove bookmark button redirects back to bookmark page.
    '''

    #mocking
    def mock_get_id(self):
        return 'Dimitripl5'

    def mock_get_bookmarks(self, name, existing_pages):
        bookmarks = ['Test Page', 'Hello World', 'Sucks']
        for bookmark in bookmarks:
            if bookmark not in existing_pages:
                bookmarks.remove(bookmark)
        return bookmarks

    def mock_get_all_page_names(self):
        return ['Test Page', 'Hello World']

    def mock_remove_bookmark(self, title, name):
        return "Bookmark successfully deleted"

    def mock_sign_in(self, username, password):
        return 'Sign In Successful'

    def mock_check_page_author(self, page_title):
        return None

    def mock_get_wiki_page(self, title):
        return 'this is test text'

    monkeypatch.setattr(Backend, 'get_wiki_page', mock_get_wiki_page)
    monkeypatch.setattr(User, 'get_id', mock_get_id)
    monkeypatch.setattr(Backend, 'check_page_author', mock_check_page_author)
    monkeypatch.setattr(Backend, 'get_bookmarks', mock_get_bookmarks)
    monkeypatch.setattr(Backend, 'sign_in', mock_sign_in)
    monkeypatch.setattr(Backend, 'remove_bookmark', mock_remove_bookmark)
    monkeypatch.setattr(Backend, 'get_all_page_names', mock_get_all_page_names)

    #login then remove bookmark
    resp = client.post('/login',
                       data=dict(
                           username='Dimitripl5',
                           password='testing123',
                       ))
    resp = client.get('/remove_bookmark/Sucks/DimitriPL5')
    assert b'Bookmark deleted!' in resp.data

    #Ensure bookmarks are shown again and the right bookmark was removed
    resp = client.get('/bookmarks')
    assert resp.status_code == 200
    assert b'Bookmarks' in resp.data
    assert b'Test Page' in resp.data
    assert b'Hello World' in resp.data
    assert b'Sucks' not in resp.data


# Test correct options are displayed when user is author
user = MagicMock()
user.get_id.return_value = 'Elei'


@patch("flaskr.backend.Backend.check_page_author", return_value='Elei')
@patch("flaskr.backend.Backend.get_wiki_page",
       return_value=b"sample page content")
@patch("flaskr.backend.Backend.get_all_page_names", return_value=['test_page'])
@patch('flaskr.backend.Backend.get_bookmarks', return_value=[])
@patch("flask_login.utils._get_user", return_value=user)
def test_page_is_viewed_by_author(mock_check_page_author, mock_wiki_page,
                                  mock_logged_in, mock_get_all_page_names,
                                  mock_get_bookmarks, client):
    resp = client.get('pages/test_page')
    assert resp.status_code == 200
    #assert b'Delete' in resp.data
    assert b'Edit' in resp.data
    assert b'Report' not in resp.data
    assert b'sample page content' in resp.data


# Test correct options are displayed when user is not author
@patch("flaskr.backend.Backend.check_page_author", return_value='Elei')
@patch("flaskr.backend.Backend.get_wiki_page",
       return_value=b"sample page content")
@patch("flaskr.backend.Backend.get_all_page_names", return_value=['test_page'])
@patch('flaskr.backend.Backend.get_bookmarks', return_value=[])
@patch("flask_login.utils._get_user", return_value=MagicMock())
def test_page_is_not_viewed_by_author(mock_check_page_author, mock_wiki_page,
                                      mock_logged_in, mock_get_all_page_names,
                                      mock_get_bookmarks, client):
    resp = client.get('pages/test_page')
    assert resp.status_code == 200
    assert b'Report' in resp.data
    assert b'Delete' not in resp.data
    assert b'Edit' not in resp.data
    assert b'sample page content' in resp.data


# Test correct options are displayed when user is not signed in
@patch("flaskr.backend.Backend.check_page_author", return_value='Elei')
@patch("flaskr.backend.Backend.get_wiki_page",
       return_value=b"sample page content")
def test_page_is_viewed_by_not_signed_in_user(mock_check_page_author,
                                              mock_wiki_page, client):
    resp = client.get('pages/test_page')
    assert resp.status_code == 200
    assert b'Report' in resp.data
    assert b'Delete' not in resp.data
    assert b'Edit' not in resp.data
    assert b'sample page content' in resp.data


# Test report brings up the right page
@patch("flask_login.utils._get_user", return_value=MagicMock())
def test_user_can_make_report(mock_logged_in, client):
    resp = client.get('/report/sample page')
    assert resp.status_code == 200
    assert b'Write your report for the page:' in resp.data
    assert b'sample page' in resp.data


# Test report is saved
@patch("flaskr.backend.Backend.report",
       return_value="Your report was sent successfully.")
@patch("flask_login.utils._get_user", return_value=MagicMock())
def test_save_report(mock_report_page, mock_logged_in, client):
    resp = client.post('/save_report/sample page',
                       data={'report': 'I like this page'})
    assert resp.status_code == 200
    assert b'Report Status:' in resp.data
    assert b"Your report was sent successfully." in resp.data


# Test return message if no report is made
@patch("flaskr.backend.Backend.report",
       return_value='You need to enter a message')
@patch("flask_login.utils._get_user", return_value=MagicMock())
def test_no_report_made(mock_report_page, mock_logged_in, client):
    resp = client.post('/save_report/sample page', data={'report': ''})
    assert resp.status_code == 200
    assert b'Report Status:' in resp.data
    assert b'You need to enter a message' in resp.data


# Test page is successfully deleted
@patch("flaskr.backend.Backend.delete_page", return_value=True)
@patch("flask_login.utils._get_user", return_value=MagicMock())
def test_delete_page_successful(mock_delete_page, mock_logged_in, client):
    resp = client.get('/delete/sample page')
    assert resp.status_code == 200
    assert b'The page sample page, has been deleted.'


# Test delete page is unsuccessful
@patch("flaskr.backend.Backend.delete_page", return_value=False)
@patch("flask_login.utils._get_user", return_value=MagicMock())
def test_delete_page_unsuccessful(mock_delete_page, mock_logged_in, client):
    resp = client.get('/delete/sample page')
    assert resp.status_code == 200
    assert b'The page was not deleted. Please try again later.'


# Test that page contents is displayed in editable text box when edit is clicked
# Mock the backend functions
@patch("flaskr.backend.Backend.get_wiki_page",
       return_value=b"sample page content")
@patch("flask_login.utils._get_user", return_value=MagicMock())
def test_edit(mock_get_wiki_page, mock_logged_in, client):
    # call the page
    resp = client.get('/edit/sample page title')
    # Check that return result is correct
    assert resp.status_code == 200
    assert b'Make your edits' in resp.data
    assert b'sample page title' in resp.data
    assert b'sample page content' in resp.data


# Test edit is saved
@patch("flaskr.backend.Backend.upload", return_value=b"upload sucessful")
@patch("flask_login.utils._get_user", return_value=MagicMock())
def test_save_edit(mock_upload, mock_logged_in, client):
    resp = client.post('/save_edit/sample page',
                       data={'content': 'random data'})
    assert b'Result for editing' in resp.data
    assert b'sample page' in resp.data
    assert b"upload sucessful" in resp.data
