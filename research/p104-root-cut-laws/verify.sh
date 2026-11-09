#!/bin/sh
# Runs the exact checks; run from anywhere. Needs python3.12 only (standard library).
set -e
D="$(dirname "$0")"
exec python3.12 -I -B "$D/check.py"
