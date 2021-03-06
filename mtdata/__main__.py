from typing import Iterable, List

from .manifest import ALL_DATASETS, ALL_STORES, get_store, get_dataset
from .parameters import parse_parameters
from .registry import Registry


def _choices_warning(kind: str, value: str, choices: Iterable[str]) -> None:
    print(f'invalid {kind} ({value}) - valid values: {", ".join(choices)}')


def _main(args: List[str]) -> None:
    """
    Run the application with the given command line.
    """
    params = parse_parameters(args)

    if params.list_datasets:
        print("DATASETS")
        for dataset in ALL_DATASETS:
            print(dataset.name())

    if params.list_stores:
        print("STORES")
        for store in ALL_STORES:
            print(store.name())

    if params.list_datasets or params.list_stores:
        return

    stores = []
    if params.stores:
        for store_name in params.stores:
            next_store = get_store(store_name)
            if next_store is None:
                _choices_warning("store", store_name, [s.name() for s in ALL_STORES])
            else:
                stores.append(next_store)
    else:
        stores = list(ALL_STORES)

    configs = []
    if params.datasets:
        for dataset_name in params.datasets:
            next_dataset = get_dataset(dataset_name)
            if next_dataset is None:
                _choices_warning(
                    "dataset", dataset_name, [d.name() for d in ALL_DATASETS]
                )
            else:
                configs.append((next_dataset, stores))
    else:
        for dataset in ALL_DATASETS:
            configs.append((dataset, stores))

    registry = Registry(configs)
    results = registry.update(params.namespace)

    for update_result in results:
        status = "ok" if update_result.success else "fail"
        print(f"{update_result.name} - {status}")


def main():
    """
    Default entrypoint used py the PyPI package. This must remain
    a zero parameter function.
    """
    import sys

    _main(sys.argv[1:])


if __name__ == "__main__":
    main()
