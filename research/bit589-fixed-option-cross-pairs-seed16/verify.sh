#!/usr/bin/env bash
set -euo pipefail
CROSS_PYTHON=${CROSS_PYTHON:-python3}
HERE=$(cd "$(dirname "$0")" && pwd)
ROOT=$(cd "$HERE/../.." && pwd)
TMP=$(mktemp)
trap 'rm -f "$TMP"' EXIT
"$CROSS_PYTHON" -I -B "$HERE/atlas.py" > "$TMP"
"$CROSS_PYTHON" -I - "$ROOT" "$HERE" "$TMP" <<'PY'
import hashlib
import json
import sys
from pathlib import Path
root, here, produced = map(Path, sys.argv[1:])
sources = json.loads((here / 'SOURCES.json').read_text())
for rel, expected in sources['files'].items():
    actual = hashlib.sha256((root / rel).read_bytes()).hexdigest()
    assert actual == expected, (rel, actual, expected)
r = json.loads(produced.read_text())
expected = json.loads((here / 'result.json').read_text())
assert r == expected, 'computed result differs from result.json'
assert r['shared_registers'] == 336 and r['cross_pairs'] == 6151
assert r['assignments'] == 88181
assert r['same_profile'] == 76840 and r['worse'] == 11341
assert r.get('improving', 0) == 0 and r.get('unresolved', 0) == 0
assert r.get('illegal_copy', 0) == 0 and r.get('illegal_frame_chain', 0) == 0
assert r['same_profile'] + r['worse'] == r['assignments']
assert r['best_improving'] is None and len(r['replay_spot_checks']) == 2
assert r['replay_spot_checks'][0]['profile'] == {
    '1': 1323, '2': 1342, '3': 79, '4': 44, '5': 102, '6': 11, '7': 19
}
lo, hi = map(lambda x: __import__('fractions').Fraction(x), r['home_control'][2:4])
assert lo <= 0 <= hi
print('PASS_BIT589_FIXED_OPTION_CROSS_PAIRS seed=16 pairs=6151 assignments=88181')
PY
