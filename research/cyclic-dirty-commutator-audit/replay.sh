#!/bin/sh
# Reproduce this sprint contribution without fetching or modifying tracked files.
set -eu
if [ "$#" -ne 1 ]; then
    echo "usage: sh research/cyclic-dirty-commutator-audit/replay.sh NEW_OUTPUT_DIRECTORY" >&2
    exit 2
fi
root=$(CDPATH= cd -- "$(dirname -- "$0")/../.." && pwd)
if [ -e "$1" ]; then
    echo "Use a new output directory" >&2
    exit 2
fi
mkdir -p -- "$1"
out=$(CDPATH= cd -- "$1" && pwd)
python3 -I -B "$root/research/cyclic-dirty-commutator-audit/verify.py" --out "$out/ALIAS.json"
python3 -I -B "$root/research/cyclic-dirty-commutator-audit/verify_echo.py" --out "$out/ECHO.json"
python3 -I -B "$root/research/cyclic-dirty-commutator-audit/benchmark.py" --out "$out/BENCHMARK.json"
python3 -B "$root/research/gauge44-notri-fine-grid/verify.py" --out "$out/fine-grid"
sh "$root/research/dirty-echo-integration/replay.sh" "$out/integration"
sh "$root/research/bit-role-sharing-budget/replay.sh" "$out/bit-role-sharing"
sh "$root/research/bit-sharing-hosting-gate/replay.sh" "$out/bit-sharing-hosting-gate"
sh "$root/research/bit-paired-boundary-gate/replay.sh" "$out/bit-paired-boundary-gate"
echo PASS_DIRTY_ECHO_ALIAS_REPAIR_AND_FINE_GRID
