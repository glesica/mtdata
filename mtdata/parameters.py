from typing import NamedTuple, List


class Parameters(NamedTuple):
    out_path: str


def parse_parameters(args: List[str]) -> Parameters:
    from argparse import ArgumentParser

    parser = ArgumentParser(
        'mtdata',
        description='A tool for extracting Montana public data',
    )
    parser.add_argument(
        '--out',
        type=str,
        help='output directory',
        default='.',
    )

    parsed_args = parser.parse_args(args)

    return Parameters(
        out_path=parsed_args.out,
    )
