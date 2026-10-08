import sys as _checked_runtime
if _checked_runtime.flags.optimize:
    raise SystemExit('Checked audit requires Python without -O')
from fractions import Fraction as Q
from pathlib import Path
import json,sys

def add(x,y):return x[0]+y[0],x[1]+y[1]
def scale(k,x):return k*x[0],k*x[1]
def mul(x,y):return x[0]*y[0]-x[1]*y[1],x[0]*y[1]+x[1]*y[0]
def C(u,n=4):return [[scale(Q(1,2),add((1,1)if y==x else(0,0),(1,-1)if y==x^u else(0,0)))for y in range(n)]for x in range(n)]
def combine(A,B,s=1,divisor=1):return [[scale(Q(1,divisor),add(a,scale(s,b)))for a,b in zip(ra,rb)]for ra,rb in zip(A,B)]
def char(s,n=4):return [((-1)**((s&x).bit_count()%2),0)for x in range(n)]
def action(A,f):
 out=[]
 for row in A:
  z=(Q(0),Q(0))
  for a,b in zip(row,f):z=add(z,mul(a,b))
  out.append(z)
 return out
c1,c2=C(1),C(2);sumop=combine(c1,c2);avg=combine(c1,c2,divisor=2);diff=combine(c1,c2,s=-1)
controls=[]
for name,A,expected in [('sum',sumop,[(2,0),(1,1),(1,1),(0,2)]),('average',avg,[(1,0),(Q(1,2),Q(1,2)),(Q(1,2),Q(1,2)),(0,1)]),('difference',diff,[(0,0),(-1,1),(1,-1),(0,0)])]:
 norms=[]
 for mask,ev in enumerate(expected):
  f=char(mask);assert action(A,f)==[mul(ev,z)for z in f]
  norms.append(ev[0]*ev[0]+ev[1]*ev[1])
 controls.append({'operator':name,'all_character_eigenvalues':[list(map(str,z))for z in expected],'eigenvalue_norms_squared':list(map(str,norms)),'single_fourth_root_phase_child':False,'scalar_multiple_of_one_phase_child':False,'has_nonzero_character_in_kernel':name=='difference','invertible_over_Gaussian_rationals':all(ev!=(0,0)for ev in expected)})
 # A scalar multiple of a unitary phase child has equal eigenvalue modulus at every character.
 assert norms[0]!=norms[1]
assert any(cell!=(0,0)for row in diff for cell in row)
for s in range(4):
 for t in range(4):assert sum(char(s)[x][0]*char(t)[x][0]for x in range(4))==4*int(s==t)
receipt={'status':'PASS_exact_phase_class_closure_obstructions','dimension':2,'translation_algebra_commutativity_unchanged':True,'controls':controls,'terminology':'C1+C2 and its average remain invertible over complex/Gaussian rational coefficients. They are not unitary/fourth-root phase children, nor scalar multiples of one. C1-C2 is nonzero and singular.','scope':'Input linear forms in mixed2208operatoralgorithm can leave admissiblephasechildclass; algebraiccommutativitydoesnotcertifypaidchildwidth/profile/tapecosts.'}
Path(sys.argv[1]).write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
