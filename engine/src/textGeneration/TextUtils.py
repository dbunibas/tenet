def all_lower(list):
    return [x.lower() for x in list]


def remove_endline(text, withText=None):
    if withText is None:
        return text.replace("\n", "")
    else:
        return text.replace("\n", withText)


def remove_tabs(text, withText=None):
    if withText is None:
        return text.replace("\t", "")
    else:
        return text.replace("\t", withText)


def remove_multipleSpaces(text):
    return ' '.join(text.split())
