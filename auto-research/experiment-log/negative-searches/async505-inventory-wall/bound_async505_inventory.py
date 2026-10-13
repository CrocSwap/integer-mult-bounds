"""Necessary inventory relaxation ignoring time windows and distinct-call restrictions.
Floating bounds are diagnostic, not exact global-optimality certificates.
"""
from pathlib import Path
from collections import Counter
from fractions import Fraction
import json,math
import numpy as np
from scipy.optimize import linprog,milp,Bounds,LinearConstraint,brentq
R=Path(__file__).resolve().parent;O=R/'async505-inventory-bound';O.mkdir(exist_ok=False);D=json.load(open(R/'async505-order24-realized/PLAN.json'));ranks=Counter()
for rank,times in D['windows'].values():ranks[rank]+=120
widths=Counter(D['baseline_widths']);ws=sorted(widths);b=float(Fraction(json.load(open(R/'async505-order24-realized/audit/EXACT-ASSEMBLY.json'))['complex_lower']));m=D['M'];cost=lambda r:r*math.expm1(b*math.log(m/r))/b+32*m*m/1e16*m**b/b if r else 0
def pats(cap,j=0,p=()):
 yield p
 for k in range(j,len(ws)):
  if ws[k]<=cap:yield from pats(cap-ws[k],k,p+(ws[k],))
vs=[(r,p)for r in sorted(ranks)for p in pats(r)];rows=[('rank',r)for r in sorted(ranks)]+[('width',w)for w in ws];A=np.array([[int(r==a)if k=='rank'else p.count(a)for r,p in vs]for k,a in rows],float);rhs=np.array([ranks[a]if k=='rank'else widths[a]*len(D['order'])for k,a in rows]);c=np.array([cost(r-sum(p))for r,p in vs]);loc=json.load(open(R/'stage4-local-verification/baseline/split-centres/LOCAL-CHECKS.json'));H=Counter({int(k):v*len(D['order'])for k,v in loc['forward']['paid_profile'].items()});localcost=sum(v*cost(k)for k,v in H.items());baseH={int(k):v for k,v in D['profile'].items()};baselinecost=sum(v*cost(k)for k,v in baseH.items());lp=linprog(c,A_eq=A,b_eq=rhs,bounds=(0,None),method='highs');assert lp.success
res=dict(status='FLOAT_INVENTORY_RELAXATION_ONLY',families_by_rank=dict(ranks),variables=len(vs),lp_objective=float(lp.fun)+localcost,baseline_cost=baselinecost,lp_possible_gain=baselinecost-float(lp.fun)-localcost,scope='Drops all temporal owner windows. Necessary inventory condition only. Floating optimization is not an exact upper-bound proof.')
q=milp(c,integrality=np.ones(len(vs)),bounds=Bounds(0,np.inf),constraints=LinearConstraint(A,rhs,rhs));assert q.x is not None;x=np.rint(q.x).astype(int);assert np.array_equal(A@x,rhs)
for val,(r,p)in zip(x,vs):
 if val and r>sum(p):H[r-sum(p)]+=int(val)
res.update(milp_objective=float(c@x)+localcost,milp_possible_gain=baselinecost-float(c@x)-localcost,gap=float(q.mip_gap),profile=dict(sorted(H.items())),selection=[[r,list(p),int(v)]for (r,p),v in zip(vs,x)if v]);(O/'RESULT.json').write_text(json.dumps(res,indent=2)+'\n');print({k:v for k,v in res.items()if k not in ['selection','profile']},flush=True)
