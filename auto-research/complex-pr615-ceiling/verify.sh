#!/usr/bin/env bash
set -euo pipefail
CEILING_HERE="$(cd "$(dirname "$0")" && pwd)"
CEILING_WORK="${1:?usage: verify.sh WORKDIR}"
CEILING_PYTHON="${CEILING_PYTHON:-python3}"
"$CEILING_PYTHON" -I -O -B "$CEILING_HERE/code/check_declarations.py"
"$CEILING_PYTHON" -B "$CEILING_HERE/verify.py" --work "$CEILING_WORK" \
  --source "multicold=$CEILING_HERE/vendor/multicold" \
  --source "structural_gain=$CEILING_HERE/vendor/structural_gain" \
  --source "larger_gain=$CEILING_HERE/vendor/larger_gain" \
  --source "joint_prefix=$CEILING_HERE/vendor/joint_prefix" \
  --source "frame_coalescing=$CEILING_HERE/vendor/frame_coalescing"
"$CEILING_PYTHON" -I -O -B "$CEILING_HERE/code/check_ceiling.py" --work "$CEILING_WORK"
"$CEILING_PYTHON" -I -B "$CEILING_HERE/code/check_refinement.py" --work "$CEILING_WORK"
