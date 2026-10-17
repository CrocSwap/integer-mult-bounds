#!/usr/bin/env bash
# steps.sh WK NAME -- one self-contained rerun in its own scratch dir under WK; last line printed: STEP-OK ... or STEP-FAIL ...
# k579a: K579T impl A (a3e.c + ext.py) with the harness fixes of #3154 (SIZEONLY=1 for the size-only run; rep ids/slice split of a3e depend on mask order, so
#        the two slices are compared as a multiset ignoring rep ids).  r579: R579b K5^-, K5^-2 (needs k579a).  k579b: K579T impl B (b5.c).  types: R579b types.c.
set -u; WK=$1; N=$2; shift 2; PY="${PYTHON:-python3}"
HERE=$(cd "$(dirname "$0")" && pwd)       # .../checks
case $N in
k579a) D="$WK/k579a"; rm -rf "$D"; mkdir -p "$D"; cp -R "$HERE/K579T" "$D/K579T"; cd "$D/K579T" || exit 2
  rm -f surv_28_*.txt masks.npy a3.txt
  "$PY" -B deficit.py > deficit.log 2>&1; "$PY" -B genA3.py > genA3.log 2>&1; cc -O2 -o a3e a3e.c -lm 2>/dev/null || cc -O2 -o a3e a3e.c
  ./a3e a3.txt 28 0 2 > run28_0.new; ./a3e a3.txt 28 1 2 > run28_1.new
  [ -f surv_28_0_2.txt ] && [ -f surv_28_1_2.txt ] || { echo "STEP-FAIL k579a (a3e produced no survivors; see $D/K579T)"; exit 1; }
  "$PY" -B ext.py 28 > ext28.new 2>&1
  SIZEONLY=1 "$PY" -B ext.py 28 28 > ext28_sizeonly.new 2>&1
  U() { cat "$@" | grep '^rep' | cut -d' ' -f4- | sort; }
  q=$(U run28_0.new run28_1.new | awk '{q+=$NF} END{print q}'); r=$(U run28_0.new run28_1.new | wc -l)
  ok=1; diff <(U run28_0.new run28_1.new) <(U "$HERE/K579T/run28_0.out" "$HERE/K579T/run28_1.out") >/dev/null || ok=0
  [ "$(tail -n 2 ext28.new | sed 's/ *$//')" = "$(tail -n 2 "$HERE/K579T/ext28.out" | sed 's/ *$//')" ] || ok=0
  [ "$(tail -n 2 ext28_sizeonly.new | sed 's/ *$//')" = "$(tail -n 2 "$HERE/K579T/ext28_sizeonly.out" | sed 's/ *$//')" ] || ok=0
  grep -q 'A3 coverable states 291' ext28.new || ok=0; grep -q 'A3 coverable states 958' ext28_sizeonly.new || ok=0
  [ $ok = 1 ] && echo "STEP-OK K579T implA (a3e+ext.py): $r reps, $q quads (958), 291 coverable, A4 states 0 (cover and size-only); union of slices equals shipped run28_*.out as a multiset" || echo "STEP-FAIL K579T implA";;
# ---- (4) R579b: needs the K579T regen (k579a) -- uses its surv_28_*_2.txt and masks.npy
r579) K="$WK/k579a"; D="$WK/r579b"; rm -rf "$D"; mkdir -p "$D"; cp -R "$HERE/R579b" "$D/R579b"; ln -sfn "$K/K579T" "$D/K579T"
  [ -f "$K/K579T/masks.npy" ] || { echo "STEP-FAIL R579b (run k579a first)"; exit 1; }
  cd "$D/R579b" || exit 2
  "$PY" -B km_a.py 28 > km_a28.new 2>&1
  "$PY" -B km_a2.py 28 2 > km2_n2.new 2>&1
  cc -O2 -o b5m b5m.c -lm 2>/dev/null || cc -O2 -o b5m b5m.c; cc -O2 -o b5m2 b5m2.c -lm 2>/dev/null || cc -O2 -o b5m2 b5m2.c
  ./b5m 28 nc > b5m_28_nc.new 2>&1
  NNR=2 ./b5m2 28 nc > b5m2_n2.new 2>&1
  ok=1
  [ "$(tail -n 1 km_a28.new)" = "$(tail -n 1 $HERE/R579b/km_a28.out)" ] || ok=0
  [ "$(tail -n 1 km2_n2.new)" = "$(tail -n 1 $HERE/R579b/km2_n2.out)" ] || ok=0
  [ "$(tail -n 1 b5m_28_nc.new)" = "$(tail -n 1 $HERE/R579b/b5m_28_nc.out)" ] || ok=0
  [ "$(tail -n 1 b5m2_n2.new)" = "$(tail -n 1 $HERE/R579b/b5m2_n2.out)" ] || ok=0
  [ $ok = 1 ] && echo "STEP-OK R579b: K5^- (km_a.py, b5m.c) and K5^-2 (km_a2.py 28 2, b5m2.c NNR=2): 0 solutions, min |U| 36, final lines equal shipped" || { echo "STEP-FAIL R579b"; tail -n 1 km_a28.new km2_n2.new b5m_28_nc.new b5m2_n2.new; };;
k579b) D="$WK/k579b"; rm -rf "$D"; mkdir -p "$D"; cp -R "$HERE/K579T" "$D/K579T"; cd "$D/K579T" || exit 2
  cc -O2 -o b5 b5.c -lm 2>/dev/null || cc -O2 -o b5 b5.c
  ./b5 28 > b5_28.new 2>&1; ./b5 28 nc > b5_28_nc.new 2>&1
  grep -q 'A3 quads 958, coverable 291, A4 solutions 0' b5_28.new && grep -q 'A3 quads 958, coverable 958, A4 solutions 0' b5_28_nc.new && echo "STEP-OK K579T implB (b5.c): A3 quads 958, coverable 291, A4 solutions 0 (cover and size-only)" || { echo "STEP-FAIL K579T implB"; tail -n 2 b5_28.new b5_28_nc.new; };;
types) D="$WK/types"; rm -rf "$D"; mkdir -p "$D"; cp "$HERE"/R579b/{types.c,e8.h,types.out} "$D/"; cd "$D" || exit 2
  cc -O2 -o types types.c -lm 2>/dev/null || cc -O2 -o types types.c; ./types > types.new 2>&1
  diff <(sed 's/ *$//' types.new) <(sed 's/ *$//' types.out) >/dev/null && echo "STEP-OK R579b types.c: minimum leftovers per support S regenerated identical to types.out (D7 14, E6A1 23, E6 24, A7 25, D6 26; all other S >= 31)" || { echo "STEP-FAIL R579b types"; diff types.new types.out | head -5; };;
deg2a) bash "$HERE/DEG2A/deg2a_check.sh" "$WK/deg2a" | tail -n 1 | sed 's/^PASS/STEP-OK/;s/^FAIL/STEP-FAIL/';;
esac
