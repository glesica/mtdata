from abc import ABC, abstractmethod
from typing import Iterable, List, Optional, NamedTuple

from mtdata.backward import read_backward
from mtdata.dataset import Row


class StoreResult(NamedTuple):
    """
    The result of a write operation on a store.

    TODO: We should wrap read operation results as well
    """
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

    @property
    def namespace(self) -> str:
        """
        The namespace is tied to the instance of the running software
        and should be used to construct storage paths.
        """
        return self._namespace

    @abstractmethod
    def append(
        self,
        name: str,
        data: Iterable[Row],
        dedup_facets: Iterable[str],
        dedup_fields: Iterable[str],
    ) -> StoreResult:
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

    @abstractmethod
    def replace(self, name: str, data: Iterable[Row]) -> StoreResult:
        """
        Delete all data currently stored and replace it with the
        given rows.

        The ``name`` is the identifier associated with the dataset being
        stored and should be used to construct any files or tables
        required by the storage implementation.
        """

    def get_path(self, name: str, extension: str) -> str:
        """
        A helper for implementations that use the filesystem. Returns a path
        to a file with the given name and extension, located in a directory
        determined by the ``namespace`` property.
        """
        from os import path

        return path.join(self.namespace, f"{name}.{extension}")


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
        return "json-lines"

    def append(
        self,
        name: str,
        data: Iterable[Row],
        dedup_facets: Iterable[str],
        dedup_fields: Iterable[str],
    ) -> StoreResult:
        facets = set(dedup_facets)
        fields = set(dedup_fields)

        filtered_data: List[Row] = []

        for _ in self.load(name):
            break
        else:
            # There are no data (yet) so we can just
            # append all rows in data and return
            return self.replace(name, data)

        if facets:
            for row in data:
                matched_row: Optional[Row] = None
                for existing_row in self.load_backward(name):
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
                        filtered_data.append(row)
                else:
                    filtered_data.append(row)
        else:
            if dedup_fields:
                # This is complicated-ish. We assume that `data` are in
                # chronological order, and therefore if some element, `i`,
                # in `data` matches the last row we've got stored, then
                # every element in the range `[0, i]` is already stored,
                # and every element in the range `(i, N)` is "new".
                last_row = next(iter(self.load_backward(name)))

                for row in data:
                    equal = True
                    for field in fields:
                        if row[field] != last_row[field]:
                            equal = False
                    if equal:
                        filtered_data.clear()
                    else:
                        filtered_data.append(row)
            else:
                for row in data:
                    filtered_data.append(row)

        with open(self.name_to_path(name), "a") as file:
            import json

            for row in filtered_data:
                json.dump(row, file, sort_keys=True)
                file.write("\n")

        return StoreResult(
            success=True,
            message="",
        )

    def load(self, name: str) -> Iterable[Row]:
        try:
            with open(self.name_to_path(name), "r") as file:
                import json

                for line in file:
                    yield json.loads(line)
        except FileNotFoundError:
            # TODO: Handle file not found better
            pass

    def load_backward(self, name: str) -> Iterable[Row]:
        """
        Load data from the store in reverse order. In other words, the
        first row returned is the row that was most recently added to
        the store, and so on.

        TODO: Consider making this abstract on the base class
        """
        try:
            with open(self.name_to_path(name), "rb") as file:
                import json

                for line in read_backward(file):
                    yield json.loads(line)
        except FileNotFoundError:
            # TODO: Handle file not found better
            pass

    def name_to_path(self, name: str) -> str:
        """
        Convert a name to a file path with the correct extension.
        """
        return self.get_path(name, "lines.json")

    def replace(self, name: str, data: Iterable[Row]) -> StoreResult:
        with open(self.name_to_path(name), "w") as file:
            import json

            for row in data:
                json.dump(row, file, sort_keys=True)
                file.write("\n")

        return StoreResult(
            success=True,
            message="",
        )


class CSVBasic(Storage):
    """
    A minimal CSV implementation that uses a `DictWriter` to write rows
    to the indicated file.
    """

    def append(
        self,
        name: str,
        data: Iterable[Row],
        dedup_facets: Iterable[str],
        dedup_fields: Iterable[str],
    ) -> StoreResult:
        pass

    def load(self, name: str) -> Iterable[Row]:
        pass

    def replace(self, name: str, data: Iterable[Row]) -> StoreResult:
        pass
