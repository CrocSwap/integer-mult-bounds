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
"$PYTHON" -I -O -B "$HERE/extras/check_native_owners.py" --package "$HERE" --replay "$WORK" --out "$WORK/INDEPENDENT-NATIVE-OWNERS.json"
"$PYTHON" -I -O -B "$HERE/extras/check_owner_controls.py" --package "$HERE" --replay "$WORK" --out "$WORK/INDEPENDENT-OWNER-CONTROLS.json"
"$PYTHON" -I -O -B "$HERE/extras/check_declarations.py"
"$PYTHON" -I -O -B "$HERE/owner-search/replay_owner_map.py" --base-data "$HERE/data/nominations/PR638" --out "$WORK/owner-map-rebuilt" --negative-controls
"$PYTHON" - "$WORK/owner-map-rebuilt/OWNERS.json.gz" "$HERE/data/OWNERS.json.gz" <<'PY'
import gzip,sys
from pathlib import Path
if gzip.decompress(Path(sys.argv[1]).read_bytes()) != gzip.decompress(Path(sys.argv[2]).read_bytes()):
    raise SystemExit('Owner nomination failed exact payload reproduction')
print('PASS exact owner nomination payload')
PY
"$PYTHON" -I -O -B "$HERE/extras/check_u4_portable.py" --word "$WORK/jp8-step6-cold_end/FULL-WORD.json.gz" --provider jp8 --out "$WORK/INDEPENDENT-U4-CONTROLS.json" --negative-controls
"$PYTHON" -I -O -B "$HERE/extras/check_u4_portable.py" --word "$WORK/ck-step7-cold_end/FULL-WORD.json.gz" --provider ck --out "$WORK/INDEPENDENT-CK-U4-CONTROLS.json" --negative-controls
"$PYTHON" -B "$HERE/tools/build_ck_u4.py" --base-hpe "$WORK/ck-step6-hyperplane_end/FULL-WORD.json.gz" --out "$WORK/ck-u4-rebuilt"
"$PYTHON" - "$WORK/ck-u4-rebuilt/RECIPE.json.gz" "$HERE/data/recipes/k492-ck-cold_end.json.gz" <<'PYCODE'
import gzip,sys
from pathlib import Path
if gzip.decompress(Path(sys.argv[1]).read_bytes())!=gzip.decompress(Path(sys.argv[2]).read_bytes()):
 raise SystemExit('CK-u4 recipe payload reproduction failed')
print('PASS exact CK-u4 recipe reproduction')
PYCODE
