"""Bounded original paid birth-reuse screen on reconstructed118 frames."""
import sys,os,gzip
if sys.flags.optimize or os.environ.get('PYTHONOPTIMIZE'):raise RuntimeError('Assertions required')
from pathlib import Path
from collections import Counter,defaultdict
from functools import lru_cache
import pickle,json,time,resource,math,hashlib
ROOT=Path(__file__).resolve().parent;start=time.monotonic();resource.setrlimit(resource.RLIMIT_AS,(512*1024**2,512*1024**2));resource.setrlimit(resource.RLIMIT_CPU,(30,30));g=pickle.loads((ROOT/'FRAMES.pkl').read_bytes());Hdim=24

def basis(rows):
 piv={}
 for x in rows:
  for p in sorted(piv,reverse=True):
   if x>>p&1:x^=piv[p]
  if x:
   p=x.bit_length()-1
   for q in piv:
    if piv[q]>>p&1:piv[q]^=x
   piv[p]=x
 return tuple(piv[p]for p in sorted(piv,reverse=True))
def perp(A):
 piv={x.bit_length()-1 for x in A};out=[]
 for j in range(24):
  if j not in piv:
   x=1<<j
   for r in A:
    if r>>j&1:x|=1<<(r.bit_length()-1)
   out.append(x)
 return basis(out)
def contained(A,B):return all(not any((a&b).bit_count()%2 for a in A)for b in perp(B))
@lru_cache(None)
def characteristic(A):
 k=len(A);rows=[sum(((a&b).bit_count()%2)<<j for j,b in enumerate(A))|((a.bit_count()%2)<<k)for a in A]
 for j in range(k):
  p=next(i for i in range(j,k)if rows[i]>>j&1);rows[j],rows[p]=rows[p],rows[j]
  for i in range(k):
   if i!=j and rows[i]>>j&1:rows[i]^=rows[j]
 result=0
 for j in range(k):
  if rows[j]>>k&1:result^=A[j]
 return result
DG=defaultdict(list)
for s,last in enumerate(g['last']):
 if last in g['phase']and(s not in g['terminal']or s in g['center_roles']):DG[g['U'][g['holds'][s][-1]]].append(s)
frames=sorted(DG,key=lambda F:(-len(F),F));pool=[DG[F][:]for F in frames];byB=defaultdict(list)
for b,F in g['placed'].items():byB[F].append(b)
allgroups=(1<<len(frames))-1
@lru_cache(None)
def annihilated(q):
 mask=0
 for i,A in enumerate(frames):
  if all(not((a&q).bit_count()%2)for a in A):mask|=1<<i
 return mask
eligible={};capacity={}
for F in byB:
 mask=allgroups
 for q in perp(F):
  mask &= annihilated(q)
  if not mask:break
 # Do not introduce an unproved alternating residual normalization.
 cs=characteristic(F);good=0;total=0
 while mask:
  bit=mask&-mask;mask-=bit;i=bit.bit_length()-1;A=frames[i]
  if A==F or characteristic(A)!=cs:good|=bit;total+=len(pool[i])
 eligible[F]=good;capacity[F]=total
 if time.monotonic()-start>25:raise RuntimeError('Bounded eligibility screen capped before matching; no partial claim')
# Deterministic most-constrained frame classes, highest-rank legal donor first.
available=allgroups;pairs=[]
for F in sorted(byB,key=lambda F:(capacity[F],len(F),F)):
 for b in sorted(byB[F]):
  mask=eligible[F]&available
  if not mask:break
  i=(mask&-mask).bit_length()-1;a=pool[i].pop();A=frames[i]
  if not pool[i]:available^=1<<i
  assert a!=b and a not in g['placed']and b not in g['touched'];assert g['last'][a]in g['phase'];assert contained(A,F)
  assert A==F or characteristic(A)!=characteristic(F)
  pairs.append(dict(donor=a,recipient=b,donor_frame=list(A),birth_frame=list(F),e=len(A),s=len(F),last_donor_operation=g['last'][a],source_injection_removal='true reverse chronology at full frame'))
H=Counter(g['histogram']);v=g['v']
for row in pairs:
 e,s=row['e'],row['s'];H[24-e]-=2*v;H[552+s]-=2*v
 if s>e:H[s-e]+=2*v
assert min(H.values())>=0
roles=len(g['first'])-len(pairs);W=2*v*v+2*v*roles;mass=sum(r*n for r,n in H.items());assert mass==576*W-1862080
assert len({p['donor']for p in pairs})==len(pairs)==len({p['recipient']for p in pairs})
def moment(a):return math.fsum(n*r*math.exp(a*math.log(576/r))for r,n in H.items()if n)/(576*W)
lo,hi=0.,.001
for _ in range(65):
 mid=(lo+hi)/2
 if moment(mid)<1:lo=mid
 else:hi=mid
res=dict(status='Author exact liveness/containment/paid-profile birth-reuse screen; scalar expansion and full reflected word still to check',source_head='ec862a5af51537495c745d9f2323e8a5736ee265',base_roles=len(g['first']),donors=sum(len(v)for v in DG.values()),donor_frame_classes=len(frames),births=len(g['placed']),matched=len(pairs),R=roles,W=W,rank=mass,deficit=1862080,child_histogram=dict(sorted((r,n)for r,n in H.items()if n)),match_ranks=dict(Counter(f"{r['e']}->{r['s']}"for r in pairs)),new_positive_residuals_nonalternating=True,root_float_screen=(lo+hi)/2,zero_rank_merge_records=sum(r['e']==r['s']for r in pairs),pairs=pairs,source_frame_checkpoint_sha256=hashlib.sha256((ROOT/'FRAMES.pkl').read_bytes()).hexdigest(),seconds=time.monotonic()-start,rss_KiB=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
(ROOT/'BIRTH_MATCHES.json.gz').write_bytes(gzip.compress((json.dumps(res,indent=2)+'\n').encode(),mtime=0));print(json.dumps({k:v for k,v in res.items()if k not in('pairs','child_histogram','match_ranks')},indent=2))
