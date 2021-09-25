from time import sleep
from typing import Protocol, Callable, TypeVar

from .dataset import FetchResult


class Result(Protocol):
    """
    A generic result that can be checked for success.
    """

    @property
    def success(self) -> bool:
        """
        Indicates whether the result is a success.
        """
        ...


TResult = TypeVar("TResult", Result, FetchResult)


Operation = Callable[[], TResult]


def retry(
    operation: Operation, attempt_delta: int = 3, max_attempts: int = 3
) -> TResult:
    """
    Retry an operation some number of times with a linear back-off.
    """
    attempts = 0

    while True:
        delay = attempts * attempt_delta
        sleep(delay)

        result = operation()
        if result.success:
            return result

        attempts += 1
        if attempts >= max_attempts:
            return result
