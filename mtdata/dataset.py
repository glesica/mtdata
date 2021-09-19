from abc import ABC, abstractmethod
from typing import NamedTuple, Iterable

from mtdata.row import Row
from mtdata.transformer import Transformer


class FetchResult(NamedTuple):
    """
    The result of a completed fetch operation. If the operation was
    successful (data were acquired, or there were no new data available)
    then ``success`` should be ``True``, ``False`` otherwise.

    Upon success, it is reasonable for the ``message`` to be the empty
    string. However, if the operation failed, then the ``message`` field
    should contain some kind of explanation suitable for presentation to
    the user and inclusion in log files.

    If the fetch was successful, then ``data`` should contain the rows
    that were acquired from the data source. It may be empty if there
    were no rows available (this will depend on the source). It should
    also be empty on failure.
    """

    success: bool
    message: str
    data: Iterable[Row]


class Dataset(ABC):
    """
    A single collection of data, represented as a table.
    """

    @staticmethod
    @abstractmethod
    def name() -> str:
        """
        The dataset name, which is used in the UI and for things
        like file and table names.
        """
        pass

    @property
    @abstractmethod
    def dedup_facets(self) -> Iterable[str]:
        """
        Fields used to determine which rows should be compared for
        de-duplication.

        For example, if the data are sensor readings for various locations,
        the field that indicates the location would be listed here. That
        way, we don't drop a new reading from a different location just
        because it occurred at the same time as a reading from a different
        location.

        Uses the transformed version of the field names.
        """
        pass

    @property
    @abstractmethod
    def dedup_fields(self) -> Iterable[str]:
        """
        Fields used to compare rows for de-duplication. This is likely to
        be some kind of timestamp, but that depends on the kind of data.

        For example, if the data are sensor readings and each row is
        timestamped based on when the reading occurred, then that field
        will be listed here because two or more fetches might retrieve the
        same reading instance.

        Uses the transformed version of the field names.
        """
        pass

    @property
    @abstractmethod
    def transformer(self) -> Transformer:
        """
        The transformer to be applied to each row that is fetched from
        the data source before it is stored.
        """
        pass

    @abstractmethod
    def fetch(self) -> FetchResult:
        """
        Fetch new data from the source (generally the web).
        """
        pass
