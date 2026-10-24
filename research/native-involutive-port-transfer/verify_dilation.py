"""Portable exact Gram-code involution and three-shear replay (stdlib only)."""
from pathlib import Path
from fractions import Fraction as Q
from hashlib import sha256
import json
HERE=Path(__file__).resolve().parent
INPUT_SHA='759acb219e3b5097b10cc69ddbee54040a68f23fba689f0d2a49d1c11e0324b2'
def need(c,m):
 if not c:raise ValueError(m)
def mm(A,B):return [[sum((x*y for x,y in zip(r,c)),Q(0))for c in zip(*B)]for r in A]
def eye(n):return [[Q(i==j)for j in range(n)]for i in range(n)]
def scale(A,c):return [[c*x for x in r]for r in A]
def add(A,B):return [[x+y for x,y in zip(r,s)]for r,s in zip(A,B)]
def transpose(A):return list(map(list,zip(*A)))
def completion(A,R):
 Rt=transpose(R)
 return [A[i]+[3*x for x in Rt[i]]for i in range(112)]+[[-x for x in R[i]]+[Q(13*(i==j))for j in range(8)]for i in range(8)]
def replay_shears(R,x,h):
 # Chronological J, Sx(Rt/4), Sy(-R), Sx(Rt/4).
 h=[-v for v in h]
 Rt=transpose(R)
 def sx(x,h):return [x[i]+sum((Rt[i][k]*h[k]/4 for k in range(8)),Q(0))for i in range(112)]
 x=sx(x,h)
 h=[h[k]-sum((R[k][i]*x[i]for i in range(112)),Q(0))for k in range(8)]
 x=sx(x,h)
 return x+h
def main():
 raw=(HERE/'DYADIC-DILATION-INPUTS.json').read_bytes()
 need(sha256(raw).hexdigest()==INPUT_SHA,'Frozen source-derived input hash')
 source=json.loads(raw)
 R=[[Q(x)for x in r]for r in source['R']];A=[[Q(x)for x in r]for r in source['A']]
 need(len(R)==8 and all(len(r)==112 for r in R),'R dimensions')
 need(len(A)==112 and all(len(r)==112 for r in A),'A dimensions')
 Rt=transpose(R);G=mm(Rt,R)
 need(mm(R,Rt)==scale(eye(8),56),'RRt=56I8')
 need(A==add(eye(112),scale(G,Q(-1,4))),'A=I-RtR/4')
 C=completion(A,R)
 need(mm(C,C)==eye(120),'Literal completion is involutive')
 weights=[Q(1)]*112+[Q(-3)]*8
 WC=[[weights[i]*x for x in row]for i,row in enumerate(C)]
 W=[[weights[i]*Q(i==j)for j in range(120)]for i in range(120)]
 need(mm(transpose(C),WC)==W,'Weighted form diag(I112,-3I8) preserved')
 Ct=transpose(C)
 need(mm(Ct,Ct)==eye(120),'Contragredient block squares to identity')
 # Check every basis input; this is independent of the matrix-product implementation.
 for j in range(120):
  x=[Q(i==j)for i in range(112)];h=[Q(i+112==j)for i in range(8)]
  need(replay_shears(R,x,h)==[C[i][j]for i in range(120)],'Three-shear primitive replay')
 need(all((x.denominator&(x.denominator-1))==0 for r in C for x in r),'Dyadic coefficients')
 bad=[r[:]for r in C];bad[0][0]+=Q(1,4)
 need(mm(bad,bad)!=eye(120),'Coefficient mutation control')

 nz=sum(x!=0 for r in R for x in r)
 out={'status':'PASS','inputs_sha256':sha256(raw).hexdigest(),'dimension':120,'auxiliary_dimension':8,'R_nonzeros':nz,'scalar_ADDs':3*nz,'scalar_negations':8,'C':'[[A,3Rt],[-R,13I8]]','checks':['RRt=56I8','A=I-RtR/4','C^2=I120','all120basis_three_shear_replays','all_coefficients_dyadic','coefficient_mutation_rejected','C_transpose_W_C_equals_W','240dim_symplectic_contragredient_lift_blocks'],'scope':'Common-chart coefficient theorem only; no physical native admission or kappa improvement.'}
 print(json.dumps(out,sort_keys=True))
if __name__=='__main__':main()

