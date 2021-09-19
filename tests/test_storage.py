import tempfile

from mtdata.storage import JsonLines

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

def test_json_lines_storage_dedup():
    import os

    file, path = tempfile.mkstemp(suffix='.lines.json')
    name = path.split('.')[0]
    os.close(file)

    sto = JsonLines('')

    sto.append(name, DATA, [], [])
    with open(path, 'r') as file:
        assert len(list(file)) == 3

    sto.append(name, DATA, [], ['a'])
    with open(path, 'r') as file:
        # I'd expect this to be 3, not 5
        assert len(list(file)) == 5


def test_json_lines_storage():
    import os

    file, path = tempfile.mkstemp(suffix='.lines.json')
    name = path.split('.')[0]
    os.close(file)

    sto = JsonLines('')

    sto.replace(name, DATA)
    with open(path, 'r') as file:
        assert len(list(file)) == 3

    sto.append(name, DATA, [], [])
    with open(path, 'r') as file:
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
    with open(path, 'r') as file:
        assert len(list(file)) == 3

    data = list(sto.load(name))
    assert len(data) == 3