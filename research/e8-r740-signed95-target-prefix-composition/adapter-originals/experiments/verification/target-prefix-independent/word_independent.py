from pathlib import Path
from fractions import Fraction as Q
import json,struct,hashlib
P=Path(__file__).resolve().parent;R=Path('<workspace>');S=P/'signed-rerun';E=list(struct.iter_unpack('<6i',(S/'signed-records.bin').read_bytes()));F={int(k):v for k,v in json.loads((S/'records/frames.json').read_text())['frames'].items()};st=json.loads((S/'records/249-states.json').read_text());n=980
rows=[{i:1} for i in range(n)]+[{}]
def add(a,b,c):
 for k,v in list(b.items()):
  a[k]=a.get(k,0)+c*v
  if not a[k]:del a[k]
def replay(es):
 A=[{i:1} for i in range(n)]+[{}];norm=[1]*n+[0];peak=1;state={int(k):v for k,v in st['initial'].items()};copies=0
 for op,a,b,c,f,z in es:
  if op==0:
   assert state[a]==b and F[b]['dim']<=F[c]['dim']
   assert all(sum(Q(x)*Q(y) for x,y in zip(u,w))==0 for u in F[b]['B'] for w in F[c]['A']);state[a]=c
  elif op==1:
   assert state[a]==state[b]==f;add(A[a],A[b],c);norm[a]+=abs(c)*norm[b];peak=max(peak,norm[a])
  elif op==2:A[b]=dict(A[a]);norm[b]=norm[a];state[b]=f;copies+=1
  elif op==3:assert A[b]==A[a];A[b]={};norm[b]=0;del state[b]
 assert state=={int(k):v for k,v in st['final'].items()}
 return A,peak,copies
A,peak,copies=replay(E)
for i,row in enumerate(A):
 if 120<=i<240:
  assert row.get(i)==1 and all(k<120 or k==i for k in row)
  assert {k for k,v in row.items() if k<120 and v%2}=={i-120}
 else:assert row==({i:1} if i<n else {})
# Inverse updates directly undo the complete forward matrix, including dirty copies.
for op,a,b,c,f,z in reversed(E):
 if op==1:add(A[a],A[b],-c)
 elif op==3:A[b]=dict(A[a])
 elif op==2:assert A[b]==A[a];A[b]={}
assert A==[{i:1} for i in range(n)]+[{}]
comp=[e for e in E if e[0]==1 and e[5]==1];fees=sum(abs(e[3]) for e in comp)
out={'status':'PASS_INDEPENDENT_COLLECTIVE95_WORD_COLUMNS_DIRT_INVERSE_AND_FORWARD_FRAMES','columns':980,'copies':copies,'prefix':peak,'compensation_abs_units':fees,'instruction_signed_add_units':sum(abs(e[3]) for e in E if e[0]==1),'signed_sha256':hashlib.sha256((S/'signed-records.bin').read_bytes()).hexdigest(),'scope':'Scalar matrix and exact forward frame ledger independently replayed. Reflected source/chart compiler and full eleven-stage paid supplier require separate admission.'}
(P/'INDEPENDENT-WORD.json').write_text(json.dumps(out,indent=2)+'\n');print(out)
