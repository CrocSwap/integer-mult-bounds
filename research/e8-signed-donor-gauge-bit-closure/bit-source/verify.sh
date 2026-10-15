#!/usr/bin/env bash
# One-command verification of the e8-bit package.
# usage: bash verify.sh /fresh/output/dir     (python3 >= 3.11 with numpy, mpmath, sympy; g++ C++17 with Boost headers;
#                                               optional: ortools for step 7b)
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd); WD=$(mkdir -p "$1" && cd "$1" && pwd)
export PYTHONDONTWRITEBYTECODE=1
C=$HERE/code; B=$C/bit; CK=$B/checkers; D=$HERE/data/bit; R=$HERE/data/regression-p10; PY="python3 -B"
WORD=$D/bitE8-r865.json.gz; REC=$WD/records; BIN=$WD/bin; mkdir -p $BIN $WD/regression
echo "== 0. package manifest"; (cd $HERE && sha256sum -c MANIFEST.sha256 --quiet) && echo "   all files match MANIFEST.sha256"

echo "== 1. the word: regenerate from the producer parameters; export the PR249 records"
(cd $B/producer && E8COORD=ham $PY fullword.py params-r865.json $WD/regenerated.json.gz)
$PY -c "import gzip,json,sys;a=json.load(gzip.open('$WD/regenerated.json.gz','rt'));b=json.load(gzip.open('$WORD','rt'));assert a==b;print('   regenerated word equals the shipped word')"
$PY $B/export_records.py $WORD $REC
(cd $REC && sha256sum -c $D/RECORD-SHA256SUMS --quiet) && echo "   exported records/states/frames match RECORD-SHA256SUMS"

echo "== 2. independent all-column checker (no shared code with the producer) and its negative controls"
$PY $B/independent/checkword.py $WORD $C/pricing | tee $WD/checkword.txt
$PY $B/independent/mutate.py $WORD $C/pricing

echo "== 3. official PR #266 cohort checkers, generalized: h = 8 frames, NCOPY = 9 copied centres"
g++ -O2 -std=c++17 -DHDIM=8 -DNCOPY=9 -I$CK -o $BIN/legality $CK/legality_h.cpp
g++ -O2 -std=c++17 -DHDIM=8 -I$CK -o $BIN/legality_ncopy_h $CK/legality_h.cpp
g++ -O2 -std=c++17 -DHDIM=8 -DNCOPY=9 -DVPORTS=120 -DRHELP=865 -I$CK -o $BIN/columns $CK/columns_h.cpp
$PY $B/regression/stage_cohort.py $REC $REC $WD/cin $WD/cout
$BIN/legality $WD/cin $WD/cout $WD/cout/legality.json
$BIN/columns $WD/cout/COHORT249-RECORDS.bin $WD/cout/columns.json > /dev/null 2>$WD/cout/columns.log && echo "   five-stage formal columns PASS ($(python3 -c "import json;d=json.load(open('$WD/cout/columns.json'));print(d['status'],d['formal_columns_checked'],'columns')"))"
$PY $B/mutate_records.py $REC $WD/cin $WD/cout $BIN/legality $BIN/columns $BIN/legality_ncopy_h
echo "   regression: unmodified PR #346/#352 sources vs generalized sources (no -DNCOPY), h = 20, on the PR #325 p10b word"
mkdir -p $WD/regression/base && for f in RECORDS:249-records.bin states:249-states.json frames:frames.json; do gunzip -c $R/BASE-${f%%:*}.*gz > $WD/regression/base/${f##*:}; done
g++ -O2 -std=c++17 -DHDIM=20 -I$C/bit/regression -o $BIN/leg_orig $C/bit/regression/legality_h_pr346.cpp
g++ -O2 -std=c++17 -DHDIM=20 -I$CK -o $BIN/leg_gen $CK/legality_h.cpp
g++ -O2 -std=c++17 -DHDIM=20 -DVPORTS=960 -DRHELP=8100 -I$C/bit/regression -o $BIN/col_orig $C/bit/regression/columns_h_pr346.cpp
g++ -O2 -std=c++17 -DHDIM=20 -DVPORTS=960 -DRHELP=8100 -I$CK -o $BIN/col_gen $CK/columns_h.cpp
$PY $B/regression/stage_cohort.py $WD/regression/base $WD/regression/base $WD/regression/cin $WD/regression/cout
$BIN/leg_orig $WD/regression/cin $WD/regression/cout $WD/regression/leg_o.json > /dev/null
$BIN/leg_gen $WD/regression/cin $WD/regression/cout $WD/regression/leg_g.json > /dev/null
cmp $WD/regression/leg_o.json $WD/regression/leg_g.json && echo "   legality receipts byte-identical"
$BIN/col_orig $WD/regression/cout/COHORT249-RECORDS.bin $WD/regression/col_o.json > /dev/null 2>&1
$BIN/col_gen $WD/regression/cout/COHORT249-RECORDS.bin $WD/regression/col_g.json > /dev/null 2>&1
$PY -c "
import json;a=json.load(open('$WD/regression/col_o.json'));b=json.load(open('$WD/regression/col_g.json'))
for d in (a,b): d.pop('seconds')
assert a==b and a['status'].startswith('PASS');print('   five-stage columns receipts identical (except wall-clock seconds)')"

echo "== 4. exact nondegeneracy (E8 Gram) and prime witnesses on every frame"
$PY $CK/gram_frames.py $REC --gram e8ham --h 8 --positive
echo "   regression (G = I - J/9, h = 20, PR #325 p10b word): the original prime_new.py and the generalized check"
mkdir -p $WD/regression/empty && echo '{"frames":{}}' > $WD/regression/empty/frames.json
$PY $C/bit/regression/prime_new.py $WD/regression/empty $WD/regression/base | tee $WD/regression/prime_o.txt
$PY $CK/gram_frames.py $WD/regression/base --gram triple9 --h 20 | tee $WD/regression/prime_g.txt
$PY -c "
import re;a=open('$WD/regression/prime_o.txt').read();b=open('$WD/regression/prime_g.txt').read()
na=re.search(r'for (\d+) new frames; max determinant bits (\d+) ; primes (\[.*?\])',a).groups();nb=re.search(r'(\d+) frames checked.*bits (\d+); primes (\[.*?\])',b).groups()
assert na==nb,(na,nb);print('   same frame count, determinant bits and primes:',na)"

echo "== 5. PR234 five-stage geometry for the E8 labels (W(E8) reflection words as port isometries)"
$PY $CK/geometry_g.py e8 $WORD
$PY $CK/geometry_g.py regression

echo "== 6. banks: exact width-40 tiling of the helper residuals"
$PY $CK/tile_g.py $REC 8 1
$PY $C/bit/regression/tile_check.py $WD/regression/base > $WD/regression/tile_o.txt; $PY $CK/tile_g.py $WD/regression/base > $WD/regression/tile_g.txt
cmp $WD/regression/tile_o.txt $WD/regression/tile_g.txt && echo "   regression: generalized tiling output byte-identical to PR #346's tile_check on the p10b word"

echo "== 7. copied centres: 9 retained totals at h = 8 (admitted; charged as NCOPY = 9 everywhere)"
$PY -c "
import gzip,json,struct;w=json.load(gzip.open('$WORD','rt'));rec=open('$REC/249-records.bin','rb').read()
cp=[struct.unpack_from('<6i',rec,24*i) for i in range(len(rec)//24) if struct.unpack_from('<6i',rec,24*i)[0]==2]
assert len(cp)==len(w['ret'])==9 and all(e[5]==8 for e in cp) and [e[1] for e in cp]==w['ret']
print('   retained totals',len(w['ret']),'> h =',w['h'],'; COPY ranks',sorted({e[5] for e in cp}),'(full frame); copy loss L = 72, deficit 4v - 5L = 120')"
if python3 -c "import ortools" 2>/dev/null; then echo "   7b. CP-SAT: no F2 decoder with 8 centres; 9 suffice"; $PY $B/independent/centres_sat.py 8 120; $PY $B/independent/centres_sat.py 9 120; else echo "   7b. skipped (ortools not installed)"; fi

echo "== 8. complex supplier: Jacob Sussman's E8 unit, PR #352's checks unchanged"
CX_RECEIPT=$WD/complex-guard-e8.json $PY $C/complex/certify_complex.py

echo "== 9. bit coarse saving and outer assembly (47 constraints), PR #315 engines, h = 8, T = 1"
$PY $CK/certify_bit_g.py $REC 876248285600677/1000000000000000000 8 1 $WD/kappa.json
echo "   regression: generalized vs original certify_bit on the PR #325 p10b word (h = 20, T = 12)"
cp -r $WD/regression/base $WD/regression/base_o
PR315=$C/pricing $PY $C/bit/regression/certify_bit.py $WD/regression/base_o 876248285600677/1000000000000000000 > /dev/null
$PY $CK/certify_bit_g.py $WD/regression/base 876248285600677/1000000000000000000 20 12 $WD/regression/kappa_g.json > /dev/null
$PY -c "
import json;a=json.load(open('$WD/regression/base_o/kappa.json'));b=json.load(open('$WD/regression/kappa_g.json'))
assert all(a[k]==b[k] for k in a if k!='word');print('   identical kappa receipt fields; p10b kappa',a['kappa'])"

echo "== 10. finite bill at m = 40"
$PY $B/receipts_e8.py $WORD $REC $WD/cout/legality.json $WD/cout/columns.json $WD/kappa.json $WD/finite-input.json
$PY $CK/finite_g.py e8 $WD/finite-input.json $WD/finite.json
mkdir -p $WD/regression/loans && for f in raw scalar banks math finite global_result; do gunzip -c $R/receipts-loans/$f.json.gz > $WD/regression/loans/$f.json; done
$PY $CK/finite_g.py regression $WD/regression/loans

echo "== 11. SECONDARY (conditional on PR #363): kappa under the seven-stage complex value; the bit word in B_3"
$PY $C/secondary/seven_stage.py $WD/kappa.json | tee $WD/seven-stage.txt

$PY -c "
import json;k=json.load(open('$WD/kappa.json'))
assert k['kappa']=='875481145306751/1000000000000000000' and k['binding']=='complex' and k['bit_coarse']=='452036410121261/500000000000000000',k
from fractions import Fraction as F
print('PASS conditional kappa =',k['kappa'],'=',k['kappa_float'],'(complex-bound; bit coarse',k['bit_coarse'],'=',float(F(k['bit_coarse'])),')')"
