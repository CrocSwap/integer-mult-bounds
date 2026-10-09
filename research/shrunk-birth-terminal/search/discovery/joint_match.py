"""Joint birth-reuse and terminal-elision surrogate discovery.

Chafik Boukhalfa with OpenAI Codex assistance, Apache-2.0.
Builds on James Chang PR124 birth reuse, Joel Pulikkan PR125 frames,
eumemic PR117 DAG, SovereignSteak PR122 terminal elimination and root R12
weighted integer transport. Protected deferral coordinates are our R12 work.
No physical-word or globally optimal kappa claim is made by this solver.
"""
import sys,os,gzip
if sys.flags.optimize or os.environ.get('PYTHONOPTIMIZE'):raise RuntimeError('Assertions required')
from pathlib import Path
from collections import Counter,defaultdict
from functools import lru_cache
import pickle,json,time,resource,math,hashlib
ROOT=Path(__file__).resolve().parent;start=time.monotonic();(resource.setrlimit(resource.RLIMIT_AS,(4*1024**3,4*1024**3)) if sys.platform == "linux" else None);resource.setrlimit(resource.RLIMIT_CPU,(240,240));g=pickle.loads((ROOT/'FRAMES.pkl').read_bytes());Hdim=24

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
 if last in g['phase'] and s not in g['terminal']:DG[g['U'][g['holds'][s][-1]]].append(s)
frames=sorted(DG,key=lambda F:(-len(F),F));pool=[DG[F][:]for F in frames];byB=defaultdict(list)
for b,F in g['placed'].items():
 if g['first'][b] > g['v']: byB[F].append(b)
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
 if time.monotonic()-start>220:raise RuntimeError('Bounded eligibility screen capped before matching; no partial claim')
# Optimize a complete integer first-moment surrogate over frame classes.
# Exact paid moments and physical word audits certify every resulting candidate.
from fractions import Fraction as Q
from transport_cpp import transport
def log_upper(value):
 value=Q(value);power=0
 while value>2:value/=2;power+=1
 def series(x):
  z=(x-1)/(x+1)
  return 2*sum((z**(2*j+1)/Q(2*j+1)for j in range(24)),Q(0))+2*z**49/(49*(1-z*z))
 return power*series(Q(2))+series(value)
@lru_cache(None)
def fcost(t):return Q(t)*log_upper(Q(576,t))if t else Q(0)
@lru_cache(None)
def score(e,s):
 q=(fcost(24-e)+fcost(552+s)-fcost(s-e))*10**12
 return q.numerator//q.denominator
# Joint capacitated choice: a virtual role receives either a real birth donor
# or its target's one terminal-elision token. Classes preserve frame and target.
options=json.loads((ROOT/'TERMINAL_OPTIONS.json').read_text())
assert options['joint_optimization_options']
assert any(hashlib.sha256((ROOT/'FRAMES.pkl').read_bytes()).hexdigest()==value for path,value in options['input_sha256'].items() if path.endswith('FRAMES.pkl'))
terminal={r['role']:r for r in options['eligible']}
assert len(terminal)==len(options['eligible'])
assert all(r['sigma']==r['M']==r['F0'] for r in terminal.values())
classes=defaultdict(list)
for F,roles in byB.items():
 for role in roles:classes[(F,terminal[role]['target'] if role in terminal else -1)].append(role)
classkeys=sorted(classes,key=lambda key:(len(key[0]),key[0],key[1]))
terminal_targets=sorted({row['target'] for row in terminal.values()})
dummy={t:len(frames)+i for i,t in enumerate(terminal_targets)}
@lru_cache(None)
def terminal_score(s):
 q=(fcost(552+s)+fcost(1)+fcost(23-s))*10**12
 return q.numerator//q.denominator
edges=[]
for j,(F,t) in enumerate(classkeys):
 mask=eligible[F]
 while mask:
  bit=mask&-mask;mask-=bit;i=bit.bit_length()-1
  edges.append((i,j,score(len(frames[i]),len(F))))
 if t>=0:
  assert all(role in terminal and terminal[role]['target']==t and terminal[role]['sigma']==len(F) for role in classes[(F,t)])
  edges.append((dummy[t],j,terminal_score(len(F))))
flows,flow_receipt=transport([len(pool[i])for i in range(len(frames))]+[1]*len(dummy),[len(classes[key])for key in classkeys],edges)
(ROOT/'TRANSPORT.json').write_text(json.dumps(flow_receipt,indent=2)+'\n')
birthpool={key:sorted(roles,reverse=True) for key,roles in classes.items()};pairs=[];selected_terminal=[]
# Allocate dummy choices first so target slots choose stable lowest role IDs.
for i,j,count in sorted(flows,key=lambda row:(row[0]<len(frames),row[0],row[1])):
 F,t=classkeys[j]
 if i>=len(frames):
  assert count==1 and i==dummy[t]
  role=birthpool[(F,t)].pop();selected_terminal.append(role)
  continue
 A=frames[i]
 for _ in range(count):
  a=pool[i].pop();b=birthpool[(F,t)].pop()
  assert a!=b and a not in g['placed'] and b not in g['touched'] and a not in g['terminal']
  assert g['last'][a]in g['phase']and contained(A,F)
  assert A==F or characteristic(A)!=characteristic(F)
  pairs.append(dict(donor=a,recipient=b,donor_frame=list(A),birth_frame=list(F),e=len(A),s=len(F),last_donor_operation=g['last'][a],source_injection_removal='true reverse chronology at full frame'))
assert len({terminal[s]['target'] for s in selected_terminal})==len(selected_terminal)
assert not set(selected_terminal)&{row['recipient'] for row in pairs}
(ROOT/'TERMINAL_ROLES.json').write_text(json.dumps(sorted(selected_terminal),indent=2)+'\n')
H=Counter(g['histogram']);v=g['v']
for row in pairs:
 e,s=row['e'],row['s'];H[24-e]-=2*v;H[552+s]-=2*v
 if s>e:H[s-e]+=2*v
assert min(H.values())>=0
roles=len(g['first'])-len(pairs);W=2*v*v+2*v*roles;mass=sum(r*n for r,n in H.items());assert mass==576*W-1862080
assert len({p['donor']for p in pairs})==len(pairs)==len({p['recipient']for p in pairs})
res=dict(status='Author exact liveness/containment/paid-profile birth-reuse screen; scalar expansion and full reflected word still to check',source_head='ec862a5af51537495c745d9f2323e8a5736ee265',base_roles=len(g['first']),donors=sum(len(v)for v in DG.values()),donor_frame_classes=len(frames),births=len(g['placed']),matched=len(pairs),R=roles,W=W,rank=mass,deficit=1862080,child_histogram=dict(sorted((r,n)for r,n in H.items()if n)),match_ranks=dict(Counter(f"{r['e']}->{r['s']}"for r in pairs)),new_positive_residuals_nonalternating=True,zero_rank_merge_records=sum(r['e']==r['s']for r in pairs),pairs=pairs,source_frame_checkpoint_sha256=hashlib.sha256((ROOT/'FRAMES.pkl').read_bytes()).hexdigest(),seconds=time.monotonic()-start,rss_KiB=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
(ROOT/'BIRTH_MATCHES.json.gz').write_bytes(gzip.compress((json.dumps(res,indent=2)+'\n').encode(),mtime=0));print(json.dumps({k:v for k,v in res.items()if k not in('pairs','child_histogram','match_ranks')},indent=2))

# Predict the complete packet profile without presenting it as physical proof.
J=Counter(H)
for role in selected_terminal:
 row=terminal[role]
 assert row['old_packet']==[552+row['sigma'],1,0,23-row['sigma']]
 for width in row['old_packet']:
  if width:J[width]-=2*v
assert min(J.values())>=0
JR=roles-len(selected_terminal);JW=2*v*v+2*v*JR;mass=sum(r*n for r,n in J.items())
assert 576*JW-mass==1862080
summary=dict(status='DISCOVERY ONLY exact capacitated surrogate optimum from transport; physical packet verification pending',real_births=len(pairs),terminal_elisions=len(selected_terminal),physical_roles=JR,W=JW,rank=mass,deficit=1862080,child_histogram=dict(sorted((r,n) for r,n in J.items() if n)),terminal_roles=sorted(selected_terminal),source_and_input_sha256={str(p.name):hashlib.sha256(p.read_bytes()).hexdigest() for p in (Path(__file__),ROOT/'FRAMES.pkl',ROOT/'TERMINAL_OPTIONS.json',ROOT/'transport_cpp.py',ROOT/'transport.cpp',ROOT/'transport-bin')},integer_surrogate=flow_receipt,seconds=time.monotonic()-start)
(ROOT/'JOINT_PROFILE.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps({k:v for k,v in summary.items() if k not in ('child_histogram','terminal_roles','source_and_input_sha256')},indent=2))
