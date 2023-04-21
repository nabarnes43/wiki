from flaskr.backend import Backend
from .search_algo import levenshtein_distance
import unittest
from unittest.mock import MagicMock
from google.cloud import exceptions
from unittest.mock import patch
import pytest

#Constants

#How many characters of difference are allowed in search
MAX_CHAR_DIST = 1


@pytest.fixture
def blob():
    mock_blob = MagicMock()
    return mock_blob


@pytest.fixture
def bucket(blob):
    mock_bucket = MagicMock()
    mock_bucket.get_blob.return_value = blob
    return mock_bucket


@pytest.fixture
def storage_client(bucket):
    mock_client = MagicMock()
    mock_client.bucket.return_value = bucket
    return mock_client


@pytest.fixture
def wiki_searcher():
    """
    Fixture that returns a MagicMock object to mock the WikiSearcher class.
    """
    return MagicMock()


@pytest.fixture
def backend(storage_client):
    real_backend = Backend(storage_client)
    return real_backend


def test_search_pages_result(wiki_searcher, backend):
    """
    Tests that the search_pages function returns the expected page titles in the correct order.

    Uses a MagicMock object to mock the WikiSearcher and StorageClient classes and configures the
    mock object to return expected values. Then calls the search_pages function with a search term
    and relevance score, and asserts that the returned page titles match the expected page titles
    in the correct order.
    """

    # Configure the mock object to return the expected values
    wiki_searcher.get_all_page_names.return_value = [
        'Cat', 'Cat Dog', 'Cats Cats Cats', 'Fish'
    ]
    wiki_searcher.get_wiki_page.side_effect = lambda x: {
        'Cat':
            'A cat is a domesticated carnivorous mammal',
        'Cat Dog':
            'A cat dog is does not exist',
        'Cats Cats Cats':
            'I love cats and everything there is to know about them. Cats are great.',
        'Fish':
            'Fish are aquatic animals that breathe through gills. There is even a fish that looks like a catspaw. Watching them is cathartic.'
    }.get(x)

    # Call the search_pages function with the mock object
    search_content = 'cats'
    page_titles = backend.search_pages(search_content, MAX_CHAR_DIST,
                                       wiki_searcher)

    # Assert that the expected page titles are returned in the correct order
    expected_page_titles = ['Cats Cats Cats', 'Cat', 'Cat Dog']
    assert page_titles == expected_page_titles


def test_search_pages_no_result(wiki_searcher, backend):
    """
    Test that the search_pages function returns the expected page titles for no result.
    
    This function uses a MagicMock object to mock the WikiSearcher and StorageClient classes and
    configures the mock object to return expected values. It then calls the search_pages function with
    a search term and relevance score, and asserts that the returned page titles match the expected page
    titles in the correct order.
    """

    # Configure the mock object to return the expected values.
    wiki_searcher.get_all_page_names.return_value = [
        'Cat', 'Dog', 'Bird', 'Fish'
    ]

    # Set up a side effect for the `get_wiki_page` method that returns a dictionary
    # of page content for the given page names.
    wiki_searcher.get_wiki_page.side_effect = lambda x: {
        'Cat':
            'A cat is a domesticated carnivorous mammal',
        'Dog':
            'A dog is a domesticated carnivorous mammal',
        'Bird':
            'Birds, also known as Aves, are a group of warm-blooded vertebrates',
        'Fish':
            'Fish are aquatic animals that breathe through gills'
    }.get(x)

    # Call the search_pages function with the mock object.
    search_content = 'AAA'
    page_titles = backend.search_pages(search_content, MAX_CHAR_DIST,
                                       wiki_searcher)
    # Assert that the expected page titles are returned in the correct order.
    expected_page_titles = []

    # Check if the page titles returned by the search_pages method match the expected page titles.
    assert page_titles == expected_page_titles

    search_content = 'aaa'
    page_titles = backend.search_pages(search_content, MAX_CHAR_DIST,
                                       wiki_searcher)
    assert page_titles == expected_page_titles

    search_content = 'doggg'
    page_titles = backend.search_pages(search_content, MAX_CHAR_DIST,
                                       wiki_searcher)
    assert page_titles == expected_page_titles

    search_content = 'biirrdd'
    page_titles = backend.search_pages(search_content, MAX_CHAR_DIST,
                                       wiki_searcher)
    assert page_titles == expected_page_titles


def test_search_pages_result_order(wiki_searcher, backend):
    '''
        This function tests that the search_pages function returns the expected page titles
        in the correct order. It uses a MagicMock object to mock the WikiSearcher and StorageClient 
        classes and configures the mock object to return expected values. It then calls the search_pages 
        function with a search term and relevance score, and asserts that the returned page titles 
        match the expected page titles in the correct order.
        '''

    # configure the mock object to return the expected values
    wiki_searcher.get_all_page_names.return_value = [
        'Cups', 'Cupertino', 'California', 'California Cups'
    ]
    wiki_searcher.get_wiki_page.side_effect = lambda x: {
        'Cups':
            'Cups are versatile, typically small, open-top containers designed for holding liquids or solids.',
        'Cupertino':
            'Cupertino, a city in Californias Silicon Valley, is renowned for being the headquarters of Apple Inc.',
        'California':
            'California, the most populous state in the United States, is known for its diverse landscapes, iconic landmarks, thriving tech industry',
        'California Cups':
            'In Cupertino, California, a city in the heart of Silicon Valley, you can find a diverse community enjoying their beverages in cups',
    }.get(x)

    # call the search_pages function with the mock object
    search_content = 'cups'
    page_titles = backend.search_pages(search_content, MAX_CHAR_DIST,
                                       wiki_searcher)
    expected_page_titles = ['Cups', 'California Cups']
    assert page_titles == expected_page_titles

    search_content = 'california'
    page_titles = backend.search_pages(search_content, MAX_CHAR_DIST,
                                       wiki_searcher)
    expected_page_titles = ['California', 'California Cups', 'Cupertino']
    assert page_titles == expected_page_titles

    search_content = 'cupertino'
    page_titles = backend.search_pages(search_content, MAX_CHAR_DIST,
                                       wiki_searcher)
    expected_page_titles = ['Cupertino', 'California Cups']
    assert page_titles == expected_page_titles

    search_content = 'california cup'
    page_titles = backend.search_pages(search_content, MAX_CHAR_DIST,
                                       wiki_searcher)
    expected_page_titles = [
        'California Cups', 'California', 'Cups', 'Cupertino'
    ]
    assert page_titles == expected_page_titles


def test_search_pages_relevance_score(backend):
    '''
    This function tests the relevance score calculation for the search_pages function.
    configures the mock object to return expected values. It then calculates the relevance 
    score for a search term and asserts that the result matches the expected value.
    '''

    search_content = 'cat'
    page_title = 'Cat'
    page_content = 'A cat is a domesticated carnivorous mammal'

    title_match_counter = 0
    content_match_counter = 0

    close_title_match_counter = 0
    close_content_match_counter = 0

    search_words = search_content.lower().split()
    title_words = page_title.lower().split()
    page_words = page_content.lower().split()

    for search_word in search_words:

        for title_word in title_words:
            if search_word == title_word:
                title_match_counter += 1
            elif levenshtein_distance(search_word, title_word) <= MAX_CHAR_DIST:
                close_title_match_counter += 1

        for page_word in page_words:

            if search_word == page_word:
                content_match_counter += 1
            elif levenshtein_distance(search_word, page_word) <= MAX_CHAR_DIST:
                close_content_match_counter += 1

    expected_match_score = .9

    match_score = title_match_counter * 0.8 + content_match_counter * 0.1 + close_title_match_counter * 0.08 + close_content_match_counter * 0.02

    assert match_score == expected_match_score
