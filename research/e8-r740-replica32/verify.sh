#!/usr/bin/env bash
set -euo pipefail
QUICK=0
if [ "${1:-}" = --quick ]; then QUICK=1; shift; fi
HERE=$(cd "$(dirname "$0")" && pwd)
OUT=$(mkdir -p "$1" && cd "$1" && pwd)
case "$OUT" in "$HERE"*) echo 'Output must be outside this package'; exit 2;; esac
PY=${PYTHON:-python3}
export PYTHONDONTWRITEBYTECODE=1
export PYTHON="$PY"

echo '== Frozen package and complete upstream provenance'
"$PY" -I -B - "$HERE" <<'PY'
import hashlib,json,pathlib,sys
p=pathlib.Path(sys.argv[1])
manifest=json.loads((p/'MANIFEST.json').read_text())
actual={str(f.relative_to(p)):hashlib.sha256(f.read_bytes()).hexdigest()
        for f in p.rglob('*') if f.is_file() and '__pycache__' not in f.parts and f.name!='MANIFEST.json'}
assert actual==manifest, 'package differs from frozen manifest'
source=json.loads((p/'SOURCE.json').read_text())
for rel,expected in source['parent436_blobs'].items():
    data=(p/'parent436'/rel).read_bytes()
    assert hashlib.sha1(b'blob %d\0'%len(data)+data).hexdigest()==expected,rel
for rel,expected in (source['kernel_identical_blobs'] | source['witness_identical_blobs']).items():
    data=(p/rel).read_bytes()
    assert hashlib.sha1(b'blob %d\0'%len(data)+data).hexdigest()==expected,rel
print('PASS package manifest, byte-identical PR436 parent, PR417 code and PR441 witnesses')
PY

echo '== Reproduce PR436 with its unchanged verification wrapper'
if [ "$QUICK" = 1 ]; then
  bash "$HERE/parent436/verify.sh" --quick "$OUT/parent"
else
  bash "$HERE/parent436/verify.sh" "$OUT/parent"
fi

echo '== Rebuild primitive retiming, kernel and 32-replica bank admission'
"$PY" -B "$HERE/code/rebuild.py" | tee "$OUT/REBUILD.json"
B=$HERE/parent436/code/bit
WORD=$HERE/data/word.json.gz
mkdir -p "$OUT/candidate/nine"
"$PY" -I -B "$B/export_records.py" "$WORD" "$OUT/candidate/records"
"$PY" -I -B "$B/regression/stage_cohort.py" "$OUT/candidate/records" "$OUT/candidate/records" "$OUT/candidate/cin" "$OUT/candidate/cout"
"$OUT/parent/bin/legality" "$OUT/candidate/cin" "$OUT/candidate/cout" "$OUT/candidate/cout/legality.json"
"$OUT/parent/bin/columns_h" "$OUT/candidate/cout/COHORT249-RECORDS.bin" "$OUT/candidate/cout/columns.json"
"$OUT/parent/bin/columns_k4" "$OUT/candidate/cout/COHORT249-RECORDS.bin" "$OUT/candidate/cout/columns_k4.json"
"$PY" -I -B "$B/mutate_records.py" "$OUT/candidate/records" "$OUT/candidate/cin" "$OUT/candidate/cout" "$OUT/parent/bin/legality" "$OUT/parent/bin/columns_k4" "$OUT/parent/bin/legality_ncopy_h"
"$PY" -I -B "$B/checkers/gram_frames.py" "$OUT/candidate/records" --gram e8ham --h 8 --positive

echo '== Compressed geometry, residual routes, global audit and finite invoice'
cp "$OUT/parent/nine/GEOMETRY.json" "$OUT/candidate/nine/GEOMETRY.json"
"$PY" -B "$HERE/code/global_kernel.py" --word "$WORD" --local-check "$OUT/candidate" --out "$OUT/candidate/nine" --isometries "$HERE/data/residual-isometries.json"
"$PY" -B "$HERE/code/audit_kernel.py" --word "$WORD" --local-check "$OUT/candidate" --out "$OUT/candidate/nine"
"$PY" -B "$HERE/code/compose_kernel.py" --pricing "$HERE/parent436/code/pricing" --out "$OUT/candidate/nine" --cited "$HERE/parent436/data/complex-b-433.json" --receipt "$HERE/parent436/data/controls/pr433/CERTIFICATE.json"
"$PY" -I -B - "$HERE" "$OUT" <<'PY'
import json,pathlib,sys
p,out=map(pathlib.Path,sys.argv[1:])
g=json.loads((out/'candidate/nine/GLOBAL.json').read_text())
r=json.loads((out/'candidate/nine/COMPOSED-433.json').read_text())
expected=json.loads((p/'EXPECTED.json').read_text())
for key,value in expected['global'].items(): assert g[key]==value,(key,g[key],value)
for key,value in expected['result'].items(): assert r[key]==value,(key,r[key],value)
assert len(r['strict_outer_constraints'])==47 and len(r['outer_controls'])==4
print('PASS conditional kappa',r['kappa'],'=',r['kappa_decimal'])
PY
