#!/usr/bin/env bash
# Bundle A (sections 1-2: Erratum and scope E1-E2; Invoice calculus and prices P1-P5).  Prints one PASS/FAIL line per
# assertion; exit status 0 only if all pass.  Standard library only (python >= 3.11); a C++ compiler is used by E2 if present
# (otherwise E2 parses the shipped evidence).  About 20 s.   usage: bash verify.part.sh        (PYTHON=... to choose python)
#   E1_FULL=1 bash verify.part.sh   also runs #595's a5_scope_multipliers.py unchanged (all 7 variants, +56 s).
set -uo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
PY="${PYTHON:-python3}"
export PYTHONDONTWRITEBYTECODE=1
status=0
run() { "$PY" -I -B "$HERE/checks/$1" || status=1; }
echo "== A.1 erratum and scope"; run e1_scope_multipliers.py; run e2_rho.py
echo "== A.2 invoice calculus and prices"; run p1_knobs.py; run p2_bit.py; run p3_rate.py; run p4_s7.py; run p5_cover.py
if [ $status -eq 0 ]; then echo "== bundle A: all PASS"; else echo "== bundle A: FAILURES"; fi
exit $status
