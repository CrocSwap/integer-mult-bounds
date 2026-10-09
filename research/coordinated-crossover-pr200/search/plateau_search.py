"""Exact admissibility search on equal-frame operation plateaux.

Searches frame enlargements on connected equal-frame operation components.
The floating entropy objective proposes moves only; paid-moment and scalar-word
admission belong to the parent verifier. Every output candidate is checked with
the inherited exact rational frame and physical-chain predicates.

Prepared with OpenAI Codex assistance. Apache-2.0.
Retains PR200's physical word and exact integer checker (Chafik Boukhalfa),
and consumes PR211's frozen cascade frame input (Rohan Arun, Claude assisted).
"""
from pathlib import Path
from collections import Counter,defaultdict
import sys,json,time,math,argparse
sys.dont_write_bytecode=True
ap=argparse.ArgumentParser(description=__doc__)
ap.add_argument('--bit-package',required=True,type=Path)
ap.add_argument('--frames',required=True,type=Path)
ap.add_argument('--out',required=True,type=Path)
args=ap.parse_args();P=args.bit_package.resolve();D=args.out.resolve();D.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(P/'bit'))
from word import Candidate
started=time.monotonic();W=Candidate();C=W.C
for i,rows in json.loads((args.frames).read_text()):W.opframe[i]=W.register(rows)
base=W.opframe[:]
W.changed_frames=[i for i,(a,b) in enumerate(zip(W.original_opframe,W.opframe))if a!=b]
W.endframe={s:W.opframe[xs[-1]]for s,xs in W.role_ops.items()}
W.exact_frames();baseline=W.row();print('initialized',len(W.ops),len(C.B),'frames',time.monotonic()-started,flush=True)
# Fixed boundary refs are encoded as -frame-1, while zero frame gets its own id.
zero=W.register([]);full=W.w['full_frame'];before=[[]for _ in W.ops];after=[[]for _ in W.ops]
starts={b:W.w['source_frame'][x]for x,b in W.source.items()};starts.update({b:z['frame']for b,z in W.gauge.items()})
ends={s:W.w['root_frame'][j]for j,s in enumerate(W.w['rootroles'])}
ends.update({d:W.gauge[b]['frame']for b,d in W.pairs})
for s,xs in W.role_ops.items():
 chain=[-starts.get(s,zero)-1]+xs+[-ends.get(s,full)-1]
 for j,i in enumerate(xs,1):before[i].append(chain[j-1]);after[i].append(chain[j+1])
assert all(len(x)==2 for x in before+after)
def frame(ref):return W.opframe[ref]if ref>=0 else-ref-1
F=[0]+[r*math.log(r)for r in range(1,W.h+1)]
def merit(d,prev,nxt):return sum(F[d-C.dimf[p]]for p in prev)+sum(F[C.dimf[n]-d]for n in nxt)
nondeg={};intersections={};changes=[];tot=0

def good(f):
 if f not in nondeg:nondeg[f]=C.nondeg(f)
 return nondeg[f]
def intersection(a,b):
 if C.sub(a,b):return a
 if C.sub(b,a):return b
 k=tuple(sorted((a,b)))
 if k not in intersections:
  rows,_=W.module.kernel(C.A[a]+C.A[b],W.h)
  intersections[k]=W.register(rows)
 return intersections[k]
# Move connected equal-frame plateaux as units.
parent=list(range(len(W.ops)))
def find(i):
 while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
 return i
def union(i,j):
 i,j=find(i),find(j)
 if i!=j:parent[j]=i
for i,ns in enumerate(after):
 for j in ns:
  if j>=0 and C.dimf[W.opframe[i]]==C.dimf[W.opframe[j]] and C.sub(W.opframe[i],W.opframe[j]):union(i,j)
groups=defaultdict(list)
for i in range(len(W.ops)):groups[find(i)].append(i)
print('groups',len(groups),'largest',sorted(map(len,groups.values()),reverse=True)[:20],flush=True)
stats=Counter();gains=[]
for sweep in range(8):
 num=0;gain=0
 for xs in groups.values():
  members=set(xs);old=W.opframe[xs[0]];d=C.dimf[old]
  if any(not(C.dimf[W.opframe[i]]==d and C.sub(old,W.opframe[i]))for i in xs):continue
  prev=[frame(j)for i in xs for j in before[i]if j not in members]
  nxt=[frame(j)for i in xs for j in after[i]if j not in members]
  stats['groups']+=1
  if min(C.dimf[f]for f in nxt)<=d:continue
  stats['dimension_room']+=1;f=nxt[0]
  for n in nxt[1:]:
   f=intersection(f,n)
   if C.dimf[f]<=d:break
  dd=C.dimf[f]
  if dd<=d:continue
  stats['intersection_room']+=1
  if not good(f):stats['degenerate']+=1;continue
  assert C.sub(old,f)
  improvement=merit(dd,prev,nxt)-merit(d,prev,nxt)
  stats['positive'if improvement>1e-10 else 'nonpositive']+=1
  gains.append([improvement,len(xs),d,dd])
  if improvement<=1e-10:continue
  for i in xs:W.opframe[i]=f
  num+=len(xs);gain+=improvement;changes.append(dict(ops=xs,old_dim=d,new_dim=dd,gain=improvement))
 print('sweep',sweep,'changes',num,'entropy_gain',gain,'stats',dict(stats),'seconds',time.monotonic()-started,flush=True)
 tot+=gain
 if not num:break
print('best gains',sorted(gains,reverse=True)[:20],flush=True)
W.changed_frames=[i for i,(a,b)in enumerate(zip(W.original_opframe,W.opframe))if a!=b]
W.endframe={s:W.opframe[xs[-1]]for s,xs in W.role_ops.items()}
W.exact_frames();row=W.row();delta=Counter({int(k):n for k,n in row['child_histogram'].items()});delta.subtract({int(k):n for k,n in baseline['child_histogram'].items()})
frames=[[i,C.B[f]]for i,f in enumerate(W.opframe)if f!=base[i]]
(D/'plateau-additional-frames.json').write_text(json.dumps(frames,separators=(',',':'))+'\n')
(D/'plateau-all-frames.json').write_text(json.dumps([[i,C.B[f]]for i,f in enumerate(W.opframe)if f!=W.w['op_frame'][i]],separators=(',',':'))+'\n')
out=dict(status='EXACT_FRAMES_AND_NESTED_CHAINS_PASS_NOT_FULL_REPLAY',baseline=baseline,profile=row,child_delta={str(k):v for k,v in sorted(delta.items())if v},changes=changes,entropy_gain=tot,elapsed=time.monotonic()-started)
(D/'plateau-result.json').write_text(json.dumps(out,indent=2)+'\n');print('DONE additional',len(frames),'delta',out['child_delta'],'gain',tot,flush=True)
