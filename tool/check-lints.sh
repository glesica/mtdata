#!/usr/bin/env sh

set -e

pipenv run python -m pylint mtdata/
