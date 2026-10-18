import json,gzip,copy,importlib.util,time
from pathlib import Path
from fractions import Fraction as F
P=Path(__file__).resolve().parent;ROOT=P.parents[2];s=importlib.util.spec_from_file_location('M',ROOT/'research/k8-eight-ends/discovery/frame_model.py');M=importlib.util.module_from_spec(s);s.loader.exec_module(M);w=json.loads(gzip.decompress((ROOT/'research/k8-eight-ends/FULL-WORD.json.gz').read_bytes()));results=[]
for i,r in enumerate(json.loads((P/'HELPER-ALIASES.json').read_text())['candidates']):
 nw=copy.deepcopy(w);q=F(r['coefficient']);nw['B'][r['B']]=['add',r['target'],r['source'],q.numerator,q.denominator,r['frame']]
 try:
  m=M.Model(nw,relax_given=True);out=dict(status='FRAME_FEASIBLE',free=len(m.domain),profile=m.profile(m.baseline()));(P/f'alias-{i}.json.gz').write_bytes(gzip.compress(json.dumps(nw).encode()))
 except AssertionError as e:out=dict(status='FRAME_INFEASIBLE',reason=str(e))
 r.update(out);results.append(r)
 if i%10==0 or out['status']=='FRAME_FEASIBLE':print(i,out,flush=True)
(P/'ALIASES-REFRAMED.json').write_text(json.dumps(results,indent=2)+'\n');print('feasible',sum(r['status']=='FRAME_FEASIBLE' for r in results),'of',len(results),flush=True)
