#!/usr/bin/env bash
# One-command verification. usage: bash verify.sh [--quick] /fresh/output/dir
#   needs python3 >= 3.11 with numpy and mpmath, a C++17 compiler (CXX, default c++) and Boost headers (BOOST_INCLUDE).
#   --quick skips the control that rebuilds PR #346's published word from the unstaged parity word.
set -euo pipefail
QUICK=0; if [ "${1:-}" = "--quick" ]; then QUICK=1; shift; fi
HERE=$(cd "$(dirname "$0")" && pwd); WD=$(mkdir -p "$1" && cd "$1" && pwd)
PY=${PYTHON:-python3}; CXX=${CXX:-c++}; BI=${BOOST_INCLUDE:-/usr/include}; C=$HERE/code; DA=$HERE/data
case "$WD" in "$HERE"*) echo "output dir must be outside the package"; exit 2;; esac
echo "== 0. manifest"; (cd "$HERE" && $PY -c "
import hashlib,sys
bad=0
for line in open('MANIFEST.sha256'):
    h,p=line.split('  ',1);p=p.strip()
    if hashlib.sha256(open(p,'rb').read()).hexdigest()!=h: print('MISMATCH',p);bad+=1
import os
listed={l.split('  ',1)[1].strip() for l in open('MANIFEST.sha256')}
files={os.path.relpath(os.path.join(r,f)) for r,_,fs in os.walk('.') for f in fs if '__pycache__' not in r}-{'MANIFEST.sha256'}
extra=files-listed
if extra: print('UNLISTED',sorted(extra));bad+=1
sys.exit(1 if bad else 0)") && echo "   all files match MANIFEST.sha256"
unz(){ mkdir -p "$2"; for f in 249-records.bin 249-states.json frames.json; do gunzip -c "$1/$f.gz" > "$2/$f"; done; }
unz $DA/staged $WD/staged; unz $DA/parity $WD/parity; unz $DA/parity325 $WD/parity325
(cd $WD && sha256sum -c "$DA/SHA256SUMS-inputs" --quiet 2>/dev/null || shasum -a 256 -c "$DA/SHA256SUMS-inputs" --quiet) && echo "== 1. staged base word (PR #329 stack: descent, target, restore, sink; no kernel) and parity word: hashes OK"
$PY -B $C/price.py $WD/staged | tail -2
echo "== 2. Design T + twin condensation on the staged word (own reimplementation)"
$PY -B $C/dt.py $WD/staged $WD/T
$PY -B $C/comp.py $WD/T
TWIN_CAP=470 $PY -B $C/twin.py $WD/T $WD/TT
gunzip -c $DA/designt/249-records.bin.gz | cmp - $WD/TT/249-records.bin && echo "   rebuilt Design T word equals the shipped one (PR #354's final word)"
(cd $WD && sha256sum -c "$DA/SHA256SUMS-designt" --quiet 2>/dev/null || shasum -a 256 -c "$DA/SHA256SUMS-designt" --quiet) && echo "   Design T word records hash OK"
echo "== 2b. transcript stages on the Design T word: shared-donor kernel, retiming, reorder, reorder2 (frozen selections)"
$PY -B $C/stages.py kernel $WD/TT $WD/K $HERE/stages/kernel-selection.json $DA/labels.json
$PY -B $C/stages.py retime $WD/K $WD/KR $HERE/stages/retime-selection.json $DA/labels.json
$PY -B $C/stages.py reorder $WD/KR $WD/KRO $HERE/stages/reorder-selection.json $DA/labels.json
$PY -B $C/stages.py reorder $WD/KRO $WD/F $HERE/stages/reorder2-selection.json $DA/labels.json
gunzip -c $DA/final/249-records.bin.gz | cmp - $WD/F/249-records.bin && echo "   rebuilt final word equals the shipped word"
(cd $WD && sha256sum -c "$DA/SHA256SUMS-final" --quiet 2>/dev/null || shasum -a 256 -c "$DA/SHA256SUMS-final" --quiet) && echo "   final records hash OK"
if [ $QUICK = 0 ]; then
  echo "== 2c. control: the same transform on the unstaged parity word gives PR #346's published final word byte for byte"
  $PY -B $C/dt.py $WD/parity325 $WD/T346 > /dev/null && $PY -B $C/comp.py $WD/T346 > /dev/null && $PY -B $C/twin.py $WD/T346 $WD/TT346 > /dev/null
  test "$( (sha256sum $WD/TT346/249-records.bin 2>/dev/null || shasum -a 256 $WD/TT346/249-records.bin) | cut -c1-64)" = c6a9311acfcf85f4a5775ed0187e31f84531614bb08434ef887ae1e63dda99c4 && echo "   PR #346 final records c6a9311a... reproduced"
fi
echo "== 3. legality and F2 (own exact replay), official PR #266 checkers (h = 20 port), nondegeneracy, bank tiling"
$PY -B $C/f2.py $WD/F | tee $WD/f2.txt; grep -q "'violations': 0, 'first_bad': \[\], 'final_mismatch': 0, 'copies': 20, 'X_not_restored': 0, 'H_not_restored': 0, 'resid_sigma0': 0, 'resid_other': 0" $WD/f2.txt
N=$($PY -c "import json;s=json.load(open('$WD/F/249-states.json'));print(s['n']-2*s['v'])")
$CXX -O2 -std=c++17 -DHDIM=20 -I$C/checkers -I$BI -o $WD/legality $C/checkers/legality_h.cpp
$CXX -O2 -std=c++17 -DHDIM=20 -DVPORTS=960 -DRHELP=$N -I$C/checkers -I$BI -o $WD/columns $C/checkers/columns_h.cpp
$PY -B $C/stage_official.py $WD/parity $WD/F $WD/cin $WD/cout
$WD/legality $WD/cin $WD/cout $WD/legality.json
$WD/columns $WD/cout/COHORT249-RECORDS.bin $WD/columns.json > /dev/null 2> $WD/columns.err
$PY -c "import json;j=json.load(open('$WD/columns.json'));assert j['status']=='PASS_NEW_COHORT249_ALL_FIVE_STAGE_FORMAL_COLUMNS_AND_PREFIX_BILL';print('   official five-stage formal columns PASS:',j['formal_columns_checked'],'columns, prefix payload',j['payload_prefix_bits'],'bits')"
$PY -B $C/nondeg.py $WD/F $WD/parity
$PY -B $C/tile.py $WD/F
echo "== 4. complex supplier: Sussman's E8 unit (gcert1-e8-r783, wht-power-saving-lean 9c94857): gx.check1 + gxcore, exact b"
$PY -B $C/complex_b.py $HERE/complex/gcert1-e8-r783.json.gz $HERE/complex/gx | tee $WD/complex.txt
grep -q "complex b = 876248285600677/1000000000000000000" $WD/complex.txt
echo "== 5. bit coarse saving and PR #315 outer assembly (bit-bound)"
$PY -B $C/price.py $WD/F 876248285600677/1000000000000000000 | tail -2
$PY -c "import json;k=json.load(open('$WD/F/kappa.json'));assert k['kappa']=='201219842699733/250000000000000000' and k['binding']=='bit',k;print('PASS conditional kappa =',k['kappa'],'=',k['kappa_float'])"
