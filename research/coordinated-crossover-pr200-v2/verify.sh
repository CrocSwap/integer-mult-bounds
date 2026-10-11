#!/usr/bin/env sh
set -eu
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
WORK=$(mktemp -d "/tmp/coordinated-crossover-v2.XXXXXX")
mkdir -p "$WORK/inputs" "$WORK/deps" "$WORK/results"
(cd "$ROOT" && sha256sum -c SHA256SUMS)
unzip -q "$ROOT/native-inputs.zip" -d "$WORK/inputs"
unzip -q "$ROOT/native/native-deps.zip" -d "$WORK/deps"
for name in frame-admission bit-columns native-pricing; do
  c++ -O3 -std=c++20 -I"$WORK/deps/include" "$ROOT/native/$name.cpp" -o "$WORK/$name"
done
"$WORK/frame-admission" "$WORK/inputs" "$WORK/results" "$ROOT/witnesses/additional-bases.json" "$WORK/inputs/packed-baseline.json"
"$WORK/bit-columns" "$WORK/inputs" "$WORK/results/ALL-COLUMNS.json"
"$WORK/native-pricing" price "$WORK/results/new-profile.json" "$ROOT/witnesses/complex-profile.json" "$WORK/results/ASSEMBLY.json" 4 "$WORK/inputs/public-complex-and-bridge.json"
grep -q '"kappa": "427415195711/625000000000000"' "$WORK/results/ASSEMBLY.json"
grep -q '"adjacent_kappa_rejected": true' "$WORK/results/ASSEMBLY.json"
(cd "$ROOT" && sha256sum -c SHA256SUMS)
printf '%s\n' "PASS: conditional kappa=0.000683864313137600; fresh receipts: $WORK/results"