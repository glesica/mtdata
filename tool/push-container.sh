#!/usr/bin/env sh

set -e

pkg_version=$(python mtdata/_version.py)

docker push glesica/mtdata:${pkg_version}
docker push glesica/mtdata:latest
