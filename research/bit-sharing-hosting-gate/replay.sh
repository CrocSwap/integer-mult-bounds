#!/bin/sh
set -eu
if [ "$#" -ne 1 ] || [ -e "$1" ]; then
    echo "usage: sh research/bit-sharing-hosting-gate/replay.sh NEW_OUTPUT_DIRECTORY" >&2
    exit 2
fi
here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
mkdir -p -- "$1"
out=$(CDPATH= cd -- "$1" && pwd)
python3 -I -B "$here/verify.py" --out "$out/PRICE.json"
cmp "$out/PRICE.json" "$here/evidence/PRICE.json"
echo PASS_BIT_SHARING_HOSTING_GATE_REPLAY
