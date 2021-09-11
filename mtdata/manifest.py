from typing import Callable, Iterable

from mtdata.dataset import Dataset
from mtdata.datasets.air_quality import AirQuality
from mtdata.datasets.missoula_911 import Missoula911

DatasetFactory = Callable[[], Dataset]

# Add new datasets below to have them run automatically.

ALL_DATASETS: Iterable[DatasetFactory] = (
    lambda: AirQuality(),
    lambda: Missoula911()
)
