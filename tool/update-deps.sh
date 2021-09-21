#!/usr/bin/env sh

set -e

# Update dependencies. Run this whenever a dependency changes.

pipenv lock --pre
pipenv sync --pre
pip freeze --exclude mtdata > requirements.txt

