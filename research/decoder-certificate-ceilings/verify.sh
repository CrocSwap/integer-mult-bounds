#!/usr/bin/env bash
# Verification of research/decoder-certificate-ceilings (no kappa claim).   usage: bash verify.sh      PYTHON=/path/to/python (needs numpy, scipy)
#   0  MANIFEST.sha256
#   1  Theorem C: exact Fraction ceilings 360/17 (P120), 15968/757 (P112), 945/71 (E7), 12 (E6)  [thmC.py; enumerates all orthogonal sets]
#   2  F' (zero-cost terms dropped): proven Bonferroni ceilings P120 <= 24, P112 <= 15968/667 = 23.94  [fprime_bonferroni.py];
#      MILP-computed (HiGHS) E7 <= 13.90, E6 <= 13.06  [fprime_milp.py + fprime_wrap.py]
#   3  Lemma S: flat sizes over all 417,199 subspaces of F2^8 [lemmaS_flats.py], size-relaxation DP for e in [15,112] [lemmaS_dp.py]
# Runtime about 10 minutes, one process at a time.  A missing numpy/scipy gives FAIL (exit 1).
set -uo pipefail
HERE=$(cd "$(dirname "$0")" && pwd); C="$HERE/checks"; PY="${PYTHON:-python3}"
export PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 OPENBLAS_NUM_THREADS=1
OUT=$(mktemp -d "${TMPDIR:-/tmp}/certceil.XXXXXX"); : > "$OUT/all.out"; T0=$SECONDS
note() { echo "$@" | tee -a "$OUT/all.out"; }
"$PY" -c "import numpy, scipy" 2>/dev/null || { echo "FAIL python needs numpy and scipy (PYTHON=...)"; exit 1; }
echo "== 0. manifest"
"$PY" -B "$C/manifest_check.py" | tee -a "$OUT/all.out" | sed 's/^/   /'
grep -q '^FAIL' "$OUT/all.out" && { echo "step 0 FAILED"; exit 1; }

run() { local n=$1 to=$2; shift 2; ( cd "$C" && timeout "$to" nice -n 10 "$@" > "$OUT/$n.log" 2>&1 ); local rc=$?
  grep -E '^(PASS|FAIL)' "$OUT/$n.log" | sed 's/^/   /'
  if [ $rc = 0 ] && ! grep -q '^FAIL' "$OUT/$n.log" && grep -q '^PASS' "$OUT/$n.log"; then note "PASS ran $n"; else note "FAIL ran $n (exit $rc)"; tail -3 "$OUT/$n.log"; fi; }
echo "== 1. Theorem C (fake decoder witness, exact)"
run thmC 1200 "$PY" -B thmC.py
echo "== 2. F' ceilings"
run bonf 1200 "$PY" -B fprime_bonferroni.py
for u in "E6 135 6 13.0 13.1" "E7 135 7 13.8 13.95"; do set -- $u
  ( cd "$C" && timeout 1500 nice -n 10 "$PY" -B fprime_milp.py $1 > "$OUT/milp_$1.log" 2>&1 )
  ( cd "$C" && "$PY" -B fprime_wrap.py $1 $2 $3 $4 $5 < "$OUT/milp_$1.log" > "$OUT/wrap_$1.log" 2>&1 ); cat "$OUT/wrap_$1.log" | sed 's/^/   /'
  grep -q "^PASS F' ceiling $1" "$OUT/wrap_$1.log" && note "PASS F' MILP $1" || note "FAIL F' MILP $1"; done
echo "== 3. Lemma S"
run flats 1200 "$PY" -B lemmaS_flats.py
run dp 1200 "$PY" -B lemmaS_dp.py
npass=$(grep -c '^PASS' "$OUT/all.out"); nfail=$(grep -c '^FAIL' "$OUT/all.out")
echo "== done in $((SECONDS - T0))s: $npass PASS, $nfail FAIL; logs in $OUT"
[ "$nfail" = 0 ] && { echo "PASS: all assertions hold"; exit 0; }
echo "FAIL"; exit 1
