#!/usr/bin/env bash
# Bundle D (sections 7-9: rows Y1-Y2, F1-F3, O1-O2).  Run from anywhere; prints one PASS/FAIL line per assertion.
# Needs python3 >= 3.11 with numpy and scipy.  Runtime about 15 s. 
set -uo pipefail
HERE=$(cd "$(dirname "$0")" && pwd); PY="${PYTHON:-python3}"; st=0
export PYTHONDONTWRITEBYTECODE=1
echo "== D.1 checks"
for c in y1_centre_cut o1_faces f1_frag f1_pack f1_s3s4 f1_carriers f6_log; do
  echo "-- $c"; ( cd "$HERE/checks" && "$PY" -B "$c.py" ) || st=1
done
[ $st = 0 ] && echo "D: all PASS" || echo "D: FAILURES"
exit $st
