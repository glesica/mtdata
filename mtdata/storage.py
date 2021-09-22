from abc import ABC, abstractmethod
from typing import Iterable, List, Optional, NamedTuple

from .backward import read_backward
from .dataset import Row


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

    @staticmethod
    def dedup(
        existing_data: Iterable[Row],
        new_data: Iterable[Row],
        dedup_facets: Iterable[str] = (),
        dedup_fields: Iterable[str] = (),
    ) -> Iterable[Row]:
        """
        A helper function to de-duplicate data based on the given facets
        and fields. This algorithm won't work for every possible case,
        but it ought to cover the most common situations nicely.

        Important: the ``existing_data`` iterable MUST be in reverse-
        chronological order. In other words, the first element of this
        iterable must be the most recent row added to the store.

        If ``dedup_facets`` are provided, then for each new row, search
        backward through the existing data to find the most recent row
        that matches on those facets, then compare based on the
        ``dedup_fields``. If they match, then the row will not be included
        in the returned iterable.

        If there are no ``dedup_facets``, but there are ``dedup_fields``,
        then grab the most recent row from the stored data and compare it
        against each row of new data. If any of the new rows match, then
        drop that row and all rows that occurred before it, and add the
        remaining rows to the returned iterable.

        If both dedup parameters are empty, then the new data are passed
        through unfiltered.

        >>> list(Storage.dedup(
        ...   reversed([{'a': 1}, {'a': 2}]),
        ...   [{'a': 3}], [], ['a']))
        [{'a': 3}]
        >>> list(Storage.dedup(
        ...   reversed([{'a': 1}, {'a': 2}]),
        ...   [{'a': 2}, {'a': 3}], [], ['a']))
        [{'a': 3}]
        """
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
                # This is complicated-ish. We assume that `data` are in
                # chronological order, and therefore if some element, `i`,
                # in `data` matches the last row we've got stored, then
                # every element in the range `[0, i]` is already stored,
                # and every element in the range `(i, N)` is "new".
                last_row = next(iter(existing_data))

                for row in new_data:
                    equal = True
                    for field in fields:
                        if row[field] != last_row[field]:
                            equal = False
                    if equal:
                        deduped_data.clear()
                    else:
                        deduped_data.append(row)
            else:
                for row in new_data:
                    deduped_data.append(row)

        return deduped_data

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

        for _ in self.load(name):
            break
        else:
            # There are no data (yet) so we can just
            # append all rows in data and return
            return self.replace(name, data)

        existing_data = self.load_backward(name)
        deduped_data = self.dedup(
            existing_data,
            data,
            dedup_facets,
            dedup_fields,
        )

        with open(self.name_to_path(name), "a") as file:
            import json

            for row in deduped_data:
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

    @staticmethod
    def name() -> str:
        return "csv"

    def append(
        self,
        name: str,
        data: Iterable[Row],
        dedup_facets: Iterable[str],
        dedup_fields: Iterable[str],
    ) -> StoreResult:

        for _ in self.load(name):
            break
        else:
            # There are no data (yet) so we can just
            # append all rows in data and return
            return self.replace(name, data)

        existing_data = self.load_backward(name)
        deduped_data = self.dedup(
            existing_data,
            data,
            dedup_facets,
            dedup_fields,
        )

        with open(self.name_to_path(name), "a") as file:
            from csv import DictWriter, QUOTE_NONNUMERIC

            writer = None
            for row in deduped_data:
                if writer is None:
                    writer = DictWriter(
                        file,
                        fieldnames=list(row.keys()),
                        quoting=QUOTE_NONNUMERIC,
                    )
                writer.writerow(row)

        return StoreResult(success=True, message="")

    def load(self, name: str) -> Iterable[Row]:
        from csv import DictReader, QUOTE_NONNUMERIC

        try:
            with open(self.name_to_path(name), "r") as file:
                reader = DictReader(file, quoting=QUOTE_NONNUMERIC)
                for row in reader:
                    yield row
        except FileNotFoundError:
            pass

    def load_backward(self, name: str) -> Iterable[Row]:
        """
        Load the data in reverse order. Used for de-duplication.
        """
        from csv import DictReader, QUOTE_NONNUMERIC
        from itertools import chain

        # We have to kind of hack this because the reader doesn't have
        # support for loading a CSV backward.

        # First grab the header line
        with open(self.name_to_path(name), "r") as header_file:
            header_line = header_file.readline()

        # Then read the file backward and parse each line, but adding
        # the header line at the beginning of the iterator. Skip the
        # last line of the iterator since that's the header row again.
        with open(self.name_to_path(name), "rb") as data_file:
            reader = DictReader(
                chain([header_line], read_backward(data_file)),
                quoting=QUOTE_NONNUMERIC,
            )

            curr = next(reader, None)
            if curr is None:
                return

            while True:
                prev = curr
                curr = next(reader, None)
                if prev is not None:
                    if curr is None:
                        break
                    else:
                        yield prev

    def replace(self, name: str, data: Iterable[Row]) -> StoreResult:
        with open(self.name_to_path(name), "w") as file:
            from csv import DictWriter, QUOTE_NONNUMERIC

            writer = None
            for row in data:
                if writer is None:
                    writer = DictWriter(
                        file,
                        fieldnames=list(row.keys()),
                        quoting=QUOTE_NONNUMERIC,
                    )
                    writer.writeheader()
                writer.writerow(row)

        return StoreResult(
            success=True,
            message="",
        )

    def name_to_path(self, name: str) -> str:
        """
        Name to path conversion that assumes the file extension.
        """
        return self.get_path(name, "csv")
