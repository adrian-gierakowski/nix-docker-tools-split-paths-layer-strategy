#!/usr/bin/env bash
set -ueo pipefail

test_args=${@:-"src/test.py"}

nodemon -e py -x "python -m unittest ${test_args[@]}"
