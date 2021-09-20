from typing import Iterable, Type, Optional

from mtdata.dataset import Dataset
from mtdata.datasets.air_quality import AirQuality
from mtdata.datasets.missoula_911 import Missoula911
from mtdata.datasets.mt_covid_counts import CovidCounts
from mtdata.storage import CSVBasic, Storage, JsonLines

# +----------------------------------------------------+
# | Add new datasets below to have them made available |
# | when the software is run.                          |
# +----------------------------------------------------+

ALL_DATASETS: Iterable[Type[Dataset]] = (
    AirQuality,
    Missoula911,
    CovidCounts,
)

# +----------------------------------------------------+
# | Add new storages below to have them made available |
# | when the software is run.                          |
# +----------------------------------------------------+

ALL_STORES: Iterable[Type[Storage]] = (
    JsonLines,
    CSVBasic,
)

# +-------------------------------------+
# | Helpers for accessing the manifests |
# +-------------------------------------+


def get_store(name: str) -> Optional[Type[Storage]]:
    """
    Get the store class with the given name, or ``None`` if there is
    no store implementation in the manifest with that name.
    """
    for store in ALL_STORES:
        if store.name() == name:
            return store
    return None


def get_dataset(name: str) -> Optional[Type[Dataset]]:
    """
    Get the dataset class with the given name, or ``None`` if there is
    no dataset implementation in the manifest with that name.
    """
    for dataset in ALL_DATASETS:
        if dataset.name() == name:
            return dataset
    return None
