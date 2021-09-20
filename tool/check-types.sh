#!/usr/bin/env sh

set -e

pipenv run python -m mypy -p mtdata
