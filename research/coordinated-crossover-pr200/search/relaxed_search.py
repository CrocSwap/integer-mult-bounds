"""Seeded cascade perturbation and exact admissibility search.

The frozen output frames require independent paid-moment and scalar-word replay.
Float entropy is used only to propose candidates. The final output passes exact
rational value-span, nondegeneracy and complete physical-chain checks.

Prepared with OpenAI Codex assistance; Apache-2.0. Uses PR200's physical word
and checkers (Chafik Boukhalfa), PR211's cascade frame witness (Rohan Arun with
Anthropic Claude assistance), and our independently found plateau additions.
"""
from pathlib import Path
from collections import Counter,defaultdict
import sys,json,time,math,argparse
sys.dont_write_bytecode=True
ap=argparse.ArgumentParser(description=__doc__)
ap.add_argument('--bit-package',required=True,type=Path)
ap.add_argument('--frames',required=True,type=Path)
ap.add_argument('--additional-frames',required=True,type=Path)
ap.add_argument('--out',required=True,type=Path)
args=ap.parse_args();P=args.bit_package.resolve();D=args.out.resolve();D.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(P/'bit'))
from word import Candidate
started=time.monotonic();W=Candidate();C=W.C
for i,rows in json.loads((args.frames).read_text()):W.opframe[i]=W.register(rows)

for i,rows in json.loads((args.additional_frames).read_text()):W.opframe[i]=W.register(rows)
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
unions={}
def join(a,b):
 if C.sub(a,b):return b
 if C.sub(b,a):return a
 k=tuple(sorted((a,b)))
 if k not in unions:unions[k]=W.register(list(C.B[a])+list(C.B[b]))
 return unions[k]
# Complete upper envelope determined solely by immutable endpoint boundaries.
cap=[None]*len(W.ops)
for i in range(len(W.ops)-1,-1,-1):
 ns=[cap[j]if j>=0 else frame(j)for j in after[i]]
 cap[i]=intersection(*ns)
 assert C.sub(W.opframe[i],cap[i])
print('global caps built',time.monotonic()-started,flush=True)

def transaction(seed,f):
 old=W.opframe[seed]
 if C.sub(f,old):return None
 if not C.sub(old,f):f=join(old,f)
 if not C.sub(f,cap[seed]) or not good(f):return None
 update={seed:f};pending=[seed]
 while pending:
  i=pending.pop();f=update[i]
  for j in after[i]:
   old=update.get(j,frame(j))
   if C.sub(f,old):continue
   if j<0:return None
   z=join(f,old)
   if not C.sub(z,cap[j])or not good(z):return None
   update[j]=z;pending.append(j)
  if len(update)>1000:return None
 gain=0.0
 for i,f in update.items():
  d=C.dimf[f];od=C.dimf[W.opframe[i]]
  for j in before[i]:
   pd=C.dimf[update.get(j,frame(j))];opd=C.dimf[frame(j)]
   gain+=F[d-pd]-F[od-opd]
  for j in after[i]:
   if j not in update:
    nd=C.dimf[frame(j)];gain+=F[nd-d]-F[nd-od]
 return gain,update

valueframes={i:f for i,f in enumerate(W.w['source_frame'])}
def valueframe(n):
 if n not in valueframes:
  a,b=W.g['args'][n];valueframes[n]=join(valueframe(a),valueframe(b))
 return valueframes[n]
floor=[None]*len(W.ops)
for i in range(len(W.ops)):
 ps=[floor[j]if j>=0 else frame(j)for j in before[i]]
 floor[i]=join(join(*ps),valueframe(W.ops[i][2]))
 assert C.sub(floor[i],W.opframe[i])
print('global floors built',time.monotonic()-started,flush=True)

def lower_transaction(seed,f):
 old=W.opframe[seed]
 if C.sub(old,f):return None
 if not C.sub(f,old):f=intersection(old,f)
 if not C.sub(floor[seed],f) or not good(f):return None
 update={seed:f};pending=[seed]
 while pending:
  i=pending.pop();f=update[i]
  for j in before[i]:
   old=update.get(j,frame(j))
   if C.sub(old,f):continue
   if j<0:return None
   z=intersection(f,old)
   if not C.sub(floor[j],z)or not good(z):return None
   update[j]=z;pending.append(j)
  if len(update)>1000:return None
 gain=0.0
 for i,f in update.items():
  d=C.dimf[f];od=C.dimf[W.opframe[i]]
  for j in before[i]:
   pd=C.dimf[update.get(j,frame(j))];opd=C.dimf[frame(j)]
   gain+=F[d-pd]-F[od-opd]
  for j in after[i]:
   if j not in update:
    nd=C.dimf[frame(j)];gain+=F[nd-d]-F[nd-od]
 return gain,update
import random
rng=random.Random(2116205)
stats=Counter();score=0.;bestscore=0.;bestframes=W.opframe[:];bestchanges=[]
for sweep,T in enumerate([.8,.4,.15,.05]+[0]*15+[.5,.2,.05,.01]+[0]*15):
 num=0;gain=0
 order=list(range(len(W.ops)));rng.shuffle(order)
 for oi,i in enumerate(order):
  old=W.opframe[i]
  direction,bounds,neighbors,fn=rng.choice([('down',floor,before,lower_transaction),('up',cap,after,transaction)])
  if C.dimf[old]==C.dimf[bounds[i]]:continue
  candidates={bounds[i]}
  for chain in range(2):
   j=neighbors[i][chain]
   for depth in range(8):
    candidates.add(frame(j))
    if j<0:break
    if depth<3:candidates.update(frame(k)for k in neighbors[j])
    j=min(neighbors[j],key=lambda k:C.dimf[frame(k)])
  best=None
  for f in candidates:
   if f==old:continue
   stats['proposed']+=1;r=fn(i,f)
   if r is None:continue
   stats['feasible']+=1
   if best is None or r[0]>best[0]:best=r
  if best and(best[0]>1e-10 or T and rng.random()<math.exp(min(0,best[0]/T))):
   improvement,updates=best
   for j,f in updates.items():W.opframe[j]=f
   num+=len(updates);gain+=improvement;score+=improvement
   if improvement>1e-10:stats['improving']+=1
   else:stats['annealed']+=1
   changes.append(dict(direction=direction,seed=i,ops=sorted(updates),gain=improvement))
   if score>bestscore+1e-9:
    bestscore=score;bestframes=W.opframe[:];bestchanges=changes[:]
  if oi%10000==0:print('scan',sweep,oi,'T',T,'current_gain',score,'best_gain',bestscore,'seconds',time.monotonic()-started,flush=True)
 print('sweep',sweep,'T',T,'changes',num,'entropy_gain',gain,'current',score,'best',bestscore,'stats',dict(stats),'seconds',time.monotonic()-started,flush=True)
 if sweep==18:
  # Restart second excursion from strongest state after full greedy relaxation.
  W.opframe=bestframes[:];score=bestscore
W.opframe=bestframes;tot=bestscore;changes=bestchanges
W.changed_frames=[i for i,(a,b)in enumerate(zip(W.original_opframe,W.opframe))if a!=b]
W.endframe={s:W.opframe[xs[-1]]for s,xs in W.role_ops.items()}
W.exact_frames();row=W.row();delta=Counter({int(k):n for k,n in row['child_histogram'].items()});delta.subtract({int(k):n for k,n in baseline['child_histogram'].items()})
frames=[[i,C.B[f]]for i,f in enumerate(W.opframe)if f!=base[i]]
(D/'relaxed-additional-frames.json').write_text(json.dumps(frames,separators=(',',':'))+'\n')
(D/'relaxed-all-frames.json').write_text(json.dumps([[i,C.B[f]]for i,f in enumerate(W.opframe)if f!=W.w['op_frame'][i]],separators=(',',':'))+'\n')
out=dict(status='EXACT_FRAMES_AND_NESTED_CHAINS_PASS_NOT_FULL_REPLAY',baseline=baseline,profile=row,child_delta={str(k):v for k,v in sorted(delta.items())if v},changes=changes,entropy_gain=tot,elapsed=time.monotonic()-started)
(D/'relaxed-result.json').write_text(json.dumps(out,indent=2)+'\n');print('DONE additional',len(frames),'delta',out['child_delta'],'gain',tot,flush=True)
