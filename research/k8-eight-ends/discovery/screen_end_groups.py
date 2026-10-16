import os
import json,gzip,copy,importlib.util,math,itertools,time
from pathlib import Path
from collections import Counter
import numpy as np
from scipy.optimize import linprog,milp,Bounds,LinearConstraint,brentq
from scipy.sparse import csc_matrix
P=Path(__file__).resolve().parent;ROOT=P.parents[2]
def mod(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
M=mod('M',P/'frame_model.py');promo=mod('promo',ROOT/'research/gauge44-slots/construction/promo/build_promotion.py')
w=json.loads(gzip.decompress(Path(os.environ['K8_BASE_WORD']).read_bytes()));b=.001675
cost_rank=[0,0]+[(r**(1-b)-r)/b for r in range(2,10)]
def optimize(nw):
 m=M.Model(nw,relax_given=True);new=m.baseline();gaps=[]
 for comp in m.components():
  labels,unary,pairs=m.component_problem(comp);rr,rhs,cols=M.lp(labels,unary,pairs);ri=[];ci=[];val=[]
  for j,(_,_,es) in enumerate(cols):
   for i,a in es:ri.append(i);ci.append(j);val.append(a)
  A=csc_matrix((np.array(val,float),(ri,ci)),shape=(len(rr),len(cols)));c=np.array([sum(n*cost_rank[d] for d,n in enumerate(vec)) for _,vec,_ in cols]);sol=linprog(c,A_eq=A,b_eq=rhs,bounds=(0,None),method='highs');assert sol.success
  if any(1e-7<x<1-1e-7 for x in sol.x):
   sol=milp(c,integrality=np.ones(len(cols)),bounds=Bounds(0,1),constraints=LinearConstraint(A,rhs,rhs),options={'time_limit':10});assert sol.x is not None
  choose={key[1]:key[2] for j,(key,_,_) in enumerate(cols) if key[0]=='x' and sol.x[j]>.9};assert len(choose)==len(comp);M.assignment_cost(labels,unary,pairs,choose);new.update(choose)
 for i in range(len(m.gates)):
  fr=m.frame_of(('G',i),new)
  if i<m.nA:nw['A'][i][-1]=list(fr)
  elif i<m.nA+m.nB:nw['B'][i-m.nA][-1]=list(fr)
  else:nw['early_cleanup'][i-m.nA-m.nB][1]=list(fr)
 profile=m.profile(new);assert Counter(profile)==promo.chain_profile(nw)+Counter({8:8});nw['report']['local_profile']={str(r):c for r,c in profile.items()};nw['report']['local_rank_mass']=sum(r*c for r,c in profile.items());nw['report']['width_inventory']={str(r):c for r,c in promo.widths(nw).items()};return nw

def screen(nw):
 inv=promo.widths(nw);ws=sorted(inv);caps={8:672,16:448,32:448,48:448};cols=[];idle=[]
 for i,cap in enumerate(caps):
  for ns in itertools.product(*(range(cap//r+1) for r in ws)):
   used=sum(r*n for r,n in zip(ws,ns))
   if used>cap:continue
   cols.append([int(i==j) for j in range(4)]+list(ns));idle.append(cap-used)
 A=np.array(cols).T;rhs=np.array(list(caps.values())+[9*inv[r] for r in ws]);c=np.array([r*math.expm1(b*math.log(73/r))/b if r else 0 for r in idle]);sol=linprog(c,A_eq=A,b_eq=rhs,bounds=(0,None),method='highs');assert sol.success
 H=Counter({int(r):9*c for r,c in nw['report']['local_profile'].items()})
 for r,x in zip(idle,sol.x):
  if r and x>1e-8:H[r]+=x
 root=brentq(lambda z:sum(c*(r/73)**(1-z) for r,c in H.items())/896-1,0,.005,xtol=1e-15)
 return dict(complex_relaxed=root,kappa_relaxed=root/(1+root),widths=dict(inv))
if __name__=='__main__':
 results=[]
 for i,g in enumerate([None]+json.loads((P/'END-GROUPS.json').read_text())):
  nw=copy.deepcopy(w);t=time.monotonic()
  if g:
   for q in g['helpers']:nw['helper_final'][str(q)]=g['new']
  try:
   nw=optimize(nw);r=dict(group=i-1,helpers=g['helpers'] if g else [],profile=nw['report']['local_profile'],**screen(nw));(P/f'end-group-{i-1}.json.gz').write_bytes(gzip.compress(json.dumps(nw,sort_keys=True,separators=(',',':')).encode(),mtime=0))
  except AssertionError as e:r=dict(group=i-1,status='INFEASIBLE',reason=str(e))
  r['seconds']=time.monotonic()-t;results.append(r);print(json.dumps(r),flush=True);(P/'END-GROUP-SCREEN.json').write_text(json.dumps(results,indent=2)+'\n')
