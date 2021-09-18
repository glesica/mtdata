from typing import NamedTuple, List, Tuple

from mtdata._version import VERSION


def comma_tuple(arg: str) -> Tuple[str]:
    return tuple((a.strip() for a in arg.split(',')))


class Parameters(NamedTuple):
    datasets: Tuple[str]
    namespace: str
    stores: Tuple[str]


def parse_parameters(args: List[str]) -> Parameters:
    from argparse import ArgumentParser

    parser = ArgumentParser(
        'mtdata',
        description='A tool to help anyone build a mountain of public data',
    )

    parser.add_argument(
        '--datasets',
        '-d',
        type=comma_tuple,
        help='datasets to fetch, comma-delimited',
        default=(),
    )
    parser.add_argument(
        '--namespace',
        '-n',
        type=str,
        help='project namespace',
        default='data',
    )
    parser.add_argument(
        '--stores',
        '-s',
        type=comma_tuple,
        help='stores to use for fetched data, comma-delimited',
        default=(),
    )
    parser.add_argument(
        '--version',
        '-v',
        action='version',
        version=f'mtdata {VERSION}',
    )

    parsed_args = parser.parse_args(args)

    return Parameters(
        datasets=parsed_args.datasets,
        namespace=parsed_args.namespace,
        stores=parsed_args.stores,
    )
