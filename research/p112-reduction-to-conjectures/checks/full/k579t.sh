#!/usr/bin/env bash
# K579T rerun in a scratch copy: k579t.sh WORKDIR PART   PART: A (impl A: a3e + ext.py, ~5 min) | B (impl B: b5.c cover + size-only) | T (root-premise types, typA.py + typB.c)
set -u; PY="${PYTHON:-python3}"
HERE=$(cd "$(dirname "$0")/.." && pwd); W=$1; P=$2; D="$W/K579T"; mkdir -p "$W"
[ -d "$D" ] || { cp -R "$HERE/K579T" "$D"; }
cd "$D" || exit 2
last() { tail -n "${2:-1}" "$1" | sed 's/ *$//'; }
case $P in
 A) [ -f masks.npy ] || "$PY" -B deficit.py > deficit.log 2>&1
    "$PY" -B genA3.py > genA3.log 2>&1; cc -O2 -o a3e a3e.c -lm 2>/dev/null || cc -O2 -o a3e a3e.c
    ./a3e a3.txt 28 0 2 > run28_0.new; ./a3e a3.txt 28 1 2 > run28_1.new
    "$PY" -B ext.py 28 > ext28.new 2>&1; "$PY" -B ext.py 28 28 > ext28_sizeonly.new 2>&1
    if [ "$(last ext28.new 2)" = "$(last "$HERE/K579T/ext28.out" 2)" ] && [ "$(last ext28_sizeonly.new 2)" = "$(last "$HERE/K579T/ext28_sizeonly.out" 2)" ] && cmp -s run28_0.new "$HERE/K579T/run28_0.out"; then echo "STEP-OK K579T implA (A3 coverable 291, A4 states 0, matches shipped outputs)"; else echo "STEP-FAIL K579T implA"; fi;;
 B) cc -O2 -o b5 b5.c 2>/dev/null; ./b5 28 > b5_28.new 2>&1; ./b5 28 nc > b5_28_nc.new 2>&1
    if [ "$(last b5_28.new 1)" = "$(last "$HERE/K579T/b5_28.out" 1)" ] && grep -q "A4 solutions 0" b5_28.new && grep -q "A3 quads 958, coverable 291" b5_28.new; then echo "STEP-OK K579T implB (958 quads, 291 coverable, A4 0)"; else echo "STEP-FAIL K579T implB"; fi;;
 T) "$PY" -B typA.py > typA.new 2>&1; cc -O2 -o typB typB.c 2>/dev/null; ./typB > typB.new 2>&1
    if diff <(sed 's/ *$//' typA.new) <(sed 's/ *$//' "$HERE/K579T/typA.out") >/dev/null && diff <(sed 's/ *$//' typB.new) <(sed 's/ *$//' "$HERE/K579T/typB.out") >/dev/null; then echo "STEP-OK K579T types (matches shipped typA.out/typB.out)"; else echo "STEP-FAIL K579T types"; fi;;
esac
