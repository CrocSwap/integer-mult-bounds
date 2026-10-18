#!/usr/bin/env bash
# Verification of research/two-sided-ten-term-floor (no kappa claim).   usage: bash verify.sh [/fresh/output/dir]
# Needs Python >= 3.10 with numpy, sympy, networkx (PYTHON=/path/to/python to choose).  No SAT solver.  About 18 minutes wall, at most 4 processes, each command under timeout 1200, niced.
#   0  MANIFEST.sha256
#   1  four streams: clique.py (+ witness16, diag9) | caseb4.py chunks 0, 1, 2 of 3
#   2  four streams: clique2.py 5 on the 93 sets I^c (|I^c| <= 3), four chunks
#   3  four streams: clique2.py 4 + d4A + d4A2 + d4A3 | verify_cl (2 representatives) x2 | sym + stab
#   4  check_logs.py: every number of the README as a PASS/FAIL line
set -uo pipefail
JOBS=${JOBS:-4}
HERE=$(cd "$(dirname "$0")" && pwd)
OUT=${1:-$(mktemp -d "${TMPDIR:-/tmp}/two-sided-floor.XXXXXX")}
mkdir -p "$OUT"; OUT=$(cd "$OUT" && pwd)
case "$OUT/" in "$HERE"/*) echo "output dir must be outside the package"; exit 2;; esac
PY="${PYTHON:-python3}"; export PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 OPENBLAS_NUM_THREADS=1
TMO=""; command -v timeout >/dev/null 2>&1 && TMO="timeout 1200"; command -v gtimeout >/dev/null 2>&1 && TMO="gtimeout 1200"
W="$OUT/work"; LOG="$OUT/logs"; mkdir -p "$W" "$LOG"; : > "$OUT/all.out"; : > "$OUT/times.out"; T0=$SECONDS
echo "== 0. manifest"
"$PY" -B "$HERE/checks/manifest_check.py" | tee -a "$OUT/all.out" | sed 's/^/   /'; grep -q '^FAIL' "$OUT/all.out" && { echo "step 0 FAILED"; exit 1; }
cp "$HERE"/checks/*.py "$HERE"/data/data.json "$W"/
cd "$W"
run() { local n=$1; shift; local s=$SECONDS; $TMO nice -n 10 "$@" > "$LOG/$n.log" 2>&1; local rc=$?; echo "ran $n rc=$rc in $((SECONDS - s))s" >> "$OUT/times.out"; return 0; }
# the 93 sets I^c with |I^c| <= 3, as "a,b,c;..." strings, dealt into four chunks
"$PY" -B - <<'PYE'
import itertools
sets = [c for k in range(4) for c in itertools.combinations(range(8), k)]
for j in range(4):
    open('ics_%d.txt' % j, 'w').write(';'.join(','.join(map(str, c)) for i, c in enumerate(sets) if i % 4 == j))
PYE
echo "== 1. computations, phase 1 (four streams)"
( run clique "$PY" -B clique.py; run w16 "$PY" -B witness16.py; run d9 "$PY" -B diag9.py ) & P1=$!
( run cb4_0 "$PY" -B caseb4.py 0 3 ) & P2=$!
[ "$JOBS" -le 2 ] && { wait $P1; wait $P2; }
( run cb4_1 "$PY" -B caseb4.py 1 3 ) & P3=$!
( run cb4_2 "$PY" -B caseb4.py 2 3 ) & P4=$!
wait $P1; wait $P2; wait $P3; wait $P4
echo "== 1. computations, phase 2 (four streams)"
( run c2_0 "$PY" -B clique2.py 5 "$(cat ics_0.txt)" ) & P1=$!
( run c2_1 "$PY" -B clique2.py 5 "$(cat ics_1.txt)" ) & P2=$!
[ "$JOBS" -le 2 ] && { wait $P1; wait $P2; }
( run c2_2 "$PY" -B clique2.py 5 "$(cat ics_2.txt)" ) & P3=$!
( run c2_3 "$PY" -B clique2.py 5 "$(cat ics_3.txt)" ) & P4=$!
wait $P1; wait $P2; wait $P3; wait $P4
echo "== 1. computations, phase 3 (four streams)"
( run c24 "$PY" -B clique2.py 4 "0,1,2,4"; run d4A "$PY" -B d4A.py found_0_1_2_4.pkl; run d4A2 "$PY" -B d4A2.py; run d4A3 "$PY" -B d4A3.py ) & P1=$!
( run vcl_none "$PY" -B verify_cl.py ""; run vcl_0_1_2 "$PY" -B verify_cl.py "0,1,2" ) & P2=$!
[ "$JOBS" -le 2 ] && { wait $P1; wait $P2; }
( run vcl_0 "$PY" -B verify_cl.py "0"; run vcl_0_1 "$PY" -B verify_cl.py "0,1" ) & P3=$!
( run sym "$PY" -B sym.py; run stab "$PY" -B stab.py ) & P4=$!
wait $P1; wait $P2; wait $P3; wait $P4
sed 's/^/   /' "$OUT/times.out"
grep -v 'rc=0 ' "$OUT/times.out" | sed 's/^/FAIL nonzero exit: /' | tee -a "$OUT/all.out"
echo "== 4. assertions (check_logs.py)"
"$PY" -B "$HERE/checks/check_logs.py" "$LOG" | tee -a "$OUT/all.out" | sed 's/^/   /'
npass=$(grep -c '^PASS' "$OUT/all.out"); nfail=$(grep -c '^FAIL' "$OUT/all.out")
echo "== done in $((SECONDS - T0))s: $npass PASS, $nfail FAIL; logs in $OUT"
[ "$nfail" = 0 ] && { echo "PASS: all assertions hold"; exit 0; }
echo "FAIL"; exit 1
