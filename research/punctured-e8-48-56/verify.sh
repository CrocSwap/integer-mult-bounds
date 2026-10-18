#!/usr/bin/env bash
# Verification of research/punctured-e8-48-56 (no kappa claim).
#   0  MANIFEST.sha256 and SOURCES.json pins (hard stop)
#   1  c1: tallies of the shipped state files / lane summaries (all 8 flat types UNSAT-VERIFIED for P = 53, k = 6 and P = 56, k = 17), leaf-table row counts, exact arithmetic
#   2  rebuild of the option sets (sat/opts.py) for flat types 7, 0, 6, 1 (all 8 types with FULL=1)
#   3  c2: encoding checks (counter, leaf CNF vs. direct numpy test; kissat);  3b c3: tree coverage (the orbit trees re-walked with an oracle leaf)
#   4  replay (scripts/replay.py) per (type, P): ALL counting leaves; a spread sample of leaves has its CNF regenerated and compared with the recorded md5 / pinned sha256,
#      and a smaller sample re-solved (kissat 4.0.4 UNSAT + drat-trim VERIFIED).  FULL=1: every leaf of all 8 types (hours; every kissat run is capped at 20 min).
# Sequential, one heavy process at a time, run under nice 10.  Needs numpy, sympy, python-sat, networkx (requirements.txt), kissat and drat-trim; without them the steps
# 2-4 print SKIP lines (never PASS).   PYTHON=/path/to/python3  KISSAT=  DRAT_TRIM=   usage: bash verify.sh [/fresh/output/dir]
set -uo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
OUT=${1:-$(mktemp -d "${TMPDIR:-/tmp}/punctured-e8-48-56.XXXXXX")}
mkdir -p "$OUT"; OUT=$(cd "$OUT" && pwd)
case "$OUT/" in "$HERE"/*) echo "output dir must be outside the package"; exit 2;; esac
PY="${PYTHON:-python3}"; export PYTHONDONTWRITEBYTECODE=1 KISSAT="${KISSAT:-kissat}" DRAT_TRIM="${DRAT_TRIM:-drat-trim}"
NICE="nice -n 10"; T0=$SECONDS; : > "$OUT/all.out"
echo "== 0. manifest and provenance"
if ! "$PY" -B "$HERE/scripts/provenance.py" | tee "$OUT/provenance.log" | sed 's/^/   /' || grep -q '^FAIL' "$OUT/provenance.log" \
   || [ "$(grep -c '^PASS' "$OUT/provenance.log")" != 2 ]; then echo "step 0 FAILED"; exit 1; fi
emit() { tee -a "$OUT/all.out" | sed 's/^/   /'; }
echo "== 1. c1 tallies of the shipped states and summaries, arithmetic"
( cd "$HERE/checks" && "$PY" -B c1_tallies.py ) 2>&1 | emit
HAVE=1
"$PY" -c "import numpy, sympy, networkx, pysat" 2>/dev/null || HAVE=0
command -v "$KISSAT" >/dev/null 2>&1 || HAVE=0
command -v "$DRAT_TRIM" >/dev/null 2>&1 || HAVE=0
if [ "$HAVE" = 0 ]; then
  echo "SKIP steps 2-4: need numpy, sympy, networkx, python-sat, kissat, drat-trim (see requirements.txt)" | emit
else
  if [ "${FULL:-0}" = 1 ]; then TYPES="0 1 2 3 4 5 6 7"; NM=1000000; NS=1000000; else TYPES="7 0 6 1"; NM=60; NS=15; fi
  echo "== 2. option sets for flat types: $TYPES"
  $NICE "$PY" -B "$HERE/sat/opts.py" "$OUT/opts" $TYPES 2>&1 | sed 's/^/   /'
  echo "== 3. c2 encoding checks (type 7)"
  ( cd "$HERE/checks" && OPTSDIR="$OUT/opts" MIDWORK="$OUT/w_c2" $NICE "$PY" -B c2_encoding.py ) 2>&1 | emit
  echo "== 3b. c3 tree coverage (oracle walk of the orbit trees)"
  for pk in "56 17" "53 6"; do for t in $TYPES; do
    $NICE "$PY" -B "$HERE/checks/c3_cover.py" $t $pk "$OUT/opts" "$OUT/w3_$t" 2>&1 | grep -E '^(PASS|FAIL)' | emit
  done; done
  echo "== 4. replay of recorded leaves"
  : > "$OUT/sha256_regenerated.tsv"
  for pk in "56 17" "53 6"; do for t in $TYPES; do
    SHAOUT="$OUT/sha256_regenerated.tsv" FULL="${FULL:-0}" $NICE "$PY" -B "$HERE/scripts/replay.py" $t $pk "$OUT/opts" "$OUT/w_$t" $NM $NS 2>&1 | grep -E '^(PASS|FAIL|   )' | emit
    rm -rf "$OUT/w_$t/red"
  done; done
  if [ "${FULL:-0}" != 1 ]; then
    if diff <(sort "$OUT/sha256_regenerated.tsv") <(sort "$HERE/evidence/sample_cnf_sha256.tsv") >/dev/null; then echo "PASS regenerated sample CNFs: sha256 equals evidence/sample_cnf_sha256.tsv ($(wc -l < "$OUT/sha256_regenerated.tsv") files)" | emit
    else echo "FAIL regenerated sample CNF sha256 differs from evidence/sample_cnf_sha256.tsv" | emit; fi
  fi
fi
npass=$(grep -c '^PASS' "$OUT/all.out"); nfail=$(grep -c '^FAIL' "$OUT/all.out"); nskip=$(grep -c '^SKIP' "$OUT/all.out")
echo "== done in $((SECONDS - T0))s: $((npass + 2)) PASS (2 in step 0), $nskip SKIP, $nfail FAIL; logs in $OUT"
if [ "$nfail" = 0 ] && [ "$nskip" = 0 ]; then echo "PASS: all assertions hold"; exit 0; fi
if [ "$nfail" = 0 ]; then echo "INCOMPLETE: no FAIL but $nskip SKIP (tools missing)"; exit 1; fi
echo "FAIL"; exit 1
