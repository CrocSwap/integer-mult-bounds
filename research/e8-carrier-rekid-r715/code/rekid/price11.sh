#!/bin/bash
# usage: price11.sh WORD.json.gz|json NAME [mix]  -- eleven-stage cross-copy hosted bit price of a (plain) bitE8/1 word, as in e8-eleven-stage-cross-copy/verify.py
set -euo pipefail
SPD=/private/tmp/claude-501/-Users-mason-yarl/378ef358-ade1-45de-8708-27df77339c28/scratchpad
F2=$SPD/brain/f2cancel
P443=$SPD/s11x/research/e8-r740-replica32; P=$P443/parent436; PK=$SPD/s11x/research/e8-eleven-stage-cross-copy; CODE=$PK/code
BIN0=$SPD/xrec_out/base443/parent/bin; UP=$SPD/xrec_out/upstream448
WORD=$(cd $(dirname $1) && pwd)/$(basename $1); ORIG=$WORD; NAME=$2; MIX=${3:-nomix}
OUT=$F2/p11/$NAME; mkdir -p $OUT; 
PY="/usr/bin/python3 -B"; CXX=/opt/homebrew/bin/g++-16
B=$P/code/bit; CK=$B/checkers; INC="-I$P/portable-include -I$CK -I/opt/homebrew/include"
R=$($PY -c "import gzip,json;print(json.load(gzip.open('$WORD','rt'))['R'])")
if [ "$MIX" = mix ]; then
  $PY /private/tmp/claude-501/-Users-mason-yarl/378ef358-ade1-45de-8708-27df77339c28/scratchpad/brain/f2cancel/code/mix_target_nochain.py $WORD $OUT/word-mixed.json
  WORD=$OUT/word-mixed.json
fi
echo "== $NAME word R=$R mix=$MIX"
$PY $B/export_records.py $WORD $OUT/records > /dev/null
$PY $B/regression/stage_cohort.py $OUT/records $OUT/records $OUT/cin $OUT/cout > /dev/null
$BIN0/legality $OUT/cin $OUT/cout $OUT/cout/legality.json > /dev/null
mkdir -p $OUT/bin
$CXX -O2 -std=c++17 -DHDIM=8 -DNCOPY=9 -DVPORTS=120 -DRHELP=$R $INC -o $OUT/bin/columns_h $CK/columns_h.cpp
$CXX -O2 -std=c++17 -DHDIM=8 -DNCOPY=9 -DVPORTS=120 -DRHELP=$R -DKPAIRS=5 $INC -o $OUT/bin/columns_k5 $CK/columns_k.cpp
$OUT/bin/columns_h $OUT/cout/COHORT249-RECORDS.bin $OUT/cout/columns.json > /dev/null 2> $OUT/cout/columns.log
$OUT/bin/columns_k5 $OUT/cout/COHORT249-RECORDS.bin $OUT/cout/columns_k5.json > /dev/null 2> $OUT/cout/columns_k5.log
$PY -c "
import json
l=json.load(open('$OUT/cout/legality.json'));c=json.load(open('$OUT/cout/columns.json'));k=json.load(open('$OUT/cout/columns_k5.json'))
assert l['status']=='PASS_INDEPENDENT_COHORT_LEGALITY_SOURCE_OWNERS_AND_LIFECYCLE' and l['copies']==l['erasures']==9
assert c['status']=='PASS_NEW_COHORT249_ALL_FIVE_STAGE_FORMAL_COLUMNS_AND_PREFIX_BILL' and c['formal_columns_checked']==4*120+$R
assert k['status']=='PASS_NEW_COHORT249_ALL_BRIDGED_STAGE_FORMAL_COLUMNS_AND_PREFIX_BILL' and k['formal_columns_checked']==10*120+$R
assert k['bridge_additions']==24*120 and len(k['stages'])==11 and len(k['negative_controls'])==24 and all(x['rejected'] for x in k['negative_controls'])
print('  local legality + 5-stage + K=5 (11-stage) formal columns PASS')"
if [ "$MIX" = mix ]; then $PY $CODE/mix_check.py $WORD $OUT/records --controls $ORIG > $OUT/mix-check.json; $PY -c "
import json;m=json.load(open('$OUT/mix-check.json'));print('  mix-check',m['status'],len(m['mutation_controls']),'controls rejected' if set(m['mutation_controls'].values())=={'REJECTED'} else 'CONTROL FAILURE')"
else $PY $B/independent/checkword.py $WORD $P/code/pricing | grep -E "PASS|saving" | head -3 || true; fi
$PY $CK/gram_frames.py $OUT/records --gram e8ham --h 8 --positive | tail -1 | cut -c1-120
# eleven-stage
GEO=$F2/p11/geo11; if [ ! -f $GEO/nine/GEOMETRY.json ]; then mkdir -p $GEO/nine; $PY $CODE/geometry_k.py --source $P --out $GEO/nine --stages 11 --no-timing > /dev/null; fi
V=$OUT/eleven; mkdir -p $V/nine; cp $GEO/nine/GEOMETRY.json $V/nine/; [ -e $V/records ] || ln -s $OUT/records $V/records
# isometries for a plain word: helpers all start at frame 0 -> the frame-0 entry only
$PY -c "
import json;i=json.load(open('$P443/data/residual-isometries.json'));print(len(i),'entries in #443 file');json.dump([e for e in i if e['frame']==0 or e['entrance_rank']==0][:1],open('$OUT/iso0.json','w'))"
$PY $CODE/global_k.py --word $WORD --local-check $OUT --out $V/nine --isometries $OUT/iso0.json --stages 11 --replicas 1 --no-banks | cut -c1-200 | tail -1
$PY /private/tmp/claude-501/-Users-mason-yarl/378ef358-ade1-45de-8708-27df77339c28/scratchpad/brain/f2cancel/code/audit_parent_k_plain.py --local-check $OUT --out $V/nine --word $WORD | cut -c1-200 | tail -1
rm -rf $V/hosted
$PY $CODE/emit_tape_k.py $V/nine $OUT $V/hosted --selection $OUT/sel.json --key bit11_tape --discover --host-all --depth 3 --redigest --version-tag e8-eleven-stage-idle-hosting-cross-copy-v1 | cut -c1-200 | tail -1
$PY $CODE/audit_tape_k.py $V $V/hosted $V/hosted/AUDIT.json | cut -c1-200 | tail -1
$PY $CODE/assemble_k.py $V $UP $V/hosted $V/hosted/AUDIT.json $V/RESULT.json --route-extra 3 --parent-kappa 1330733966732373/1000000000000000000 --label '#448' | cut -c1-300 | tail -3
$PY -c "
import json;r=json.load(open('$V/RESULT.json'));print('RESULT',r['kappa_decimal'],'binding',r['binding_component'],'bit_lower',r['bit_lower'],'live',r['bit']['live'],'maxchild',r['bit']['maxchild'])"
