"""Frame descent after target mixing; strict target x-support and exact replay after each accepted batch."""
from pathlib import Path
from collections import Counter,defaultdict
import json,hashlib,math,sys,time
r=Path.cwd();source=Path(sys.argv[1]);out=r/'r715-factored-extreme-frames';assert not out.exists();out.mkdir()
raw=source.read_bytes();w=json.loads(raw)
sys.path.insert(0,str(r/'source443-review/code'));import e8core as E
L=E.Lat(w['lines']);fs=E.to_masks(w,L);dims=[L.dim(f) for f in fs];n=2*w['v']+w['R'];full=w['final'][0]
events=[];positions=[];chains=[[] for _ in range(n)]
def event(f,regs,loc=None):
 i=len(events);events.append([f,regs,loc])
 for x in regs:chains[x].append(i)
for x,f in enumerate(w['start']):event(f,[x])
for phase in ('D','A','B','C'):
 w[phase]=[[f,d,[s]] for f,d,ss in w[phase] for s in ss]
 if phase=='B':
  for x in w['ret']:event(full,[x])
  for x in range(w['v'],2*w['v']):event(0,[x])
 for i,(f,d,ss) in enumerate(w[phase]):positions.append(len(events));event(f,[d]+ss,(phase,i))
for x,f in enumerate(w['final']):event(f,[x])
prev={};nxt={}
for x,chain in enumerate(chains):
 for j,i in enumerate(chain):
  if j:prev[i,x]=chain[j-1]
  if j+1<len(chain):nxt[i,x]=chain[j+1]
support=[1<<i if i<w['v'] else 0 for i in range(n)];needs={}
for ph in ('D','A','B','C'):
 for j,(f,d,ss) in enumerate(w[ph]):
  required=0
  for src in ss:required|=support[src];support[d]|=support[src]
  if d>=2*w['v']:required|=support[d]
  assert required&~fs[f]==0,(ph,j,'source outside frame')
  needs[ph,j]=required
from fractions import Fraction
c=float(Fraction(json.loads((r/'r715-factor-replica64-strong-RESULT.json').read_text())['bit_lower']));chi=lambda d:d*math.expm1(c*math.log(78/d)) if d else 0
frame_index={mask:i for i,mask in enumerate(fs)}
def add_frame(mask):
 mask=L.close(mask)
 if mask not in frame_index:
  frame_index[mask]=len(fs);fs.append(mask);dims.append(L.dim(mask));w['frames'].append([j for j in range(w['v']) if mask>>j&1])
 return frame_index[mask]
ranked=sorted(range(len(fs)),key=lambda i:(dims[i],i));mutable={i for i in positions if events[i][2][0] in ('A','B','C')}
def evaluate(gs):
 chosen=set(gs);lo=0;hi=fs[full];edges=set()
 for i in gs:
  lo|=needs[events[i][2]]
  for x in events[i][1]:
   a,b=prev[i,x],nxt[i,x];edges.add((a,i,x));edges.add((i,b,x))
   if a not in chosen:lo|=fs[events[a][0]]
   if b not in chosen:hi&=fs[events[b][0]]
 if lo&~hi:return
 candidates=[add_frame(lo),add_frame(hi)]
 best=None
 for nf in set(candidates):
  delta=Counter()
  for a,b,x in edges:
   oldrank=dims[events[b][0]]-dims[events[a][0]];newrank=dims[nf if b in chosen else events[b][0]]-dims[nf if a in chosen else events[a][0]]
   assert oldrank>=0 and newrank>=0
   delta[oldrank]-=1;delta[newrank]+=1
  delta.pop(0,None);delta={k:v for k,v in delta.items() if v};score=sum(chi(k)*v for k,v in delta.items())
  if score<-1e-12 and (best is None or score<best[0]):best=(score,nf,delta)
 return best
selected=[]
def apply(gs,z):
 score,nf,delta=z;changes=[]
 for i in gs:
  f=events[i][0];events[i][0]=nf;ph,j=events[i][2];w[ph][j][0]=nf;changes.append([ph,j,f,nf])
 selected.append(dict(changes=changes,score=score,delta=delta))
for sweep in range(20):
 moved=0;order=sorted(mutable,reverse=bool(sweep%2))
 for i in order:
  z=evaluate([i])
  if z:apply([i],z);moved+=1
 print('single sweep',sweep,'gates',len(order),'moves',moved,flush=True)
 if not moved:break
adj=defaultdict(set)
for chain in chains:
 for a,b in zip(chain,chain[1:]):
  if a in mutable and b in mutable:adj[a].add(b);adj[b].add(a)
frontier={(a,) for a in mutable};counts=[]
for size in range(2,3):
 groups=set()
 for gs in frontier:
  for b in set().union(*(adj[x] for x in gs))-set(gs):groups.add(tuple(sorted((*gs,b))))
 frontier=groups;positive=[]
 for gs in sorted(groups):
  z=evaluate(gs)
  if z:positive.append((z[0],gs))
 accepted=0
 for _,gs in sorted(positive):
  z=evaluate(gs)
  if z:apply(gs,z);accepted+=1
 counts.append(dict(size=size,tested=len(groups),positive=len(positive),accepted=accepted));print('groups',counts[-1],flush=True)
# Independent exact rational span and all scalar columns after the transformations.
check=E.replay(w,span_mode='z');assert not check['viol'],check['viol'][:10]
data=json.dumps(w,sort_keys=True,separators=(',',':')).encode();(out/'WORD.json').write_bytes(data)
res=dict(status='PASS_EXACT_RETIMER_REPLAY_GLOBAL_PENDING' if selected else 'PASS_NO_IMPROVING_RETIMER_MOVES',source_sha256=hashlib.sha256(raw).hexdigest(),word_sha256=hashlib.sha256(data).hexdigest(),changes=selected,group_counts=counts,local_profile=dict(check['H']),columns=check['n'],scope='Smallest and largest legal root-spanned frames for singles and connected pairs, allowing new frames; global hosting and physical prefix pending.')
(out/'RESULT.json').write_text(json.dumps(res,indent=2)+'\n');print(res['status'],'moves',len(selected),flush=True)
