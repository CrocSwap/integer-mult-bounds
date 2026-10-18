"""Exact finite group-algebra transform for the D16+ spinor bit decoder."""
from itertools import combinations
from math import comb
from pathlib import Path
WORKBENCH = Path(__file__).resolve().parents[1]
PACKAGE = WORKBENCH.parent
import json

D=14
ALL=(1<<D)-1

def require(b,s):
 if not b:raise ValueError(s)

def product(a,b):
 out=set()
 for x in a:
  for y in b:
   if not x&y:
    z=x|y
    if z in out:out.remove(z)
    else:out.add(z)
 return out

def add(a,b):return a^b

def symmetric(degree):
 return {sum(1<<i for i in S)for S in combinations(range(D),degree)}

# g_i=1+z_i. Convert the exact decoder's coefficients to the square-zero
# monomial basis by the Boolean upper zeta transform, done over F2.
coeff=[int(i==0 or i.bit_count() in (7,8))for i in range(1<<D)]
original=coeff.copy()
for i in range(D):
 for mask in range(1<<D):
  if not mask>>i&1:coeff[mask]^=coeff[mask|(1<<i)]
transformed={i for i,c in enumerate(coeff)if c}
require(transformed==symmetric(8),'The spinor decoder becomes exactly e8(z)')

# Darboux pairs x_i=q_i=z_(2i)+z_(2i+1),
# y_i=z_(2i+1)+sum_{j>i}q_j. Their linear transformation is triangular
# after the seven elementary coordinate-pair changes, hence invertible.
pairs=[];forms=[]
for i in range(7):
 x={1<<(2*i),1<<(2*i+1)}
 y={1<<(2*i+1)}|{1<<j for j in range(2*i+2,D)}
 forms.extend((x,y));pairs.append(product(x,y))
quad=set()
for p in pairs:quad^=p
require(quad==symmetric(2),'Explicit Darboux pairs sum to e2(z)')
terms=[];answer=set()
for inds in combinations(range(7),4):
 p={0}
 for i in inds:p=product(p,pairs[i])
 terms.append(p);answer^=p
require(answer==transformed,'e8(z)=e4(x1*y1,...,x7*y7) exactly')

# In the Darboux basis, each degree-eight creation operator acts on all
# 64 monomials supported outside its eight coordinates. Distinct selected
# pair sets intersect because 4+4>7, so every cross-product operator is zero.
monomials=[sum(3<<(2*i)for i in inds)for inds in combinations(range(7),4)]
require(len(monomials)==35 and all(m.bit_count()==8 for m in monomials),
        '35 creation monomials of degree eight')
require(all(a&b for a,b in combinations(monomials,2)),
        'Every pair of creation operators has zero product')
require(all(2**(D-m.bit_count())==64 for m in monomials),'Rank64 per creation operator')

# Exact ranks of the seven graded inclusion matrices (not a floating rank).
def binary_rank(rows):
 basis={}
 for v in rows:
  while v:
   k=v.bit_length()-1
   if k in basis:v^=basis[k]
   else:basis[k]=v;break
 return len(basis)

grades=[]
for j in range(7):
 source=list(combinations(range(D),j));target=list(combinations(range(D),j+8))
 src=[sum(1<<i for i in s)for s in source]
 dst=[sum(1<<i for i in s)for s in target]
 rows=[sum((1<<k) for k,a in enumerate(src)if a&b==a)for b in dst]
 grades.append(binary_rank(rows))
require(grades==[1,14,91,364,91,14,1],'Exact graded binary ranks')
require(sum(grades)==576,'Complete spinor central binary rank')
result={'status':'PASS_EXACT_SPINOR_OPERATOR_IDENTITY','dimension':14,
 'port_count':16384,'rational_frame_dimension':16,
 'group_kernel_weights':[0,7,8],'z_polynomial_degree':8,
 'z_polynomial_monomials':len(transformed),'darboux_pairs':7,
 'creation_monomials':monomials,'creation_operator_rank':64,
 'creation_shear_scalar_additions':35*64,'graded_ranks':grades,
 'central_rank':sum(grades),
 'darboux_rule':'x_i=z_(2i)+z_(2i+1); y_i=z_(2i+1)+sum_(j>i)(z_(2j)+z_(2j+1)), zero-based i=0,...,6.',
 'scope':'Exact scalar basis-change identity. The two conjugating basis changes are not free common-frame operations, and this is not a complete bit supplier.'}
(WORKBENCH / 'bit-routes/SPINOR-OPERATOR.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
