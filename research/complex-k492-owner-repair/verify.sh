#!/usr/bin/env bash
set -euo pipefail
K492_HERE="$(cd "$(dirname "$0")" && pwd)"
K492_WORK="${1:?usage: verify.sh WORKDIR}"
K492_PYTHON="${K492_PYTHON:-python3}"
"$K492_PYTHON" -I -O -B "$K492_HERE/extras/check_declarations.py"
"$K492_PYTHON" -B "$K492_HERE/verify.py" --work "$K492_WORK" \
  --source "multicold=$K492_HERE/vendor/multicold" \
  --source "structural_gain=$K492_HERE/vendor/structural_gain" \
  --source "larger_gain=$K492_HERE/vendor/larger_gain" \
  --source "joint_prefix=$K492_HERE/vendor/joint_prefix" \
  --source "frame_coalescing=$K492_HERE/vendor/frame_coalescing" \
  --source "direct_delivery=$K492_HERE/vendor/direct_delivery"
"$K492_PYTHON" -I -O -B "$K492_HERE/extras/check_owner_map.py" --work "$K492_WORK" --out "$K492_WORK/INDEPENDENT-MAP-CHECK.json"
