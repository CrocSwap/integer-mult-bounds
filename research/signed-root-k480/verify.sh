#!/bin/sh
# Standard-library strict replay; source commits are pinned in data/SPEC.json.
set -eu
WORK=${1:?usage: verify.sh WORKDIR SOURCE_ROOT}
SRC=${2:?usage: verify.sh WORKDIR SOURCE_ROOT}
HERE=$(cd "$(dirname "$0")" && pwd)
python3 -B "$HERE/check_declarations.py"
python3 -B "$HERE/check_schedule.py" --hamming "$SRC/pr531/research/direct-delivery504-global/inputs/hamming" --out "${WORK}.schedule-controls.json"
exec python3 -B "$HERE/verify.py" --work "$WORK" --jobs 2 \
  --source multicold="$SRC/pr568/research/complex-multicold" \
  --source structural_gain="$SRC/pr571/research/structural-gain" \
  --source larger_gain="$SRC/pr569/research/larger-gain" \
  --source joint_prefix="$SRC/pr575/research/complex-joint-prefix" \
  --source frame_coalescing="$SRC/pr583/research/kernel-frame-coalescing" \
  --source direct_delivery="$SRC/pr531/research/direct-delivery504-global"
