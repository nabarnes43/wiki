from flaskr.backend import Backend
import unittest 
from unittest.mock import MagicMock
from unittest.mock import Mock
from google.cloud import exceptions
from unittest.mock import patch



# TODO(Project 1): Write tests for Backend methods.
def test_get_wiki_successful():
    storage_client = MagicMock()
    bucket = MagicMock()
    blob = MagicMock()

    # set up mock objects
    content = "This is a test wiki page."
    storage_client.bucket.return_value = bucket
    bucket.blob.return_value = blob
    blob.open.return_value.__enter__.return_value.read.return_value = content

    # call the function
    backend = Backend(storage_client)
    result = backend.get_wiki_page("test_wiki")

    # assert the result
    assert result == content

def test_get_wiki_page_blob_not_found():
    storage_client = MagicMock()
    bucket = MagicMock()
    bucket.name = 'mock_bucket_name'
    blob = MagicMock()
    blob.name = 'mock_name'
    blob.open.side_effect = exceptions.NotFound('Blob not found')
    bucket.blob.return_value = blob
    storage_client.bucket.return_value = bucket

    backend = Backend(storage_client)
    wiki_name = 'mock_wiki_name'
    result = backend.get_wiki_page(wiki_name)

    assert result == f"Error: Wiki page {wiki_name} not found."

#def network error exeption next.



def test_unsuccessful_upload():
    blob = MagicMock()
    blob.name = 'mock_name'
    storage_client = MagicMock()
    storage_client.list_blobs.return_value = [blob]

    backend = Backend(storage_client)
    upload_result = backend.upload('random stuff', 'mock_name')
    assert upload_result == 'Upload failed. You cannot overrite an existing page'

def test_successful_upload():
    storage_client = MagicMock()
    blob = MagicMock()
    storage_client.list_blobs.return_value = [blob]
    
    backend = Backend(storage_client)
    upload_result = backend.upload('random stuff', 'mock_name')
    assert 'uploaded to sdswiki_contents.' in upload_result

def test_upload_to_empty_database():
    storage_client = MagicMock()
    storage_client.list_blobs.return_value = []

    backend = Backend(storage_client)
    upload_result = backend.upload('random stuff', 'mock_name')
    assert 'uploaded to sdswiki_contents.' in upload_result

def test_successful_sign_up():
    blob1 = MagicMock()
    blob2 = MagicMock()
    blob1.name = 'Mary'
    blob2.name = 'Nkata'
    storage_client = MagicMock()
    storage_client.list_blobs.return_value = [blob1, blob2]

    backend = Backend(storage_client)
    sign_up_result = backend.sign_up('Test user', 'no password')

    assert 'successfully created.' in sign_up_result

def test_unsuccessful_sign_up():
    blob1 = MagicMock()
    blob2 = MagicMock()
    blob1.name = 'Mary'
    blob2.name = 'Nkata'
    storage_client = MagicMock()
    storage_client.list_blobs.return_value = [blob1, blob2]

    backend = Backend(storage_client)
    sign_up_result = backend.sign_up('Mary', 'no password')

    assert 'already exists in the database' in sign_up_result

#Testing that wrong usernames are found and that "Username not found" is returned 
def test_no_username_sign_in():
    blob1 = MagicMock()
    blob1.name = 'randomuser3456'
    storage_client = MagicMock()
    storage_client.list_blobs.return_value = [blob1]

    backend = Backend(storage_client)
    result = backend.sign_in('Mary', 'no_password')

    assert result == 'Username not found'

#Testing that wrong passwords are found and that "incorrect password" is returned 
def test_wrong_password_sign_in():
    blob1 = MagicMock()
    blob1.name = 'randomuser3456'
    storage_client = MagicMock()
    storage_client.list_blobs.return_value = [blob1]
    blob1.open.return_value.__enter__.return_value.read.return_value = 'test'

    backend = Backend(storage_client)
    result = backend.sign_in('randomuser3456', 'no_password')

    assert result == 'Incorrect Password'

#Testing that successful sign ins are happening
def test_successful_sign_in():
    blob1 = MagicMock()
    blob1.name = 'dimitripl5'
    storage_client = MagicMock()
    storage_client.list_blobs.return_value = [blob1]
    expected = '44753b854331dc6fbaf617deec25f1aee7d8a25133ca585c70aba5884ef9a1dd'
    blob1.open.return_value.__enter__.return_value.read.return_value = expected
    
    backend = Backend(storage_client)
    result = backend.sign_in("dimitripl5", "testing123")

    assert result == 'Sign In Successful'

#Testing that the get image function is properly returning
def test_get_image_successful():
    storage_client = MagicMock()
    bucket = MagicMock()
    blob = MagicMock()

    # set up mock objects
    content = "Test image"
    storage_client.bucket.return_value = bucket
    bucket.blob.return_value = blob
    blob.name = 'Dimitri.jpg'
    blob.open.return_value.__enter__.return_value.read.return_value = content

    # call the function
    backend = Backend(storage_client)
    result = backend.get_image("Dimitri.jpg")

    # assert the result
    assert result == content