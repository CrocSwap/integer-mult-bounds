from pathlib import Path
from collections import defaultdict,Counter,deque
import json,gzip,sys,copy,math,argparse
ap=argparse.ArgumentParser();ap.add_argument('--input',type=Path,required=True);ap.add_argument('--source',type=Path,required=True);ap.add_argument('--gk',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();sys.path.insert(0,str(args.gk))
import gk_word as g, gk_common as c
g.V=c.V=112;g.DATA=c.DATA=7168
p=Path(__file__).resolve().parent
src=args.input
a=json.load(gzip.open(src));b=json.load(gzip.open(args.source))
old=copy.deepcopy(a);before=g.profile(a);sp={}
def span(E):
 E=g.basis(E)
 if E not in sp:sp[E]=g.span(E)
 return sp[E]
def meet(A,B):return g.basis(span(A)&span(B))
def join(A,B):return g.basis(tuple(A)+tuple(B))
N=728;V=112
changes=[]
for sec in ('B','A'):
 mapping=defaultdict(deque)
 for e in b[sec]:mapping[tuple(e[:-1])].append(e[-1])
 desired=[]
 for e in a[sec]:
  d=mapping[tuple(e[:-1])];desired.append(d.popleft()if d else e[-1])
 nxt=[g.FULL]*N
 for r in range(V,2*V):nxt[r]=g.perp(a['ports'][r-V])
 if sec=='A':
  for e in reversed(a['B']):
   for r in (e[1:3]if e[0]=='add'else e[1:2]):nxt[r]=g.basis(e[-1])
  for r,F in zip(a['centers'],a['center_frames']):nxt[r]=g.basis(F)
  for r in range(V,2*V):nxt[r]=g.basis(a.get('target_levels',{}).get(str(r-V),[]))
 for i in reversed(range(len(a[sec]))):
  e=a[sec][i];rs=e[1:3]if e[0]=='add'else e[1:2]
  upper=nxt[rs[0]]
  for r in rs[1:]:upper=meet(upper,nxt[r])
  E=join(e[-1],meet(desired[i],upper))
  assert span(E)<=span(upper)
  if E!=g.basis(e[-1]):changes.append([sec,i,e[-1],list(E)]);e[-1]=list(E)
  for r in rs:nxt[r]=E
prof=g.profile(a);gain=sum((prof[r]-before[r])*r*math.log(r)for r in set(prof)|set(before))
a['report']['local_profile']={str(k):v for k,v in sorted(prof.items())}
a['cleanup']=[g.inverse(e,g.FULL)for e in reversed(a['A']+a['B'])if not V<=e[1]<2*V]
out=args.out;out.mkdir(exist_ok=False);(out/'FULL-WORD.json.gz').write_bytes(gzip.compress(json.dumps(a,sort_keys=True,separators=(',',':')).encode(),mtime=0))
r=dict(before=dict(before),after=dict(prof),delta={r:prof[r]-before[r]for r in set(prof)|set(before)if prof[r]!=before[r]},changes=changes,entropy_gain=gain)
(out/'PORT.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({k:v for k,v in r.items()if k!='changes'}));print('changes',len(changes))

assert len(changes)==477 and dict(prof)=={1:2284,2:456,3:488,4:168,5:56,6:56,8:8}
assert all(old[k]==a[k] for k in ('cut','precondition','centers','center_frames','start_extra','target_levels'))
assert all(x[:-1]==y[:-1] for sec in ('A','B') for x,y in zip(old[sec],a[sec]))
assert all(span(x[-1])<=span(y[-1]) for sec in ('A','B') for x,y in zip(old[sec],a[sec]))
