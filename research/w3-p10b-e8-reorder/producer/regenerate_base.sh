#!/bin/bash
# dT.sh DESIGN_JSON|none PLAIN TAG  -> /tmp/dt/TAG/{snap,T,TT} and bit saving
set -e
DES=$1; PL=$2; TAG=$3; W=/tmp/dt/$TAG; rm -rf $W; mkdir -p $W
cp -r /tmp/dt/C/base/pkg325 $W/pkg
P=$W/pkg
if [ "$DES" != none ]; then python3 -c "
import json,sys;p='$P/bitword/producer/data/local_design_p10.json';d=json.load(open(p));d['design']=json.load(open('$DES'));json.dump(d,open(p,'w'))"; fi
IMB_PLAIN=$PL IMB_TRIAL_A=0.00065 IMB_TIER=dim IMB_PARITY=last python3 -B $P/bitword/producer/regenerate.py --work $W/w --solve-matching --emit $W/e > $W/regen.log 2>&1
cp $W/e/selected/* $P/bitword/selected/bit/; cp $W/e/arcs_p10.json $P/bitword/producer/data/arcs_p10.json
cd $W && python3 -B - <<PY > $W/export.log 2>&1
import sys
sys.argv=['x','$P','$W/snap']
sys.path.insert(0,'$P'); import word_pins; word_pins.RECORD={}
exec(open('/tmp/radical/pkg346/w3-p10b-complex-p10/code/export_p10.py').read())
PY
# Design T + twin on this snapshot
B=/tmp/tt/p346; C=$B/code; WD=$W/dt; export W3WORK=$WD/work W3LABELS=$B/data/bit/labels.json PR315=$C/pricing
mkdir -p $W3WORK/eval $W3WORK/agentA/T $W3WORK/snap $WD/T $WD/TT
cp $C/pricing/cost.py $W3WORK/eval/ && cp $C/builders/decomp.py $W3WORK/agentA/ && cp $W/snap/* $W3WORK/snap/
python3 $C/builders/interface.py > $W/iface.log && python3 $C/builders/gather.py > $W/gather.log && python3 $C/builders/build_v5.py $WD/T > $W/build.log
/tmp/tt/build/verifyT $WD/T $WD/T/resid.txt 2> $W/vT1.log && python3 $C/builders/addcomp.py $WD/T && /tmp/tt/build/verifyT $WD/T 2>> $W/vT1.log
python3 $C/builders/twin.py $WD/T $WD/TT > $W/twin.log && /tmp/tt/build/verifyT $WD/TT 2> $W/vTT.log
python3 -c "
import sys;sys.path.insert(0,'$C/pricing');import cost
for d in ('$W/snap','$WD/T','$WD/TT'):
    s,fr,dim,rec=cost.load_snapshot(d);r=cost.evaluate(rec,s,dim,h=20);print(d.split('/')[-1],'saving %.12e'%float(r['saving']))
"; grep legality $W/vTT.log; tail -2 $W/twin.log
