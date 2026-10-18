#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Changed inventory construction, adapted from Marius-Paul Dumitrean PR2843.

Exact pattern/time integer flows and regular bipartite edge coloring. Scientific
admission is external. Discovery adds four independently audited shared kernels.
"""
import os
os.environ['PYTHONDONTWRITEBYTECODE']='1'
import sys
sys.dont_write_bytecode=True
import argparse, collections, gzip, hashlib, json, pathlib, types
import numpy as np
from scipy.sparse import coo_matrix, csr_matrix
from scipy.sparse.csgraph import maximum_bipartite_matching
from scipy.optimize import milp, Bounds, LinearConstraint
P33=pathlib.Path('/tmp/frontier-2833/research/gmx-t74-borrow43-handoff')
P39=pathlib.Path('/tmp/frontier-2839/research/tensor-block-kappa')
P43=pathlib.Path('/tmp/frontier-2843/research/replica-integer-prefix')
NEW=pathlib.Path('/tmp/larger-dirtentry/groups-478-460-462-480')
def read(p):
 b=pathlib.Path(p).read_bytes();return json.loads(gzip.decompress(b)if b[:2]==b'\x1f\x8b'else b)
def save(p,x):
 b=json.dumps(x,sort_keys=True,separators=(',',':')).encode()
 if str(p).endswith('.gz'):
  b=bytearray(gzip.compress(b,mtime=0));b[9]=255;b=bytes(b)
 pathlib.Path(p).write_bytes(b)
ap=argparse.ArgumentParser();ap.add_argument('--work',type=pathlib.Path,required=True);ap.add_argument('--solver',choices=['cp','highs'],default='cp');ap.add_argument('--seconds',type=int,default=240);ap.add_argument('--workers',type=int,default=4);ap.add_argument('--reuse',type=pathlib.Path);ap.add_argument('--freeze45',action='store_true');ap.add_argument('--T',type=int,choices=[37,74,124],default=124);a=ap.parse_args()
out=a.work.resolve();out.mkdir(parents=True,exist_ok=False)
owner=types.ModuleType('frozen_owner');exec(compile((P39/'independent_candidate_owners_retired7.py').read_bytes(),'frozen_owner','exec'),owner.__dict__)
template=read(P33/'inputs/GLOBAL-TEMPLATE.json.gz');plan=read(P33/'inputs/PLAN.json')
providers=read(P33/'new/BORROW-PROVIDERS.json');oldwidth=providers['gauge44']['widths']
assert oldwidth==providers['extra']['widths']
for pid,short in [('gauge44','base'),('extra','extra')]:
 # Audited ordered helper IDs are the contiguous224..631. Width changes are
 # independently rechecked by the local audit and by the external verifier.
 providers[pid]['widths']=list(oldwidth)
 for rid in [478,460,462,480]:
  assert providers[pid]['widths'][rid-224]==9
  providers[pid]['widths'][rid-224]=8
 providers[pid]['actual_paid_profile']={1:2394,2:642,3:266,4:128,5:26,8:8}
widths=providers['gauge44']['widths'];WID=[4,5,7,8,9];T=a.T
SOURCEDATA=P43/'data' if T==124 else P33/'new/borrow-fill'
if T==37:
 oldowners=read(P33/'inputs/OWNERS.json.gz');timecalls={r['time']:(r['stage'],r['replica'])for r in oldowners};order=[list(timecalls[t])for t in range(9*T)]
 oldfill={'columns':['time','helper','owner_replica','child','port','offset'],'rows':[]};dispatch=read(P33/'inputs/DISPATCH.json')
 assert {(s,r)for s,r,p in dispatch}==set(map(tuple,order))
else:order=read(SOURCEDATA/'ORDER.json');oldfill=read(SOURCEDATA/'FILL.json.gz');dispatch=read(SOURCEDATA/'DISPATCH.json')
win=owner.windows(template,order,T)
family=lambda b:b[0]*896+(2*plan['pairs'][str(b[1])]+plan['sides'][str(b[1])])*112+b[2]
fw=collections.defaultdict(list)
for(o,c),(cap,lo,hi)in win.items():fw[family((o,c,0))].append((lo,hi,c))
for ww in fw.values():
 for i,(lo,hi,c)in enumerate(ww):
  assert all(max(lo,l)>=min(hi,h)for l,h,d in ww[i+1:])
oldbybin=collections.defaultdict(list)
for row in oldfill['rows']:oldbybin[tuple(row[2:5])].append(row)
fixed=[];active={};need={t:collections.Counter(widths)for t in range(len(order))}
fixed45=set();f9=collections.Counter()
for b,rs in oldbybin.items():
 ww=[oldwidth[r[1]]for r in rs]
 if 4 in ww or 5 in ww:
  fixed45.add(b)
  for r in rs:
   if oldwidth[r[1]]==9:f9[r[0]]+=1
bad={t for t,n in f9.items()if n>234}
if a.freeze45:fixed45={b for b in fixed45 if not any(r[0]in bad for r in oldbybin[b])}
else:fixed45=set()
fixedpat=collections.Counter()
for(o,c),(cap,lo,hi)in win.items():
 for port in range(112):
  b=(o,c,port);rr=oldbybin[b];ww=[oldwidth[r[1]]for r in rr]
  if (cap==8 and T!=37) or b in fixed45:
   if b in fixed45:fixedpat[cap,tuple(ww.count(w)for w in WID)]+=1
   for t,h,oo,cc,pp,z in rr:
    w=oldwidth[h];fixed.append((t,w,oo,cc,pp,z));need[t][w]-=1
  else:active[b]=(cap,lo,hi)
assert all(n>=0 for cc in need.values()for n in cc.values())
assert all(set(w for w,n in cc.items()if n)<=set(WID)for cc in need.values())
pats={16:[(0,0,1,0,1),(0,0,0,2,0),(0,0,1,0,0)],32:[(0,0,2,0,2),(0,0,0,0,3),(1,0,0,0,3),(0,1,0,0,3)],48:[(0,0,0,0,0),(0,0,0,0,5)]}
residue=1 if T==37 else 2
target={(16,(0,0,1,0,1)):406*T-residue,(16,(0,0,0,2,0)):42*T,(16,(0,0,1,0,0)):residue,(32,(0,0,2,0,2)):76*T,(32,(0,0,0,0,3)):120*T,(32,(1,0,0,0,3)):234*T,(32,(0,1,0,0,3)):18*T,(48,(0,0,0,0,5)):(432*T+residue)//5,(48,(0,0,0,0,0)):448*T-(432*T+residue)//5}
if T==37:pats[8]=[(0,0,0,1,0)];target[8,(0,0,0,1,0)]=672*T
for key,n in fixedpat.items():target[key]-=n
assert (432*T+residue)%5==0
groups=collections.defaultdict(list)
for b,(cap,lo,hi)in active.items():groups[cap,tuple(range(max(0,lo+1),min(len(order),hi+1)))].append(b)
G=sorted(groups);groupof={b:gi for gi,g in enumerate(G)for b in groups[g]}
oldx=collections.Counter();oldz=collections.Counter()
for b in active:
 q=tuple(sum(oldwidth[r[1]]==w for r in oldbybin[b])for w in WID);gi=groupof[b];oldx[gi,q]+=1
 for t,h,o,c,p,z in oldbybin[b]:oldz[gi,q,t,oldwidth[h]]+=1
edge=[];lb=[];ub=[];rl=[];ru=[];X={};Z={};hints={}
def cr(l,u=None):j=len(rl);rl.append(l);ru.append(l if u is None else u);return j
def cv(u,hint=0):j=len(lb);lb.append(0);ub.append(u);hints[j]=hint;return j
def put(r,v,n):
 if n:edge.append((r,v,n))
callrow={(t,w):cr(n)for t,c in need.items()for w,n in c.items()if n};globalrow={key:cr(n)for key,n in target.items()}
for gi,(cap,ts)in enumerate(G):
 nb=len(groups[G[gi]]);br=cr(nb)
 for q in pats[cap]:
  xv=cv(nb,oldx[gi,q]);X[gi,q]=xv;put(br,xv,1);put(globalrow[cap,q],xv,1)
  residual={w:q[j]for j,w in enumerate(WID)if q[j]};wr={w:cr(0)for w in residual}
  for w,n in residual.items():put(wr[w],xv,-n)
  for t in ts:
   tr=cr(-nb,0);put(tr,xv,-1)
   for w in residual:
    if(t,w)not in callrow:continue
    zv=cv(min(nb,need[t][w]),oldz[gi,q,t,w]);Z[gi,q,t,w]=zv;put(tr,zv,1);put(wr[w],zv,1);put(callrow[t,w],zv,1)
modelinfo=dict(T=T,groups=len(G),variables=len(lb),pattern_variables=len(X),flow_variables=len(Z),constraints=len(rl),nonzeros=len(edge),fixed_roles=len(fixed),workers=a.workers)
save(out/'MODEL.json',modelinfo);print('MODEL',modelinfo,flush=True)
rr=np.fromiter((e[0]for e in edge),np.int32);cc=np.fromiter((e[1]for e in edge),np.int32);vv=np.fromiter((e[2]for e in edge),np.float64);mat=coo_matrix((vv,(rr,cc)),shape=(len(rl),len(lb))).tocsr();del edge
if a.reuse:
 saved=read(a.reuse);value=np.zeros(len(lb),dtype=np.int64)
 for gi,q,n in saved['x']:value[X[gi,tuple(q)]]=n
 for gi,q,t,w,n in saved['z']:value[Z[gi,tuple(q),t,w]]=n
 status='EXACT_FLOW_REPLAY'
elif a.solver=='highs':
 r=milp(np.zeros(len(lb)),integrality=np.ones(len(lb)),bounds=Bounds(lb,ub),constraints=LinearConstraint(mat,rl,ru),options={'threads':a.workers,'time_limit':a.seconds,'mip_rel_gap':0,'disp':True});status=r.message;value=None if r.x is None else np.rint(r.x).astype(np.int64)
 if value is not None:assert np.max(abs(value-r.x))<1e-5
else:
 from ortools.sat.python import cp_model
 model=cp_model.CpModel();vs=[model.NewIntVar(l,u,'')for l,u in zip(lb,ub)]
 for j,(l,u)in enumerate(zip(rl,ru)):
  b,e=mat.indptr[j:j+2];ind=mat.indices[b:e];co=mat.data[b:e];model.AddLinearConstraint(cp_model.LinearExpr.WeightedSum([vs[int(k)]for k in ind],[int(k)for k in co]),l,u)
 for j,v in hints.items():model.AddHint(vs[j],v)
 solver=cp_model.CpSolver();solver.parameters.num_search_workers=a.workers;solver.parameters.max_time_in_seconds=a.seconds;solver.parameters.random_seed=124;solver.parameters.log_search_progress=True
 result=solver.Solve(model);status=solver.StatusName(result);value=np.array([solver.Value(v)for v in vs],dtype=np.int64)if result in(cp_model.OPTIMAL,cp_model.FEASIBLE)else None
 print(solver.ResponseStats(),flush=True)
print('SOLVER',status,flush=True)
if value is None:save(out/'SOLVER.json',dict(status=status,candidate=False));raise SystemExit(2)
assert not(np.any(value<lb)or np.any(value>ub)or np.any(mat@value<rl)or np.any(mat@value>ru))
xc=collections.defaultdict(collections.Counter);zc=collections.defaultdict(collections.Counter)
for(gi,q),v in X.items():
 if value[v]:xc[gi][q]=int(value[v])
for(gi,q,t,w),v in Z.items():
 if value[v]:zc[gi,q][t,w]=int(value[v])
save(out/'FLOW.json.gz',{'x':[[gi,list(q),n]for gi,c in xc.items()for q,n in c.items()],'z':[[gi,list(q),t,w,n]for(gi,q),c in zc.items()for(t,w),n in c.items()]})
def color_pattern(n,q,counts):
 slots=[w for j,w in enumerate(WID)for _ in range(q[j])]
 if not slots:assert not counts;return [[]for _ in range(n)]
 times=sorted({t for t,w in counts});K=len(times);assert K>=len(slots);ti={t:j for j,t in enumerate(times)};A=np.zeros((K,K),dtype=np.int64);slot_by_w=collections.defaultdict(list)
 for j,w in enumerate(slots):slot_by_w[w].append(j)
 for w,js in slot_by_w.items():
  atslot=0;remaining=n
  for t in times:
   needed=counts.get((t,w),0)
   while needed:
    take=min(needed,remaining);A[ti[t],js[atslot]]+=take;needed-=take;remaining-=take
    if remaining==0:atslot+=1;remaining=n
  assert atslot==len(js)
 assert all(v<=n for v in A.sum(axis=1));j=len(slots);remaining=n
 for r in range(K):
  needed=n-int(A[r].sum())
  while needed:
   assert j<K;take=min(needed,remaining);A[r,j]+=take;needed-=take;remaining-=take
   if remaining==0:j+=1;remaining=n
 assert np.all(A.sum(axis=0)==n)and np.all(A.sum(axis=1)==n)
 output=[]
 for color in range(n):
  matching=maximum_bipartite_matching(csr_matrix(A>0),perm_type='column');assert len(matching)==K and min(matching)>=0 and len(set(map(int,matching)))==K
  output.append([(times[r],slots[int(c)])for r,c in enumerate(matching)if c<len(slots)]);A[np.arange(K),matching]-=1
 assert not A.any();return output
slots=list(fixed)
for gi,(cap,ts)in enumerate(G):
 bins=groups[G[gi]];offset=0
 for q,n in sorted(xc[gi].items()):
  result=color_pattern(n,q,zc[gi,q]);assert len(result)==n
  for b,it in zip(bins[offset:offset+n],result):
   z=0
   for t,w in sorted(it):slots.append((t,w,*b,z));z+=w
  offset+=n
 assert offset==len(bins)
available={t:collections.defaultdict(list)for t in range(len(order))}
for t in available:
 for h,w in enumerate(widths):available[t][w].append(h)
final=[]
for t,w,o,c,p,z in sorted(slots):final.append([t,available[t][w].pop(),o,c,p,z])
assert not any(v for d in available.values()for v in d.values())
fill={'columns':oldfill['columns'],'dispatch_overrides':[],'rows':sorted(final)}
result,_,_=owner.check(T,order,fill,{(s,r):pid for s,r,pid in dispatch},None,plan,template,providers)
for n,obj in [('ORDER.json',order),('FILL.json.gz',fill),('DISPATCH.json',dispatch),('PROFILE.json',result['profile']),('PROVIDERS.json',providers)]:save(out/n,obj)
save(out/'LITERAL-PRODUCER-CHECK.json',dict(result,status='PASS_LITERAL_PRODUCER_CHECK_REQUIRES_EXTERNAL_REPLAY',solver=status))
print('LITERAL_PRODUCER_PASS',out,result['roles'],result['idle'],flush=True)
