#!/bin/sh
set -eu
cd -- "$(dirname -- "$0")"
actual=$(mktemp)
trap 'rm -f -- "$actual"' EXIT HUP INT TERM
python3 -IB review.py > "$actual"
cmp REVIEW.json "$actual"
printf '%s\n' 'Public-only chart-282 cut, fifth-arrival control, and signed price reproduced.'
