#!/usr/bin/env bash
# Verification of research/one-sided-six-multisets (no kappa claim).   usage: bash verify.sh [/fresh/output/dir]
# Needs: Python >= 3.11 with numpy >= 2.0 (np.bitwise_count; PYTHON=/path/to/python to choose) and a C compiler `cc` (128-bit integers: gcc/clang). No SAT solver.
# Everything runs under `nice -n 10`, at most 6 processes at a time, each under `timeout 1200`; there are no wait loops.  Expected: about 30-40 minutes.
#   0  MANIFEST.sha256
#   1  data regeneration (gen.py, ~15 s) + Parity Lemma (ii) search (quad.py)
#   2  Lemma S66 and S66+t, C implementation s66.c, plus the 7+7 control (3 processes)
#   3  Lemma S66, independent implementation indep.py mode 0, 6 chunks (reps i::6)
#   4  Lemma S66+t, independent implementation indep.py mode 1, 6 chunks
#   5  check_logs.py: every assertion of the README as a PASS/FAIL line
# Inherited inputs of #2816 are NOT recomputed here (see README section 2); this package re-runs everything that is new.
set -uo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
OUT=${1:-$(mktemp -d "${TMPDIR:-/tmp}/six-multisets.XXXXXX")}
mkdir -p "$OUT"; OUT=$(cd "$OUT" && pwd)
case "$OUT/" in "$HERE"/*) echo "output dir must be outside the package"; exit 2;; esac
PY="${PYTHON:-python3}"; export PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 OPENBLAS_NUM_THREADS=1
TMO=""; command -v timeout >/dev/null 2>&1 && TMO="timeout 1200"; command -v gtimeout >/dev/null 2>&1 && TMO="gtimeout 1200"
[ -n "$TMO" ] || { echo "need timeout or gtimeout"; exit 2; }
WK="$OUT/work"; LOG="$OUT/logs"; mkdir -p "$WK" "$LOG"; : > "$OUT/all.out"; T0=$SECONDS
echo "== 0. manifest"
"$PY" -B "$HERE/checks/manifest_check.py" | tee -a "$OUT/all.out" | sed 's/^/   /'; grep -q '^FAIL' "$OUT/all.out" && { echo "step 0 FAILED"; exit 1; }
cp "$HERE"/checks/*.py "$HERE"/checks/*.c "$HERE"/data/* "$WK"/
cd "$WK"
echo "== 1. data regeneration and Parity Lemma search"
mkdir -p gen && ( cd gen && cp ../gen.py . && $TMO nice -n 10 "$PY" -B gen.py 77 > "$LOG/gen.log" 2>&1 )
if cmp -s gen/data.txt data.txt && cmp -s gen/gens.txt gens.txt; then echo IDENTICAL > "$LOG/gen_cmp.log"; else echo DIFFERENT > "$LOG/gen_cmp.log"; fi
$TMO nice -n 10 "$PY" -B quad.py > "$LOG/quad.log" 2>&1
echo "== 2. s66.c (3 processes)"
cc -O2 -o s66 s66.c 2> "$LOG/cc_s66.log" || { echo "cc failed"; exit 1; }
for d in m0 m1 ctl; do mkdir -p "r_$d"; cp data.txt gens.txt "r_$d"/; done
( cd r_m0  && $TMO nice -n 10 ../s66 0 6 > "$LOG/s66_m0.out"  2> "$LOG/s66_m0.err" ) &
( cd r_m1  && $TMO nice -n 10 ../s66 1 6 > "$LOG/s66_m1.out"  2> "$LOG/s66_m1.err" ) &
( cd r_ctl && $TMO nice -n 10 ../s66 0 7 > "$LOG/s66_ctl.out" 2> "$LOG/s66_ctl.err" ) &
wait
for mode in 0 1; do
  echo "== $((3 + mode)). indep.py mode $mode, 6 chunks"
  for c in 0 1 2 3 4 5; do
    $TMO nice -n 10 "$PY" -B indep.py $mode $c 6 > "$LOG/indep_m${mode}_c$c.out" 2>&1 &
  done
  wait
done
echo "== 5. assertions (check_logs.py)"
"$PY" -B "$HERE/checks/check_logs.py" "$LOG" | tee -a "$OUT/all.out" | sed 's/^/   /'
npass=$(grep -c '^PASS' "$OUT/all.out"); nfail=$(grep -c '^FAIL' "$OUT/all.out")
echo "== done in $((SECONDS - T0))s: $npass PASS, $nfail FAIL; logs in $OUT"
[ "$nfail" = 0 ] && { echo "PASS: all assertions hold"; exit 0; }
echo "FAIL"; exit 1
