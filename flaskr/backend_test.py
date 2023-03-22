# GRADED - Samuel Davidson - March 21, 2023 
from flaskr.backend import Backend
import unittest
from unittest.mock import MagicMock
from google.cloud import exceptions
from unittest.mock import patch

# TODO(Project 1): Write tests for Backend methods.


def test_get_wiki_successful():
    """
    Test that getting a wiki page with a valid name returns the expected content.
    """
    # Setup mock objects for the test
    storage_client = MagicMock()
    bucket = MagicMock()
    blob = MagicMock()
    content = "This is a test wiki page."
    storage_client.bucket.return_value = bucket
    bucket.blob.return_value = blob
    blob.open.return_value.__enter__.return_value.read.return_value = content

    # Create a backend instance and call the method being tested
    backend = Backend(storage_client)
    result = backend.get_wiki_page("test_wiki")

    # Check that the expected content is returned
    assert result == content


def test_get_wiki_page_blob_not_found():
    """
    Test that getting a wiki page with an invalid name returns an error message.
    """
    # Setup mock objects for the test
    storage_client = MagicMock()
    bucket = MagicMock()
    bucket.name = 'mock_bucket_name'
    blob = MagicMock()
    blob.name = 'mock_name'
    blob.open.side_effect = exceptions.NotFound('Blob not found')
    bucket.blob.return_value = blob
    storage_client.bucket.return_value = bucket

    # Create a backend instance and call the method being tested
    backend = Backend(storage_client)
    wiki_name = 'mock_wiki_name'
    result = backend.get_wiki_page(wiki_name)

    # Check that the expected error message is returned
    assert result == f"Error: Wiki page {wiki_name} not found."


def test_get_wiki_page_network_error():
    """
    Test that getting a wiki page when there is a network error returns an error message.
    """
    # Setup mock objects for the test
    storage_client = MagicMock()
    storage_client.bucket.side_effect = Exception("Network error")

    # Create a backend instance and call the method being tested
    backend = Backend(storage_client)
    page_name = "example_page"
    expected_error_message = 'Network error: Network error'
    result = backend.get_wiki_page(page_name)

    # Check that the expected error message is returned
    assert result == expected_error_message


def test_get_all_page_names_success():
    """
    Test that getting all the wiki page names returns the expected list of names.
    """
    # Setup mock objects for the test
    storage_client = MagicMock()
    blob1 = MagicMock()
    blob2 = MagicMock()
    blob3 = MagicMock()
    blob1.name = "blob1"
    blob2.name = "blob2"
    blob3.name = "blob3"
    storage_client.list_blobs.return_value = [blob1, blob2, blob3]

    # Create a backend instance and call the method being tested
    backend = Backend(storage_client)
    expected_result = ["blob1", "blob2", "blob3"]
    result = backend.get_all_page_names()

    # Check that the expected list of names is returned
    assert result == expected_result


def test_get_all_page_names_not_found():
    """
    Test that getting all the wiki page names when there are no pages in the bucket returns an error message.
    """
    # Setup mock objects for the test
    storage_client = MagicMock()
    storage_client.list_blobs.return_value = []

    # Create a backend instance and call the method being tested
    backend = Backend(storage_client)
    expected_result = "Error: No pages found in bucket."
    result = backend.get_all_page_names()

    # Check that the expected error message is returned
    assert result == expected_result


def test_get_all_page_names_network_error():
    """
    Test that getting all the wiki page names when there is a network error returns an error message.
    """
    # Create a mock storage client that raises an exception when listing blobs
    storage_client = MagicMock()
    storage_client.list_blobs.side_effect = Exception("Network error")

    # Create a backend instance with the mock storage client
    backend = Backend(storage_client)

    # Define the expected error message to be returned
    expected_error_message = 'Network error: Network error'

    # Call the get_all_page_names method and verify that it returns the expected error message
    result = backend.get_all_page_names()
    assert result == expected_error_message


def test_upload_existing_page():
    '''
    Test that you cannot upload a page when it already exists
    '''

    blob = MagicMock()
    blob.name = 'mock_name'
    storage_client = MagicMock()
    storage_client.list_blobs.return_value = [blob]

    backend = Backend(storage_client)
    upload_result = backend.upload('random stuff', 'mock_name')

    assert upload_result == 'Upload failed. You cannot overrite an existing page'

def test_upload_no_page_name():
    '''
    Test error message displayed if no page name is provided.
    '''
    backend = Backend()
    upload_result = backend.upload('random stuff', '')
    assert upload_result == 'Please provide the name of the page.'

def test_upload_no_file():
    '''
    Test error message displayed if no data for the page is provided.
    '''
    backend = Backend()
    upload_result = backend.upload(b'', 'mock_name')
    assert upload_result == 'Please upload a file.'

def test_successful_upload():
    '''
    Test successful upload.
    '''
    storage_client = MagicMock()
    blob = MagicMock()
    storage_client.list_blobs.return_value = [blob]

    backend = Backend(storage_client)
    upload_result = backend.upload('random stuff', 'mock_name')
    assert 'uploaded to Wiki.' in upload_result


def test_upload_to_empty_database():
    '''
    Test that uploads are still possible even if database was previously empty.
    '''
    storage_client = MagicMock()
    storage_client.list_blobs.return_value = []

    backend = Backend(storage_client)
    upload_result = backend.upload('random stuff', 'mock_name')
    assert 'uploaded to Wiki.' in upload_result


def test_successful_sign_up():
    '''
    Test that sign up is successful if it is a new user
    '''
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
    '''
    Test that sign up is unsuccessful if it is not a new user
    '''
    blob1 = MagicMock()
    blob2 = MagicMock()
    blob1.name = 'Mary'
    blob2.name = 'Nkata'
    storage_client = MagicMock()
    storage_client.list_blobs.return_value = [blob1, blob2]

    backend = Backend(storage_client)
    sign_up_result = backend.sign_up('Mary', 'no password')

    assert 'already exists in the database' in sign_up_result
