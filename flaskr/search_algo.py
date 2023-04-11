from .backend import Backend


#normalized distance for different
def levenshtein_distance(str1, str2):
    m, n = len(str1), len(str2)
    if m < n:
        str1, str2 = str2, str1
        m, n = n, m
    if n == 0:
        return m
    prev = list(range(n + 1))
    for i, char1 in enumerate(str1):
        curr = [i + 1]
        for j, char2 in enumerate(str2):
            curr.append(
                min(curr[-1] + 1, prev[j + 1] + 1, prev[j] + (char1 != char2)))
        prev = curr
    distance = prev[-1]
    normalized_distance = distance / m
    return normalized_distance


#Going to get the distance for each one and combine it into a list
def search_algo(search_content, min_relevance_score):
    min_relevance_score = min_relevance_score / len(search_content)

    search_results = []

    backend = Backend()
    all_pages = backend.get_all_page_names()

    for page_title in all_pages:
        page_content = backend.get_wiki_page(page_title)

        title_distance = levenshtein_distance(search_content, page_title)
        content_similarity = levenshtein_distance(search_content, page_content)
        relevance_score = 0.7 * content_similarity + 0.3 * title_distance

        # scale relevance score by length of search
        relevance_score /= len(search_content)

        print('min relavance score' + str(min_relevance_score))
        print('relavance score' + str(relevance_score))

        if relevance_score <= min_relevance_score:
            search_results.append((page_title, relevance_score))

    search_results.sort(key=lambda x: x[1])

    return search_results
