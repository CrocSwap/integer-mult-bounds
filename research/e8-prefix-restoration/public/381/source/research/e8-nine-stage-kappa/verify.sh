#!/usr/bin/env bash
# One-command verification of the e8-nine-stage-kappa package: PR #370's E8 bit word in the nine-stage bridged word B_4
# (idle climbs unsplit, halving degree two) and PR #377's compressed nine-stage E8 complex component.
# usage: bash verify.sh /fresh/output/dir   (python3 >= 3.11 with numpy, mpmath, sympy; g++ C++17 with Boost headers)
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd); WD=$(mkdir -p "$1" && cd "$1" && pwd)
export PYTHONDONTWRITEBYTECODE=1
C=$HERE/code; B=$C/bit; CK=$B/checkers; D=$HERE/data/bit; R=$HERE/data/regression-p10; PY="python3 -B"
WORD=$D/bitE8-r865.json.gz; REC=$WD/records; BIN=$WD/bin; mkdir -p $BIN $WD/regression $WD/k2 $WD/k4
B2=876248285600677/1000000000000000000; B377=999240641319551/1000000000000000000
echo "== 0. package manifest; provenance from PR #370, PR #373, PR #375 and PR #377"
(cd $HERE && sha256sum -c MANIFEST.sha256 --quiet) && echo "   all files match MANIFEST.sha256"
$PY $C/provenance.py

echo "== 1. the word (PR #370): regenerate from the producer parameters; export the PR249 records"
(cd $B/producer && E8COORD=ham $PY fullword.py params-r865.json $WD/regenerated.json.gz)
$PY -c "import gzip,json;a=json.load(gzip.open('$WD/regenerated.json.gz','rt'));b=json.load(gzip.open('$WORD','rt'));assert a==b;print('   regenerated word equals the shipped word')"
$PY $B/export_records.py $WORD $REC
(cd $REC && sha256sum -c $D/RECORD-SHA256SUMS --quiet) && echo "   exported records/states/frames match RECORD-SHA256SUMS"

echo "== 2. independent all-column checker of one invocation (PR #370) and its negative controls"
$PY $B/independent/checkword.py $WORD $C/pricing | tee $WD/checkword.txt
$PY $B/independent/mutate.py $WORD $C/pricing

echo "== 3. legality of one invocation (PR #266/#370) and the all-column formal check of the whole bridged word B_4"
g++ -O2 -std=c++17 -DHDIM=8 -DNCOPY=9 -I$CK -o $BIN/legality $CK/legality_h.cpp
g++ -O2 -std=c++17 -DHDIM=8 -I$CK -o $BIN/legality_ncopy_h $CK/legality_h.cpp
g++ -O2 -std=c++17 -DHDIM=8 -DNCOPY=9 -DVPORTS=120 -DRHELP=865 -I$CK -o $BIN/columns_h $CK/columns_h.cpp
for K in 2 4; do g++ -O2 -std=c++17 -DHDIM=8 -DNCOPY=9 -DVPORTS=120 -DRHELP=865 -DKPAIRS=$K -I$CK -o $BIN/columns_k$K $CK/columns_k.cpp; done
$PY $B/regression/stage_cohort.py $REC $REC $WD/cin $WD/cout
$BIN/legality $WD/cin $WD/cout $WD/cout/legality.json
$BIN/columns_h $WD/cout/COHORT249-RECORDS.bin $WD/k2/columns_h.json > /dev/null 2>$WD/k2/columns_h.log
$BIN/columns_k2 $WD/cout/COHORT249-RECORDS.bin $WD/k2/columns.json > /dev/null 2>$WD/k2/columns.log
$BIN/columns_k4 $WD/cout/COHORT249-RECORDS.bin $WD/k4/columns.json > /dev/null 2>$WD/k4/columns.log
$PY -c "
import json;a=json.load(open('$WD/k2/columns_h.json'));b=json.load(open('$WD/k2/columns.json'));c=json.load(open('$WD/k4/columns.json'))
for d in (a,b): d.pop('seconds')
assert a==b,'K = 2 must reproduce PR #370 columns_h';print('   regression: columns_k at K = 2 gives PR #370 columns_h receipt (except wall-clock seconds):',a['status'])
assert c['status']=='PASS_NEW_COHORT249_ALL_BRIDGED_STAGE_FORMAL_COLUMNS_AND_PREFIX_BILL' and c['formal_columns_checked']==c['global_live_registers']==8*120+865
assert len(c['stages'])==9 and [s['signed_inverse'] for s in c['stages']]==[False,True,False,True,False,True,False,True,False] and c['bridge_additions']==18*120 and c['fresh_center_copies']==81
assert len(c['negative_controls'])==18 and all(x['rejected'] for x in c['negative_controls'])
print('   B_4 formal columns PASS: all %d physical columns over F2 (dirty helpers) through 9 invocations, 18 twin bridges, terminal exchange; 18 omitted-bridge controls rejected'%c['formal_columns_checked'])"
$PY $B/mutate_records.py $REC $WD/cin $WD/cout $BIN/legality $BIN/columns_k4 $BIN/legality_ncopy_h
echo "   regression (PR #370): unmodified PR #346/#352 sources vs generalized sources (no -DNCOPY), h = 20, on the PR #325 p10b word"
mkdir -p $WD/regression/base && for f in RECORDS:249-records.bin states:249-states.json frames:frames.json; do gunzip -c $R/BASE-${f%%:*}.*gz > $WD/regression/base/${f##*:}; done
g++ -O2 -std=c++17 -DHDIM=20 -I$C/bit/regression -o $BIN/leg_orig $C/bit/regression/legality_h_pr346.cpp
g++ -O2 -std=c++17 -DHDIM=20 -I$CK -o $BIN/leg_gen $CK/legality_h.cpp
g++ -O2 -std=c++17 -DHDIM=20 -DVPORTS=960 -DRHELP=8100 -I$C/bit/regression -o $BIN/col_orig $C/bit/regression/columns_h_pr346.cpp
g++ -O2 -std=c++17 -DHDIM=20 -DVPORTS=960 -DRHELP=8100 -I$CK -o $BIN/col_gen $CK/columns_k.cpp
$PY $B/regression/stage_cohort.py $WD/regression/base $WD/regression/base $WD/regression/cin $WD/regression/cout
$BIN/leg_orig $WD/regression/cin $WD/regression/cout $WD/regression/leg_o.json > /dev/null
$BIN/leg_gen $WD/regression/cin $WD/regression/cout $WD/regression/leg_g.json > /dev/null
cmp $WD/regression/leg_o.json $WD/regression/leg_g.json && echo "   legality receipts byte-identical"
$BIN/col_orig $WD/regression/cout/COHORT249-RECORDS.bin $WD/regression/col_o.json > /dev/null 2>&1
$BIN/col_gen $WD/regression/cout/COHORT249-RECORDS.bin $WD/regression/col_g.json > /dev/null 2>&1
$PY -c "
import json;a=json.load(open('$WD/regression/col_o.json'));b=json.load(open('$WD/regression/col_g.json'))
for d in (a,b): d.pop('seconds')
assert a==b and a['status'].startswith('PASS');print('   five-stage columns receipts identical, PR #346 original vs columns_k (K = 2, no -DNCOPY), except wall-clock seconds')"

echo "== 4. exact nondegeneracy (E8 Gram) and prime witnesses on every frame of the invocation (PR #370)"
$PY $CK/gram_frames.py $REC --gram e8ham --h 8 --positive

echo "== 5. PR234 route and idle geometry for the E8 labels: five stages (PR #370 regression) and B_4 unsplit"
$PY $CK/geometry_g.py e8 $WORD | tail -1
$PY $CK/geometry_k.py 2 $WORD | tail -1
$PY $CK/geometry_k.py 4 $WORD unsplit | tail -2

echo "== 6. banks: exact zero-padding tiling of the helper residuals, width 40 (PR #370 regression) and width 72 (B_4, 9 replicas)"
$PY $CK/tile_g.py $REC 8 1 > $WD/k2/tile_g.txt; $PY $CK/tile_k.py $REC 2 8 1 > $WD/k2/tile_k.txt
cmp $WD/k2/tile_g.txt $WD/k2/tile_k.txt && echo "   regression: tile_k at K = 2 byte-identical to PR #370 tile_g"
$PY $CK/tile_k.py $REC 4 8 9 | tee $WD/k4/tile.txt

echo "== 7. copied centres: 9 retained totals at h = 8 (PR #370's admission; charged as NCOPY = 9 per invocation everywhere)"
$PY -c "
import gzip,json,struct;w=json.load(gzip.open('$WORD','rt'));rec=open('$REC/249-records.bin','rb').read()
cp=[struct.unpack_from('<6i',rec,24*i) for i in range(len(rec)//24) if struct.unpack_from('<6i',rec,24*i)[0]==2]
assert len(cp)==len(w['ret'])==9 and all(e[5]==8 for e in cp) and [e[1] for e in cp]==w['ret']
print('   retained totals',len(w['ret']),'at the full frame; copy loss L = 72 per invocation; B_4 deficit 8v - 9L = 312')"

echo "== 8. complex supplier: PR #377's compressed nine-stage E8 component, its own verifier unchanged"
(cd $HERE/complex377 && $PY verify.py --work $WD/complex377) | tail -2
$PY -c "
import json;r=json.load(open('$WD/complex377/VERIFICATION.json'))
assert r['status']=='PASS_PORTABLE_NINE_STAGE_COMPLEX_FINITE_COMPONENT' and r['complex_coarse']=='$B377',r['status']
print('   PR #377 complex coarse saving b =',r['complex_coarse'],'(two moment engines, adjacent grid point rejected, halving degree two)')"

echo "== 9. bit coarse saving and outer assembly (47 constraints), PR #315 engines, h = 8"
$PY $CK/certify_bit_g.py $REC $B2 8 1 $WD/k2/kappa_g.json > /dev/null
$PY $CK/certify_bit_k.py $REC $B2 2 8 1 $WD/k2/kappa.json > /dev/null
$PY -c "
import json;a=json.load(open('$WD/k2/kappa_g.json'));b=json.load(open('$WD/k2/kappa.json'))
assert all(a[k]==b[k] for k in a if k!='word') and a['kappa']=='875481145306751/1000000000000000000'
print('   regression: certify_bit_k at K = 2 gives PR #370 receipt fields; five-stage kappa',a['kappa'])"
$PY $CK/certify_bit_k.py $REC $B377 4 8 9 $WD/kappa.json unsplit
echo "   regression (PR #370): generalized vs original certify_bit on the PR #325 p10b word (h = 20, T = 12)"
cp -r $WD/regression/base $WD/regression/base_o
PR315=$C/pricing $PY $C/bit/regression/certify_bit.py $WD/regression/base_o $B2 > /dev/null
$PY $CK/certify_bit_g.py $WD/regression/base $B2 20 12 $WD/regression/kappa_g.json > /dev/null
$PY -c "
import json;a=json.load(open('$WD/regression/base_o/kappa.json'));b=json.load(open('$WD/regression/kappa_g.json'))
assert all(a[k]==b[k] for k in a if k!='word');print('   identical kappa receipt fields; p10b kappa',a['kappa'])"

echo "== 10. finite bill: m = 40 (PR #370 regression) and m = 72 (B_4, T = 9, halving degree two)"
$PY $B/receipts_e8.py $WORD $REC $WD/cout/legality.json $WD/k2/columns_h.json $WD/k2/kappa_g.json $WD/k2/finite-input-g.json > /dev/null
$PY $CK/finite_g.py e8 $WD/k2/finite-input-g.json $WD/k2/finite_g.json > /dev/null
$PY $B/receipts_k.py $WORD $REC $WD/cout/legality.json $WD/k2/columns.json $WD/k2/kappa.json $WD/k2/finite-input.json > /dev/null
$PY $CK/finite_k.py e8 $WD/k2/finite-input.json $WD/k2/finite.json > /dev/null
cmp $WD/k2/finite_g.json $WD/k2/finite.json && echo "   regression: receipts_k + finite_k at K = 2 give PR #370's finite bill byte for byte"
$PY $B/receipts_k.py $WORD $REC $WD/cout/legality.json $WD/k4/columns.json $WD/kappa.json $WD/finite-input.json
$PY $CK/finite_k.py e8 $WD/finite-input.json $WD/finite.json
$PY -c "import json;d=json.load(open('$WD/finite.json'));r=d['row_reserve'];assert r['halving_degree']==2 and r['internal_coefficient']==2*(72*72+1);print('   internal row reserve',r)"
mkdir -p $WD/regression/loans && for f in raw scalar banks math finite global_result; do gunzip -c $R/receipts-loans/$f.json.gz > $WD/regression/loans/$f.json; done
$PY $CK/finite_k.py regression $WD/regression/loans

$PY -c "
import json;k=json.load(open('$WD/kappa.json'))
assert k['K']==4 and k['stages']==9 and k['m']==72 and k['T']==9 and k['W']==9*(8*120+865) and k['maxchild']==50 and k['halving_degree']==2
assert k['bit_coarse']=='249162322049641/250000000000000000' and k['complex_coarse']=='$B377'
assert k['kappa']=='995656966441037/1000000000000000000' and k['binding']=='bit',k
from fractions import Fraction as F
print('PASS conditional kappa =',k['kappa'],'=',k['kappa_float'],'(bit-bound: E8 bit word in B_4 at halving degree two, c =',k['bit_coarse'],'=',float(F(k['bit_coarse'])),'; PR #377 complex b =',float(F(k['complex_coarse'])),'); above 2^-10 =',2**-10)"
