#!/usr/bin/env bash
set -ueo pipefail

nodemon -e py -x "flake8 ${@}"
