from typing import Iterable, Type, Optional

from mtdata.dataset import Dataset
from mtdata.datasets.air_quality import AirQuality
from mtdata.datasets.missoula_911 import Missoula911
from mtdata.storage import Storage, JsonLines

# +----------------------------------------------------+
# | Add new datasets below to have them made available |
# | when the software is run.                          |
# +----------------------------------------------------+

ALL_DATASETS: Iterable[Type[Dataset]] = (
    AirQuality,
    Missoula911,
)

# +----------------------------------------------------+
# | Add new storages below to have them made available |
# | when the software is run.                          |
# +----------------------------------------------------+

ALL_STORES: Iterable[Type[Storage]] = (
    JsonLines,
)

# +-------------------------------------+
# | Helpers for accessing the manifests |
# +-------------------------------------+


def get_store(name: str) -> Optional[Type[Storage]]:
    for store in ALL_STORES:
        if store.name() == name:
            return store
    return None


def get_dataset(name: str) -> Optional[Type[Dataset]]:
    for dataset in ALL_DATASETS:
        if dataset.name() == name:
            return dataset
    return None
