#!/usr/bin/env bash
# Verification of research/nine-term-outside-colspace (no kappa claim).  usage: bash verify.sh [/fresh/output/dir]     FULL=1 bash verify.sh ...  (hours)
# Default mode (single process at a time, Python >= 3.11 with numpy + networkx; PYTHON=/path/to/python to choose):
#   0  MANIFEST.sha256
#   1  rank_formula_check.py (exact-rank formula spot check) and inputs_check.py: the finite geometric inputs (frames, label table, survivors, survivor-pair ranks, 7-cliques) on P112 and P104
#   2  regeneration of the geometric data (orbits, cliques, pair census) and exact replay of the counting scripts for d0 = 2, 3, 7, 8 (+ cnt4),
#      each log compared line-for-line (elapsed seconds dropped) with the recorded working-card log
#   3  SUBSET replays of the census (cnt.py orbits 8, 13; cnt104b.py orbits 9, 30, 56), compared with the recorded logs
#   4  cnt9 / cnt9b replayed from the RECORDED compact census output (data/lb22_le7_*.json), compared with the recorded logs
#   5  controls ctl8.py, ctlb.py
#   6  log_counts.py: headline counts in the shipped long-run logs (RECORDED, not re-run)
# NOT re-run in default mode: full census (cnt.py / cnt104b.py), d0 = 4, 5, 6 (cnt6 / cnt7 / cnt8).  FULL=1 runs them too.
set -uo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
OUT=${1:-$(mktemp -d "${TMPDIR:-/tmp}/nine-term.XXXXXX")}
mkdir -p "$OUT"; OUT=$(cd "$OUT" && pwd)
case "$OUT/" in "$HERE"/*) echo "output dir must be outside the package"; exit 2;; esac
PY="${PYTHON:-python3}"; export PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 OPENBLAS_NUM_THREADS=1
C="$HERE/checks"; REC="$HERE/evidence/logs"; W="$OUT/work"; mkdir -p "$W" "$OUT/logs"; : > "$OUT/all.out"
T0=$SECONDS
note() { echo "$@" | tee -a "$OUT/all.out"; }
echo "== 0. manifest"
if ! "$PY" -B "$C/manifest_check.py" | tee -a "$OUT/all.out" | sed 's/^/   /' || grep -q '^FAIL' "$OUT/all.out"; then echo "step 0 FAILED"; exit 1; fi
# run NAME SCRIPT ARGS...   (cwd = work dir; log -> logs/NAME.log)
run() { local n=$1; shift; local s=$SECONDS
  ( cd "$W" && "$PY" -B "$C/$1" "${@:2}" > "$OUT/logs/$n.log" 2>&1 ); local rc=$?
  if [ $rc = 0 ]; then note "PASS ran $n ($1 ${*:2}) in $((SECONDS - s))s"; else note "FAIL ran $n exit $rc"; tail -3 "$OUT/logs/$n.log" | sed 's/^/      /'; fi; }
# cmp NAME RECORDED [--subset]
cmpl() { local o; o=$("$PY" -B "$C/cmp_logs.py" "$OUT/logs/$1.log" "$REC/$2.txt" ${3:-}); echo "$o" >> "$OUT/all.out"; echo "$o" | sed 's/^/   /'; }
echo "== 1. geometric inputs (inputs_check.py)"
"$PY" -B "$C/inputs_check.py" 2>&1 | tee "$OUT/logs/inputs_check.log" | sed 's/^/   /'; grep '^PASS\|^FAIL' "$OUT/logs/inputs_check.log" >> "$OUT/all.out"
run rank_formula rank_formula_check.py; grep -q "tests 2974 bad 0" "$OUT/logs/rank_formula.log" && grep -q "tests 2973 bad 0" "$OUT/logs/rank_formula.log" && note "PASS rank formula spot check: 2974 + 2973 random blocks, 0 mismatches" || { note "FAIL rank formula check"; tail -3 "$OUT/logs/rank_formula.log"; }
echo "== 2. geometry regeneration and exact replays (P112)"
run orbits_P112 orbits.py P112; run cliques_P112 cliques.py P112; run pairs_P112 pairs_fast.py P112
cmpl orbits_P112 orbits_P112.log; cmpl cliques_P112 cliques_P112.log
run cnt4_P112_2 cnt4.py P112 2; cmpl cnt4_P112_2 cnt4_P112_2.log
run cnt4_P112_3 cnt4.py P112 3; cmpl cnt4_P112_3 cnt4_P112_3.log
for D in 2 3; do
  run cnt7_P112_$D cnt7.py P112 $D cnt4; cmpl cnt7_P112_$D cnt7_P112_$D.log
  run cnt8_P112_$D cnt8.py P112 $D; cmpl cnt8_P112_$D cnt8_P112_$D.log
done
for D in 8 7; do
  run cnt10_P112_$D cnt10.py P112 $D
  run cnt7_P112_$D cnt7.py P112 $D cnt6; cmpl cnt7_P112_$D cnt7_P112_$D.log
  run cnt8_P112_$D cnt8.py P112 $D; cmpl cnt8_P112_$D cnt8_P112_$D.log
done
if [ "${FULL:-0}" = 1 ]; then
  echo "== 2f. FULL: d0 = 4, 5, 6 from scratch (hours)"
  for D in 4 5 6; do
    run cnt6_P112_$D cnt6.py P112 $D; cmpl cnt6_P112_$D cnt6_P112_$D.log
    run cnt7_P112_$D cnt7.py P112 $D cnt6; cmpl cnt7_P112_$D cnt7_P112_$D.log
    run cnt8_P112_$D cnt8.py P112 $D; cmpl cnt8_P112_$D cnt8_P112_$D.log
  done
fi
echo "== 3. census: subset replays (P112 orbits 8, 13; P104 orbits 9, 30, 56)"
ONLY_ORBITS=8,13 run census_P112_subset cnt.py P112; cmpl census_P112_subset cnt_P112.log --subset
run orbits_P104 aut104.py; run cliques_P104 cliques.py P104; run pairs_P104 pairs_fast.py P104
cmpl orbits_P104 aut104_P104.log; cmpl cliques_P104 cliques_P104.log
ONLY_ORBITS=9,30,56 run census_P104_subset cnt104b.py P104; cmpl census_P104_subset cnt_P104.log --subset
if [ "${FULL:-0}" = 1 ]; then
  echo "== 3f. FULL census (P112 ~45 min, P104 ~30 min)"
  run census_P112 cnt.py P112; cmpl census_P112 cnt_P112.log; run census_P104 cnt104b.py P104; cmpl census_P104 cnt_P104.log
else
  echo "== 4. cnt9 / cnt9b from the recorded compact census output"
  run mkcnt_P112 mk_cnt_pkl.py P112; run mkcnt_P104 mk_cnt_pkl.py P104
fi
run cnt9_P112 cnt9.py P112; cmpl cnt9_P112 cnt9_P112.log
run cnt9b_P104 cnt9b.py P104; cmpl cnt9b_P104 cnt9b_P104.log
echo "== 5. controls"
run ctl8 ctl8.py P112; run ctlb ctlb.py P112
grep -q "coordinate decoder + empty term: (True, True) | drop one term: (True, False)" "$OUT/logs/ctl8.log" && note "PASS ctl8: coordinate decoder passes (D) and (C); dropping a term fails (C)" || { note "FAIL ctl8 output"; cat "$OUT/logs/ctl8.log"; }
grep -q "ctlb checks 294 violations 0" "$OUT/logs/ctlb.log" && note "PASS ctlb: 294 checks, 0 violations" || { note "FAIL ctlb output"; tail -3 "$OUT/logs/ctlb.log"; }
echo "== 6. recorded long-run logs (not re-run)"
"$PY" -B "$C/log_counts.py" 2>&1 | tee "$OUT/logs/log_counts.log" | sed 's/^/   /'; grep '^PASS\|^FAIL' "$OUT/logs/log_counts.log" >> "$OUT/all.out"
npass=$(grep -c '^PASS' "$OUT/all.out"); nfail=$(grep -c '^FAIL' "$OUT/all.out")
echo "== done in $((SECONDS - T0))s: $npass PASS, $nfail FAIL; logs in $OUT"
[ "$nfail" = 0 ] && { echo "PASS: all assertions hold (mode: $([ "${FULL:-0}" = 1 ] && echo FULL || echo default))"; exit 0; }
echo "FAIL"; exit 1
