import tempfile

from mtdata.storage import JsonLines, JsonArray

DATA = [
    {
        'c': 3,
        'a': 1,
        'b': 2,
    },
    {
        'c': 30,
        'a': 10,
        'b': 20,
    },
    {
        'c': 300,
        'a': 100,
        'b': 200,
    }
]


def test_json_lines_storage():
    import os

    file, name = tempfile.mkstemp()
    os.close(file)

    sto = JsonLines('')

    sto.replace(name, DATA)
    with open(name, 'r') as file:
        assert len(list(file)) == 3

    sto.append(name, DATA, [], [])
    with open(name, 'r') as file:
        assert len(list(file)) == 6

    data = list(sto.load(name))
    assert len(data) == 6
    assert data[0]['a'] == 1
    assert data[1]['b'] == 20
    assert data[2]['c'] == 300
    assert data[3]['a'] == 1
    assert data[4]['b'] == 20
    assert data[5]['c'] == 300

    sto.replace(name, DATA)
    with open(name, 'r') as file:
        assert len(list(file)) == 3

    data = list(sto.load(name))
    assert len(data) == 3


def test_json_array_storage():
    import json
    import os

    file, name = tempfile.mkstemp()
    os.close(file)

    sto = JsonArray(name)

    sto.replace(name, DATA)
    with open(name, 'r') as file:
        data = json.load(file)
        assert len(data) == 3

    sto.append(name, DATA, [], [])
    with open(name, 'r') as file:
        data = json.load(file)
        assert len(data) == 6
        assert data[0]['a'] == 1
        assert data[1]['b'] == 20
        assert data[2]['c'] == 300
        assert data[3]['a'] == 1
        assert data[4]['b'] == 20
        assert data[5]['c'] == 300

    sto.replace(name, DATA)
    data = list(sto.load(name))
    assert len(data) == 3
    assert data[0]['a'] == 1
    assert data[1]['b'] == 20
    assert data[2]['c'] == 300
