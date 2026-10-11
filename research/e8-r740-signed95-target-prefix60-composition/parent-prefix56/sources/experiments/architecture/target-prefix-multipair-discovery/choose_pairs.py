from pathlib import Path
import json,math
import numpy as np
from scipy.optimize import milp,Bounds,LinearConstraint
P=Path(__file__).resolve().parent;R=P.parents[2];rows=[e for e in json.loads((P/'SINGLES.json').read_text())['candidates']if e['passed']];old=json.loads((R/'experiments/stage-search/pr445-signed95-eleven/LOCAL-SUMMARY.json').read_text())['local_profile'];old={int(k):v for k,v in old.items()};a=.00125
scores=[]
for e in rows:
 H={int(k):v for k,v in e['profile'].items()};score=-sum((H.get(r,0)-old.get(r,0))*r**(1-a)for r in H.keys()|old.keys());scores.append(score+1e-10*(16640-e['units']))
receivers={e['pair']['receiver']for e in rows};A=[];hi=[]
for u in receivers:
 x=[float(e['pair']['receiver']==u)for e in rows];A.append(x);hi.append(1)
 for j,e in enumerate(rows):
  if e['pair']['donor']==u:
   z=list(x);z[j]+=1;A.append(z);hi.append(1)
q=milp(-np.array(scores),integrality=np.ones(len(rows)),bounds=Bounds(0,1),constraints=LinearConstraint(np.array(A),np.full(len(A),-np.inf),np.array(hi)),options={'time_limit':60,'mip_rel_gap':0})
assert q.success,q.message
sel=[e['pair']for e,x in zip(rows,q.x)if x>.5];assert len({e['receiver']for e in sel})==len(sel);assert not{e['receiver']for e in sel}&{e['donor']for e in sel}
out=dict(status='BOUNDED_SINGLE_OBJECTIVE_MILP_NOMINATION_PENDING_COMPLETE_SIGNED_PRICE',pairs=sel,objective_exponent=a,score=-q.fun,successful_singles=len(rows),scope='Moment objective using actual singleton profiles; shared donors unchanged, receiver roles never donors, therefore acyclic. Exact complete word and paid global gates required.')
(P/'PAIR-SELECTION.json').write_text(json.dumps(out,indent=2)+'\n');print(len(sel),out['score']);print([(e['receiver'],e['donor'],e['frame'])for e in sel])
