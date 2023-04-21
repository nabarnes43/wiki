from .search_algo import levenshtein_distance


def test_levenshtein_distance():
    """
    Test the levenshtein_distance function by comparing the output of the function with the
    expected Levenshtein distance between two input strings.
    """

    # Test case 1: Identical strings
    expected_distance = 0
    ld = levenshtein_distance('kitten', 'kitten')
    assert ld == expected_distance

    # Test case 2: Strings with a single different character
    expected_distance = 1
    ld = levenshtein_distance('kitten', 'sitten')
    assert ld == expected_distance

    # Test case 3: Strings with different lengths and multiple different characters
    expected_distance = 2
    ld = levenshtein_distance('hel', 'hello')
    assert ld == expected_distance
