"""Solve the Strassen balance by exact elimination and compare the paid ledger."""
import argparse,json
from fractions import Fraction as F
from pathlib import Path
assert __debug__
P=Path(__file__).resolve().parent
ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args()
receipt=json.loads((P/'FRONTIER-FUSION-ARITHMETIC.json').read_text())
row=receipt['rows']['strassen']; rat=lambda x:F(x['rational'])
b=F('0.00167975495612');q=b-F(1,10**10);a=(b+q)/2
r=F(1,10**6);z=F(1,10**8);slack=F(1,10**5);c=F(3,32)
# E(1+q)+qX=1+q(1-r-z); -(1+q)E+X=slack-c.
matrix=[[1+q,q,1+q*(1-r-z)],[-(1+q),F(1),slack-c]]
factor=matrix[1][0]/matrix[0][0]
matrix[1]=[v-factor*w for v,w in zip(matrix[1],matrix[0])]
X=matrix[1][2]/matrix[1][1];E=(matrix[0][2]-matrix[0][1]*X)/matrix[0][0];B=1-X-r-z
assert (E,X,B)==tuple(rat(row[k])for k in ['epsilon','xi','beta'])
assert E*q==1-E+q*B and c+X-E==E*q+slack
assert 7**16<2**45 and 0<q<a<b<F(receipt['complex_lower_pinned']['rational'])<F('0.001733427039589844234749')
assert (1-F(1,10**9))*b>a
margins=[E*q,a,1-E+q*B,1-E+a*B,1-E+B,c+X-E,1-E-B-F(1,2)+X,E,4-E-B,1-E-B-F(1,2)+X-(B+1-E)]
k=F((E*q*10**18).__floor__(),10**18)-F(1,10**11)
assert k==F('0.001677201606743120')==rat(row['kappa'])
assert min(margins)==E*q and all(x>k for x in margins)
assert len(row['strict_checks'])==45 and all(rat(x)>0 for x in row['strict_checks'].values())
assert len(receipt['rejecting_controls']['strassen'])==5
out=dict(status='PASS_SEPARATE_EXACT_BALANCE_DERIVATION',kappa=str(k),epsilon=str(E),cap=str(X),beta=str(B),cost_rows=len(margins),strict_checks=45,rejecting_controls=5,scope='Separate derivation in the same research session; not independent human review. Only the Strassen branch is claimed.')
args.out.write_text(json.dumps(out,sort_keys=True,indent=2)+'\n');print(out['status'])
