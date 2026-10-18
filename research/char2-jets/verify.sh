#!/usr/bin/env bash
# One-command verification of research/char2-jets (no kappa claim).  Step 0 checks the package against MANIFEST.sha256 and stops hard on any mismatch.
# Then five check groups run one after the other in a single process chain (python3 with numpy and python-sat, and a C compiler for one small enumerator):
#   a  Theorem T': the first-order jet for tied_min (exact over F2) and the 518 stored matrices B            b  Lemma CR2: stored realisations of 21 configurations; tied_min and the 44 atoms
#   c  Corollary J on all 4095 sub-configurations of tied_min and 1500 all-harmonic configurations              d  Lemma A (T = 2) and spot checks of Theorem B2
#   e  jetfail jf0/jf1/jf2: first-order and order-2 failure, exact costs
# One PASS/FAIL line per assertion; exit status 0 only if every assertion passes.  The Lean project (lean/) is NOT needed; with LEAN=1 and `lake` on PATH the Lean build is run as an extra last step.
#   usage: bash verify.sh [/fresh/output/dir]     (inside a checkout or `git archive` of the repository; nothing outside the package is read)
#   env:   PYTHON (default python3), CC (default cc), LEAN=1 (optional Lean build; needs Mathlib at the revision pinned in lean/lake-manifest.json)
# Not re-run here (RECORDED in the README, scripts included): the 217 SAT-enumerated optima of tied_min, the 1889/1892 random run, the min-max of the split bound, the 300 wild-cycle
# configurations, the CR2 status of the 192 jf1 minimisers, the minimum cost 8 of the seven-line atoms.
set -uo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
OUT=${1:-$(mktemp -d "${TMPDIR:-/tmp}/char2-jets.XXXXXX")}
mkdir -p "$OUT"; OUT=$(cd "$OUT" && pwd)
case "$OUT/" in "$HERE"/*) echo "output dir must be outside the package"; exit 2;; esac
PY="${PYTHON:-python3}"; CC="${CC:-cc}"; export PYTHONDONTWRITEBYTECODE=1
T0=$SECONDS; FAILED=0
echo "== 0. manifest"
if ! "$PY" -B "$HERE/checks/provenance.py" | tee "$OUT/provenance.log" | sed 's/^/   /' || grep -q '^FAIL' "$OUT/provenance.log" \
   || [ "$(grep -c '^PASS' "$OUT/provenance.log")" != 1 ]; then
  echo "step 0 FAILED"; exit 1
fi
R="$OUT/tree"; mkdir -p "$R/bin" "$OUT/logs"
cp -R "$HERE/checks" "$HERE/lib" "$HERE/data" "$HERE/c" "$R/"
export TTD_BIN="$R/bin"
echo "== compile c/enumall.c"
if ! $CC -O2 -o "$R/bin/enumall" "$R/c/enumall.c" 2> "$OUT/logs/cc.log"; then echo "FAIL compile enumall"; cat "$OUT/logs/cc.log"; exit 1; fi
run() {  # name, script
  echo "== $1"
  ( cd "$OUT" && "$PY" -B "$R/checks/$2" ) 2>&1 | tee "$OUT/logs/$2.log" | sed 's/^/   /'
  rc=${PIPESTATUS[0]}
  if [ "$rc" != 0 ] || grep -q '^FAIL' "$OUT/logs/$2.log"; then FAILED=$((FAILED+1)); fi
}
run "a. Theorem T' (cost(tied_min) >= 12 by a first-order jet)" a_tprime.py
run "b. Lemma CR2: stored realisations, tied_min, atoms" b_cr2.py
run "c. Corollary J (first-order jet test)" c_jets.py
run "d. Lemma A (T = 2) and Theorem B2 spot checks" d_lemmaA_B2.py
run "e. jetfail jf0..2" e_jetfail.py
if [ "${LEAN:-0}" = 1 ]; then
  echo "== f. Lean build (optional)"
  if command -v lake >/dev/null 2>&1; then
    L="$OUT/lean"; rm -rf "$L"; cp -R "$HERE/lean" "$L"
    if ( cd "$L" && LEAN_NUM_THREADS=4 lake build ) > "$OUT/logs/lean.log" 2>&1; then echo "   PASS lake build (DecoderDuality)"; else echo "   FAIL lake build, see $OUT/logs/lean.log"; FAILED=$((FAILED+1)); fi
  else echo "   SKIP: LEAN=1 but lake not found"; fi
fi
PASSN=$(cat "$OUT"/logs/*.py.log | grep -c '^PASS'); FAILN=$(cat "$OUT"/logs/*.py.log | grep -c '^FAIL')
echo "== summary: $PASSN PASS, $FAILN FAIL line(s), $((SECONDS-T0))s"
if [ "$FAILED" = 0 ]; then echo "ALL CHECKS PASSED"; exit 0; else echo "SOME CHECKS FAILED"; exit 1; fi
