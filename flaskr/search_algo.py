

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


