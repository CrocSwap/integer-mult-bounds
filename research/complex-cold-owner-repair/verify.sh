#!/usr/bin/env bash
set -euo pipefail
COLD_REPAIR_HERE="$(cd "$(dirname "$0")" && pwd)"
COLD_REPAIR_WORK="${1:?usage: verify.sh WORKDIR}"
COLD_REPAIR_PYTHON="${COLD_REPAIR_PYTHON:-python3}"
"$COLD_REPAIR_PYTHON" -I -O -B "$COLD_REPAIR_HERE/code/check_declarations.py"
"$COLD_REPAIR_PYTHON" -B "$COLD_REPAIR_HERE/verify.py" --work "$COLD_REPAIR_WORK" \
  --source "multicold=$COLD_REPAIR_HERE/vendor/multicold" \
  --source "structural_gain=$COLD_REPAIR_HERE/vendor/structural_gain" \
  --source "larger_gain=$COLD_REPAIR_HERE/vendor/larger_gain" \
  --source "joint_prefix=$COLD_REPAIR_HERE/vendor/joint_prefix" \
  --source "frame_coalescing=$COLD_REPAIR_HERE/vendor/frame_coalescing"
"$COLD_REPAIR_PYTHON" -I -O -B "$COLD_REPAIR_HERE/code/check_owner_map.py" --work "$COLD_REPAIR_WORK" --out "$COLD_REPAIR_WORK/INDEPENDENT-MAP-CHECK.json"
