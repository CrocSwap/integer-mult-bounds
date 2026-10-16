#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""PR2833/T124 composition by per-pattern/time flow and exact edge coloring.

Source chronology/masks: Tekalign, Marius-Paul Dumitrean, and PR2827 lineage.
Construction model and deterministic realization prepared with OpenAI Codex.
No source bytes are modified; independent native owner admission is external.
"""
import argparse,collections,gzip,hashlib,json,pathlib,sys,time,types
from fractions import Fraction as Q
import numpy as np
from scipy.sparse import coo_matrix,csr_matrix
from scipy.sparse.csgraph import maximum_bipartite_matching
from scipy.optimize import milp,Bounds,LinearConstraint
HERE=pathlib.Path(__file__).resolve().parent
OLD=pathlib.Path('/home/marius/kappa/kappa-frontier-20261015-2357')
SOURCE=OLD/'coordination/pr2827/research/superior-replica-kappa'
PIN={'data/ORDER.json':'b9b3eb71f8082a2349224a7a7cddab1cc0e4590ef27c3542755ff7c4c75c7fd0','data/FILL.json.gz':'2f43f57725a7b1d9293d8c4a9617ffc5bb413c4e1539a60e806fdcdecfd82588','data/DISPATCH.json':'5360d34ca04cf4973f37dce872db1f36e57e3f40382da75e4e2676d412a8b509','data/PROFILE.json':'f8146c8703e5c865d45c618ff291ff542fb792cb6cda21e0feb45ad2c5c5ff62','independent_candidate_owners_retired7.py':'77a848729159e271ba64f403dfd59dddb13044b17b2950fa56700f442e2fe461'}
for n,pin in PIN.items():
 if hashlib.sha256((SOURCE/n).read_bytes()).hexdigest()!=pin:raise ValueError('source pin '+n)
def read(p):
 b=pathlib.Path(p).read_bytes();return json.loads(gzip.decompress(b)if b[:2]==b'\x1f\x8b'else b)
def save(p,x):
 b=json.dumps(x,sort_keys=True,separators=(',',':')).encode()
 if str(p).endswith('.gz'):
  b=bytearray(gzip.compress(b,mtime=0));b[9]=255;b=bytes(b)
 pathlib.Path(p).write_bytes(b)
owner=types.ModuleType('pinned_owner');exec(compile((SOURCE/'independent_candidate_owners_retired7.py').read_bytes(),'pinned_owner','exec'),owner.__dict__)
P33=HERE.parent/'coordination/pr2833/research/gmx-t74-borrow43-handoff'
P33PIN={'new/BORROW-PROVIDERS.json':'3666edf67d61b01336e58166ec9edebd72902cc37a2da693b05691ab2a387cda','new/borrow-fill/ORDER.json':'aa7c53c188c90fd74421a804f4c6fb13aa1187c06dbac51fa147830a40e00667','new/borrow-fill/DISPATCH.json':'fd8132ec8957b908ee6d871216848f18bafc6bd9304acd6185519ee26d97b1ca','new/borrow-fill/FILL.json.gz':'0cb7522e071ff064ada2efec169e23a2fe7d3daf928eec6ba752b166cffb3468'}
for n,pin in P33PIN.items():
 if hashlib.sha256((P33/n).read_bytes()).hexdigest()!=pin:raise ValueError('P33 source pin '+n)
P=SOURCE/'vendor/frontier';template=read(P/'inputs/GLOBAL-TEMPLATE.json.gz');plan=read(P/'inputs/PLAN.json.gz');providers=read(P33/'new/BORROW-PROVIDERS.json')
for pid in providers:providers[pid]['actual_paid_profile']={int(r):n for r,n in providers[pid]['actual_paid_profile'].items()}
widths=providers['gauge44']['widths'];assert widths==providers['extra']['widths'] and providers['gauge44']['actual_paid_profile']==providers['extra']['actual_paid_profile']
ap=argparse.ArgumentParser();ap.add_argument('--T',type=int,choices=[114,124],default=124);ap.add_argument('--late',type=int,default=300);ap.add_argument('--seconds',type=int,default=240);ap.add_argument('--solver',choices=['cp','highs'],default='cp');ap.add_argument('--reuse',action='store_true');ap.add_argument('--workers',type=int,default=40);a=ap.parse_args()
assert 0<a.workers<=40
out=HERE/f'p33-t{a.T}-late{a.late}';out.mkdir(exist_ok=True)
oldorder=read(P33/'new/borrow-fill/ORDER.json');oldfill=read(P33/'new/borrow-fill/FILL.json.gz');old_dispatch={(s,r):p for s,r,p in read(P33/'new/borrow-fill/DISPATCH.json')}
off=list(map(Q,['0','4003/500','10007/1000','13001/1000','2626/125','12501/500','29003/1000','8251/250','7401/200']))
order=sorted(([s,r]for r in range(a.T)for s in range(9)),key=lambda sr:sr[1]+off[sr[0]])
assert [sr for sr in order if sr[1]<74]==oldorder
at={tuple(sr):t for t,sr in enumerate(order)};rows=[[at[tuple(oldorder[t])],h,o,c,p,k]for t,h,o,c,p,k in oldfill['rows']]
win=owner.windows(template,order,a.T)
# Different children of a physical family have disjoint strict time windows.
family=lambda b:b[0]*896+(2*plan['pairs'][str(b[1])]+plan['sides'][str(b[1])])*112+b[2]
fam_windows=collections.defaultdict(list)
for(o,c),(cap,lo,hi)in win.items():fam_windows[family((o,c,0))].append((lo,hi,c))
for windows in fam_windows.values():
 for i,(lo,hi,c)in enumerate(windows):
  if any(max(lo,l)<min(hi,h)for l,h,d in windows[i+1:]):raise ValueError('overlapping physical-family windows')
newtimes={t for t,(_,r)in enumerate(order)if r>=74};oldtimes=[t for t,(_,r)in enumerate(order)if r<74];selected=newtimes|set(oldtimes[-a.late:]if a.late else[])
WID=[4,5,7,8,9]
tight=read(OLD/'pricing/T-EXACT-BOUND.json')['tight_patterns'];pats=collections.defaultdict(list)
for cap,p in tight:pats[cap].append(tuple(p.count(w)for w in WID))
pats[16].append((0,0,1,0,0))
fixed=collections.defaultdict(list);oldbybin=collections.defaultdict(list);need=collections.defaultdict(collections.Counter)
for row in rows:
 t,h,o,c,p,k=row;oldbybin[o,c,p].append(row)
 if t in selected:need[t][widths[h]]+=1
 else:fixed[o,c,p].append(row)
for t in newtimes:need[t]=collections.Counter(widths)
groups=collections.defaultdict(list);oldpattern={};target=collections.Counter()
for(o,c),(cap,lo,hi)in win.items():
 ts=tuple(t for t in sorted(selected)if lo<t<=hi)
 for p in range(112):
  b=(o,c,p);fp=tuple(sum(widths[r[1]]==w for r in fixed[b])for w in WID)
  if not any(all(qi>=fi for qi,fi in zip(q,fp))for q in pats[cap]):raise ValueError('fixed pattern outside admissible face')
  groups[cap,ts,fp].append(b)
  if o<74:
   q=tuple(sum(widths[r[1]]==w for r in oldbybin[b])for w in WID);assert q in pats[cap];oldpattern[b]=q;target[cap,q]+=1
for cap,p,n in [(8,[8],672),(16,[7,9],448),(32,[9,9,9],129),(32,[4,9,9,9],234),(32,[5,9,9,9],18),(32,[7,7,9,9],43),(32,[7,8,8,9],24),(48,[],Q(1799,5)),(48,[9]*5,Q(441,5))]:
 v=Q(n)*(a.T-74);assert v.denominator==1;target[cap,tuple(p.count(w)for w in WID)]+=int(v)
G=sorted(groups);groupof={b:gi for gi,g in enumerate(G)for b in groups[g]}
# Every Z variable names an actual pattern, time and width. A pattern/time can
# use at most one item per assigned bin. Each pattern-width supply is exact.
edge=[];lb=[];ub=[];rl=[];ru=[];X={};Z={};hints={}
def cr(l,u=None):j=len(rl);rl.append(l);ru.append(l if u is None else u);return j
def cv(u,hint=0):j=len(lb);lb.append(0);ub.append(u);hints[j]=hint;return j
def put(r,v,n):
 if n:edge.append((r,v,n))
callrow={(t,w):cr(n)for t,c in need.items()for w,n in c.items()};globalrow={key:cr(n)for key,n in target.items()}
oldx=collections.Counter();oldz=collections.Counter()
for b,q in oldpattern.items():oldx[groupof[b],q]+=1
for t,h,o,c,p,k in rows:
 if t in selected:oldz[groupof[o,c,p],oldpattern[o,c,p],t,widths[h]]+=1
for gi,(cap,ts,fp)in enumerate(G):
 nb=len(groups[G[gi]]);br=cr(nb)
 for q in pats[cap]:
  if not all(qi>=fi for qi,fi in zip(q,fp))or(not ts and q!=fp):continue
  if(cap,q)not in globalrow:continue
  xv=cv(nb,oldx[gi,q]);X[gi,q]=xv;put(br,xv,1);put(globalrow[cap,q],xv,1)
  residual={w:q[j]-fp[j]for j,w in enumerate(WID)if q[j]>fp[j]}
  wr={w:cr(0)for w in residual}
  for w,n in residual.items():put(wr[w],xv,-n)
  for t in ts:
   tr=cr(-nb,0);put(tr,xv,-1)
   for w in residual:
    if(t,w)not in callrow:continue
    zv=cv(min(nb,need[t][w]),oldz[gi,q,t,w]);Z[gi,q,t,w]=zv;put(tr,zv,1);put(wr[w],zv,1);put(callrow[t,w],zv,1)
modelinfo=dict(T=a.T,late=a.late,selected_calls=len(selected),groups=len(G),variables=len(lb),pattern_variables=len(X),flow_variables=len(Z),constraints=len(rl),nonzeros=len(edge),workers=a.workers,same_family_windows_disjoint=True)
save(out/'MODEL.json',modelinfo);print('MODEL',modelinfo,flush=True)
rr=np.fromiter((e[0]for e in edge),np.int32);cc=np.fromiter((e[1]for e in edge),np.int32);vv=np.fromiter((e[2]for e in edge),np.float64);mat=coo_matrix((vv,(rr,cc)),shape=(len(rl),len(lb))).tocsr();del edge
if a.reuse:
 saved=read(out/'FLOW.json.gz');value=np.zeros(len(lb),dtype=np.int64)
 for gi,q,n in saved['x']:value[X[gi,tuple(q)]]=n
 for gi,q,t,w,n in saved['z']:value[Z[gi,tuple(q),t,w]]=n
 status='REPLAY_EXACT_FLOW'
elif a.solver=='highs':
 r=milp(np.zeros(len(lb)),integrality=np.ones(len(lb)),bounds=Bounds(lb,ub),constraints=LinearConstraint(mat,rl,ru),options={'threads':a.workers,'time_limit':a.seconds,'mip_rel_gap':0,'disp':True})
 status=r.message;value=None if r.x is None else np.rint(r.x).astype(np.int64)
 if value is not None and np.max(abs(value-r.x))>1e-5:raise ValueError('fractional solver output')
else:
 sys.path.insert(0,str(OLD/'pricing/cp-deps'));from ortools.sat.python import cp_model
 model=cp_model.CpModel();vs=[model.NewIntVar(l,u,'')for l,u in zip(lb,ub)]
 for j,(l,u)in enumerate(zip(rl,ru)):
  b,e=mat.indptr[j:j+2];ind=mat.indices[b:e];co=mat.data[b:e];expr=cp_model.LinearExpr.WeightedSum([vs[int(k)]for k in ind],[int(k)for k in co]);model.AddLinearConstraint(expr,l,u)
 for j,v in hints.items():model.AddHint(vs[j],v)
 solver=cp_model.CpSolver();solver.parameters.num_search_workers=a.workers;solver.parameters.max_time_in_seconds=a.seconds;solver.parameters.random_seed=124;solver.parameters.log_search_progress=True
 result=solver.Solve(model);status=solver.StatusName(result);value=np.array([solver.Value(v)for v in vs],dtype=np.int64)if result in(cp_model.OPTIMAL,cp_model.FEASIBLE)else None
 print(solver.ResponseStats(),flush=True)
print('SOLVER',status,flush=True)
if value is None:save(out/'SOLVER.json',{'status':status,'candidate':False});raise SystemExit(2)
if np.any(value<lb)or np.any(value>ub)or np.any(mat@value<rl)or np.any(mat@value>ru):raise ValueError('exact integer constraint failure')
xc=collections.defaultdict(collections.Counter);zc=collections.defaultdict(collections.Counter)
for(gi,q),v in X.items():
 if value[v]:xc[gi][q]=int(value[v])
for(gi,q,t,w),v in Z.items():
 if value[v]:zc[gi,q][t,w]=int(value[v])
save(out/'FLOW.json.gz',{'x':[[gi,list(q),n]for gi,c in xc.items()for q,n in c.items()],'z':[[gi,list(q),t,w,n]for(gi,q),c in zc.items()for(t,w),n in c.items()]})
# For one pattern, split each width into q_w identical slots. Balance each slot
# to degree n, complete the bipartite multigraph to n-regular with dummy slots,
# then peel n perfect matchings. Each color is a literal bin, never twice/time.
def color_pattern(n,residual,counts):
 slots=[w for j,w in enumerate(WID)for _ in range(residual[j])]
 if not slots:
  assert not counts;return [[]for _ in range(n)]
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
  output.append([(times[r],slots[int(c)])for r,c in enumerate(matching)if c<len(slots)])
  A[np.arange(K),matching]-=1
 assert not A.any();return output
assigned=collections.defaultdict(list)
for gi,(cap,ts,fp)in enumerate(G):
 bins=groups[G[gi]];offset=0
 for q,n in sorted(xc[gi].items()):
  result=color_pattern(n,tuple(qi-fi for qi,fi in zip(q,fp)),zc[gi,q]);assert len(result)==n
  for b,it in zip(bins[offset:offset+n],result):assigned[b]=it
  offset+=n
 assert offset==len(bins)
available=collections.defaultdict(lambda:collections.defaultdict(list))
for t in selected:
 for h,w in enumerate(widths):available[t][w].append(h)
final=[]
for b in assigned:
 offset=0
 for row in sorted(fixed[b]):
  row=list(row);row[5]=offset;offset+=widths[row[1]];final.append(row)
 for t,w in sorted(assigned[b]):
  h=available[t][w].pop();final.append([t,h,*b,offset]);offset+=w
assert not any(v for d in available.values()for v in d.values());final.sort()
fill={'columns':oldfill['columns'],'dispatch_overrides':[],'rows':final};dispatch=[[st,r,old_dispatch[st,r]if r<74 else'gauge44']for st,r in order]
target_idle={1:234*a.T,3:(441*a.T+1)//5,5:129*a.T,9:1,48:(1799*a.T-1)//5};profile=collections.Counter(target_idle)
for st,r,pid in dispatch:profile.update(providers[pid]['actual_paid_profile'])
result,_,_=owner.check(a.T,order,fill,{(st,r):pid for st,r,pid in dispatch},profile,plan,template,providers)
assert result['idle']==target_idle
for n,obj in [('ORDER.json',order),('FILL.json.gz',fill),('DISPATCH.json',dispatch),('PROFILE.json',dict(profile))]:save(out/n,obj)
save(out/'LITERAL-PRODUCER-CHECK.json',dict(result,status='PASS_LITERAL_PRODUCER_CHECK_REQUIRES_EXTERNAL_INDEPENDENT_REPLAY',source_head='e9307b48d7d1b690939935ecef0f8e524e6d92f4',source_sha256={'PR2827':PIN,'PR2833':P33PIN},solver=status,method='Exact per-pattern/time flow; regular bipartite multigraph edge coloring; disjoint same-family source windows'))
print('LITERAL_PRODUCER_PASS',out,result['roles'],result['idle'],flush=True)
