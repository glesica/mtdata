from mtdata.parameters import parse_parameters
from mtdata.registry import Registry


def main() -> None:
    from sys import argv
    params = parse_parameters(argv[1:])

    registry = Registry()
    results = registry.fetch_all(params.out_path)
    for result in results:
        print(f'{result.name} - {"ok" if result.status.success else "fail"}')


if __name__ == '__main__':
    main()
