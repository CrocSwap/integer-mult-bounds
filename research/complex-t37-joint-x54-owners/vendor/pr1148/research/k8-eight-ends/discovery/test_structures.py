import os
import sys,json,gzip,copy,importlib.util,time
from pathlib import Path
from fractions import Fraction as F
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('M',HERE/'frame_model.py');M=importlib.util.module_from_spec(spec);spec.loader.exec_module(M)
w=json.loads(gzip.decompress(Path(os.environ['K8_BASE_WORD']).read_bytes()))
results=[]
for r in json.loads((HERE/'SOURCE-CENSUS.json').read_text())['candidates']:
 nw=copy.deepcopy(w);q=F(r['coefficient']);nw['B'][r['B']]=['add',r['target'],r['source'],q.numerator,q.denominator,r['frame']]
 t=time.monotonic()
 try:
  m=M.Model(nw,relax_given=True);out=dict(status='FRAME_FEASIBLE',free=len(m.domain),profile=m.profile(m.baseline()))
 except AssertionError as e:out=dict(status='FRAME_INFEASIBLE',reason=str(e))
 r.update(out,seconds=time.monotonic()-t);results.append(r);print(json.dumps(r),flush=True)
(HERE/'SOURCE-REFRAME.json').write_text(json.dumps(results,indent=2)+'\n')
