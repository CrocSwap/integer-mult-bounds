"""Joint local recursive interfaces and aggregate owner-bin relaxation.

All existing positive entrances may choose any subspace of their backward
ceiling. Exact native/global admission remains mandatory after nomination.
"""
import os,sys,json,gzip,copy,time,functools,itertools,math
from pathlib import Path
from collections import Counter
import numpy as np
from scipy.optimize import linprog,milp,Bounds,LinearConstraint
from scipy.sparse import coo_matrix,vstack
import argparse
ROOT=Path(__file__).resolve().parents[3]
ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--work',type=Path,required=True);args=ap.parse_args();OUT=args.work.resolve();assert not OUT.is_relative_to(ROOT);OUT.mkdir(parents=True,exist_ok=True)
os.environ['K8_BASE_WORD']=str(OUT/'candidate.json.gz');sys.path.insert(0,str(ROOT/'research/k8-eight-ends/discovery'));import screen_end_groups as S
M=S.M
@functools.lru_cache(None)
def quotient_spaces(k):
 assert k<=5,('unbounded enumeration',k)
 seen={()};level={()}
 while level:
  nxt={M.basis(list(b)+[v]) for b in level for v in range(1,1<<k)}-seen
  seen.update(nxt);level=nxt
 return sorted(seen,key=lambda b:(len(b),b))
@functools.lru_cache(None)
def interval(lo,hi):
 assert M.contained(lo,hi)
 comp=[];cur=lo
 for x in hi:
  new=M.basis(list(cur)+[x])
  if len(new)>len(cur):comp.append(x);cur=new
 def lift(v):
  x=0
  for i,z in enumerate(comp):
   if v>>i&1:x^=z
  return x
 return sorted([M.basis(list(lo)+[lift(x) for x in b]) for b in quotient_spaces(len(comp))],key=lambda b:(len(b),b))
M.interval=interval
w=copy.deepcopy(S.w);census=json.loads((OUT/'INTERFACE-CENSUS.json').read_text());domains={};ends={h:len(w['helper_final'].get(str(h),range(9))) for h in range(224,704)}
for g in census:
 ds=interval((),tuple(g['hi']))
 for h in g['helpers']:domains[('S',h)]=ds;w['start_extra'][str(h)]=[]
print('SOURCE_DOMAINS',len(domains),Counter(len(v) for v in domains.values()),flush=True)
m=M.Model(w,relax_given=True);new=m.baseline()
for node,ds in domains.items():
 del m.fixed_frames[node];m.domain[node]=ds;new[node]=tuple(S.w['start_extra'][str(node[1])])
print('MODEL',len(m.domain),'components',len(m.components()),flush=True)
b=.00167838
phi=lambda r:r*math.expm1(b*math.log(73/r))/b if r else 0
rows=[];columns=[];rhs=[];ri=[];cj=[];val=[];cost=[];integrality=[]
# Four bin capacities and width inventory, all constraints per one replica.
caps={8:672,16:448,32:448,48:448};ws=sorted({ends[q]-len(fr) for (tag,q),ds in domains.items() for fr in ds}|{ends[q]-len(w['start_extra'].get(str(q),[])) for q in ends if ('S',q) not in domains})
fixed_inv=Counter(ends[q]-len(w['start_extra'].get(str(q),[])) for q in ends if ('S',q) not in domains)
assert min(ws)>0
rhs=list(caps.values())+[9*fixed_inv[r] for r in ws];rowwidth={r:4+i for i,r in enumerate(ws)}
for ci,comp in enumerate(m.components()):
 t=time.monotonic();labels,unary,pairs=m.component_problem(comp);rr,bb,cols=M.lp(labels,unary,pairs);rbase=len(rhs);rhs.extend(bb)
 for key,vec,es in cols:
  j=len(columns);columns.append(key);cost.append(9*sum(n*phi(d) for d,n in enumerate(vec)));integrality.append(1 if key[0]=='x' else 0)
  for i,a in es:ri.append(rbase+i);cj.append(j);val.append(a)
  if key[0]=='x' and key[1][0]=='S':
   width=ends[key[1][1]]-len(key[2]);ri.append(rowwidth[width]);cj.append(j);val.append(-9)
 if ci%10==0:print('COMPONENT',ci,'columns',len(columns),'seconds',time.monotonic()-t,flush=True)
locals_n=len(columns)
for i,cap in enumerate(caps):
 for ns in itertools.product(*(range(cap//r+1) for r in ws)):
  used=sum(r*n for r,n in zip(ws,ns))
  if used>cap:continue
  j=len(columns);columns.append(('bin',cap,ns));cost.append(phi(cap-used));integrality.append(0);ri.append(i);cj.append(j);val.append(1)
  for r,n in zip(ws,ns):
   if n:ri.append(rowwidth[r]);cj.append(j);val.append(n)
A=coo_matrix((np.array(val,float),(ri,cj)),shape=(len(rhs),len(columns))).tocsc();c=np.array(cost);rhs=np.array(rhs);print('SOLVING',A.shape,'nnz',A.nnz,'widths',ws,flush=True)
t=time.monotonic();sol=linprog(c,A_eq=A,b_eq=rhs,bounds=(0,None),method='highs-ipm',options={'time_limit':180});assert sol.success,sol.message
fractional=int(sum(integrality[j] and 1e-7<x<1-1e-7 for j,x in enumerate(sol.x)));lp=float(sol.fun);print('LP',lp,'fractional x',fractional,'seconds',time.monotonic()-t,flush=True)
if fractional:
 bounds=Bounds(np.zeros(len(columns)),np.array([1 if k[0] in ('x','y') else np.inf for k in columns]));sol=milp(c,integrality=np.array(integrality),bounds=bounds,constraints=LinearConstraint(A,rhs,rhs),options={'time_limit':180,'mip_rel_gap':1e-10});assert sol.x is not None,sol.message
print('SOLUTION',sol.message,float(sol.fun),flush=True)
for j,key in enumerate(columns[:locals_n]):
 if key[0]=='x' and sol.x[j]>.9:new[key[1]]=key[2]
for node in m.domain:assert node in new
for comp in m.components():
 labels,unary,pairs=m.component_problem(comp);M.assignment_cost(labels,unary,pairs,new)
for i in range(len(m.gates)):
 fr=m.frame_of(('G',i),new)
 if i<m.nA:w['A'][i][-1]=list(fr)
 elif i<m.nA+m.nB:w['B'][i-m.nA][-1]=list(fr)
 else:w['early_cleanup'][i-m.nA-m.nB][1]=list(fr)
for node in domains:w['start_extra'][str(node[1])]=list(new[node])
profile=m.profile(new);assert Counter(profile)==S.promo.chain_profile(w)+Counter({8:8});w['report']['local_profile']={str(r):c for r,c in profile.items()};w['report']['local_rank_mass']=sum(r*c for r,c in profile.items());w['report']['width_inventory']={str(r):c for r,c in S.promo.widths(w).items()}
(OUT/'joint-global-ipm.json.gz').write_bytes(gzip.compress(json.dumps(w,sort_keys=True,separators=(',',':')).encode(),mtime=0));changed={h:fr for h,fr in w['start_extra'].items() if fr!=S.w['start_extra'][h]};r=dict(status='NOMINATED_GLOBAL_INTERFACE_LP_REQUIRES_NATIVE_AND_PHYSICAL_PACKING',profile=w['report']['local_profile'],changed_starts=changed,lp_objective=lp,integer_local_objective=float(sol.fun),lp_fractional_x=fractional,**S.screen(w));(OUT/'JOINT-GLOBAL-IPM.json').write_text(json.dumps(r,indent=2)+'\n');print('JOINT_RESULT',json.dumps(r),flush=True)
