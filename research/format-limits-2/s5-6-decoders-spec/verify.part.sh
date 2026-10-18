#!/usr/bin/env bash
# Bundle C (sections 5-6: D1-D4, S1-S4).  Sourced/called by the package verify.sh with PY, OUT and PKG (package root) set; also runnable alone:
#   PY=python3 PKG=<dir containing checks/> bash verify.part.sh [outdir]       (needs numpy, scipy, sympy)
# Prints one PASS/FAIL line per assertion; fails if any FAIL.  Wall time about 35 s on 3 cores (longest check d1_frames ~20 s).
set -u
PKG=${PKG:-$(cd "$(dirname "$0")" && pwd)}
PY=${PY:-${PYTHON:-python3}}
OUT=${1:-${OUT:-$(mktemp -d "${TMPDIR:-/tmp}/fl2-C.XXXXXX")}}
mkdir -p "$OUT"
export PYTHONDONTWRITEBYTECODE=1
cd "$PKG/checks"
checks="d1_decoder_floor d1_frames d3_punctures d4_structured s1_inplace s3_r2_toy log_checks anchors"
for c in $checks; do ( nice -n 19 "$PY" -B "$c.py" > "$OUT/C-$c.log" 2>&1; echo $? > "$OUT/C-$c.rc" ) & done
wait
status=0
for c in $checks; do
  cat "$OUT/C-$c.log"
  [ "$(cat "$OUT/C-$c.rc")" = 0 ] || { echo "FAIL C.$c (exit $(cat "$OUT/C-$c.rc"))"; status=1; }
done
exit $status
