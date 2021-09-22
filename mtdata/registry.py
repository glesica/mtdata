from datetime import datetime
from typing import Iterable, NamedTuple, Type, Tuple

from .dataset import FetchResult, Dataset
from .storage import Storage, StoreResult

RegistryList = Iterable[Tuple[Type[Dataset], Iterable[Type[Storage]]]]


class UpdateResult(NamedTuple):
    """
    An accumulation of the results from the various steps in the update
    process. If anything at all failed, success will be ``False``. Finding
    the failure within the various sub-results is, at this time, up to
    the consumer.
    """

    success: bool
    fetch_result: FetchResult
    store_results: Iterable[StoreResult]
    name: str
    timestamp: datetime


class Registry:
    """
    A collection of datasets mapped to stores that are used to persist
    the data they retrieve. This is where the actual ETL process happens,
    using the facilities provided by the datasets and stores.
    """

    _configs: RegistryList

    def __init__(self, configs: RegistryList = ()):
        self._configs = list(configs)

    def update(self, namespace: str) -> Iterable[UpdateResult]:
        """
        Fetch new data for all datasets and store it accordingly.
        """
        for dataset_class, store_classes in self._configs:
            dataset = dataset_class()
            fetch_result = dataset.fetch()

            if fetch_result.success:
                transformer = dataset.transformer
                transformed_data = (transformer(d) for d in fetch_result.data)
                store_results = []
                success = True
                for store_class in store_classes:
                    store = store_class(namespace=namespace)
                    store_result = store.append(
                        name=dataset.name(),
                        data=transformed_data,
                        dedup_facets=dataset.dedup_facets,
                        dedup_fields=dataset.dedup_fields,
                    )
                    store_results.append(store_result)
                    success = success and store_result.success

                if success:
                    yield UpdateResult(
                        success=True,
                        fetch_result=fetch_result,
                        store_results=store_results,
                        name=dataset.name(),
                        timestamp=datetime.now(),
                    )
                else:
                    yield UpdateResult(
                        success=False,
                        fetch_result=fetch_result,
                        store_results=store_results,
                        name=dataset.name(),
                        timestamp=datetime.now(),
                    )
            else:
                yield UpdateResult(
                    success=False,
                    fetch_result=fetch_result,
                    store_results=(),
                    name=dataset.name(),
                    timestamp=datetime.now(),
                )
