#!/usr/bin/env bash
set -euo pipefail
ROOT=$(cd "$(dirname "$0")" && pwd)
exec "${SW4_FRAME8_PYTHON:-python3}" -B "$ROOT/verify.py" --work "${1:?usage: verify.sh NEW_OUTPUT_DIRECTORY}"
