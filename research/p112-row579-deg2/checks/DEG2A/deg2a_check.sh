#!/usr/bin/env bash
# DEG2 impl A, 4th -> 5th -> 6th seven stage on the recorded 4-seven survivors (reps 1 and 8), plus one quad-stage chunk per rep as a regression.
# usage: deg2a_check.sh [workdir]. Needs cc, python3 (fractions only, no numpy).  Prints PASS/FAIL lines.  Default cost: a few minutes, 1 process.
set -u; H=$(cd "$(dirname "$0")" && pwd); W=${1:-$(mktemp -d "${TMPDIR:-/tmp}/deg2a.XXXXXX")}; mkdir -p "$W"; cd "$W" || exit 2
cp "$H"/{quad.c,ext.c,e8.h,geom.py,geomN.py} .; PY=${PYTHON:-python3}
cc -O2 -o quad quad.c -lm 2>/dev/null || cc -O2 -o quad quad.c; cc -O2 -o ext ext.c -lm 2>/dev/null || cc -O2 -o ext ext.c
bad=0
for r in 1 8; do
  timeout 1100 ./ext < "$H/q4_rep$r.txt" > e5_$r.txt 2> /dev/null
  [ "$(wc -l < e5_$r.txt)" = "$(wc -l < "$H/e5_raw_$r.txt")" ] && sort e5_$r.txt | cmp -s - <(sort "$H/e5_raw_$r.txt") && echo "PASS DEG2A rep $r: 4-seven survivors $(wc -l < "$H/q4_rep$r.txt") -> 5-seven $(wc -l < e5_$r.txt) (equals shipped e5_raw_$r.txt)" || { echo "FAIL DEG2A rep $r five-set stage"; bad=1; }
  # six-sets from the UNFILTERED five-sets (the geometry filter geomN.py is then not needed for the conclusion)
  timeout 1100 ./ext < e5_$r.txt > e6_$r.txt 2> /dev/null
  [ -s e6_$r.txt ] && { echo "FAIL DEG2A rep $r: six-sets exist"; bad=1; } || echo "PASS DEG2A rep $r: six-sets from unfiltered five-sets = 0"
  "$PY" -B geomN.py x < e5_$r.txt 2> geom_$r.err > ok_$r.txt; echo "     (geomN.py realisability: $(wc -l < ok_$r.txt) of $(wc -l < e5_$r.txt) five-sets kept; informational)"
done
# quad-stage regression: one chunk per rep, same final DONE line as shipped (survivor counts)
for spec in "8 11 12 T8" "1 39 40 S1"; do set -- $spec
  timeout 1100 ./quad 28 $1 $2 $3 2> /dev/null | grep -o 'DONE rep.*' > chunk.out
  a=$(sed 's/ tri.*surv/ surv/' chunk.out); b=$(grep -o 'DONE rep.*' "$H/rec/$4_$2.out" | sed 's/ tri.*surv/ surv/')
  [ -n "$a" ] && [ "$a" = "$b" ] && echo "PASS DEG2A quad chunk rep $1 $2/$3: $a" || { echo "FAIL DEG2A quad chunk rep $1 $2/$3 (got '$a' want '$b')"; bad=1; }
done
[ $bad = 0 ] && echo "PASS DEG2A_implA stages 5,6 and chunk regressions" || echo "FAIL DEG2A_implA"
