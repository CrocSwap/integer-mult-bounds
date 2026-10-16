#!/usr/bin/env bash
# Verification of research/decoder-floors-reduction (no kappa claim).   usage: bash verify.sh [/fresh/output/dir]
# Needs Python >= 3.10 with numpy (PYTHON=/path/to/python to choose).  No SAT solver.  About 5 minutes, at most 3 processes, each under timeout 1200.
#   0  MANIFEST.sha256
#   1  three parallel streams: s1close (~2 min) | twinblk (~0.5 min) | the fast group (cat1 cat2 gtab pair2 fold transport p104prem c_batch_arith c_clique_lemmaE d4 omega)
#   2  check_logs.py: every number of the README as a PASS/FAIL line
set -uo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
OUT=${1:-$(mktemp -d "${TMPDIR:-/tmp}/decoder-floors.XXXXXX")}
mkdir -p "$OUT"; OUT=$(cd "$OUT" && pwd)
case "$OUT/" in "$HERE"/*) echo "output dir must be outside the package"; exit 2;; esac
PY="${PYTHON:-python3}"; export PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 OPENBLAS_NUM_THREADS=1
TMO=""; command -v timeout >/dev/null 2>&1 && TMO="timeout 1200"; command -v gtimeout >/dev/null 2>&1 && TMO="gtimeout 1200"
W="$OUT/work"; LOG="$OUT/logs"; mkdir -p "$W" "$LOG"; : > "$OUT/all.out"; : > "$OUT/times.out"; T0=$SECONDS
echo "== 0. manifest"
"$PY" -B "$HERE/checks/manifest_check.py" | tee -a "$OUT/all.out" | sed 's/^/   /'; grep -q '^FAIL' "$OUT/all.out" && { echo "step 0 FAILED"; exit 1; }
cp "$HERE"/checks/*.py "$HERE"/data/* "$W"/
cd "$W"
run() { local n=$1; shift; local s=$SECONDS; $TMO nice -n 10 "$@" > "$LOG/$n.log" 2>&1; local rc=$?; echo "ran $n rc=$rc in $((SECONDS - s))s" >> "$OUT/times.out"; return 0; }
echo "== 1. computations (three parallel streams)"
( run s1close "$PY" -B s1close.py ) & P1=$!
( run twinblk "$PY" -B twinblk.py ) & P2=$!
( for n in cat1 cat2 gtab fold transport c_batch_arith c_clique_lemmaE d4 omega p104prem pair2; do run $n "$PY" -B $n.py; done ) & P3=$!
wait $P1; wait $P2; wait $P3
sed 's/^/   /' "$OUT/times.out"
grep -v 'rc=0 ' "$OUT/times.out" | sed 's/^/FAIL nonzero exit: /' | tee -a "$OUT/all.out"
echo "== 2. assertions (check_logs.py)"
"$PY" -B "$HERE/checks/check_logs.py" "$LOG" | tee -a "$OUT/all.out" | sed 's/^/   /'
npass=$(grep -c '^PASS' "$OUT/all.out"); nfail=$(grep -c '^FAIL' "$OUT/all.out")
echo "== done in $((SECONDS - T0))s: $npass PASS, $nfail FAIL; logs in $OUT"
[ "$nfail" = 0 ] && { echo "PASS: all assertions hold"; exit 0; }
echo "FAIL"; exit 1
