"""Exact PR117-DAG lifted frames, PR125 shrink pass and PR114 saturated placement; no upstream imports."""
import sys,os
if sys.flags.optimize or os.environ.get('PYTHONOPTIMIZE'):raise RuntimeError('Assertions required')
from pathlib import Path
from itertools import combinations
from collections import Counter,defaultdict
from functools import lru_cache
from fractions import Fraction
import pickle,json,time,resource,hashlib
ROOT=Path(__file__).resolve().parent;REPO=Path(os.environ.get('BIRTH_REPO',ROOT.parents[1]));start=time.monotonic();(sys.platform=='darwin' or resource.setrlimit(resource.RLIMIT_AS,(2048*1024**2,2048*1024**2)));resource.setrlimit(resource.RLIMIT_CPU,(120,120))
H=24;FULL=(1<<H)-1

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
@lru_cache(65536)
def contained(A,B):
 for x in A:
  for r in B:
   if x>>(r.bit_length()-1)&1:x^=r
  if x:return False
 return True
@lru_cache(65536)
def perpendicular(A):
 piv={r.bit_length()-1 for r in A};out=[]
 for j in range(H):
  if j not in piv:
   x=1<<j
   for r in A:
    if r>>j&1:x|=1<<(r.bit_length()-1)
   out.append(x)
 return basis(out)
@lru_cache(65536)
def intersection(A,B):return perpendicular(basis(perpendicular(A)+perpendicular(B)))
@lru_cache(65536)
def nondeg(A):return len(basis(sum(((x&y).bit_count()%2)<<j for j,y in enumerate(A))for x in A))==len(A)
@lru_cache(65536)
def regular_part(A):
 remain=list(A);chosen=[]
 while remain:
  odd=next((i for i,x in enumerate(remain)if x.bit_count()%2),None)
  if odd is not None:
   a=remain.pop(odd);chosen.append(a);remain=[x^a if (x&a).bit_count()%2 else x for x in remain];continue
  pair=next(((i,j)for i,x in enumerate(remain)for j in range(i+1,len(remain))if (x&remain[j]).bit_count()%2),None)
  if pair is None:break
  i,j=pair;a,b=remain[i],remain[j];chosen.extend((a,b));remain=[x^(a if(x&b).bit_count()%2 else 0)^(b if(x&a).bit_count()%2 else 0)for k,x in enumerate(remain)if k not in(i,j)]
 return basis(chosen)
def bits(mask):
 while mask:
  x=mask&-mask;mask-=x;yield x.bit_length()-1

def save(name,value):
 raw=pickle.dumps(value,protocol=4);(ROOT/name).write_bytes(raw);return hashlib.sha256(raw).hexdigest()

if (ROOT/'LIFTED.pkl').exists():g=pickle.loads((ROOT/'LIFTED.pkl').read_bytes())
else:
 g=pickle.loads((ROOT/'ROLES.pkl').read_bytes());args,core,cover,rank,kind=[g[k]for k in('args','core','cover','rank','kind')];active=g['active'];roots=g['roots'];uses=g['uses'];use=g['use'];links=g['links'];matched=g['matched_use'];n=len(args);v=g['v']
 tm=[sum(1<<i for i in t)for t in combinations(range(H),3)];fun=[tm[t]if t>=0 else 1<<(j-(len(roots)-H))for j,t in enumerate(g['targets'])]
 succ=[set()for _ in range(n)];rootf=[[]for _ in range(n)]
 def connect(x,uid):
  _,typ,dest,_=use[uid]
  if typ:rootf[x].append(fun[dest])
  else:succ[x].add(dest)
 for x in active:
  for uid in uses[x]:
   if matched[uid]<0:connect(x,uid)
 for x,uid in links.items():connect(x,uid)
 order=sorted(active,key=lambda x:(rank[x],x),reverse=True);demand=[()]*n
 for x in order:demand[x]=basis(rootf[x]+[r for y in sorted(succ[x])for r in demand[y]])
 def envelope(x):
  if not args[x]:return (tm[x-1],)
  if kind[x]==2:return basis(1<<i for i in bits(cover[x]))
  assert kind[x]==1
  return basis(core[x]|(1<<i)for i in bits(cover[x]&~core[x]))
 U=[()]*n
 for x in active:
  E=envelope(x)
  if not args[x]:U[x]=E
  else:
   K=perpendicular(demand[x]);assert contained(E,K);U[x]=K if nondeg(K)else E
 changed=True
 while changed:
  changed=False
  for x in order:
   if args[x]and any(not contained(U[x],U[y])for y in succ[x]):
    E=envelope(x)
    if U[x]!=E:U[x]=E;changed=True
 assert sum(bool(args[x])and len(U[x])>rank[x]for x in active)==39989
 # Shrunk frames (PR125): replace U_x by the minimal span Lb_x=label+sum U_pred when Lb_x is
 # nondegenerate, inside U_x and every successor frame, and lowers the local one-child cost.
 import math
 pred=[[]for _ in range(n)]
 for x in active:
  for y in succ[x]:pred[y].append(x)
 dim=[len(F)for F in U];holds=g['holds'];occ=defaultdict(list)
 for s,chain in enumerate(holds):
  for i,x in enumerate(chain):occ[x].append((s,i))
 f=lambda t:t*math.log(576/t)if t>0 else 0.0
 def local(x,d):
  c=0.0
  for s,i in occ[x]:
   ch=holds[s];c+=f(d-dim[ch[i-1]])if i else f(d)
   if i+1<len(ch):c+=f(dim[ch[i+1]]-d)
   elif s in g['terminal']:c+=f(H-1-d)
   else:c+=f(H-d)
  return c
 shrunk=0
 for x in sorted(active,key=lambda x:(rank[x],x)):
  if not args[x]:continue
  Lb=basis(list(envelope(x))+[r for p in pred[x]for r in U[p]])
  if len(Lb)>=dim[x]or not contained(Lb,U[x])or not nondeg(Lb)or not all(contained(Lb,U[y])for y in succ[x]):continue
  if local(x,len(Lb))<local(x,dim[x])-1e-9:U[x]=Lb;dim[x]=len(Lb);shrunk+=1
 assert shrunk==16031,shrunk
 roles=len(g['first']);reach=[0]*roles;dense=[False]*roles
 for s,j in g['terminal'].items():
  if j>=len(roots)-H:dense[s]=True
  else:reach[s]=1<<g['targets'][j]
 for op,s,t,x in reversed(g['ops']):
  if op==1:reach[t]|=reach[s];dense[t]|=dense[s]
  elif op==2:reach[s]|=reach[t];dense[s]|=dense[t]
 cand={}
 for s,x in enumerate(g['first']):
  if s in g['touched']or dense[s]:continue
  constraint=basis(tm[t]for t in bits(reach[s]));X=intersection(U[x],perpendicular(constraint))
  if X and nondeg(X):cand[s]=X
 g.update(U=U,reach=reach,reach_all=dense,candidates=cand,tm=tm,lifted=sum(bool(args[x])and len(U[x])>rank[x]for x in active))
 expected_profile=json.loads((REPO/'research/shrunk-frames/complex-profile.json').read_text())
 assert g['lifted']==expected_profile['lifted_additions'],g['lifted'];save('LIFTED.pkl',g)
 print('Lifted checkpoint',len(cand),'candidates',round(time.monotonic()-start,2),flush=True)
# Only this saturating placement is repeated if a previous cap ended after LIFTED.
# PR114 saturated placement: priority 2^dim/targets^2; a degenerate intersection keeps its regular part.
U=g['U'];reach=g['reach'];cand=g['candidates'];bytarget=defaultdict(list);placed={};order=sorted(cand,key=lambda s:(Fraction(-(1<<len(cand[s])),max(1,reach[s].bit_count())**2),-len(cand[s]),s))
for step,s in enumerate(order):
 X=cand[s];changed=True
 while changed and X:
  changed=False
  for t in bits(reach[s]):
   for prior in bytarget[t]:
    B=placed[prior]
    if (len(B)>=len(X)and not contained(X,B))or(len(B)<len(X)and not contained(B,X)):
     X=intersection(X,B);changed=True
    if not X:break
   if not X:break
  if X and not nondeg(X):
   before=X;X=regular_part(X);assert contained(X,before)and nondeg(X)and len(X)<len(before);changed=True
 if X:
  assert nondeg(X)and contained(X,cand[s]);placed[s]=X
  for t in bits(reach[s]):bytarget[t].append(s)
 if step and step%2000==0:print('Placed',step,'/',len(order),'time',round(time.monotonic()-start,2),flush=True)
for ss in bytarget.values():
 ss.sort(key=lambda s:(len(placed[s]),s));assert all(contained(placed[a],placed[b])for a,b in zip(ss,ss[1:]))
assert len(placed)==4706,len(placed)
# Reconstruct EVERY paid bin, not merely total mass.
v=g['v'];N=v*v;roles=len(g['first']);hist=Counter();chains={}
for s,chain in enumerate(g['holds']):
 actual=[placed.get(s,())]+[U[x]for x in chain]
 if s in g['terminal']:
  j=g['terminal'][s];terminal_frame=perpendicular((1<<(j-(len(g['roots'])-H)),))if j>=len(g['roots'])-H else perpendicular((g['tm'][g['targets'][j]],))
  actual.append(terminal_frame)
 assert all(contained(a,b)for a,b in zip(actual,actual[1:]))and all(nondeg(A)for A in actual)
 ds=[len(A)for A in actual];chains[s]=ds
 for a,b in zip(ds,ds[1:]):
  if b>a:hist[b-a]+=2*v
 if s in g['terminal']and g['terminal'][s]>=len(g['roots'])-H:hist[H-1]+=2*v
 if H>ds[-1]:hist[H-ds[-1]]+=2*v
 hist[576-H+ds[0]]+=2*v
for t in range(v):
 levels=sorted({0,H-1}|{len(placed[s])for s in bytarget[t]})
 for a,b in zip(levels,levels[1:]):hist[b-a]+=2*v
hist[H-1]+=2*N;hist[(H-1)**2]+=2*N;hist[1]+=N
expected=json.loads((REPO/'research/shrunk-frames/complex-profile.json').read_text())
assert dict(hist)=={int(k):v for k,v in expected['child_multiplicities'].items()},('Histogram mismatch',hist)
assert Counter(len(A)for A in placed.values())==Counter({int(k):v for k,v in expected['deferred_dims'].items()})
g.update(placed=placed,bytarget=dict(bytarget),histogram=dict(hist),chain_dims=chains);digest=save('FRAMES.pkl',g)
result=dict(status='PASS shrunk/saturated full frame/profile reconstruction',roles=roles,deferred=len(placed),maxchild=max(hist),weighted_rank=sum(t*n for t,n in hist.items()),all_bins_match=True,frame_sha256=digest,seconds=time.monotonic()-start,rss_KiB=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
(ROOT/'FRAMES_CHECK.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
