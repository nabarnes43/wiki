from flaskr.backend import Backend
import unittest 
from unittest.mock import MagicMock
from unittest.mock import Mock
from unittest.mock import patch

# TODO(Project 1): Write tests for Backend methods.

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
