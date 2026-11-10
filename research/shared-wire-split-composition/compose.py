#!/usr/bin/env python3
"""Compose #6937 wh's 16 wires with #6936's two plain helper splits.
All source events used by the composition are preserved with exact rational
coefficients. A dependency DAG preserves runs of commuting ADD destinations
and ADD sources on both branch words; other accesses are exclusive.
"""
import json,gzip,heapq,copy,collections,pathlib,sys
ROOT=pathlib.Path(__file__).resolve().parent
OUT=ROOT/'build'

def read(p):return json.load(gzip.open(p))
def access(e):
 if e[0] in ('MOVE','INIT','CLEAR','SCALE'):return [(e[1],'M')]
 return [(e[1],'M' if e[0]=='COPY' else 'A'),(e[2],'R')]
def tokens(seq):
 c=collections.Counter();a=[]
 for e in seq:
  e=tuple(e);c[e]+=1;a.append((e,c[e]))
 return a

def main():
 m=read(ROOT/'data/main_6936.json.gz');w=read(ROOT/'data/wh_6937.json.gz')
 assert m['frames']==w['frames']
 # Reserve 1459 and 1460 for the split tails; shift wh's 16 helper wires and owned scratch.
 def shift(e):
  e=e.copy();e[1]+=2*(e[1]>=1459)
  if e[0] in ('ADD','COPY'):e[2]+=2*(e[2]>=1459)
  return e
 wp=[shift(e) for e in w['program']]
 # main's owned roles must move by the 16 wh wires.
 def shiftmain(e):
  e=e.copy();e[1]+=16*(e[1]>=1461)
  if e[0] in ('ADD','COPY'):e[2]+=16*(e[2]>=1461)
  return e
 mp=[shiftmain(e) for e in m['program']]
 split={1452,1455,1459,1460}
 touches=lambda e:any(r in split for r,c in access(e))
 p=[e for e in wp if not touches(e)]+[e for e in mp if touches(e)]
 ts=tokens(p);ids={x:i for i,x in enumerate(ts)}
 assert len(ids)==len(ts)
 adj=[set()for _ in ts];deg=[0]*len(ts);priority=[10**8+i for i in range(len(ts))]
 constraints=[]
 for nm,program in [('wh',wp),('main',mp)]:
  # Source occurrence labels are safe here: any repeated exact event has unchanged multiplicity.
  nt=tokens(program); regs={}
  for pos,t in enumerate(nt):
   if t not in ids:continue
   idx=ids[t];priority[idx]=min(priority[idx],pos)
   for r,c in access(t[0]):regs.setdefault(r,[]).append((c,idx))
  count=0
  for r,seq in regs.items():
   runs=[]
   for c,i in seq:
    if runs and runs[-1][0]==c and c in ('A','R'):runs[-1][1].append(i)
    else:runs.append((c,[i]))
   for (_,a),(_,b) in zip(runs,runs[1:]):
    for i in a:
     for j in b:
      if j not in adj[i]:adj[i].add(j);deg[j]+=1;count+=1
  constraints.append((nm,count))
 q=[(priority[i],i) for i,d in enumerate(deg) if not d];heapq.heapify(q);order=[]
 while q:
  _,i=heapq.heappop(q);order.append(i)
  for j in adj[i]:
   deg[j]-=1
   if deg[j]==0:heapq.heappush(q,(priority[j],j))
 print('events',len(ts),'ordered',len(order),'constraints',constraints)
 if len(order)!=len(ts):
  remaining=[i for i,d in enumerate(deg) if d]
  (OUT/'cycles.json').write_text(json.dumps([ts[i] for i in remaining],indent=1))
  print('remaining',len(remaining),'first',[(i,ts[i])for i in remaining[:15]])
  return 1
 z=copy.deepcopy(w);z['initial']=w['initial'][:1459]+[m['initial'][1459],m['initial'][1460]]+w['initial'][1459:]
 z['final']=w['final'][:1459]+[m['final'][1459],m['final'][1460]]+w['final'][1459:]
 z['final'][1452]=m['final'][1452];z['final'][1455]=m['final'][1455]
 z['public']=len(z['initial']);z['program']=[list(ts[i][0])for i in order]
 with gzip.open(OUT/'composed.json.gz','wt')as f:json.dump(z,f,separators=(',',':'))
 (OUT/'composition.json').write_text(json.dumps({'events':len(ts),'constraints':constraints,'split_roles':sorted(split),'source_event_counts':{'wh_removed':sum(touches(e)for e in wp),'main_added':sum(touches(e)for e in mp)}},indent=2))
 print('WROTE',OUT/'composed.json.gz')
 return 0
if __name__=='__main__':sys.exit(main())
