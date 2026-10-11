#!/bin/sh
# run_one.sh TAG P TMOD PMOD QMOD
TAG=$1; P=$2; T=$3; PM=$4; Q=$5
cd /home/claude/cx
rm -rf $TAG
python3 -B make_layer_p.py --set $TAG --p $P --tree /home/claude/cx/tree --tmod $T --pmod $PM --qmod $Q --out /home/claude/cx/$TAG > /home/claude/cx/$TAG.log 2>&1 || { echo FAIL >> /home/claude/cx/$TAG.log; exit 1; }
cd /home/claude/cx/tree && python3 -B research/source-assisted/decision/exact_complex_flow_lift.py --witness /home/claude/cx/$TAG/tree-mw/flow.witness.json --profile /home/claude/cx/$TAG/tree-mw/flow.json --out /home/claude/cx/$TAG/lift.json > /home/claude/cx/$TAG/lift.log 2>&1
cd /home/claude/cx && python3 -B gcert_emit.py --cache $TAG/tree-mw/cache --flow $TAG/tree-mw/flow.json --witness $TAG/tree-mw/flow.witness.json --lift $TAG/lift.certificate.json.gz --out $TAG/gcert1.json --name $TAG > $TAG/emit.log 2>&1
python3 -c "
import json,sys
sys.path.insert(0,'/home/claude/work')
from cprice import price_cert
c=json.load(open('/home/claude/cx/$TAG/gcert1.json')); r=price_cert(c); print('PRICE $TAG R',c['R'],'a %.7e'%r['a'],r)
" >> /home/claude/cx/$TAG.log 2>&1
echo PIPEDONE >> /home/claude/cx/$TAG.log
