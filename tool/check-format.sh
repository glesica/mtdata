#!/usr/bin/env sh

set -e

pipenv run python -m black -t py39 --check mtdata/
