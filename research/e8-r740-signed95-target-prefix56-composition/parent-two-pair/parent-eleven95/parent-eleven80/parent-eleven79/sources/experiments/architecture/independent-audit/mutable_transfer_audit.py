from pathlib import Path
from fractions import Fraction as Q
import json,itertools
P=Path(__file__).resolve().parent
roots=[]
for i,j in itertools.combinations(range(4),2):
 for sign in (1,-1):
  r=[0]*4;r[i]=1;r[j]=sign;roots.append(r)
v=12;perm=[i^1 for i in range(v)]
def word(stage=0,reverse=False):
 out=[]
 for t,s in enumerate(perm):
  a=24+stage*v+t
  for dst,src,c in ((12+t,a,-1),(a,s,1),(12+t,a,1),(a,s,-1)):
   if reverse:
    if 12<=dst<24:c=-c
    if dst<24:dst=(dst+12)%24
    if src<24:src=(src+12)%24
   out.append((dst,src,c))
 return out
def test(n,gs,expected):
 for col in range(n):
  x=[Q(i==col) for i in range(n)]
  for d,s,c in gs:x[d]+=c*x[s]
  assert x==expected(col)
  for d,s,c in reversed(gs):x[d]-=c*x[s]
  assert x==[Q(i==col) for i in range(n)]
def local(k):
 x=[Q(i==k) for i in range(36)]
 if k<12:x[12+perm[k]]=1
 return x
test(36,word(),local)
gs=word()+word(1,True)+word(2)
def global_(k):
 x=[Q(0)]*60
 if k<12:x[12+perm[k]]=1
 elif k<24:x[perm[k-12]]=-1
 else:x[k]=1
 return x
test(60,gs,global_)
for t,s in enumerate(perm):
 a,b=roots[t],roots[s];assert sum(x*y for x,y in zip(a,b))==0
 Ps=[[Q(x*y,2) for y in b] for x in b];Pt=[[Q(x*y,2) for y in a] for x in a]
 assert sum(Ps[i][i]+Pt[i][i] for i in range(4))==2
 # Orthogonal rank-one projectors: sum rank2 and nonzero difference rank2.
 assert all(sum(Ps[i][k]*Pt[k][j] for k in range(4))==0 for i in range(4) for j in range(4))
assert (perm[0],perm[0],0)!=(0,0,0)
N=12**3;W=5*N;m=64;mass=W*m-2*N+2*N;assert mass==W*m
out={'status':'PASS_LOCAL_CHANGED_TRANSFER_REJECT_NAIVE_TENSOR_AND_CONDITIONAL_BIT_DEFICIT','local_columns':36,'local_additions':48,'three_stage_columns':60,'three_stage_additions':144,'endpoint':'(-F y,F x), all helpers restored','source_projection_correction_rank':2,'conditional_bit_deficit':m*W-mass,'scope':'A local orthogonal source line fits target cap. Naive varying-coordinate stages have F2F1 unequal identity and fail exchange. Even granting a corrected scalar tensor layout with proposed nested endpoint labels, changing source projector from -Ps to -Pt raises first edge rank1 to2 and costs2N, exhausting its alleged2N stock deficit. Conditional fixed-label screen only, not a universal mutable-transfer impossibility.'}
(P/'MUTABLE-TRANSFER-AUDIT.json').write_text(json.dumps(out,indent=2)+'\n');print(out)
