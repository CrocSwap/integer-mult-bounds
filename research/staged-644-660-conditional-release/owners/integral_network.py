"""Deterministic lower-bounded integral networks; standard library only.

The exact algorithm used by the original finite expansion, extracted for portable replay.
"""
from collections import Counter,defaultdict
if not __debug__:
 raise RuntimeError('enabled assertions required for exact integral network realization')
W=(4,5,6,7,8,9)
INV=(26,2,18,52,97,213)

class Network:
 def __init__(self,n):self.adj=[[] for _ in range(n)];self.to=[];self.cap=[]
 def add(self,u,v,capacity):
  assert capacity>=0
  i=len(self.to);self.to.extend((v,u));self.cap.extend((int(capacity),0));self.adj[u].append(i);self.adj[v].append(i+1);return i
 def maxflow(self,s,t,limit):
  total=0;n=len(self.adj)
  while total<limit:
   level=[-1]*n;level[s]=0;queue=[s]
   for u in queue:
    for e in self.adj[u]:
     v=self.to[e]
     if self.cap[e] and level[v]<0:level[v]=level[u]+1;queue.append(v)
   if level[t]<0:break
   pos=[0]*n
   def push(u,amount):
    if u==t:return amount
    while pos[u]<len(self.adj[u]):
     e=self.adj[u][pos[u]];v=self.to[e]
     if self.cap[e] and level[v]==level[u]+1:
      sent=push(v,min(amount,self.cap[e]))
      if sent:self.cap[e]-=sent;self.cap[e^1]+=sent;return sent
     pos[u]+=1
    return 0
   while total<limit:
    sent=push(s,limit-total)
    if not sent:break
    total+=sent
  return total

def copy_colors(task_indices,task_bin,task_width,bin_group,group_n,S):
 """Decompose one macro-call by lower-bounded integral network flows."""
 bucket=defaultdict(list)
 for i in task_indices:bucket[int(task_bin[i]),int(task_width[i])].append(int(i))
 db=Counter();dg=Counter()
 for (b,w),items in bucket.items():db[b]+=len(items);dg[int(bin_group[b])]+=len(items)
 assert sum(db.values())==408*S and max(db.values())<=S
 copies={};stats=Counter()
 for copy in range(S):
  R=S-copy
  if R==1:
   assert all(n<=1 for n in db.values()) and all(n<=group_n[g] for g,n in dg.items())
   for ids in bucket.values():
    for i in ids:copies[i]=copy
   assert len(copies)==408*S
   break
  gs=sorted(g for g,n in dg.items() if n);bs=sorted(b for b,n in db.items() if n)
  gn={g:1+j for j,g in enumerate(gs)};bn={b:1+len(gs)+j for j,b in enumerate(bs)}
  wn={w:1+len(gs)+len(bs)+j for j,w in enumerate(W)};ss=1+len(gs)+len(bs)+len(W);tt=ss+1
  net=Network(tt+1);bal=[0]*(tt+1);bal[0]=408
  for w,n in zip(W,INV):bal[wn[w]]=-n
  def edge(u,v,lo,hi):
   assert 0<=lo<=hi
   bal[u]-=lo;bal[v]+=lo;return net.add(u,v,hi-lo)
  for g in gs:edge(0,gn[g],max(0,dg[g]-(R-1)*group_n[g]),group_n[g])
  for b in bs:edge(gn[int(bin_group[b])],bn[b],int(db[b]==R),1)
  handles={}
  for (b,w),ids in bucket.items():
   if ids:handles[b,w]=net.add(bn[b],wn[w],len(ids))
  target=0
  for n,b in enumerate(bal[:ss]):
   if b>0:net.add(ss,n,b);target+=b
   elif b<0:net.add(n,tt,-b)
  got=net.maxflow(ss,tt,target)
  assert got==target,('copy circulation',copy,got,target,dict(dg),dict(db))
  selected=[];wc=Counter();gc=Counter();bc=set()
  for key,e in handles.items():
   n=net.cap[e^1]
   assert n in (0,1)
   if n:
    b,w=key;i=bucket[key].pop();selected.append(i);wc[w]+=1;g=int(bin_group[b]);gc[g]+=1
    assert b not in bc;bc.add(b);db[b]-=1;dg[g]-=1;copies[i]=copy
  assert len(selected)==408 and wc==Counter(dict(zip(W,INV)))
  assert all(n<=group_n[g] for g,n in gc.items())
  assert max(db.values(),default=0)<=R-1 and all(n<=(R-1)*group_n[g] for g,n in dg.items())
  stats['flows']+=1;stats['max_nodes']=max(stats['max_nodes'],tt+1);stats['max_edges']=max(stats['max_edges'],len(net.to)//2)
 return copies,stats
