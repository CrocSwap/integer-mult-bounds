"""Exact elimination for the classical-matrix branch and all paid cost powers.

This derives the balance separately in the same research session. The cited
published matrix-exponent theorem is a mathematical input, not a finite test.
"""
import argparse,json
from fractions import Fraction as F
from pathlib import Path
assert __debug__
P=Path(__file__).resolve().parent
ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args()
receipt=json.loads((P/'CLASSICAL-BOUNDARY-ARITHMETIC.json').read_text())
source=json.loads((P/'PUBLISHED-THEOREM-SOURCE.json').read_text())
row=receipt['rows']['classical_matrix_12_5'];rat=lambda x:F(x['rational'])
pinned=F(json.loads((P/'SUPPLIER.json').read_text())['expected']['complex_lower'])
b=pinned-F(1,10**30);q=b-F(1,10**30);a=(q+b)/2
r=F(1,10**30);z=F(1,10**32);slack=F(1,10**30);stop=F(1,10**36)
tau=F(12,5);published=F('2.3728639');c=(3-tau)/2
assert source['arxiv']=='1401.7714v1' and 2<published<tau<F(5,2) and c==F(3,10)
# Solve E(1+q)+qX=1+q(1-r-z), -(1+q)E+2X=1/2+slack-r-z.
matrix=[[1+q,q,1+q*(1-r-z)],[-(1+q),F(2),F(1,2)+slack-r-z]]
factor=matrix[1][0]/matrix[0][0]
matrix[1]=[v-factor*w for v,w in zip(matrix[1],matrix[0])]
X=matrix[1][2]/matrix[1][1];E=(matrix[0][2]-matrix[0][1]*X)/matrix[0][0];B=1-X-r-z
assert (E,X,B)==tuple(rat(row[k])for k in ['epsilon','xi','beta'])
assert E*q==1-E+q*B and 1-E-B-F(1,2)+X==E*q+slack
assert 0<q<a<b<pinned<F('0.001733427039589844234749') and (1-stop)*b>a
assert F(1,2)<X<E<1 and 0<B<E and X-B-F(1,2)>0
assert 1-X-r-B==z>0 and 1-E-r>0 and B+2*(1-E)<1
costs={
 'main_transform':1-E*q,
 'global_coordinate_router':1-a,
 'fused_gaussian':E-q*B,
 'group_bit_router':E-a*B,
 'group_scans':E-B,
 'boundary_algebraic_matrix':E-X+(tau-1)/2,
 'sparse_union_movement':E+B+F(1,2)-X,
 'polynomial_products':1-E,
 'microbox_face_corrections':E+B+3-8+2,
}
k=F((E*q*10**48).__floor__(),10**48)-F(1,10**42)
assert k==rat(row['kappa']) and max(costs.values())==1-E*q
assert all(v<1-k for v in costs.values())
assert {n:1-v for n,v in costs.items()}=={n:rat(v) for n,v in row['margins'].items()}
assert len(row['strict_checks'])==47 and all(rat(x)>0 for x in row['strict_checks'].values())
assert len(receipt['rejecting_controls']['classical_matrix_12_5'])==6
# Replacing tau by a bound below the cited theorem would lack source support.
assert F(9,4)-published<0
# Reintroducing a full union-key sort fails the paid movement inequality.
assert costs['sparse_union_movement']+(B+1-E)>1-k
out=dict(status='PASS_SEPARATE_CLASSICAL_MATRIX_BALANCE',kappa=str(k),epsilon=str(E),cap=str(X),beta=str(B),cost_powers={n:str(v)for n,v in costs.items()},matrix_exponent=str(tau),published_bound=str(published),boundary_constant=str(c),strict_checks=47,rejecting_controls=6,source_input='Le Gall 2014, arXiv:1401.7714v1; established theorem, not re-proved here',scope='Separate derivation in the same research session; no independent human review. Inherited all-size assumptions remain.')
args.out.write_text(json.dumps(out,sort_keys=True,indent=2)+'\n');print(out['status'])
