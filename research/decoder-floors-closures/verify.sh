#!/usr/bin/env bash
# Verification of research/decoder-floors-closures (no kappa claim).  Step 0: MANIFEST.sha256 and SOURCES.json pins (hard stop).  Then three check scripts:
#   c1 exact (Fraction) arithmetic of the closure statements;  c2 E7 / punctured-unit clique facts + the E7 frame hitting number 10 (kissat, drat-trim optional);
#   c4 counts of the shipped working-card logs / state files (RE-RUNS NOTHING).
# Single process at a time; standard-library Python only (>= 3.11).  kissat 4.0.4 (KISSAT=/path or on PATH) and drat-trim (DRAT_TRIM=/path or on PATH) are
# OPTIONAL: lines needing them are SKIP lines, never PASS.  The big SAT / DRAT runs of the cards (571 puncture cubes, h = 10 / 11 queries, Case-B census)
# are NOT re-run here; see README section 6.   usage: bash verify.sh [/fresh/output/dir]
set -uo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
OUT=${1:-$(mktemp -d "${TMPDIR:-/tmp}/decoder-floors-closures.XXXXXX")}
mkdir -p "$OUT"; OUT=$(cd "$OUT" && pwd)
case "$OUT/" in "$HERE"/*) echo "output dir must be outside the package"; exit 2;; esac
PY="${PYTHON:-python3}"; export PYTHONDONTWRITEBYTECODE=1
T0=$SECONDS
echo "== 0. manifest and provenance"
if ! "$PY" -B "$HERE/scripts/provenance.py" | tee "$OUT/provenance.log" | sed 's/^/   /' || grep -q '^FAIL' "$OUT/provenance.log" \
   || [ "$(grep -c '^PASS' "$OUT/provenance.log")" != 2 ]; then echo "step 0 FAILED"; exit 1; fi
echo "   tools: kissat=$(command -v "${KISSAT:-kissat}" 2>/dev/null || echo none)  drat-trim=$(command -v "${DRAT_TRIM:-drat-trim}" 2>/dev/null || echo none)"
mkdir -p "$OUT/logs"; : > "$OUT/all.out"
run() { echo "== $1"; ( cd "$HERE/checks" && "$PY" -B "$2" > "$OUT/logs/$2.log" 2>&1; echo $? > "$OUT/logs/$2.rc" )
  tee -a "$OUT/all.out" < "$OUT/logs/$2.log" | sed 's/^/   /'
  [ "$(cat "$OUT/logs/$2.rc")" = 0 ] || echo "FAIL $2 exit status $(cat "$OUT/logs/$2.rc")" | tee -a "$OUT/all.out"; }
run "c1 closure arithmetic (bars, E7q table, M8 cases, template, f(s) >= 7s)" c1_closure_arith.py
run "c2 E7 facts, Lemma CA inputs, E7 frame hitting number" c2_e7_cliques.py
run "c4 counts of the shipped logs and state files (re-runs nothing)" c4_log_counts.py
npass=$(grep -c '^PASS' "$OUT/all.out"); nfail=$(grep -c '^FAIL' "$OUT/all.out"); nskip=$(grep -c '^SKIP' "$OUT/all.out")
EXPECT=$((35 - nskip))
echo "== done in $((SECONDS - T0))s: $((npass + 2)) PASS (2 in step 0), $nskip SKIP, $nfail FAIL; logs in $OUT"
if [ "$nfail" = 0 ] && [ "$npass" = "$EXPECT" ]; then echo "PASS: all expected assertions hold"; exit 0; fi
echo "FAIL: expected $EXPECT assertion PASS lines after step 0, got $npass PASS / $nfail FAIL / $nskip SKIP"; exit 1
