"""Apply pinned common-frame retimings and derive the complete paid profile."""
from pathlib import Path
from collections import Counter
import copy,gzip,hashlib,json,sys
assert __debug__
ROOT=Path(__file__).resolve().parent
source,target=map(Path,sys.argv[1:3]);expected=json.loads((ROOT/'CONSTRUCTION.json').read_text())
assert hashlib.sha256(source.read_bytes()).hexdigest()==expected['source_full_sha256']
w=json.loads(gzip.decompress(source.read_bytes()));old=copy.deepcopy(w);v=w['report']['v'];R=w['report']['R'];h=w['report']['h']
def basis(vs):
 b={}
 for x in vs:
  for p in sorted(b,reverse=True):
   if x>>p&1:x^=b[p]
  if x:
   p=x.bit_length()-1
   for j in b:
    if b[j]>>p&1:b[j]^=x
   b[p]=x
 return tuple(b[p] for p in sorted(b,reverse=True))
def tau(x):return x^(43 if (x&43).bit_count()%2 else 0)
for plan in json.loads((ROOT/'SELECTION.json').read_text()):
 e=w[plan['part']][plan['index']]
 assert basis([tau(x) for x in e[-1]])==tuple(plan['old_basis'])
 e[-1]=list(basis([tau(x) for x in plan['new_basis']]))
assert all([e[:-1] for e in w[k]]==[e[:-1] for e in old[k]] for k in ('A','B','cut','cleanup','precondition'))
assert all(w[k]==old[k] for k in ('ports','root_lines','centers','scatter','cut','cleanup','precondition'))
full=tuple(1<<i for i in reversed(range(h)));cur=[(p,) for p in w['ports']]+[()]*(v+R);paid=Counter()
def climb(r,F):
 F=basis(F);assert basis(cur[r]+F)==F
 d=len(F)-len(cur[r]);assert d>=0
 if d:paid[d]+=1
 cur[r]=F
for part in ('A','B'):
 if part=='B':
  assert all(cur[r]==full for r in w['centers']) and all(cur[r]==() for r in range(v,2*v));paid[h]+=len(w['centers'])
 for e in w[part]:
  for r in [e[1]]+([e[2]] if e[0]=='add' else []):climb(r,e[-1])
for r in range(2*v+R):climb(r,[x for x in range(1,1<<h) if not (x&w['ports'][r-v]).bit_count()%2] if v<=r<2*v else full)
assert sum(k*z for k,z in paid.items())==h*R+2*v*(h-1)+h*len(w['centers'])
# Supplier PR425 fixes nine windows, eight replicas and this data skeleton.
L,T=9,8;globalH=Counter({k:z*L*T for k,z in paid.items()})
for k in (16,8,32,8,48,8,48,32,16):globalH[k]+=2*v*T
globalH[1]+=L*R
assert w['report']['m']*w['report']['W']-sum(k*z for k,z in globalH.items())==2496
assert {str(k):z for k,z in paid.items()}==expected['local_profile']
w['report'].update(local_profile=dict(sorted(paid.items())),global_profile=dict(sorted(globalH.items())),status='FRAME_RETIMING_CANDIDATE_NOT_ADMITTED')
raw=gzip.compress(json.dumps(w,sort_keys=True,separators=(',',':')).encode(),mtime=0);assert hashlib.sha256(raw).hexdigest()==expected['candidate_sha256'];target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw)
print('PASS unchanged scalar word, all nested common frames, center boundary, complete histogram and pinned output hash',flush=True)
