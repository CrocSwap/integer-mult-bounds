#!/bin/sh
# Fresh strict admission and supplemental composition checks.
# Chi Zhao, with substantial OpenAI Codex assistance. Apache-2.0.
set -eu
WORK=${1:?usage: verify.sh NEW_WORK_DIRECTORY}
HERE=$(CDPATH='' cd -- "$(dirname -- "$0")" && pwd)
PYTHON=${PYTHON:-python3}
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
"$PYTHON" -B "$HERE/tools/check_basis_proof.py" \
  --word "$WORK/jp8-step6-cold_end/FULL-WORD.json.gz" --out "$WORK/COMPOSITION-BASIS-PROOF.json"
"$PYTHON" -B "$HERE/tools/check_composition_controls.py" \
  --word "$WORK/jp8-step6-cold_end/FULL-WORD.json.gz" --out "$WORK/composition-controls"
"$PYTHON" -B "$HERE/tools/build_combined_end.py" \
  --base-hpe "$WORK/jp8-step5-hyperplane_end/FULL-WORD.json.gz" --out "$WORK/nomination-rebuilt"
"$PYTHON" - "$WORK/nomination-rebuilt/RECIPE.json.gz" "$HERE/data/recipes/k492-jp8-cold_end.json.gz" <<'PY'
import gzip,sys
from pathlib import Path
if gzip.decompress(Path(sys.argv[1]).read_bytes()) != gzip.decompress(Path(sys.argv[2]).read_bytes()):
    raise SystemExit('Combined recipe nomination failed exact payload reproduction')
print('PASS exact combined recipe nomination payload')
PY
"$PYTHON" -I -O -B "$HERE/extras/check_native_owners.py" --package "$HERE" \
  --replay "$WORK" --out "$WORK/INDEPENDENT-NATIVE-OWNERS.json"
"$PYTHON" -I -O -B "$HERE/extras/check_owner_controls.py" --package "$HERE" \
  --replay "$WORK" --out "$WORK/INDEPENDENT-OWNER-CONTROLS.json"
"$PYTHON" -I -O -B "$HERE/extras/check_declarations.py"
"$PYTHON" -I -O -B "$HERE/owner-search/replay_owner_map.py" --base-data "$HERE/data/nominations/PR635" --out "$WORK/owner-map-rebuilt" --negative-controls
"$PYTHON" - "$WORK/owner-map-rebuilt/OWNERS.json.gz" "$HERE/data/OWNERS.json.gz" <<'PYCODE'
import gzip,sys
from pathlib import Path
if gzip.decompress(Path(sys.argv[1]).read_bytes()) != gzip.decompress(Path(sys.argv[2]).read_bytes()):
    raise SystemExit('Owner nomination failed exact payload reproduction')
print('PASS exact owner nomination payload')
PYCODE
