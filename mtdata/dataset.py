from abc import ABC, abstractmethod
from typing import NamedTuple, Optional, Dict, List, Any

Row = Dict[Any, Any]


class FetchStatus(NamedTuple):
    success: bool
    message: str


class Dataset(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def fetch(self, out_path: str) -> Optional[FetchStatus]:
        pass
