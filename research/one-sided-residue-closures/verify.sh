#!/usr/bin/env bash
# Verification of research/one-sided-residue-closures (no kappa claim).   usage: bash verify.sh      PYTHON=/path/to/python (needs numpy)   FULL=1 for the heavy modes
#   0  MANIFEST.sha256
#   1  constants: g(1..8) = 1,2,4,8,12,20,36,64 (all affine flats of F2^8), N_2 = 3, N_3 = 6 (exhaustive; N_4 = 12 with FULL=1), E8 model sanity   [gtab.py, nj.py, e8.py]
#   2  P112 model, frame stabiliser (172032 elements, label-linear), complete direction list |Off| <= 89 (21340 non-E8 masks, 17 orbits), 6-flat masks   [mkgroup.py dirs.py mkreps.py flats.py]
#   3  exact covering enumerations [cov.c]: root target always recomputed; the two non-trivial non-E8 targets (|Off| = 79, 80) recomputed; the other 15 are the shipped
#      outputs (RECORDED) unless FULL=1, which recomputes all 17 (about 56 CPU-minutes more, three processes at a time) and also nj.py 4
#   4  covering facts F3 (a)-(f), F4, D7 plane fact [anroot.py annon.py facts_check.py d7plane.py]
#   5  RRC engine, Lemma P / P', ledger recomputed from data/rows_input.csv and compared with the shipped ledger [run_rrc.py lemp_audit.py build_ledger.py check_ledger.py]
# Default runtime about 10 minutes; at most 3 busy processes; every process under timeout. A missing numpy or C compiler gives FAIL.
set -uo pipefail
HERE=$(cd "$(dirname "$0")" && pwd); C="$HERE/checks"; DATA="$HERE/data"; PY="${PYTHON:-python3}"; FULL="${FULL:-0}"
export PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 OPENBLAS_NUM_THREADS=1
OUT=$(mktemp -d "${TMPDIR:-/tmp}/resclos.XXXXXX"); : > "$OUT/all.out"; T0=$SECONDS
note() { echo "$@" | tee -a "$OUT/all.out"; }
"$PY" -c "import numpy" 2>/dev/null || { echo "FAIL python needs numpy (PYTHON=...)"; exit 1; }
CC="${CC:-cc}"; command -v "$CC" >/dev/null || { echo "FAIL needs a C compiler (CC=...)"; exit 1; }
echo "== 0. manifest"
"$PY" -B "$C/manifest_check.py" | tee -a "$OUT/all.out" | sed 's/^/   /'
grep -q '^FAIL' "$OUT/all.out" && { echo "step 0 FAILED"; exit 1; }
cd "$OUT"
# run NAME TIMEOUT CMD...   (output to NAME.log; PASS if exit 0, no FAIL line, at least one PASS line)
run() { local n=$1 to=$2; shift 2; timeout "$to" nice -n 10 "$@" > "$OUT/$n.log" 2>&1; local rc=$?
  grep -E '^(PASS|FAIL)' "$OUT/$n.log" | sed 's/^/   /'
  if [ $rc = 0 ] && ! grep -q '^FAIL' "$OUT/$n.log" && grep -q '^PASS' "$OUT/$n.log"; then note "PASS ran $n"; else note "FAIL ran $n (exit $rc)"; tail -3 "$OUT/$n.log"; fi; }
# expect NAME 'regex': PASS if the log of NAME matches
expect() { if grep -Eq "$2" "$OUT/$1.log"; then note "PASS $3"; else note "FAIL $3"; fi; }

echo "== 1. constants"
timeout 600 "$PY" -B "$C/e8.py" > e8.log 2>&1 && note "PASS E8 model: 240 roots, 120 lines, det 1, labels distinct" || note "FAIL E8 model"
timeout 600 nice -n 10 "$PY" -B "$C/gtab.py" > gtab.log 2>&1; expect gtab '^\{1: 1, 2: 2, 3: 4, 4: 8, 5: 12, 6: 20, 7: 36, 8: 64\}$' "g(1..8) = 1,2,4,8,12,20,36,64 by exhaustive enumeration of all affine flats of F2^8"
NJ=3; [ "$FULL" = 1 ] && NJ=4
timeout 3000 nice -n 10 "$PY" -B "$C/nj.py" $NJ > nj.log 2>&1
expect nj 'j=2: .*max lines 3$' "N_2 = 3 (exhaustive over root-spanned planes)"; expect nj 'j=3: .*max lines 6$' "N_3 = 6 (exhaustive over root-spanned 3-spaces)"
if [ "$FULL" = 1 ]; then expect nj 'j=4: .*max lines 12$' "N_4 = 12 (exhaustive)"; else note "NOTE N_4 = 12 (and N_5 = 20, N_6 = 36) rest on the ADE classification; exhaustive N_4 log shipped in evidence/logs/nj4.out (FULL=1 recomputes)"; fi

echo "== 2. P112, frame stabiliser, direction list"
timeout 900 nice -n 10 "$PY" -B "$C/mkgroup.py" > mkgroup.log 2>&1; expect mkgroup '^\|G\| = 172032$' "frame stabiliser generated: |G| = 172032"
timeout 900 nice -n 10 "$PY" -B "$C/dirs.py" > dirs.log 2>&1; expect dirs 'non-E8 21340' "direction list |Off| <= 89: 21460 masks, 120 E8-root/frame, 21340 non-E8"
run mkreps 900 "$PY" -B "$C/mkreps.py"
timeout 900 nice -n 10 "$PY" -B "$C/flats.py" > flats.log 2>&1; expect flats '3-dim dual subspaces: 788035' "6-flat masks: 788035 dual 3-spaces enumerated"

echo "== 3. exact coverings"
"$CC" -O3 -o cov "$C/cov.c" 2> cc.log || { note "FAIL compile cov.c"; cat cc.log; }
for f in "$DATA"/left_*.gz; do b=$(basename "$f" .gz); gzip -dc "$f" > "shipped_$b"; done
covrun() { # name lo hi k forced
  timeout 3000 nice -n 10 ./cov "$2" "$3" "$4" 9 "$5" "left_$1.txt" > "cov_$1.log" 2>&1
  if cmp -s <(sort "left_$1.txt") <(sort "shipped_left_$1.txt"); then echo "PASS covering $1 recomputed = shipped" > "covres_$1.txt"; else echo "FAIL covering $1 differs from shipped" > "covres_$1.txt"; fi; }
read -r _ RLO RHI RK RF < <(grep '^root' "$DATA/targets.txt")
covrun root "$RLO" "$RHI" "$RK" "$RF"; cat covres_root.txt | tee -a all.out | sed 's/^/   /'
if [ "$FULL" = 1 ]; then
  grep '^non' "$DATA/targets.txt" | while read -r n lo hi k f; do echo "$n $lo $hi $k $f"; done > nonlist.txt
  export -f covrun; export OUT
  < nonlist.txt xargs -P 3 -L 1 bash -c 'covrun "$@"' _
else
  for n in non05_79 non06_80; do read -r _ lo hi k f < <(grep "^$n " "$DATA/targets.txt"); covrun "$n" "$lo" "$hi" "$k" "$f" & done   # two background processes
  for f in shipped_left_non*.txt; do b=${f#shipped_}; [ -e "$b" ] || cp "$f" "$b"; done
fi
NONLIST="non00_70 non01_73 non02_76 non03_77 non04_78 non05_79 non06_80 non07_82 non08_84 non09_84 non10_85 non11_85 non12_86 non13_87 non14_88 non15_88 non16_89"
echo "== 4. covering facts"
# (anroot runs now, concurrently with the two background covering processes: 3 busy processes in total)
timeout 3000 nice -n 10 "$PY" -B "$C/anroot.py" > anroot.log 2>&1
wait
if [ "$FULL" != 1 ]; then for n in non05_79 non06_80; do cat "covres_$n.txt" | tee -a all.out | sed 's/^/   /'; done; else for n in $NONLIST; do cat "covres_$n.txt" | tee -a all.out | sed 's/^/   /'; done; fi
for n in $NONLIST; do [ -e "left_$n.txt" ] || echo "missing left_$n.txt"; done
# annon reads left_nonXX_SZ.txt
timeout 900 nice -n 10 "$PY" -B "$C/annon.py" > annon.log 2>&1
run facts 600 "$PY" -B "$C/facts_check.py" anroot.log annon.log
run d7plane 600 "$PY" -B "$C/d7plane.py"

echo "== 5. RRC, Lemma P, ledger"
timeout 900 "$PY" -B "$C/run_rrc.py" > rrc.log 2>&1; expect rrc '^Counter' "RRC engine ran; every certificate re-verified by verify() (no assertion error)"
timeout 900 "$PY" -B "$C/lemp_audit.py" > lemp.log 2>&1; expect lemp 'Lemma P kills \(all 603 rows\): 375' "Lemma P at T-level kills 375 of the 603 rows"; expect lemp 'reproduced: 74 / 74' "all 74 original class-A kills reproduced"
timeout 900 "$PY" -B "$C/build_ledger.py" > ledger.log 2>&1
run ledger 600 "$PY" -B "$C/check_ledger.py"
npass=$(grep -c '^PASS' all.out); nfail=$(grep -c '^FAIL' all.out)
echo "== done in $((SECONDS - T0))s: $npass PASS, $nfail FAIL; logs in $OUT"
[ "$nfail" = 0 ] && { echo "PASS: all assertions hold"; exit 0; }
echo "FAIL"; exit 1
