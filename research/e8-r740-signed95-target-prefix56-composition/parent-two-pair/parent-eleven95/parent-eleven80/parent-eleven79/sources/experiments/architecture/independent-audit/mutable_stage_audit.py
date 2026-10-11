from pathlib import Path
from fractions import Fraction as Q
import json,hashlib,importlib.util
P=Path(__file__).resolve().parent; R=P.parents[2]
def replay(n,word):
 columns=[];peak=1
 for k in range(2*n):
  x=[Q(i==k) for i in range(2*n)]
  for t,s,a in word:x[t]+=a*x[s]
  columns.append(x)
 # row sums along complete literal prefixes, including both banks
 A=[[Q(i==j) for j in range(2*n)] for i in range(2*n)]
 for t,s,a in word:
  A[t]=[u+a*v for u,v in zip(A[t],A[s])];peak=max(peak,max(sum(map(abs,row)) for row in A))
 return columns,peak
rows=[]
for n in (3,4,12):
 # Independent vector update construction: F x changes only coordinate zero.
 F=[[int(i==j or i==0 and j>0) for j in range(n)] for i in range(n)]
 Fi=[[int(i==j)-int(i==0 and j>0) for j in range(n)] for i in range(n)]
 word=[]
 for direction,A in ((1,F),(0,[[-a for a in row] for row in Fi]),(1,F)):
  for i,row in enumerate(A):
   for j,a in enumerate(row):
    if a:word.append((n+i if direction else i,j if direction else n+j,a))
 for j in range(1,n):word.append((0,j,1));word.append((n,n+j,-1))
 cols,fp=replay(n,word);rev=[(t,s,-a) for t,s,a in reversed(word)];back,bp=replay(n,rev)
 for k,c in enumerate(cols):
  wanted=[Q(0)]*(2*n);wanted[n+k if k<n else k-n]=1 if k<n else -1
  assert c==wanted
  x=c[:]
  for t,s,a in rev:x[t]+=a*x[s]
  assert x==[Q(i==k) for i in range(2*n)]
 assert len(word)==8*n-5 and fp==bp==2*n-1
 rows.append(dict(width=n,columns=2*n,updates=len(word),forward_prefix=str(fp),inverse_prefix=str(bp)))
# An actual orthogonal D4 tetrad, with each line contributing independently.
T=[[1,1,0,0],[1,-1,0,0],[0,0,1,1],[0,0,1,-1]]
assert all(sum(x*y for x,y in zip(a,b))==2*int(i==j) for i,a in enumerate(T) for j,b in enumerate(T))
# Every sum coefficient is nonzero. The response's support span has rank four,
# despite its scalar value being stored in one transformed register.
assert sum(sum(x*x for x in a) for a in T)==8
E=R/'experiments/bit-search/pr436/source/research/e8-bit-elimination-reuse/code/pricing/moment.py'
s=importlib.util.spec_from_file_location('moment',E);M=importlib.util.module_from_spec(s);s.loader.exec_module(M)
price=[]
for d in (4,5):
 m=3*d;v=12;H={d-1:6*v};mass=6*v*(d-1)
 lo,hi=M.moment(H,m,1,Q(1,99),False)
 bounds=[(2-(m*x-mass)/v)/3 for x in (hi,lo)]
 assert bounds[1]<1
 price.append(dict(d=d,copy_loss_per_stage_per_port_upper_interval=list(map(str,bounds)),optimistic_data_only=True))
source=R/'experiments/architecture/mutable-stage-word'
out=dict(status='PASS_SCALAR_ENDPOINT_ONLY',literal=rows,pricing=price,tetrad_support_rank=4,two_stage_proof='For two opposite transfers, one diagonal block is the product of intervening invertible diagonal bank blocks. Same-direction transfers keep both diagonal blocks invertible. Exterior invertible diagonal changes preserve those ranks. This covers arbitrary invertible block diagonal basis changes only.',boundary='F mixes source ports; each transfer needs a new raw endpoint and common-frame compiler. Scalar cleanup is paid, but its geometric frame/climb, retained response, inverse, routing and precision bills are not supplied. A full rank tetrad response does not become rank one when stored in one register.',pins={f:hashlib.sha256((source/f).read_bytes()).hexdigest() for f in ('check.py','price.py','README.md')})
(P/'MUTABLE-STAGE-AUDIT.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
