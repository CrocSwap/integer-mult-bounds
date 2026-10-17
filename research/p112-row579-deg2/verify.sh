#!/usr/bin/env bash
# Verification of research/p112-row579-deg2.   usage: bash verify.sh [fresh/output/dir]
# PYTHON=/path/to/python (needs numpy; default python3), FULL=1 adds the heavy reruns (checks/full.sh; chunked, each < 20 min).
# At most 3 processes at a time; every process under `timeout 1200` (the DEG2A step is a chain of sub-runs, each under timeout 1100); default run: a few minutes.
# No claim in this package is a kappa claim.
set -uo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
OUT=${1:-$(mktemp -d "${TMPDIR:-/tmp}/p112deg2.XXXXXX")}; mkdir -p "$OUT"; OUT=$(cd "$OUT" && pwd)
case "$OUT/" in "$HERE"/*) echo "output dir must be outside the package"; exit 2;; esac
PY="${PYTHON:-python3}"; export PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 PYTHON="$PY"
C="$HERE/checks"; : > "$OUT/all.out"
note() { echo "$@" | tee -a "$OUT/all.out"; }
echo "== 0. manifest"
"$PY" -B "$C/manifest_check.py" | tee -a "$OUT/all.out" | sed 's/^/   /'; [ "${PIPESTATUS[0]}" = 0 ] || { echo "step 0 FAILED"; exit 1; }
echo "== 1. ledger4 recomputed from ledger3 (#3154); all 603 rows KILLED"
"$PY" -B "$C/build_ledger4.py" "$OUT/ledger4.csv" | tee -a "$OUT/all.out" | sed 's/^/   /'
cmp -s "$OUT/ledger4.csv" "$HERE/data/ledger4_consolidated.csv" && note "PASS ledger4_consolidated.csv reproduced byte-for-byte" || note "FAIL ledger4 differs"
echo "== 2. reruns (K579T impl A -> R579b chain, K579T impl B + types, DEG2 impl A stages; 3 chains in parallel)"
S="$C/steps.sh"; export S OUT
chain() { # name cmd...: run steps and print PASS/FAIL
  n=$1; s=$2; r=$(timeout 1200 bash "$S" "$OUT/work" $s 2>&1 | tail -n 1)
  case "$r" in STEP-OK*) echo "PASS $n: ${r#STEP-OK }";; *) echo "FAIL $n: $r";; esac; }
export -f chain
mkdir -p "$OUT/work"
{ ( chain K579T_implA k579a; chain R579b_K5minus r579 ) &
  ( chain K579T_implB k579b; chain R579b_types types ) &
  ( chain DEG2A_implA deg2a ) &
  wait; } 2>&1 | sort | tee -a "$OUT/all.out"
if [ "${FULL:-0}" = 1 ]; then
  echo "== 3. FULL=1: heavy reruns (see PROOF_MAP.md, section D)"
  bash "$HERE/checks/full.sh" "$OUT" 2>&1 | tee -a "$OUT/all.out"
fi
nf=$(grep -Ec '^(FAIL|FULL-FAIL)' "$OUT/all.out"); np=$(grep -c '^PASS' "$OUT/all.out")
if [ "$nf" = 0 ] && [ "$np" -ge 7 ]; then echo "ALL PASS ($np checks)"; else echo "SOME FAILED ($nf failures, $np passes)"; exit 1; fi
