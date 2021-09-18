#!/usr/bin/env sh

set -e

pkg_version=$(python mtdata/_version.py)

docker build \
  -t glesica/mtdata:${pkg_version} \
  -t glesica/mtdata:latest \
  .
