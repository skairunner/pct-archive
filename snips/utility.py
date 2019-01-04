from re import sub
import string

# Django is dumb and won't let you access 
# keys prefixed with underscores in templates.
# Elasticsearch returns many, many fields with
# underscore prefixes, so have to rename.
def sanitize_keys(data):
    if isinstance(data, list):
        newlist = []
        for item in data:
            newlist.append(sanitize_keys(item))
        return newlist
    if isinstance(data, dict):
        newdata = {}
        for key, value in data.items():
            if key[0] == '_':
                newdata[key[1:]] = sanitize_keys(value)
            else:
                newdata[key] = sanitize_keys(value)
        return newdata
    return data


def elastic_filter(term):
    term = term.lower().translate({ord(c): None for c in string.punctuation})
    return term.replace(' ', '_')

