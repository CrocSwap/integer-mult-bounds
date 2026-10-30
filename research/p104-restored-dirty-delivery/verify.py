"""Read-only portable exact local replay; no full supplier claim."""
from pathlib import Path
import importlib.util,json,hashlib
P=Path(__file__).resolve().parent
def require(c,msg):
 if not c:raise ValueError(msg)
def load(name,file):
 s=importlib.util.spec_from_file_location(name,P/file);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
pins=json.loads((P/'UPSTREAM.json').read_text())
for path,row in pins['inputs'].items():
 require(hashlib.sha256((P/'source'/path).read_bytes()).hexdigest()==row['sha256'],'source changed: '+path)
producer=load('dirty_producer','dirty_delivery.py')
w=producer.build();require(json.loads(json.dumps(w))==json.loads((P/'DIRTY-WITNESS.json').read_text()),'witness mismatch')
r=producer.run();require(json.loads(json.dumps(r))==json.loads((P/'DIRTY-RESULT.json').read_text()),'receipt mismatch')
ind=load('free_charts','operator_verify.py');ind.main()
print('PASS_P104_RESTORED_DIRTY_DELIVERY columns=144 carriers=32 width=9 COPY=56 controls=9 no_new_kappa')

# Full low-rank channel extension; inputs remain independently hash-pinned above.
low=load('lowrank_producer','lowrank.py')
final={r:(low.g['target_frames'][int(r[1:])] if r.startswith('Y') else low.full) for r in low.start}
lw=dict(initial_frames=low.start,final_frames=final,program=low.program)
require(json.loads(json.dumps(lw,default=str))==json.loads((P/'LOWRANK-WITNESS.json').read_text()),'low-rank witness differs')
lr=low.audit(low.program);stored=json.loads((P/'LOWRANK-RESULT.json').read_text())
for key,value in lr.items():require(json.loads(json.dumps(value))==stored[key],'low-rank invoice differs: '+key)
from copy import deepcopy
for name,index in [('missing_initial_query_compensation',0),('missing_final_query_cleanup',len(low.program)-1)]:
 mutant=deepcopy(low.program);mutant.pop(index)
 try:low.audit(mutant)
 except ValueError as exc:require(str(exc)==stored['controls'][name],'control mismatch')
 else:raise ValueError('accepted bad low-rank control')
li=load('lowrank_free_charts','lowrank_independent.py');li.main()
print('PASS_P104_LOW_RANK_CHANNEL columns=280 helpers=72 COPY=56 controls=3 no_new_kappa')
