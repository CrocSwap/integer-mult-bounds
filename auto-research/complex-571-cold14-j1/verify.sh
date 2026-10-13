#!/bin/sh
# Official replay of complex-571-cold14-j1 from data/SPEC.json (standard library only, assertions on).
# usage: research/complex-571-cold14-j1/verify.sh WORKDIR [SOURCE_ROOT]
#   SOURCE_ROOT holds worktrees pr568 pr569 pr571 pr575 pr583 at the pinned commits (default: ..).
set -eu
WORK=${1:?usage: verify.sh WORKDIR [SOURCE_ROOT]}
SRC=${2:-..}
HERE=$(cd "$(dirname "$0")" && pwd)
exec python3 -B "$HERE/verify.py" --work "$WORK" \
  --source multicold="$SRC/pr568/research/complex-multicold" \
  --source structural_gain="$SRC/pr571/research/structural-gain" \
  --source larger_gain="$SRC/pr569/research/larger-gain" \
  --source joint_prefix="$SRC/pr575/research/complex-joint-prefix" \
  --source frame_coalescing="$SRC/pr583/research/kernel-frame-coalescing"
