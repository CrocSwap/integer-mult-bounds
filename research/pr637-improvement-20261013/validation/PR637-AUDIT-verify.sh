#!/bin/sh
set -eu
HERE=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
PYTHON=${PYTHON:-python3}
WORK=${1:?Choose a new replay output directory}
"$PYTHON" - <<'PY'
import sys
if sys.version_info < (3,10):
    raise SystemExit('Python >=3.10 required')
if not __debug__:
    raise SystemExit('Assertions required; unset PYTHONOPTIMIZE and do not use -O')
PY
"$PYTHON" -B "$HERE/verify.py" --jobs 2 --work "$WORK" \
  --source multicold="$HERE/vendor/multicold" \
  --source structural_gain="$HERE/vendor/structural_gain" \
  --source larger_gain="$HERE/vendor/larger_gain" \
  --source joint_prefix="$HERE/vendor/joint_prefix" \
  --source frame_coalescing="$HERE/vendor/frame_coalescing" \
  --source direct_delivery="$HERE/vendor/direct_delivery"
