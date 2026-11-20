#!/bin/sh
set -eu
cd -- "$(dirname -- "$0")"
result=$(mktemp)
trap 'rm -f -- "$result"' EXIT HUP INT TERM
python3 -IB review.py > "$result"
cmp REVIEW.json "$result"
printf '%s\n' 'All three scoped cut reviews reproduced.'
