#!/bin/sh
set -eu
cd "$(dirname "$0")"
exec "${PYTHON:-python3}" -B verify.py
