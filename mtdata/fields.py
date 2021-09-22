from typing import Dict, Iterable

from .row import Row


def prune_fields(row: Row, keys: Iterable[str]) -> Row:
    """
    Remove fields from the row that are not included in the iterable
    of keys provided. The row is mutated, but also returned to the
    caller.

    >>> prune_fields({'a': 1, 'b': 2}, ['b'])
    {'b': 2}
    """
    keys_set = set(keys)
    keys_bad = [k for k in row.keys() if k not in keys_set]
    for key in keys_bad:
        del row[key]

    return row


def rename_fields(row: Row, mapping: Dict[str, str]) -> Row:
    """
    Rename the fields of the given row using the name mapping provided.
    The row is mutated, but also returned to the caller.

    >>> rename_fields({'A': 1, 'b': 2}, {'A': 'a', 'b': 'b'})
    {'a': 1, 'b': 2}
    """
    for old, new in mapping.items():
        value = row[old]
        del row[old]
        row[new] = value

    return row
