#!/bin/sh
# Runs the exact checks (about a minute); run from anywhere. Needs python3.12 (standard library only).
# Add --drat to also run drat-trim on the retained proof (drat-trim on PATH or in $DRAT_TRIM).
set -e
exec python3.12 -I -B "$(dirname "$0")/check.py" "$@"
