if not __debug__:
 raise RuntimeError('Assertions are required; run without optimized Python.')
"""Independent exact-rational weak-duality/lattice certificate, no upstream checker import."""
from pathlib import Path
from fractions import Fraction as F
from collections import Counter
from math import prod
import json,gzip,importlib.util,time,hashlib,heapq
import numpy as np
from scipy.optimize import linprog
HERE=Path(__file__).resolve().parent
sp=importlib.util.spec_from_file_location('own_bounds',HERE.parent/'independent.py');bounds=importlib.util.module_from_spec(sp);sp.loader.exec_module(bounds)
rd=lambda p:json.loads(gzip.decompress(p.read_bytes())if p.suffix=='.gz'else p.read_bytes())
def main(pkg,out):
 start=time.process_time();pins=rd(HERE/'SOURCE-PINS.json');assert all(hashlib.sha256((HERE/n).read_bytes()).hexdigest()==h for n,h in pins['sha256'].items());manifest=rd(pkg/'MANIFEST.json');assert all(hashlib.sha256((pkg/n).read_bytes()).hexdigest()==h for n,h in manifest.items());out.mkdir(parents=True,exist_ok=False);a=F('0.0017161404259975');pv=rd(pkg/'PROVIDERS.json');assert pv['gauge44']==pv['extra'];W=[4,5,7,8,9];widths=Counter(pv['gauge44']['widths']);N=[666*widths[w]for w in W];paid={int(k):v for k,v in pv['gauge44']['actual_paid_profile'].items()};parent=rd(pkg/'GLOBAL-TEMPLATE.json.gz');B=Counter()
 for c in parent['idle_children']:B[c['rank']]+=2*c['replicas']
 assert dict(B)=={8:49728,16:33152,32:33152,48:33152};caps=sorted(B)
 def patterns(cap,i=0):
  if i==len(W):yield ();return
  for k in range(cap//W[i]+1):
   for rest in patterns(cap-k*W[i],i+1):yield(k,)+rest
 P=[(c,p)for c in caps for p in patterns(c)];idle=lambda c,p:c-sum(w*k for w,k in zip(W,p));den=1<<256
 def down(q):return F(q.numerator*den//q.denominator,den)
 phi={0:F(0)}
 for z in range(1,max(caps)+1):phi[z]=down(bounds.cost(z,a)[0]/66304)
 A=[[int(c==cc)for cc in caps]+list(p)for c,p in P];rhs=[float(phi[idle(c,p)])*10**6 for c,p in P];sol=linprog([-B[c]for c in caps]+[-n for n in N],A_ub=np.array(A),b_ub=rhs,bounds=[(None,None)]*9,method='highs');assert sol.success
 pi=[F.from_float(float(v))/10**6 for v in sol.x[4:]];dot=lambda p:sum(k*q for k,q in zip(p,pi));y={c:min(phi[idle(cc,p)]-dot(p)for cc,p in P if cc==c)for c in caps}
 # A triangular integer lattice basis; validate full rank, every generator, index, and complete quotient.
 Z=[(8,(0,0,0,1,0)),(16,(0,0,0,2,0)),(16,(0,0,1,0,1)),(32,(0,0,0,0,3)),(32,(0,0,0,4,0)),(32,(0,0,1,2,1)),(32,(0,0,2,0,2)),(32,(0,1,0,0,3)),(32,(1,0,0,0,3)),(48,(0,0,0,0,0)),(48,(0,0,0,0,5))]
 vec=lambda c,p:tuple([int(c==cc)for cc in caps]+list(p));rows=[list(vec(c,p))for c,p in Z];basis=[]
 for j in range(9):
  nz=[r for r in rows if r[j]];rows=[r for r in rows if not r[j]]
  while len(nz)>1:
   nz.sort(key=lambda r:abs(r[j]));pivot=nz[0];next_=[pivot]
   for row in nz[1:]:
    q=row[j]//pivot[j];row=[x-q*z for x,z in zip(row,pivot)];(next_ if row[j]else rows).append(row)
   nz=next_
  assert nz;row=nz[0];row=[-x for x in row]if row[j]<0 else row;basis.append(row)
 assert all(not any(r)for r in rows);index=prod(basis[j][j]for j in range(9));assert index==20
 def red(v):
  v=list(v)
  for j,row in enumerate(basis):q=v[j]//row[j];v=[x-q*z for x,z in zip(v,row)]
  return tuple(v)
 zero=(0,)*9;assert all(red(vec(c,p))==zero for c,p in Z);best={}
 for c,p in P:
  rc=phi[idle(c,p)]-dot(p)-y[c];assert rc>=0;g=red(vec(c,p))
  if g!=zero and(g not in best or rc<best[g]):best[g]=rc
 dist={zero:F(0)};queue=[(F(0),zero)]
 while queue:
  d,g=heapq.heappop(queue)
  if d!=dist[g]:continue
  for h,v in best.items():
   z=red([x+y for x,y in zip(g,h)]);cand=d+v
   if z not in dist or cand<dist[z]:dist[z]=cand;heapq.heappush(queue,(cand,z))
 assert len(dist)==index;target=red([B[c]for c in caps]+N);lb=sum(B[c]*y[c]for c in caps)+sum(n*q for n,q in zip(N,pi))+dist[target];paidlb=sum(666*n*bounds.cost(r,a)[0]/66304 for r,n in paid.items());total=down(lb+paidlb);assert total>1
 candidate_price=rd(HERE.parent/'evidence/EXACT-PRICE.json');candidate=F(candidate_price['endpoint']['lower']);baseline=F(rd(HERE/'PR2696-CLAIM.json')['kappa']);gap=a-candidate;ratio=(candidate-baseline)/(a-baseline);assert 0<ratio<1
 result={'source_bindings':{str(q.relative_to(HERE.parent))if q.is_relative_to(HERE.parent)else str(q):hashlib.sha256(q.read_bytes()).hexdigest()for q in [Path(__file__),HERE.parent/'independent.py',HERE/'SOURCE-PINS.json',HERE/'PR2696-CLAIM.json',HERE.parent/'evidence/EXACT-PRICE.json',pkg/'MANIFEST.json',*[pkg/n for n in sorted(manifest)]]},'candidate_C_lower':str(candidate),'baseline_PR2696_headline':str(baseline),'remaining_endpoint_gap_upper':str(gap),'fraction_baseline_to_ceiling_gain_realized_lower':str(ratio),'status':'PASS_EXACT_RATIONAL_INVENTORY_CEILING','endpoint_upper':str(a),'moment_lower':str(total),'moment_margin':str(total-1),'moment_margin_float':float(total-1),'bins':dict(B),'per_call_width_counts':dict(widths),'calls':666,'paid_per_call':paid,'patterns':len(P),'lattice_index':index,'quotient_states':len(dist),'integrality_correction':str(dist[target]),'pi_exact':[str(q)for q in pi],'y_exact':{str(c):str(v)for c,v in y.items()},'CPU_seconds':time.process_time()-start,'scope':'Any literal packing of the fixed415-width inventory into these fixed18childfamilies×74replicas×112ports bins, with identical fixedpaidlocalprofile and666calls; ignoreswindow/familyconstraints andthereforeappliestoallinvocationorders preservingthisinventory/stock. Boundsnativecomplexmomentroot;conservativecostisnolower. Notboundonchangedwords,inventory,childbingeometry,callcountorallsuppliers.'};(out/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:result[k]for k in ['status','patterns','lattice_index','moment_margin_float','CPU_seconds']}))
if __name__=='__main__':
 import sys;import argparse
 ap=argparse.ArgumentParser();ap.add_argument('--work',type=Path,required=True);ap.add_argument('--context',type=Path,default=HERE.parent/'independent-inputs');a=ap.parse_args();assert not a.work.resolve().is_relative_to(HERE.parent.resolve());main(a.context,a.work)
