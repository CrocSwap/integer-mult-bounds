#!/usr/bin/env bash
set -euo pipefail
here="$(cd -- "$(dirname -- "$0")" && pwd)"
if [ "$#" -eq 0 ]; then
  out="$(mktemp -d)/run"
  echo "Output: $out"
  exec python3 -B "$here/verify.py" --work "$out"
else
  exec python3 -B "$here/verify.py" "$@"
fi
