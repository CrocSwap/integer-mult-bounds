"""Strengthen aggregate flow with per-pattern call capacities before coloring."""
from pathlib import Path
from collections import Counter,defaultdict
import json,sys,time
import numpy as np
from scipy.optimize import milp,Bounds,LinearConstraint
from scipy.sparse import lil_matrix
N=Path(sys.argv[1]);O=Path(sys.argv[2]);assert not O.exists();n=json.loads(N.read_text());D=json.load(open(Path(__file__).resolve().parent/'pr507-async-screen/PLAN-SEED.json'));wc=Counter(D['baseline_widths']);patterns=[(tuple(i),tuple(a),count)for k,i,a,count in n['selection']if k=='x'];win={tuple(map(int,k.split(','))):v for k,v in n['windows'].items()}
vs=[(j,t,w)for j,(i,pat,count)in enumerate(patterns)for t in win[i][1]for w in set(pat)];rows=[('slots',j,w)for j,(i,pat,count)in enumerate(patterns)for w in set(pat)]+[('demand',t,w)for t in range(len(n['order']))for w in wc]+[('distinct',j,t)for j,(i,pat,count)in enumerate(patterns)for t in win[i][1]];ri={x:j for j,x in enumerate(rows)};A=lil_matrix((len(rows),len(vs)),dtype=float)
for k,(j,t,w)in enumerate(vs):A[ri['slots',j,w],k]=1;A[ri['demand',t,w],k]=1;A[ri['distinct',j,t],k]=1
rhs=np.array([patterns[x[1]][2]*patterns[x[1]][1].count(x[2])if x[0]=='slots'else wc[x[2]]if x[0]=='demand'else patterns[x[1]][2]for x in rows]);lo=rhs.astype(float)
for j,r in enumerate(rows):
 if r[0]=='distinct':lo[j]=-np.inf
A=A.tocsr();start=time.monotonic();print('MODEL',len(vs),len(rows),flush=True);q=milp(np.zeros(len(vs)),integrality=np.ones(len(vs)),bounds=Bounds(0,np.inf),constraints=LinearConstraint(A,lo,rhs),options={'time_limit':60});receipt=dict(status=int(q.status),message=q.message,seconds=time.monotonic()-start)
if q.x is not None:
 x=np.rint(q.x).astype(int);assert np.all(A@x<=rhs)and np.all(A@x>=lo);alloc=defaultdict(Counter)
 for v,(j,t,w)in zip(x,vs):
  if v:alloc[patterns[j][0]][t,w]+=int(v)
 n['selection']=[z for z in n['selection']if z[0]=='x']+[['y',list(i),list(tw),v]for i,q in alloc.items()for tw,v in q.items()];n['pattern_flow_repair']=receipt;O.write_text(json.dumps(n,indent=2)+'\n')
O.with_suffix('.receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(receipt,flush=True)
