#!/usr/bin/env bash
set -ueo pipefail

if [ "$#" -eq 0 ]; then
  set -- discover -p '*_test.py'
fi

python -m unittest "${@}"
