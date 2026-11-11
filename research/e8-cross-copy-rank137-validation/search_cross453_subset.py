"""Exact word-profile subset nomination, floating MILP; frozen hosting and exact replay still required."""
from pathlib import Path
exec(Path('search_kernel138_basis_exchanges.py').read_text().split('chi={')[0])
import numpy as np
from scipy.optimize import milp,LinearConstraint,Bounds
out=r/'cross453-subset-search';out.mkdir(exist_ok=True)
entries=json.loads((r/'hosting-kernel-growth/RESULT.json').read_text())['entries']
donorE={d:tuple(e) for e,p,ds in entries for d in ds};donors=sorted(donorE);ne=len(entries);nd=len(donors);di={d:ne+j for j,d in enumerate(donors)};qi=ne+nd;bi=qi+1;n=bi+56
cval=.001349600964;cost=lambda k:(k/78)**(1-cval) if k else 0.
c=np.zeros(n);lb=np.zeros(n);ub=np.ones(n);ub[qi]=1200;rows=[];lo=[];hi=[]
def row(vals,a,b):
 z=np.zeros(n)
 for i,x in vals:z[i]=x
 rows.append(z);lo.append(a);hi.append(b)
E=[]
for i,(e,p,ds) in enumerate(entries):
 rank=dims[ids[sum(1<<x for x in e)]];E.append(rank);fd=dims[first[p]];c[i]=11*(cost(fd-rank)-cost(fd))
 for d in ds:row([(i,1),(di[d],-1)],-np.inf,0)
for d in donors:
 rank=dims[ids[sum(1<<x for x in donorE[d])]];fd=dims[first[d]];c[di[d]]=11*(cost(rank)+cost(fd-rank)-cost(fd))
 row([(di[d],1)]+[(i,-1) for i,e in enumerate(entries) if d in e[2]],-np.inf,0)
H=profile([]);h0=78*1200-408-11*sum(k*v for k,v in H.items())
c[qi]=cost(56)
for rem in range(56):c[bi+rem]=cost(rem)
row([(bi+z,1) for z in range(56)],1,1)
row([(qi,56)]+[(bi+z,z) for z in range(56)]+[(i,-11*e) for i,e in enumerate(E)],h0,h0)
res=milp(c,integrality=np.ones(n),bounds=Bounds(lb,ub),constraints=LinearConstraint(np.array(rows),lo,hi),options=dict(time_limit=180,mip_rel_gap=1e-10))
assert res.x is not None
chosen=[e for i,e in enumerate(entries) if res.x[i]>.5];er=sum(E[i] for i in range(ne) if res.x[i]>.5)
record=dict(status='MILP_SUBSET_NOMINATION_GLOBAL_PENDING',solver_status=int(res.status),message=res.message,entries=chosen,rank=er,entry_count=len(chosen),donors=len({d for e,p,ds in chosen for d in ds}),objective=float(res.fun),local_profile=profile(chosen),omitted=[e[1] for e in entries if e not in chosen],scope='Relaxed concentration of idle remainder; exact source replay and hosting feasibility pending.')
(out/'RESULT.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps({k:v for k,v in record.items() if k!='entries'}),flush=True)
