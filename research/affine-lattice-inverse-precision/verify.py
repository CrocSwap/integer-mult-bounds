"""Exact affine reachable-lattice precision criterion. Apache-2.0."""
from fractions import Fraction as F
from itertools import product
from math import lcm
from pathlib import Path
import json,hashlib,subprocess,sys
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def need(ok,msg):
 if not ok:raise ValueError(msg)
def rnd(t,b):
 v=t*(1<<b)+F(1,2);return F(v.numerator//v.denominator,1<<b)
def criterion(c,q,w,v):
 need(0<=w<v,'precision ordering')
 return all((a*(1<<w)).denominator==1 for a in q) and rnd(c,w)==rnd(c,v)
def residue_oracle(c,q,w,v):
 periods=[(x*(1<<w)).denominator for x in q]
 return all(rnd(c+sum(a*k for a,k in zip(q,z)),w)==rnd(c+sum(a*k for a,k in zip(q,z)),v) for z in product(*(range(d) for d in periods)))
def main():
 for p in json.loads((HERE/'SOURCES.json').read_text())['files']:
  b=subprocess.check_output(['git','cat-file','blob',p['git_blob']],cwd=ROOT)
  need(hashlib.sha256(b).hexdigest()==p['sha256'],'provenance')
  if p['usage']=='input':need((ROOT/p['path']).read_bytes()==b,'source drift')
 qs=sorted({F(n,d) for n in range(-6,7) for d in range(1,10)})
 cs=sorted({F(n,d) for n in range(-5,6) for d in range(1,8)})
 scalar=good=0
 for q,c,w,delta in product(qs,cs,range(3),range(1,4)):
  expected=criterion(c,[q],w,w+delta)
  need(expected==residue_oracle(c,[q],w,w+delta),'scalar residue oracle')
  scalar+=1;good+=expected
 # Correlated2D domains: every2x2 A and B from a fixed rational alphabet,
 # and a finite complete period in each integer parameter.
 aa=list(product((F(0),F(1,2),F(1)),repeat=4))
 bb=list(product((-1,0,1),repeat=4)); matrices=matrix_good=0
 for av,bv in product(aa,bb):
  A=[av[:2],av[2:]];B=[bv[:2],bv[2:]]
  Q=[[sum(A[i][k]*B[k][j] for k in range(2)) for j in range(2)] for i in range(2)]
  for x0 in product((F(0),F(1,4)),repeat=2):
   c=[sum(A[i][k]*x0[k] for k in range(2)) for i in range(2)]
   for w in (0,1):
    answer=all(criterion(c[i],Q[i],w,w+1) for i in range(2))
    direct=all(residue_oracle(c[i],Q[i],w,w+1) for i in range(2))
    need(answer==direct,'matrix residue oracle');matrices+=1;matrix_good+=answer
 # Positive correlated domain: A=(1/2,1/2), B columns(1,1),(1,-1).
 # AB=(1,0): nonintegral A is harmless on this index2source lattice.
 need(criterion(F(0),[F(1),F(0)],0,3),'correlated fixture')
 need(not criterion(F(0),[F(1,2),F(1,2)],0,3),'uncorrelated control')
 # Integral step is not enough when the affine offset lies on the wrong rounding cell.
 need(not criterion(F(1,2),[F(1)],0,1),'offset control')
 # Safe nonzero offset demonstrates that exact coarse-grid membership is too strong.
 need(criterion(F(1,16),[F(1)],0,2),'safe offset fixture')
 # A finite subset is not an unrestricted lattice: only z=0 is safe here.
 need(rnd(F(0),0)==rnd(F(0),1) and rnd(F(1,2),0)!=rnd(F(1,2),1),'bounded-domain control')
 # Paired signed shears cancel arbitrary target dirt on a safe correlated domain.
 dirty=0
 for z1,z2,y in product(range(-8,9),range(-8,9),(F(-3,7),F(0),F(5,9))):
  x=(z1+z2,z1-z2);a=F(sum(x),2)
  need(y+rnd(a,0)-rnd(a,3)==y,'dirty cancellation');dirty+=1
 result={'scalar_cases':scalar,'scalar_safe':good,'matrix_affine_cases':matrices,'matrix_safe':matrix_good,'dirty_trials':dirty,'controls':5,'criterion':'2^w*A*B integral and Q_w(A*x0)=Q_v(A*x0), for every x=x0+Bz,z integer; w<v','scope':'Rounded-linear increments only; internal nonlinear rounding and bounded nonlattice sets are outside.'}
 if '--write' in sys.argv:(HERE/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
 else:need(json.loads((HERE/'RESULT.json').read_text())==result,'certificate mismatch')
 print('PASS_AFFINE_LATTICE_PRECISION scalar='+str(scalar)+' matrix='+str(matrices)+' dirty='+str(dirty))
if __name__=='__main__':main()
