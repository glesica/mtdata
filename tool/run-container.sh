#!/usr/bin/env sh

set -e

docker run --mount src="${PWD}/data",target=/data,type=bind glesica/mtdata:latest
