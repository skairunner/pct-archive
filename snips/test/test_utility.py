from snips.utility import sanitize_keys, elastic_filter

def test_keys_sanitized():
    data = {'_key1': 'val1', 'key2': 'val2'}
    cleaned = sanitize_keys(data)
    assert '_key1' not in cleaned
    assert cleaned['key1'] == 'val1'

def test_nested_sanitize():
    data = {'key1': {'key2': 'val1', '_key3': 'val2'}}
    cleaned = sanitize_keys(data)
    assert 'key3' in cleaned['key1']

def test_filtered():
    term = "Lily (Flechette)"
    term2 = elastic_filter(term)
    assert term2 == "lily_flechette"
