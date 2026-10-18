"""Exact hosted residual crossing a two-family shear. Apache-2.0."""
from pathlib import Path
from itertools import product
from collections import Counter
import json,hashlib,subprocess,sys
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def need(ok,msg):
 if not ok:raise ValueError(msg)
def rank(rows):
 p={}
 for v in rows:
  while v:
   k=v.bit_length()-1
   if k not in p:p[k]=v;break
   v^=p[k]
 return len(p)
def act(M,x):return sum(((r&x).bit_count()%2)<<i for i,r in enumerate(M))
def mul(A,B):return tuple(__import__('functools').reduce(int.__xor__,(B[j] for j in range(len(B)) if r>>j&1),0) for r in A)
def add(A,B):return tuple(x^y for x,y in zip(A,B))
def inverse(M):
 n=len(M);rows=[r|1<<(n+i) for i,r in enumerate(M)]
 for c in range(n):
  k=next(i for i in range(c,n) if rows[i]>>c&1);rows[c],rows[k]=rows[k],rows[c]
  for i in range(n):
   if i!=c and rows[i]>>c&1:rows[i]^=rows[c]
 return tuple(r>>n for r in rows)
def main():
 for p in json.loads((HERE/'SOURCES.json').read_text())['files']:
  b=subprocess.check_output(['git','cat-file','blob',p['git_blob']],cwd=ROOT)
  need(hashlib.sha256(b).hexdigest()==p['sha256'],'Git provenance')
  if p['usage']=='input':need((ROOT/p['path']).read_bytes()==b,'source drift')
 results=[];dirty=0
 for n in (2,3):
  mats=list(product(range(1<<n),repeat=n));gl=[r for r in mats if rank(r)==n];I=tuple(1<<i for i in range(n))
  source_hist=Counter();target_hist=Counter();side_difference=0;tests=0
  for R,A in product(gl,mats):
   Ri=inverse(R);E=add(R,I)
   Ds=mul(A,E);Dt=mul(E,A)
   source_hist[rank(Ds)]+=1;target_hist[rank(Dt)]+=1
   side_difference+=(bool(any(Ds))!=bool(any(Dt)))
   need(mul(R,Ri)==I and mul(Ri,R)==I,'inverse')
   # Rank-nullity through A restricted to im(E), checked using exact images.
   image={act(E,x) for x in range(1<<n)}
   intersection={v for v in image if act(A,v)==0}
   need(rank(Ds)==rank(E)-(len(intersection).bit_length()-1),'image-kernel defect rank')
   if rank(A)==n:need(rank(Ds)==rank(E)==rank(Dt),'invertible crossing floor')
   # Exact block equality on every input basis establishes all dirty linear inputs.
   basis=[(1<<i,0) for i in range(n)]+[(0,1<<i) for i in range(n)]
   inputs=list(product(range(1<<n),repeat=2)) if n==2 else basis
   for x,y in inputs:
    # Original: source residual then bridge. Moved: bridge, defect, residual.
    original=(act(R,x),y^act(A,act(R,x)))
    moved=(act(R,x),y^act(A,x)^act(Ds,x))
    need(original==moved,'source crossing identity')
    # Target residual then bridge. Moved: bridge, residual, target correction.
    original=(x,act(R,y)^act(A,x))
    moved=(x,act(R,y^act(A,x))^act(Dt,x))
    need(original==moved,'target crossing identity')
    dirty+=1
   # A post-residual source adapter must read the current source chart.
   K=mul(Ds,Ri);need(mul(K,R)==Ds,'post-residual adapter chart')
   tests+=1
  results.append({'dimension':n,'invertible_residuals':len(gl),'bridges':len(mats),'pairs':tests,'source_defect_ranks':dict(sorted(source_hist.items())),'target_defect_ranks':dict(sorted(target_hist.items())),'source_target_zero_test_disagreements':side_difference})
 # Noncommuting2D fixture; one wrong side of the annihilator gives opposite verdicts.
 R=(2,1);A=(3,0);I=(1,2);E=add(R,I);Ds=mul(A,E);Dt=mul(E,A)
 need(Ds==(0,0) and Dt!=(0,0),'orientation-specific annihilator')
 # An invertible bridge cannot hide a nonidentity residual; omitting the adapter fails.
 A=(1,2);Ds=mul(A,E);x=1;y=2
 need((act(R,x),y^act(A,act(R,x)))!=(act(R,x),y^act(A,x)),'missing correction control')
 # Wrong current-source coordinates also fail when R has order3.
 R3=(2,3);A=(1,2);D=mul(A,add(R3,I));Ri=inverse(R3)
 need(mul(D,R3)!=D and mul(mul(D,Ri),R3)==D,'wrong-chart control')
 # Independent literal XOR implementation for all2D unit-entry gates, all16dirty states.
 literal=0
 for R in [r for r in product(range(4),repeat=2) if rank(r)==2]:
  for A in product(range(4),repeat=2):
   D=mul(A,add(R,(1,2)))
   for x,y in product(range(4),repeat=2):
    bits=[x&1,x>>1,y&1,y>>1]
    for M in (A,D):
     for i,row in enumerate(M):
      for j in range(2):
       if row>>j&1:bits[2+i]^=bits[j]
    got=bits[2]|bits[3]<<1
    need(got==y^act(A,act(R,x)),'literal scalar entry engine');literal+=1
 out={'censuses':results,'all_dirty_or_basis_inputs':dirty,'independent_literal_states':literal,'controls':3,'scope':'Exact linear two-family interface; rank-one scalar adapter budget, not recursive address-frame rank or selected bridge admission.'}
 if '--write' in sys.argv:(HERE/'RESULT.json').write_text(json.dumps(out,indent=2)+'\n')
 else:need(json.loads((HERE/'RESULT.json').read_text())==json.loads(json.dumps(out)),'certificate mismatch')
 print('PASS_HOSTED_SHEAR_CROSSING pairs='+str(sum(r['pairs'] for r in results))+' input_checks='+str(dirty)+' literal='+str(literal))
if __name__=='__main__':main()
