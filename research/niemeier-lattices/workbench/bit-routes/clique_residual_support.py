"""Exact cap-span witness for a natural column of the spinor residual."""
from pathlib import Path
WORKBENCH = Path(__file__).resolve().parents[1]
PACKAGE = WORKBENCH.parent
import json
import sympy as sp
D=14
H={sum((((a&j).bit_count()&1)<<(j-1))for j in range(1,15))for a in range(16)}
support=[m for m in range(1<<D)if m.bit_count()in(7,8)and m not in H]
def port(m):return [1]+[1-2*((m>>i)&1)for i in range(D)]+[1-2*(m.bit_count()%2)]
def require(b,s):
 if not b:raise ValueError(s)
require(len(support)==6420,'Exact natural-column support count')
require(all(sum(port(m))==0 for m in support),'All targets lie in the all-positive port cap')
basis={};witness=[]
for m in support:
 row=[a%101 for a in port(m)[1:]]
 for pivot,old in sorted(basis.items()):
  c=row[pivot];row=[(a-c*b)%101 for a,b in zip(row,old)]
 nonzero=[i for i,c in enumerate(row)if c]
 if nonzero:
  pivot=nonzero[0];scale=pow(row[pivot],-1,101);basis[pivot]=[a*scale%101 for a in row];witness.append(m)
 if len(basis)==15:break
require(len(basis)==15,'Full rank15 inside the rational cap')
minor=sp.Matrix([port(m)[1:]for m in witness]);det=int(minor.det())
require(det!=0 and det%101!=0,'Nonzero exact integer fifteen-by-fifteen minor')
result={'status':'PASS_EXACT_RESIDUAL_COLUMN_CAP_SPAN','column_port':0,
 'support_count':len(support),'rational_support_rank':15,
 'support_witness_ports':witness,'support_witness_vectors':[port(m)for m in witness],
 'removed_coordinate':0,'minor_determinant':det,'modular_prime':101,
 'common_target_cap_dimension':1,'natural_column_basis_size':1268,
 'full_frame_to_common_cap_rank':15,'literal_private_copy_rank_mass':1268*15,
 'spinor_port_count':16384,'excess_over_port_count':1268*15-16384,
 'translation_proof':'XOR translation by j multiplies the sixteen real coordinates by the signs of the doubled spinor port j; this is an invertible diagonal orthogonal transformation and preserves the subgroup-removed support relation.',
 'scope':'The literal natural-column rank-basis implementation with full-frame aggregates and separately lowered private decoder copies. Not a lower bound for arbitrary rank factorizations, alternate bases, or fused shared DAGs.'}
(WORKBENCH / 'bit-routes/CLIQUE-RESIDUAL-SUPPORT.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items()if k!='support_witness_vectors'},indent=2))
