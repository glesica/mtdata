from datetime import datetime
from typing import List, Iterable, NamedTuple

from mtdata.dataset import FetchStatus
from mtdata.manifest import DatasetFactory, ALL_DATASETS


class FetchResult(NamedTuple):
    name: str
    status: FetchStatus
    timestamp: datetime


class Registry:
    _factories: List[DatasetFactory]
    _results: List[FetchResult]

    def __init__(self, factories: Iterable[DatasetFactory] = ALL_DATASETS):
        self._factories = list(factories)
        self._results = []

    def fetch_all(self, out_path: str) -> List[FetchResult]:
        self._results.clear()

        for factory in self._factories:
            dataset = factory()

            status = dataset.fetch(out_path)
            if status is None:
                continue

            self._results.append(FetchResult(
                name = dataset.name,
                status = status,
                timestamp = datetime.now(),
            ))

        return list(self._results)
