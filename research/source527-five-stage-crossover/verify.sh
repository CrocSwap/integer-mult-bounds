#!/usr/bin/env bash
set -euo pipefail
root=$(cd -- "$(dirname -- "$0")" && pwd)
work="${TMPDIR:-/tmp}/five527-$(date +%s)-$$"
mkdir -p "$work/deps"
check_payload() {
 python3 - "$root" <<'PY'
import sys,json,hashlib
from pathlib import Path
r=Path(sys.argv[1]);m=json.loads((r/'FILES.json').read_text())
for e in m['files']:assert hashlib.sha256((r/e['path']).read_bytes()).hexdigest()==e['sha256'],e['path']
PY
}
check_payload
public="$root/references/source527"
results="${PUBLIC_RESULTS:-$work/public}"
if [ -z "${PUBLIC_RESULTS:-}" ]; then python3 -B "$public/verify.py" --output "$results"; fi
python3 - "$public" "$results" <<'PY'
import sys,json,hashlib
from pathlib import Path
p,r=map(Path,sys.argv[1:]);v=json.loads((r/'verification.json').read_text())
assert v['status']=='PASS_IMMUTABLE_SOURCE527_FIVE_STAGE_BANKED_CONSTRUCTION' and v['inputs_unchanged'] and len(v['fresh_stages'])==8
assert v['manifest_sha256']==hashlib.sha256((p/'MANIFEST.json').read_bytes()).hexdigest()
PY
python3 -B "$root/native/export-prepared527.py" "$public" "$work"
python3 - "$results/records.bin.gz" "$work/records.bin" "$root/native/native-deps.zip" "$work/deps" <<'PY'
import sys,gzip,shutil,zipfile
with gzip.open(sys.argv[1],'rb') as f,open(sys.argv[2],'wb') as g:shutil.copyfileobj(f,g)
with zipfile.ZipFile(sys.argv[3]) as z:z.extractall(sys.argv[4])
PY
for name in source527-assembly independent527 stage-private527-banks check-stage-private527-banks route-interface527 extract527-physical-scalar five-stage527-columns; do
 "${CXX:-g++}" -O3 -std=c++20 -I"$work/deps/include" -I"$root/native" "$root/native/$name.cpp" -o "$work/$name"
done
"$work/stage-private527-banks" "$work/BANK-INPUTS527.json" "$work/NATIVE-BANKS.json"
"$work/check-stage-private527-banks" "$work/BANK-INPUTS527.json" "$work/NATIVE-BANKS.json" "$work/BANKS-INDEPENDENT.json"
"$work/route-interface527" "$work/LABELS527.json" "$public" "$work/ROUTES.json"
"$work/extract527-physical-scalar" "$work/records.bin" "$results/physical.json" "$results/raw.json" "$work/EVENTS.json"
"$work/five-stage527-columns" "$work/EVENTS.json" "$work/COLUMNS.json"
"$work/source527-assembly" "$results/raw.json" "$results/banks.json" "$root/witnesses/complex-native-profile.json" "$results/finite.json" "$work/NATIVE-BANKS.json" "$work/ASSEMBLY.json"
"$work/independent527" "$work/ASSEMBLY.json" "$work/INDEPENDENT-ARITHMETIC.json" "$results/banks.json" "$results/raw.json" "$work/NATIVE-BANKS.json"
python3 - "$work/ASSEMBLY.json" "$root/certificate.json" <<'PY'
import sys,json
from pathlib import Path
a,b=(json.loads(Path(p).read_text()) for p in sys.argv[1:]);assert a['kappa']==b['kappa'];print('PASS source-bound conditional kappa='+a['kappa'])
PY
check_payload
printf 'Preserved verification outputs: %s\n' "$work"
