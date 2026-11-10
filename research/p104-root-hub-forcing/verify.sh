#!/bin/sh
# Runs the exact checks; run from anywhere. Needs python3.12 (standard library only).
set -e
exec python3.12 -I -B "$(dirname "$0")/check.py"
