"""Search a pinned PR496 allocation model; exact integer profiles, floating discovery only."""
from pathlib import Path
from collections import Counter
from fractions import Fraction
import json,math,sys,time,hashlib
import numpy as np
from scipy.optimize import linprog,milp,LinearConstraint,Bounds,brentq
from scipy.sparse import lil_matrix
root=Path(__file__).resolve().parent
src=root/'source496-review/provenance/POOLED-ALLOCATION.json'
data=json.loads(src.read_text());out=root/'pooled496-moment-search';out.mkdir(exist_ok=False)
win={int(i):(int(p),int(r),list(st)) for i,(p,r,st) in data['windows'].items()}
widths=sorted(set(data['widths']));wc=Counter(data['widths']);ambient=data['ambient'];oldT=data['T'];nstages=len({s for p,r,st in win.values() for s in st});ports=data['live']//oldT//(2*(max(data['pairs'].values())+1));old={int(k):v for k,v in data['profile'].items()}
fixed=Counter(old)
for i,pat,count in data['patterns']:
 r=win[i][1]-sum(pat)
 if r:fixed[r]-=count
assert fixed==Counter({int(r):n*oldT*nstages for r,n in data['local_paid'].items()})
def patterns(cap,idx=0,pat=()):
 yield pat
 if len(pat)>=oldT:return
 for j in range(idx,len(widths)):
  w=widths[j]
  if w<=cap:yield from patterns(cap-w,j,pat+(w,))
vs=[('x',i,pat) for i,(p,r,st) in win.items() for pat in patterns(r)]
vs += [('y',i,(s,w)) for i,(p,r,st) in win.items() for s in st for w in widths]
rows=[('copies',i) for i in win]+[('balance',i,w) for i in win for w in widths]+[('demand',s,w) for s in range(nstages) for w in widths]
ri={r:j for j,r in enumerate(rows)};A=lil_matrix((len(rows),len(vs)),dtype=float)
for j,(kind,i,arg) in enumerate(vs):
 if kind=='x':
  A[ri['copies',i],j]=1
  for w,n in Counter(arg).items():A[ri['balance',i,w],j]=n
 else:
  s,w=arg;A[ri['balance',i,w],j]=-1;A[ri['demand',s,w],j]=1
A=A.tocsr()
def rhs(T):return np.array([ports*T if r[0]=='copies' else wc[r[2]]*T if r[0]=='demand' else 0 for r in rows])
def cost(z):
 # Remove the constant linear rank term for conditioning; include one fallback per remainder child.
 return np.array([(win[i][1]-sum(arg))*math.expm1(z*math.log(ambient/(win[i][1]-sum(arg))))/z + (32*ambient**2/1e16)*ambient**z/z if kind=='x' and win[i][1]>sum(arg) else 0 for kind,i,arg in vs])
def profile(x,T):
 H=Counter({int(r):n*T*nstages for r,n in data['local_paid'].items()})
 for val,(kind,i,arg) in zip(x,vs):
  if val and kind=='x':
   r=win[i][1]-sum(arg)
   if r:H[r]+=int(val)
 assert sum(r*n for r,n in H.items())==ambient*(data['live']//oldT*T)-(ambient*data['live']-sum(r*n for r,n in old.items()))*T//oldT
 return dict(sorted((r,n) for r,n in H.items() if n))
def floatroot(H,T):
 W=data['live']//oldT*T
 return brentq(lambda z:sum(n*(r/ambient)**(1-z) for r,n in H.items())/W +32*ambient**2*sum(H.values())/1e16*ambient**(z-1)/W-1,0,.01,xtol=1e-15)
z=floatroot(old,oldT);c=cost(z);b=rhs(oldT)
oldx=np.zeros(len(vs));vid={v:j for j,v in enumerate(vs)}
for i,pat,n in data['patterns']:oldx[vid['x',i,tuple(sorted(pat))]]=n
for i,w,s,n in data['stage_assignments']:oldx[vid['y',i,(s,w)]]=n
assert np.max(np.abs(A@oldx-b))==0
print('model',len(vs),len(rows),'baseline',z,'objective',float(c@oldx),flush=True)
LP=linprog(c,A_eq=A,b_eq=b,bounds=(0,None),method='highs');assert LP.success
fractions=[Fraction(float(v)).limit_denominator(10**6) for v in LP.x]
# Certify the candidate primal equalities using integers after clearing denominators.
den=math.lcm(*(f.denominator for f in fractions));ix=np.array([int(f*den) for f in fractions],dtype=np.int64);assert np.array_equal(np.asarray(A@ix,dtype=np.int64),b.astype(np.int64)*den)
record=dict(status='FLOAT_LP_WITH_EXACT_PRIMAL',variables=len(vs),rows=len(rows),objective=float(LP.fun),baseline_objective=float(c@oldx),gain_objective=float(c@oldx-LP.fun),denominator=den,scaled_replicas=oldT*den,primal_profile=profile(ix,oldT*den),float_root=floatroot(profile(ix,oldT*den),oldT*den),duals=LP.eqlin.marginals.tolist(),reduced_cost_min=float((c-A.T@LP.eqlin.marginals).min()),source_sha256=hashlib.sha256(src.read_bytes()).hexdigest(),scope='Floating objective and duals are not an exact optimality certificate; primal counts/equalities exact.')
(out/'LP.json').write_text(json.dumps(record,indent=2)+'\n');print('LP',{k:v for k,v in record.items() if k not in ['duals','primal_profile']},flush=True)
ledger=[]
for T in [oldT,2*oldT,4*oldT,8*oldT]:
 start=time.monotonic();bb=rhs(T);res=milp(c,integrality=np.ones(len(vs)),bounds=Bounds(0,np.inf),constraints=LinearConstraint(A,bb,bb),options={'time_limit':60,'mip_rel_gap':1e-12})
 if res.x is None:row=dict(T=T,status=int(res.status),message=res.message)
 else:
  x=np.rint(res.x).astype(np.int64);assert np.array_equal(A@x,bb)
  H=profile(x,T);row=dict(T=T,status=int(res.status),message=res.message,gap=float(res.mip_gap),objective=float(c@x),profile=H,float_root=floatroot(H,T),same_normalized_profile=all(H.get(r,0)*oldT==old.get(r,0)*T for r in set(H)|set(old)),seconds=time.monotonic()-start,selection=[[kind,i,list(arg),int(v)] for (kind,i,arg),v in zip(vs,x) if v])
 (out/f'T{T}.json').write_text(json.dumps(row,indent=2)+'\n');ledger.append({k:v for k,v in row.items() if k not in ['profile','selection']});print(ledger[-1],flush=True)
(out/'COMPLETE.json').write_text(json.dumps(ledger,indent=2)+'\n')
