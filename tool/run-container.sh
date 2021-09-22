#!/usr/bin/env sh

set -e

docker run --mount type=bind,src="${PWD}/data/",dst=/data glesica/mtdata python -m mtdata -n /data
