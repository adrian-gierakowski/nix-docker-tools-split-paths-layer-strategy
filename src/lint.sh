#!/usr/bin/env bash
set -ueo pipefail

flake8 --show-source "${@}"
