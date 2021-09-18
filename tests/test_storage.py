import tempfile

from mtdata.storage import JsonLines, CSVBasic

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

    file, path = tempfile.mkstemp(suffix='.lines.json')
    name = path.split('.')[0]
    os.close(file)

    sto = JsonLines('')

    sto.append(name, DATA, [], [])
    with open(path, 'r') as file:
        assert len(list(file)) == 3

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

def test_csv_storage():
    import os

    file, path = tempfile.mkstemp(suffix='.csv')
    name = path.split('.')[0]
    os.close(file)

    sto = CSVBasic('')

    sto.append(name, DATA, [], [])
    with open(path, 'r') as file:
        assert len(list(file)) == 4

    sto.replace(name, DATA)
    with open(path, 'r') as file:
        lines = list(file)
        assert len(lines) == 4
        assert lines[0] == 'c,a,b\n'
        assert lines[1] == '3,1,2\n'
        assert lines[2] == '30,10,20\n'
        assert lines[3] == '300,100,200\n'
    
    sto.append(name, DATA, [], [])
    with open(path, 'r') as file:
        lines = list(file)
        assert len(lines) == 7
        assert lines[0] == 'c,a,b\n'
        assert lines[1] == '3,1,2\n'
        assert lines[2] == '30,10,20\n'
        assert lines[3] == '300,100,200\n'
        assert lines[4] == '3,1,2\n'
        assert lines[5] == '30,10,20\n'
        assert lines[6] == '300,100,200\n'

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
        assert len(list(file)) == 4

    data = list(sto.load(name))
    assert len(data) == 3