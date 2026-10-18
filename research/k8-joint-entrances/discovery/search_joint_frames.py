"""Joint entrance/frame local-polytope search at fixed per-helper dimensions."""
import os,sys,json,gzip,copy,time,functools
from pathlib import Path
from collections import Counter
import numpy as np
from scipy.optimize import linprog,milp,Bounds,LinearConstraint
from scipy.sparse import csc_matrix
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
w=copy.deepcopy(S.w);census=json.loads((OUT/'INTERFACE-CENSUS.json').read_text());domains={}
for g in census:
 if g['old_dim']>=g['hi_dim']:continue
 ds=[b for b in interval((),tuple(g['hi'])) if len(b)==g['old_dim']]
 for h in g['helpers']:domains[('S',h)]=ds;w['start_extra'][str(h)]=[]
print('SOURCE_DOMAINS',len(domains),Counter(len(v) for v in domains.values()),flush=True)
m=M.Model(w,relax_given=True);new=m.baseline()
for node,ds in domains.items():
 del m.fixed_frames[node];m.domain[node]=ds;new[node]=tuple(S.w['start_extra'][str(node[1])])
print('MODEL',len(m.domain),'components',len(m.components()),flush=True)
results=[]
for ci,comp in enumerate(m.components()):
 t=time.monotonic();labels,unary,pairs=m.component_problem(comp);rr,rhs,cols=M.lp(labels,unary,pairs);ri=[];cj=[];val=[]
 for j,(_,_,es) in enumerate(cols):
  for i,a in es:ri.append(i);cj.append(j);val.append(a)
 A=csc_matrix((np.array(val,float),(ri,cj)),shape=(len(rr),len(cols)));c=np.array([sum(n*S.cost_rank[d] for d,n in enumerate(vec)) for _,vec,_ in cols]);sol=linprog(c,A_eq=A,b_eq=rhs,bounds=(0,None),method='highs');assert sol.success,(ci,sol.message)
 fractional=int(sum(1e-7<x<1-1e-7 for x in sol.x));lp=float(sol.fun)
 if fractional:
  print('INTEGER',ci,'vars',len(cols),'fractional',fractional,flush=True)
  sol=milp(c,integrality=np.ones(len(cols)),bounds=Bounds(0,1),constraints=LinearConstraint(A,rhs,rhs),options={'time_limit':90});assert sol.x is not None,(ci,sol.message)
 choose={key[1]:key[2] for j,(key,_,_) in enumerate(cols) if key[0]=='x' and sol.x[j]>.9};assert len(choose)==len(comp);M.assignment_cost(labels,unary,pairs,choose);new.update(choose)
 r=dict(component=ci,nodes=len(comp),variables=len(cols),lp=lp,integer=float(sol.fun),fractional=fractional,seconds=time.monotonic()-t);results.append(r);print('COMPONENT',r,flush=True)
 (OUT/'JOINT-FRAME-SOLVES.json').write_text(json.dumps(results,indent=2)+'\n')
for i in range(len(m.gates)):
 fr=m.frame_of(('G',i),new)
 if i<m.nA:w['A'][i][-1]=list(fr)
 elif i<m.nA+m.nB:w['B'][i-m.nA][-1]=list(fr)
 else:w['early_cleanup'][i-m.nA-m.nB][1]=list(fr)
for node in domains:w['start_extra'][str(node[1])]=list(new[node])
profile=m.profile(new);assert Counter(profile)==S.promo.chain_profile(w)+Counter({8:8});w['report']['local_profile']={str(r):c for r,c in profile.items()};w['report']['local_rank_mass']=sum(r*c for r,c in profile.items());w['report']['width_inventory']={str(r):c for r,c in S.promo.widths(w).items()}
(OUT/'joint-frames.json.gz').write_bytes(gzip.compress(json.dumps(w,sort_keys=True,separators=(',',':')).encode(),mtime=0));changed={h:fr for h,fr in w['start_extra'].items() if fr!=S.w['start_extra'][h]};r=dict(status='NOMINATED_JOINT_ENTRANCE_FRAME_ASSIGNMENT_REQUIRES_NATIVE',profile=w['report']['local_profile'],changed_starts=changed,**S.screen(w));(OUT/'JOINT-FRAMES.json').write_text(json.dumps(r,indent=2)+'\n');print('JOINT_RESULT',json.dumps(r),flush=True)
