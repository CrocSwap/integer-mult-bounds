"""Original exact carrier matching/role reconstruction, no upstream imports."""
import sys,os
if sys.flags.optimize or os.environ.get('PYTHONOPTIMIZE'):raise RuntimeError('Assertions required')
from pathlib import Path
from collections import deque
import pickle,json,time,resource,hashlib
ROOT=Path(__file__).resolve().parent;REPO=Path(os.environ.get('BIRTH_REPO',ROOT.parents[1]));start=time.monotonic()
(sys.platform=='darwin' or resource.setrlimit(resource.RLIMIT_AS,(512*1024**2,512*1024**2)));resource.setrlimit(resource.RLIMIT_CPU,(30,30));sys.setrecursionlimit(5000)
g=pickle.loads((ROOT/'GRAPH.pkl').read_bytes());h,v=g['h'],g['v'];args,core,cover,rank,kind=[g[k]for k in ('args','core','cover','rank','kind')];active=g['active'];roots=g['roots'];n=len(args);full=(1<<h)-1
uses=[[]for _ in range(n)];use=[];edge={}
for x in active:
 if args[x]:
  for pos,y in enumerate(args[x]):
   uid=len(use);uses[y].append(uid);use.append((y,0,x,pos));edge[x,pos]=uid
for j,x in enumerate(roots):uid=len(use);uses[x].append(uid);use.append((x,1,j,0))
def contains(x,y):
 tx,ty=kind[x],kind[y]
 if tx==ty==1:return not(core[y]&~core[x]or cover[x]&~cover[y])
 if tx in(1,2)and ty==2:return not cover[x]&~cover[y]
 if tx==1 and ty==3:return bool(core[x]&core[y])
 if tx==2 and ty==3:return not cover[x]&~core[y]
 if tx==3 and ty==2:return cover[y]==full
 return tx==ty==3 and core[x]==core[y]
left=[];adj={}
for x in active:
 if not args[x]:continue
 choices=[]
 for y in args[x]:
  for uid in uses[y]:
   _,typ,dest,pos=use[uid];target=roots[dest]if typ else dest
   orderid=n+dest if typ else dest
   if (rank[x],x)<(rank[target],orderid)and contains(x,target):choices.append(uid)
 if choices:
  left.append(x);adj[x]=sorted(set(choices),key=lambda uid:(use[uid][0],uses[use[uid][0]].index(uid)))
# Ordinary ordered Hopcroft-Karp, with explicit shortest augmenting layers.
L=[-1]*n;R=[-1]*len(use);INF=n+1;rounds=[]
while True:
 dist=[INF]*n;queue=deque()
 for x in left:
  if L[x]<0:dist[x]=0;queue.append(x)
 shortest=INF
 while queue:
  x=queue.popleft()
  if dist[x]>=shortest:continue
  for uid in adj[x]:
   y=R[uid]
   if y<0:shortest=dist[x]+1
   elif dist[y]==INF:dist[y]=dist[x]+1;queue.append(y)
 if shortest==INF:break
 def augment(x):
  for uid in adj[x]:
   y=R[uid]
   if (y<0 and dist[x]+1==shortest)or(y>=0 and dist[y]==dist[x]+1 and augment(y)):
    L[x]=uid;R[uid]=x;return True
  dist[x]=INF;return False
 gained=sum(augment(x)for x in left if L[x]<0);assert gained;rounds.append((shortest,gained))
links={x:L[x]for x in left if L[x]>=0};assert len(links)==71185,len(links)
# Every matched edge is an actual unchanged input continuation into a later use.
assert len(set(links.values()))==len(links)
for x,uid in links.items():assert use[uid][0]in args[x]and uid in adj[x]
held=[];first=[];ops=[];role_of={};terminal={}
def alloc(x):
 s=len(first);first.append(x);held.append([x]);return s
for x in sorted(active,key=lambda x:(rank[x],x)):
 free=[uid for uid in uses[x]if R[uid]<0]
 if not args[x]:
  for uid in free:
   s=alloc(x);ops.append((0,s,x,-1));role_of[uid]=s
  continue
 a,b=args[x];sa,sb=role_of.pop(edge[x,0]),role_of.pop(edge[x,1]);assert sa!=sb
 if x in links and use[links[x]][0]==a:sa,sb=sb,sa
 ops.append((1,sa,sb,x));held[sa].append(x);held[sb].append(x)
 if x in links:role_of[links[x]]=sb
 assert free;role_of[free[0]]=sa
 for uid in free[1:]:
  s=alloc(x);ops.append((2,sa,s,x));role_of[uid]=s
for uid,row in enumerate(use):
 if row[1]:terminal[role_of.pop(uid)]=row[2]
assert not role_of and len(first)==28705 and len(terminal)==len(roots)
# All original-role fresh signals, not sampled values.
values=[0]*len(first)
for op,s,t,x in ops:
 if op==0:values[s]=1<<(t-1)
 elif op==1:
  assert not(values[s]&values[t]);values[s]|=values[t];assert values[s]==g['support'][x]
 else:assert values[t]==0;values[t]=values[s];assert values[t]==g['support'][x]
for s,j in terminal.items():assert values[s]==g['support'][roots[j]]
for chain in held:
 for a,b in zip(chain,chain[1:]):assert contains(a,b)
# Dependencies in the exact selected chronological program.
previous=[-1]*len(first);pred=[[]for _ in ops];last=[-1]*len(first)
for i,(op,s,t,x)in enumerate(ops):
 if op:
  for r in(s,t):
   if previous[r]>=0:pred[i].append(previous[r])
   previous[r]=i;last[r]=i
centers=[s for s,j in terminal.items()if j>=len(roots)-h]
phase=set();todo=[last[s]for s in centers]
while todo:
 i=todo.pop()
 if i not in phase:phase.add(i);todo.extend(pred[i])
touched=set(centers)
for i in phase:
 _,s,t,_=ops[i];touched.update((s,t))
expected=json.loads((REPO/'research/shrunk-frames/complex-profile.json').read_text());assert (len(phase),len(touched))==(expected['phase_one_ops'],expected['phase_one_roles']),(len(phase),len(touched))
g.update(uses=uses,use=use,links=links,matched_use=R,holds=held,first=first,ops=ops,terminal=terminal,last=last,phase=phase,touched=touched,center_roles=centers)
raw=pickle.dumps(g,protocol=4);(ROOT/'ROLES.pkl').write_bytes(raw)
receipt=dict(status='PASS original exact118 matching/role/source reconstruction',links=len(links),roles=len(first),ops=len(ops),phase_one_ops=len(phase),phase_one_roles=len(touched),augmenting_rounds=rounds,checkpoint_sha256=hashlib.sha256(raw).hexdigest(),seconds=time.monotonic()-start,rss_KiB=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
(ROOT/'ROLES_CHECK.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
