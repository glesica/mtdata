from abc import ABC, abstractmethod
from typing import Iterable, List, Optional, NamedTuple

from mtdata.backward import read_backward
from mtdata.dataset import Row

class StoreResult(NamedTuple):
    success: bool
    message: str


class Storage(ABC):
    """
    A generic storage manager that can handle writing data to a file
    or other persistence mechanism.
    """
    _namespace: str

    def __init__(self, namespace: str):
        self._namespace = namespace

    @staticmethod
    @abstractmethod
    def name() -> str:
        """
        A human-readable name for the storage implementation. Intended for
        use in the UI.

        By convention, this should be the class name, converted to kabob
        case. So a storage class called ``FancyDatabase`` would be named
        "fancy-database".
        """
        pass

    @property
    def namespace(self) -> str:
        """
        The namespace is tied to the instance of the running software
        and should be used to construct storage paths.
        """
        return self._namespace

    @abstractmethod
    def append(self,
               name: str,
               data: Iterable[Row],
               dedup_facets: Iterable[str],
               dedup_fields: Iterable[str]) -> StoreResult:
        """
        Append some number of rows to the data currently stored. The
        existing data should remain untouched and the new data should,
        where it makes sense, be stored "after" the existing data.

        The ``name`` is the identifier associated with the dataset being
        stored and should be used to construct any files or tables
        required by the storage implementation.

        If ``dedup_facets`` and ``dedup_fields`` are non-empty, then
        de-duplication must occur before the new data are stored. See the
        documentation for ``Dataset`` for an explanation of these fields.
        """
        pass

    @abstractmethod
    def load(self, name: str) -> Iterable[Row]:
        """
        Read in all data and return it as an iterable of rows. The
        implementation may choose to read all rows into memory or
        stream them through an iterator.

        The ``name`` is the identifier associated with the dataset being
        stored and should be used to construct any files or tables
        required by the storage implementation.
        """
        pass

    @abstractmethod
    def replace(self, name: str, data: Iterable[Row]) -> StoreResult:
        """
        Delete all data currently stored and replace it with the
        given rows.

        The ``name`` is the identifier associated with the dataset being
        stored and should be used to construct any files or tables
        required by the storage implementation.
        """
        pass

    def get_path(self, name: str, extension: str) -> str:
        """
        A helper for implementations that use the filesystem. Returns a path
        to a file with the given name and extension, located in a directory
        determined by the ``namespace`` property.
        """
        from os import path
        return path.join(self.namespace, f'{name}.{extension}')

    def dedup(self, existing_data: Iterable[Row], new_data: Iterable[Row], dedup_facets, dedup_fields) -> Iterable[Row]:
        facets = set(dedup_facets)
        fields = set(dedup_fields)

        deduped_data: List[Row] = []

        if facets:
            for row in new_data:
                matched_row: Optional[Row] = None
                for existing_row in existing_data:
                    matches = True
                    for facet in facets:
                        if row[facet] != existing_row[facet]:
                            matches = False
                            break

                    if matches:
                        matched_row = existing_row
                        break

                if matched_row:
                    equal = True
                    for field in fields:
                        if row[field] != matched_row[field]:
                            equal = False
                            break
                    if not equal:
                        deduped_data.append(row)
                else:
                    deduped_data.append(row)
        else:
            if dedup_fields:
                last_row = next(iter(existing_data))

                for row in new_data:
                    equal = True
                    for field in fields:
                        if row[field] != last_row[field]:
                            equal = False

                    if not equal:
                        deduped_data.append(row)
            else:
                for row in new_data:
                    deduped_data.append(row)

        return deduped_data

class JsonLines(Storage):
    """
    A storage implementation that writes each row as a single, JSON-formatted
    line in a file. This allows the data to be "streamed" back without
    reading in the entire file. It also allows efficient append operations
    since the old data needn't be loaded in order to add more.

    Data are stored and retrieved in the order they are appended or replaced.
    Therefore, as long as data are always added in chronological order, they
    will remain in that order.
    """

    @staticmethod
    def name() -> str:
        return 'json-lines'

    def append(self,
               name: str,
               data: Iterable[Row],
               dedup_facets: Iterable[str],
               dedup_fields: Iterable[str]) -> StoreResult:

        for _ in self.load(name):
            break
        else:
            # There are no data (yet) so we can just
            # append all rows in data and return
            return self.replace(name, data)

        existing_data = self.load_backward(name)
        deduped_data = self.dedup(existing_data, data, dedup_facets, dedup_fields)

        with open(self.name_to_path(name), 'a') as file:
            import json
            for row in deduped_data:
                json.dump(row, file, sort_keys=True)
                file.write('\n')

        return StoreResult(
            success=True,
            message='',
        )

    def load(self, name: str) -> Iterable[Row]:
        try:
            with open(self.name_to_path(name), 'r') as file:
                import json
                for line in file:
                    yield json.loads(line)
        except FileNotFoundError:
            pass

    def load_backward(self, name: str) -> Iterable[Row]:
        try:
            with open(self.name_to_path(name), 'rb') as file:
                import json
                for line in read_backward(file):
                    yield json.loads(line)
        except FileNotFoundError:
            pass

    def name_to_path(self, name: str) -> str:
        return self.get_path(name, 'lines.json')

    def replace(self, name: str, data: Iterable[Row]) -> StoreResult:
        with open(self.name_to_path(name), 'w') as file:
            import json
            for row in data:
                json.dump(row, file, sort_keys=True)
                file.write('\n')

        return StoreResult(
            success=True,
            message='',
        )

class CSVBasic(Storage):
    """
    A minimal CSV implementation that uses a `DictWriter` to write rows
    to the indicated file.
    """

    @staticmethod
    def name() -> str:
        return 'csv'

    def append(self, name: str,
               data: Iterable[Row],
               dedup_facets: Iterable[str],
               dedup_fields: Iterable[str]) -> StoreResult:

        existing_data = self.load(name)
        if (existing_data == []):
            return self.replace(name, data)
        
        deduped_data = self.dedup(existing_data, data, dedup_facets, dedup_fields)

        with open(self.name_to_path(name), 'a') as file:
            import csv
            writer = None
            for row in deduped_data:
                if writer is None:
                    writer = csv.DictWriter(file, fieldnames=list(row.keys()))
                writer.writerow(row)

        return StoreResult(
            success=True,
            message=''
        )

    def load(self, name: str) -> Iterable[Row]:
        """
        Convert csv rows into an array of dictionaries
        All data types are automatically checked and converted
        """
        import ast
        from itertools import islice

        cursor = []  # Placeholder for the dictionaries/documents
        try:
            with open(self.name_to_path(name)) as csvFile:
                first_row = csvFile.readlines(1)
                if (len(first_row) == 0):
                    return []

                fieldnames = tuple(first_row[0].strip('\n').split(","))

                for row in islice(csvFile, 0, None):
                    values = list(row.strip('\n').split(","))
                    for i, value in enumerate(values):
                        nValue = ast.literal_eval(value)
                        values[i] = nValue
                    cursor.append(dict(zip(fieldnames, values)))
        except FileNotFoundError:
            pass
        
        return cursor

    def replace(self, name: str, data: Iterable[Row]) -> StoreResult:
        with open(self.name_to_path(name), 'w') as file:
            import csv
            writer = None
            for row in data:
                if writer is None:
                    writer = csv.DictWriter(file, fieldnames=list(row.keys()))
                    writer.writeheader()
                writer.writerow(row)
                
        return StoreResult(
            success=True,
            message='',
        )
    
    def name_to_path(self, name: str) -> str:
        return self.get_path(name, 'csv')