#!/bin/sh
# Runs the exact checks; run from anywhere. Needs python3.12 and numpy (pinned in VERIFY.json).
set -e
exec python3.12 -I -B "$(dirname "$0")/check.py"
