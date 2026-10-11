#!/bin/bash
# usage: verify_word.sh WORD.json.gz OUTDIR   -- parent436 steps 2-4 + nine-stage price for a candidate bitE8/1 word
set -euo pipefail
SPD=/private/tmp/claude-501/-Users-mason-yarl/378ef358-ade1-45de-8708-27df77339c28/scratchpad
P=$SPD/s11x/research/e8-r740-replica32/parent436
BIN0=$SPD/xrec_out/base443/parent/bin
WORD=$(cd $(dirname $1) && pwd)/$(basename $1); OUT=$2; mkdir -p $OUT; OUT=$(cd $OUT && pwd)
PY="${PYTHON:-/usr/bin/python3} -B"; CXX=${CXX:-/opt/homebrew/bin/g++-16}
B=$P/code/bit; CK=$B/checkers; C=$P/code
INC="-I$P/portable-include -I$CK -I/opt/homebrew/include"
R=$($PY -c "import gzip,json;print(json.load(gzip.open('$WORD','rt'))['R'])")
echo "== word R=$R"
$PY $B/export_records.py $WORD $OUT/records
$PY $B/independent/checkword.py $WORD $C/pricing | tee $OUT/checkword.txt | tail -4
$PY $B/independent/mutate.py $WORD $C/pricing | tail -3
mkdir -p $OUT/bin
$CXX -O2 -std=c++17 -DHDIM=8 -DNCOPY=9 -DVPORTS=120 -DRHELP=$R $INC -o $OUT/bin/columns_h $CK/columns_h.cpp
$CXX -O2 -std=c++17 -DHDIM=8 -DNCOPY=9 -DVPORTS=120 -DRHELP=$R -DKPAIRS=4 $INC -o $OUT/bin/columns_k4 $CK/columns_k.cpp
$PY $B/regression/stage_cohort.py $OUT/records $OUT/records $OUT/cin $OUT/cout
$BIN0/legality $OUT/cin $OUT/cout $OUT/cout/legality.json > /dev/null
$OUT/bin/columns_h $OUT/cout/COHORT249-RECORDS.bin $OUT/cout/columns.json > /dev/null 2> $OUT/cout/columns.log
$OUT/bin/columns_k4 $OUT/cout/COHORT249-RECORDS.bin $OUT/cout/columns_k4.json > /dev/null 2> $OUT/cout/columns_k4.log
$PY -c "
import json
l=json.load(open('$OUT/cout/legality.json'));c=json.load(open('$OUT/cout/columns.json'));k=json.load(open('$OUT/cout/columns_k4.json'))
assert l['status']=='PASS_INDEPENDENT_COHORT_LEGALITY_SOURCE_OWNERS_AND_LIFECYCLE' and l['copies']==l['erasures']==9
assert c['status']=='PASS_NEW_COHORT249_ALL_FIVE_STAGE_FORMAL_COLUMNS_AND_PREFIX_BILL' and c['formal_columns_checked']==4*120+$R
assert k['status']=='PASS_NEW_COHORT249_ALL_BRIDGED_STAGE_FORMAL_COLUMNS_AND_PREFIX_BILL' and k['formal_columns_checked']==8*120+$R and len(k['stages'])==9
assert k['bridge_additions']==18*120 and len(k['negative_controls'])==18 and all(x['rejected'] for x in k['negative_controls'])
print('official legality + five-stage + B4 formal columns PASS; R',$R)"
$PY $B/mutate_records.py $OUT/records $OUT/cin $OUT/cout $BIN0/legality $OUT/bin/columns_k4 $BIN0/legality_ncopy_h | tail -2
$PY $CK/gram_frames.py $OUT/records --gram e8ham --h 8 --positive | tail -2
mkdir -p $OUT/nine; cp $SPD/xrec_out/base443/parent/nine/GEOMETRY.json $OUT/nine/GEOMETRY.json
$PY $C/nine/global_word_g.py --word $WORD --local-check $OUT --out $OUT/nine | cut -c1-160 | tail -2
$PY $C/nine/audit_g.py --local-check $OUT --out $OUT/nine | cut -c1-160 | tail -2
$PY $C/nine/certify_g.py --pricing $C/pricing --out $OUT/nine --complex-b $P/data/complex-b-nine.json | tail -3
