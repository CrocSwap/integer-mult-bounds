#!/usr/bin/env bash
# Bundle B (sections 3-4: C1-C3, G1-G3). Run from the package root; prints one PASS line per assertion; exit 0 only if none fails. About 3 s.
set -uo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
PY="${PYTHON:-python3}"; st=0
for c in b_pins c1_census_656 c2_dirty_borrow c3_cap_f2_9 g1_gauge_bound; do
  "$PY" -B "$HERE/checks/$c.py" || st=1
done
echo "G3 ARGUED (no script); G2 ceiling 48/46/88 and the 504/K480 rows of G1 RECORDED (no re-run)"
exit $st
