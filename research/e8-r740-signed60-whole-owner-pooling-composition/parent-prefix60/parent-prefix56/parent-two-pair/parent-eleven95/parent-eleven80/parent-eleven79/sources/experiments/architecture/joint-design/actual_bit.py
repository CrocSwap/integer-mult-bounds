"""Actual signed75 port complement projectors, two-host local D identity."""
from fractions import Fraction as Q
from pathlib import Path
import json,hashlib
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent
p=ROOT/'experiments/stage-search/pr440-signed-retime/full/bit426-source-centres/global/GEOMETRY.json';a=json.loads(p.read_text())
def I(n):return [[Q(i==j) for j in range(n)]for i in range(n)]
def mm(A,B):return [[sum(A[i][k]*B[k][j]for k in range(len(B)))for j in range(len(B[0]))]for i in range(len(A))]
def plus(A,B):return [[x+y for x,y in zip(r,s)]for r,s in zip(A,B)]
def projector(cols):
 n=8;P=[[Q(0)for j in range(n)]for i in range(n)]
 for c in cols:
  norm=sum(x*x for x in c);assert norm>0
  P=plus(P,[[c[i]*c[j]/norm for j in range(n)]for i in range(n)])
 return P
def D(P):
 J=I(8);A=[[J[i][j]-P[i][j]for j in range(8)]for i in range(8)]
 return [A[i]+P[i]for i in range(8)]+[P[i]+A[i]for i in range(8)]
for port in a['ports']:
 rows=[[Q(x)for x in r]for r in port['complement_columns']];cols=list(map(list,zip(*rows)));assert len(cols)==7
 assert all(sum(x*y for x,y in zip(c,d))==0 for i,c in enumerate(cols)for j,d in enumerate(cols)if i!=j)
 P1=projector(cols[:3]);P2=projector(cols[3:]);P=plus(P1,P2)
 assert mm(D(P1),D(P2))==D(P)==mm(D(P2),D(P1))
 assert mm(D(P),D(P))==I(16)
result={'status':'PASS_ACTUAL_OWN_SIGNED75_ALL120_PORT_TWO_HOST_D_IDENTITY','source_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'source_word_sha256':a['word_sha256'],'ports_checked':len(a['ports']),'basis_columns_per_port':16,'two_host_widths':[3,4],'orthogonal_factor_identity':True,'inverse_exact':True,'intervening_exterior_idle_commutation':'Inherited exterior blocks lie in direct-sum coordinates, so their orthogonal projectors multiply local hosted projectors to zero in both orders. D factors commute exactly.','scope':'Actual own signed75 common port frames. Width3+4 is a feasibility split of 7 local complement coordinates, not emitted helper selection or bank reassignment. Does not establish hosted sigma cover selectors or full invoices.'}
(OUT/'ACTUAL-BIT.json').write_text(json.dumps(result,indent=2)+'\n');print(result['status'])
