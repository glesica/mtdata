#!/usr/bin/env sh

set -e

echo "+--------------------------------------+"
echo "| CHECK TYPES                          |"
echo "+--------------------------------------+"
./tool/check-types.sh

echo "+--------------------------------------+"
echo "| CHECK TESTS                          |"
echo "+--------------------------------------+"
./tool/check-tests.sh

echo "+--------------------------------------+"
echo "| CHECK FORMAT                         |"
echo "+--------------------------------------+"
./tool/check-format.sh

echo "+--------------------------------------+"
echo "| CHECK LINTS                          |"
echo "+--------------------------------------+"
./tool/check-lints.sh
