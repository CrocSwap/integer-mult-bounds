#!/bin/bash
# comp.sh TTDIR OUT [SEEDS] : #359's post-Design-T kernel/retime/reorder discovery + application on a Design T word
set -e
TT=$(readlink -f $1); O=$2; SEEDS=${3:-5}; mkdir -p $O; cd $O
D=/tmp/p359/w3-design-t-staged-p10b/discovery; C=/tmp/p329/five-stage-p10b-transcript-stages/discovery; X=/tmp/c359/code359
LAB=/tmp/p359/w3-design-t-staged-p10b/data/labels.json
python3 -B $D/census249.py $TT H.pkl > census.log 2>&1; tail -n1 census.log
python3 -B $C/coll/lines.py H.pkl L.pkl 5 > lines.log 2>&1; python3 -B $C/coll/planes.py H.pkl P.pkl 15 > planes.log 2>&1
best=""; bphi=0
for s in $SEEDS; do ORDERS=4 NT=3 NOISE=0.5 SEED=$s python3 -B $C/coll/closure_pack.py H.pkl L.pkl P.pkl K_$s.json > cl_$s.log 2>&1; python3 -B $C/coll/trim5.py H.pkl K_$s.json K5_$s.json > tr_$s.log 2>&1; tail -n1 tr_$s.log; done
python3 - $TT "$SEEDS" <<'PY'
import json,sys,hashlib,re,glob
sys.path.insert(0,'/tmp/c359/code359'); import stagelib as L
tt=sys.argv[1]; seeds=sys.argv[2].split()
best=None
for s in seeds:
    t=open('tr_%s.log'%s).read(); m=re.findall(r'phi (-?[0-9.]+)',t)
    ph=float(m[-1]); 
    if best is None or ph<best[0]: best=(ph,s)
K=json.load(open('K5_%s.json'%best[1])); ents=K if isinstance(K,list) else K.get('entries',K)
sel=dict(stage='kernel',name='kernel',provenance='shared-donor closure on the Design T word (seed %s)'%best[1],input_records_sha256=L.rec_sha(L.load_snapshot(tt)),output_records_sha256=None,count=len(ents),entries=[{k:e[k] for k in ('pivot','donors','basis')} for e in ents])
json.dump(sel,open('kernel-selection.json','w'),indent=1); print('kernel seed',best)
PY
python3 -B $X/stages.py kernel $TT K kernel-selection.json $LAB | tail -n1
