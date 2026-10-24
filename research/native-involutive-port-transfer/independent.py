"""Separate exact coefficient audit; does not import the source interpreter."""
from pathlib import Path
from fractions import Fraction as Q
import gzip,json
HERE=Path(__file__).resolve().parent
S=[0,7,20,23,86,93,108,111]
def need(c,m):
 if not c:raise ValueError(m)
def mm(a,b):return [[sum((x*y for x,y in zip(r,c)),Q(0))for c in zip(*b)]for r in a]
def main():
 R=[[Q(x)for x in r]for r in json.loads((HERE/'R.json').read_bytes())]
 K=[[R[k][i]/4 for k in range(8)]for i in range(112)]
 U=[[(-11 if i in S else 1)*v for v in row]for i,row in enumerate(K)]
 need(mm(R,U)==[[Q(2*(i==j))for j in range(8)]for i in range(8)],'Exact commuting reflection sections')
 F=[[Q(i==j)-x for j,x in enumerate(row)]for i,row in enumerate(mm(U,R))]
 word=json.loads(gzip.decompress((HERE/'INVOLUTIVE-WORD.json.gz').read_bytes()))
 need(F==[[Q(x)for x in row]for row in word['F']],'Frozen word coefficient equality')
 # Serial independent rank-one updates I-u_k r_k, each an involution.
 for j in range(112):
  x=[Q(i==j)for i in range(112)]
  for k in range(8):
   q=sum(a*b for a,b in zip(R[k],x))
   x=[v-U[i][k]*q for i,v in enumerate(x)]
  need(x==[F[i][j]for i in range(112)],'All112basis serial reflection replay')
 weights=[Q(-1 if i in S else 11)for i in range(112)]
 for i in range(112):
  for j in range(112):
   need(sum(F[k][i]*weights[k]*F[k][j]for k in range(112))==(weights[i]if i==j else 0),'Exact indefinite diagonal isometry')
 d=json.loads((HERE/'DYADIC-DILATION-INPUTS.json').read_bytes())
 need(R==[[Q(x)for x in row]for row in d['R']],'Dilation uses same source modes')
 A=[[Q(i==j)-v for j,v in enumerate(row)]for i,row in enumerate(mm(K,R))]
 need(A==[[Q(x)for x in row]for row in d['A']],'Dilation uses actual prior port code')
 print(json.dumps({'status':'PASS_SEPARATE_COEFFICIENT_AUDIT','serial_reflections':8,'basis_inputs':112,'indefinite_metric':'-1 on selected ports,11 elsewhere','scope':'Coefficient identities only, not separate native interpreter or complete kappa.'}))
if __name__=='__main__':main()
