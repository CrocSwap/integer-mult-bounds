from pathlib import Path
import sys
sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "paid-controller"))
from portable import WORKBENCH, output_path, source_name
"""Complete paid adjacency word for an orthogonal basis; exact integer replay."""
from pathlib import Path
from collections import Counter
import json
N=16;FULL=(1<<N)-1

def require(ok,msg):
 if not ok:raise ValueError(msg)

def build():
 source=list(range(N));target=list(range(N,2*N));plans=[];next_id=2*N
 for size in (1,2,4,8):
  for first in range(0,N,2*size):
   left=list(range(first,first+size));right=list(range(first+size,first+2*size))
   for child,other in ((left,right),(right,left)):
    for t in other[1:]:plans.append((size,child,other,t,next_id));next_id+=1
 frames=[1<<i for i in range(N)]+[0]*(next_id-N)
 rows=[[int(i==j) for j in range(next_id)] for i in range(next_id)]
 profile=Counter();paths=[[]for _ in rows];undo=[];events=[];helper=iter(plans)
 def grow(i,frame):
  old=frames[i];require(old&frame==old,'Nested frame growth')
  if old!=frame:
   d=frame.bit_count()-old.bit_count();profile[d]+=1;paths[i].append(d);events.append(['grow',i,old,frame]);frames[i]=frame
 def add(src,dst,coefficient=1,record=False):
  require(frames[src]==frames[dst],'Common-frame scalar ADD')
  rows[dst]=[a+coefficient*b for a,b in zip(rows[dst],rows[src])]
  events.append(['add',src,dst,coefficient])
  if record:undo.append((src,dst,-coefficient))
 for _,_,_,t,h in plans:add(h,target[t],-1)
 for size in (1,2,4,8):
  for first in range(0,N,2*size):
   left=list(range(first,first+size));right=list(range(first+size,first+2*size));parent=sum(1<<j for j in left+right)
   for child,other in ((left,right),(right,left)):
    pivot=source[child[0]];childframe=sum(1<<j for j in child);require(frames[pivot]==childframe,'Child pivot at its exact span')
    copies=[]
    for t in other[1:]:
     p=next(helper);require(p[:4]==(size,child,other,t),'Deterministic helper order');h=p[4]
     grow(h,childframe);add(pivot,h,record=True);copies.append((t,h))
    t=other[0];cap=parent^(1<<t);grow(pivot,cap);grow(target[t],cap);add(pivot,target[t])
    for t,h in copies:
     cap=parent^(1<<t);grow(h,cap);grow(target[t],cap);add(h,target[t])
   if size<8:
    a,b=source[left[0]],source[right[0]];grow(a,parent);grow(b,parent);add(b,a,record=True)
 for i in source+list(range(2*N,next_id)):grow(i,FULL)
 for src,dst,coefficient in reversed(undo):add(src,dst,coefficient)
 for i in source+list(range(2*N,next_id)):
  require(rows[i]==[int(i==j)for j in range(next_id)],'All source data and arbitrary dirty helpers restored')
 for i,t in enumerate(target):
  want=[int(j==t or j<N and j!=i)for j in range(next_id)]
  require(rows[t]==want,'Exactly clique adjacency, no diagonal, no helper dirt')
  require(frames[t]==FULL^(1<<i),'Target exact orthogonal hyperplane')
 # Removing a single direct output ADD necessarily changes a nonzero input column.
 require(any(event[0]=='add' and event[2] in target and event[1]<N for event in events),'Nontrivial direct data output')
 receipt=dict(scope='One complete orthogonal16-clique adjacency subword. Coordinates denote its orthogonal basis; arbitrary old helpers restored. No fitting kernel, complete lattice word, or exponent claim.',ports=N,helpers=next_id-2*N,helper_paths={str(k):v for k,v in sorted(Counter(tuple(p)for p in paths[2*N:]).items())},source_paths=paths[:N],target_paths=paths[N:2*N],paid_profile={str(k):v for k,v in sorted(profile.items())},paid_mass=sum(k*v for k,v in profile.items()),expected_mass=2*N*(N-1)+(next_id-2*N)*N,scalar_adds=sum(e[0]=='add'for e in events),checks=['All scalar columns over exact integers','Every ADD has identical current frames','Every frame chain is nested','All source and helper columns restored','Every output is exactly all other source inputs','Every target ends in its exact orthogonal hyperplane'])
 require(receipt['paid_mass']==receipt['expected_mass'],'Complete rank-mass identity')
 return receipt,events
if __name__=='__main__':
 receipt,events=build();root=Path(__file__).resolve().parent
 output_path('continuation/endpoint-costs/CLIQUE-WORD.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
