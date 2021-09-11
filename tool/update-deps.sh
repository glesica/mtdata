#!/usr/bin/env sh

set -e

# Update dependencies. Run this whenever a dependency changes.

pipenv lock --pre
pip freeze > requirements.txt

