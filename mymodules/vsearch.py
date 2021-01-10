def search4vowels(phrase: str) -> set:
    """Return vowels founded in word"""
    vowels = set('aeiou')
    return vowels.intersection(set(phrase))


def search4letters(phrase: str, letters='aeiou') -> set:
    """Return letters founded in word"""
    return set(letters).intersection(set(phrase))
