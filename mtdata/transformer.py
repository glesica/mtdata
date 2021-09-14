from typing import Callable, Any, Optional, Dict

from mtdata.dataset import Row
from mtdata.fields import rename_fields, prune_fields


class Transformer:
    """
    A transformation that can be applied to a single dataset row
    represented as a dictionary. The transformation can update field
    names and make arbitrary changes to field data.

    When the transformation is applied, the following will happen:

    1. Any fields not included in the transformation will be pruned
    2. Fields that have old names specified will be renamed
    3. Values will be updated for fields that have update functions

    The row will be transformed in-place but also returned to the caller.

    >>> t = Transformer()
    >>> t.add_field('a', 'A')
    >>> t.add_field('b', 'B', lambda x: x.lower())
    >>> t({'A': 'XYZ', 'B': 'XYZ'})
    {'a': 'XYZ', 'b': 'xyz'}
    """
    _name_mapping: Dict[str, str]
    _update_functions: Dict[str, Callable[[Any], Any]]

    def __init__(self):
        self._name_mapping = {}
        self._update_functions = {}

    def __call__(self, row: Row) -> Row:
        rename_fields(row, self._name_mapping)
        prune_fields(row, self._name_mapping.values())

        for name, update in self._update_functions.items():
            row[name] = update(row[name])

        return row

    def add_field(self,
                  name: str,
                  old_name: Optional[str] = None,
                  updater: Callable[[Any], Any] = lambda a: a) -> None:
        """
        Add a field to the transformation.

        >>> t = Transformer()
        >>> t.add_field('a', 'A', lambda x: x.lower())
        >>> t._name_mapping
        {'A': 'a'}
        >>> t._update_functions['a']('ABC')
        'abc'
        """
        if old_name is not None:
            self._name_mapping[old_name] = name
        else:
            self._name_mapping[name] = name

        self._update_functions[name] = updater
