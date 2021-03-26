#!/usr/bin/env bash
set -ueo pipefail
args=${@:-"discover -p '*_test.py'"}

nodemon -e py -x "python -m unittest ${args[@]}"
