# SPDX-License-Identifier: Apache-2.0
# Nomination only; the immutable predecessor reconstruct.py checks the witness.
from common import *
from collections import Counter,defaultdict
import numpy as np
from scipy.optimize import milp,Bounds,LinearConstraint
from scipy.sparse import coo_matrix
D=json.load(open(BASE/'order-screen.json'));ws=D['widths'];inv={int(k):v for k,v in D['inventory'].items()};groups=sorted(D['windows']);ints=[(min(D['windows'][g][1]),max(D['windows'][g][1])) for g in groups];sup=D['support']
# All old support plus relaxed support, allowing conservative fallback.
S2=Path(os.environ['SOURCE_PARTNER_PREPARED']);pv=json.load(open(S2/'new/BORROW-PROVIDERS.json'))['gauge44']['widths'];old=json.load(gzip.open(S2/'new/borrow-fill/FILL.json.gz','rt'));bins=defaultdict(list)
for x in old['rows']:bins[tuple(x[2:5])].append(pv[x[1]])
pats=set((r,tuple(ns),rem) for r,ns,rem in sup)
for (rep,ch,port),v in bins.items():
 cap=D['windows'][f'{rep},{ch}'][0];pats.add((cap,tuple(v.count(w) for w in ws),cap-sum(v)))
for r in [8,16,32,48]:pats.add((r,(0,)*len(ws),r))
baseline=json.loads((BASE/'baseline-packing.json').read_text());pats.update((r,tuple(ns),rem) for r,ns,rem in baseline['patterns'])
pats=sorted(pats);vars=[(g,p) for g in range(len(groups)) for p in range(len(pats)) if pats[p][0]==D['windows'][groups[g]][0]]
vr=defaultdict(list)
for i,(g,p) in enumerate(vars):vr[g].append((i,p))
# Necessary interval and flow constraints prune nominations; realization and
# the independent original literal checker remain mandatory acceptance gates.
rr=[];cc=[];vv=[];lo=[];hi=[]
def constraint(items,l,h):
 row=len(lo)
 for c,v in items:
  if v:rr.append(row);cc.append(c);vv.append(v)
 lo.append(l);hi.append(h)
for g in range(len(groups)):constraint([(i,1) for i,p in vr[g]],112,112)
for j,w in enumerate(ws):constraint([(i,pats[p][1][j]) for i,(g,p) in enumerate(vars)],666*inv[w],666*inv[w])
a=.0017137379215475043
def phi(r):return r*math.expm1(-a*math.log(r))/a if r else 0.
obj=np.array([phi(pats[p][2]) for g,p in vars]);cuts=set()
base_score=sum(n*phi(baseline['patterns'][p][2]) for g,p,n in baseline['solution'])
constraint(list(enumerate(obj)), -np.inf, base_score-0.01)
checkpoint=BASE/'CUT-CHECKPOINT.json.gz'
start_round=0
if checkpoint.exists():
 state=json.loads(gzip.decompress(checkpoint.read_bytes()));rr=state['rr'];cc=state['cc'];vv=state['vv'];lo=state['lo'];hi=state['hi'];cuts=set(map(tuple,state['cuts']));start_round=state['next_round']
 print('RESUMED',start_round,'constraints',len(lo),flush=True)
upper=np.array([112 if sum(pats[p][1])<=len(D['windows'][groups[g]][1]) else 0 for g,p in vars])
# Also ensure each group/time never needs more than112 roles: cumulative all width interval Hall bound per physical family.
for round in range(start_round,40):
 mat=coo_matrix((vv,(rr,cc)),shape=(len(lo),len(vars))).tocsr()
 res=milp(np.zeros(len(vars)),integrality=np.ones(len(vars)),bounds=Bounds(0,upper),constraints=LinearConstraint(mat,lo,hi),options={'time_limit':30,'mip_rel_gap':0})
 score=float(obj@res.x) if res.x is not None else None
 print('ROUND',round,'status',res.status,'obj',score,'vars',len(vars),'cuts',len(cuts),flush=True)
 if res.x is None:
  (BASE/'STOP.json').write_text(json.dumps(dict(round=round,status=int(res.status),reason=res.message)))
  print('STOP_NO_FEASIBLE_INCUMBENT',res.message,flush=True);break
 xx=np.rint(res.x).astype(int);counts=np.zeros((len(groups),len(ws)),dtype=int)
 for i,(g,p) in enumerate(vars):counts[g]+=xx[i]*np.array(pats[p][1])
 added=0
 for j,w in enumerate(ws):
  # overload over all [a,b] using 2d prefix: count jobs with release>=a deadline<=b
  M=np.zeros((667,667),dtype=int)
  for g,(a,b) in enumerate(ints):M[a,b]+=counts[g,j]
  S=np.cumsum(np.cumsum(M[::-1,:],axis=0)[::-1,:],axis=1)
  bad=[]
  for a in range(666):
   for b in range(a,666):
    excess=int(S[a,b])-inv[w]*(b-a+1)
    if excess>0:bad.append((excess,a,b))
  for excess,a,b in sorted(bad,reverse=True)[:80]:
   key=(j,a,b)
   if key in cuts:continue
   cuts.add(key);gs={g for g,(aa,bb) in enumerate(ints) if aa>=a and bb<=b}
   constraint([(i,pats[p][1][j]) for i,(g,p) in enumerate(vars) if g in gs],0,inv[w]*(b-a+1));added+=1
 # Enforce unit per-bin/per-call capacity, separately for each width.
 from scipy.sparse.csgraph import maximum_flow,breadth_first_order
 for j,w in enumerate(ws):
  ports=np.zeros(len(groups),dtype=int)
  for i,(g,p) in enumerate(vars):ports[g]+=xx[i]*int(pats[p][1][j]>0)
  er=[];ec=[];ev=[];sink=667+len(groups)
  def edge(a,b,c):
   if c:er.append(a);ec.append(b);ev.append(int(c))
  for t in range(666):edge(0,1+t,inv[w])
  for g,(a,b) in enumerate(ints):
   edge(667+g,sink,counts[g,j])
   for t in range(a,b+1):edge(1+t,667+g,ports[g])
  fm=coo_matrix((np.array(ev,dtype=np.int64),(er,ec)),shape=(sink+1,sink+1)).tocsr();fr=maximum_flow(fm,0,sink)
  if fr.flow_value==666*inv[w]:continue
  resid=fm-fr.flow;resid.data=(resid.data>0).astype(np.int64);resid.eliminate_zeros();reach=set(breadth_first_order(resid,0,return_predecessors=False));tt={t for t in range(666) if 1+t in reach};gg={g for g in range(len(groups)) if 667+g not in reach}
  ks={g:sum(t in tt for t in range(ints[g][0],ints[g][1]+1)) for g in gg}
  constraint([(i,pats[p][1][j]-ks[g]*int(pats[p][1][j]>0)) for i,(g,p) in enumerate(vars) if g in gg],-np.inf,inv[w]*(666-len(tt)))
  added+=1;print('FLOW_CUT',w,666*inv[w]-fr.flow_value,len(tt),len(gg),flush=True)
 print('added',added,flush=True)
 histogram=Counter()
 for i,(g,p) in enumerate(vars):
  if xx[i] and pats[p][2]:histogram[pats[p][2]]+=int(xx[i])
 print('IDLE',dict(sorted(histogram.items())),flush=True)
 (BASE/'interval-packing-neworder.json').write_text(json.dumps(dict(groups=groups,patterns=pats,solution=[[g,p,int(xx[i])] for i,(g,p) in enumerate(vars) if xx[i]],counts=counts.tolist(),round=round,added=added,obj=score)))
 checkpoint.write_bytes(gzip.compress(json.dumps(dict(rr=rr,cc=cc,vv=vv,lo=lo,hi=hi,cuts=list(cuts),next_round=round+1)).encode(),mtime=0))
 if not added:break
