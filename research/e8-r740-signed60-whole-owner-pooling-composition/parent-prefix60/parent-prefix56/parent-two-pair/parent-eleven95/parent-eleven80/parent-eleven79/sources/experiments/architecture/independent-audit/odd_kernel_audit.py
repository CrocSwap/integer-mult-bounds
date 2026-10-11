from pathlib import Path
from fractions import Fraction as Q
import json,hashlib
P=Path(__file__).resolve().parent;R=P.parents[2]
B=json.loads((R/'experiments/stage-search/pr441-signed-retime/signed/baseline.json').read_text());S=R/'experiments/architecture/odd-coefficient-kernel/RESULT.json';data=json.loads(S.read_text())
K={}
# Independent one-input-at-a-time scalar evaluation, rather than producer sparse row elimination.
for h in range(240,980):
 x=[0]*980;x[h]=1
 for frame,d,ss in B['A']:x[d]+=sum(x[s] for s in ss)
 kept=[x[i] for i in B['ret']]
 for t,ks in enumerate(B['scatter']):x[120+t]+=sum(kept[k] for k in ks)
 for frame,d,ss in B['B']:x[d]+=sum(x[s] for s in ss)
 K[h]=x[120:240]
def rank_mod(A,p=1000003):
 A=[[x%p for x in row] for row in A];r=0
 for c in range(len(A[0])):
  j=next((i for i in range(r,len(A)) if A[i][c]),None)
  if j is None:continue
  A[r],A[j]=A[j],A[r];a=pow(A[r][c],-1,p);A[r]=[x*a%p for x in A[r]]
  for i in range(r+1,len(A)):
   a=A[i][c];A[i]=[(x-a*y)%p for x,y in zip(A[i],A[r])]
  r+=1
 return r
counts={}
for row in data['rows']:
 ds=row['donors'];p=row['pivot'];A=[[K[d][i] for d in ds] for i in range(120)];bb=[Q(K[p][i]-sum(A[i]),2) for i in range(120)]
 assert all(x.denominator==1 for x in bb)
 status=row['status'];counts[status]=counts.get(status,0)+1
 if status=='UNSOLVABLE_OVER_Q_HENCE_Z':
  w={int(i):Q(x) for i,x in row['dual_witness'].items()}
  assert all(sum(wi*A[i][j] for i,wi in w.items())==0 for j in range(len(ds)))
  assert sum(wi*bb[i] for i,wi in w.items())==Q(row['dual_rhs'])!=0
 elif status=='EXACT_ODD_INTEGER_LIFT':
  cs=dict(row['coefficients']);assert set(cs)==set(ds)
  assert all(c%2 and abs(c)==1 for c in cs.values())
  assert all(sum(cs[d]*K[d][i] for d in ds)==K[p][i] for i in range(120))
  assert rank_mod(A)==len(ds) # certifies rational independence and uniqueness
 else:raise AssertionError(status)
relations={963:[(783,-1),(853,1),(962,1)],775:[(758,1),(759,1),(774,-1)],859:[(740,1),(741,1),(858,-1)],885:[(740,1),(741,1),(884,-1)],920:[(904,1),(906,1),(918,-1)]}
for p,ds in relations.items():assert all(K[p][i]==sum(c*K[d][i] for d,c in ds) for i in range(120))
out={'status':'PASS_FIXED_DONOR_CERTIFICATES_AND_FIVE_NEW_RELATIONS','counts':counts,'five_relations':relations,'source_result_sha256':hashlib.sha256(S.read_bytes()).hexdigest(),'scope':'Fixed listed donor supports only. Rational inconsistency and unique unit solutions independently checked; no broader kernel optimality or positive-frame/compiler admission. Await actual 80-pivot export.'}
(P/'ODD-KERNEL-AUDIT.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
