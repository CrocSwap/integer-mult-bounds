import sys,os
if sys.flags.optimize or os.environ.get("PYTHONOPTIMIZE"):
 raise RuntimeError("Optimized Python is not permitted for scientific checks")
"""Original PR97 mathematical reconstruction; no imported upstream code.
Adapted from our prior original paired-incidence model; credited source is Swapnil Jain NStar3 as pinned in FRONTIER_REBASE.md.
"""
from itertools import combinations,chain
from collections import defaultdict,Counter,deque
from pathlib import Path
import json,time,resource,math
ROOT=Path(__file__).resolve().parent
class DAG:
 def __init__(self,h):
  self._top=True;self.h=h;self.triples=list(combinations(range(h),3));self.v=len(self.triples)
  self.a=[None]*(self.v+1);self.s=[0]+[1<<i for i in range(self.v)]
  self.c=[0]+[sum(1<<j for j in t) for t in self.triples];self.u=self.c[:]
  self.r=[0]+[1]*self.v;self.ty=[0]+[1]*self.v;self.memo={s:i for i,s in enumerate(self.s)}
  self.variables={t:i+1 for i,t in enumerate(self.triples)}
 def plus(self,x,y,center=None):
  if not x:return y
  if not y:return x
  s=self.s[x]|self.s[y]
  if center is None:
   assert not self.s[x]&self.s[y]
   if s in self.memo:return self.memo[s]
  z=len(self.a);self.a.append((x,y));self.s.append(s);c=self.c[x]&self.c[y];u=self.u[x]|self.u[y]
  if center is not None:ty=3;c=1<<center;r=self.h-1
  elif c.bit_count()>=2:ty=1;r=s.bit_count()
  else:ty=2;r=u.bit_count()
  self.c.append(c);self.u.append(u);self.r.append(r);self.ty.append(ty)
  if center is None:self.memo[s]=z
  return z
 def tree(self,values):
  values=list(values)
  if not values:return 0
  if len(values)==1:return values[0]
  m=len(values)//2
  return self.plus(self.tree(values[:m]),self.tree(values[m:]))
 def leave_one(self,values):
  p=[0]
  for x in values:p.append(self.plus(p[-1],x))
  s=[0]*(len(values)+1)
  for j in range(len(values)-1,-1,-1):s[j]=self.plus(values[j],s[j+1])
  return p[-1],[self.plus(p[j],s[j+1]) for j in range(len(values))]
 def edges_avoid(self,pts,edges,weights):
  if len(pts)==3:
   a,b,c=pts
   e=lambda x,y:edges[tuple(sorted((x,y)))]
   u=self.plus(e(b,c),weights[b]);v=self.plus(e(a,c),weights[c]);w=self.plus(e(a,b),weights[a])
   one={a:self.plus(u,weights[c]),b:self.plus(v,weights[a]),c:self.plus(w,weights[b])}
   total=self.plus(one[a],self.plus(w,e(a,c)))
   return total,one,{(a,b):weights[c],(a,c):weights[b],(b,c):weights[a]}
  if len(pts)<=4:
   def left(e):return self.tree([w for p,w in edges.items() if not set(p)&set(e)]+[w for p,w in weights.items() if p not in e])
   return left(()),{x:left((x,)) for x in pts},{p:left(p) for p in combinations(pts,2)}
  groups=[pts[j:j+2] for j in range(0,len(pts),2)];ids=list(range(len(groups)))
  def edge(a,b):return edges[tuple(sorted((a,b)))]
  coarse={(i,j):self.tree(edge(a,b) for a in groups[i] for b in groups[j]) for i,j in combinations(ids,2)}
  inner={i:self.tree([weights[x] for x in g]+[edge(a,b) for a,b in combinations(g,2)]) for i,g in enumerate(groups)}
  total,one,two=self.edges_avoid(ids,coarse,inner)
  strip={};whole={}
  for i,g in enumerate(groups):
   others=[j for j in ids if j!=i]
   for a in g:
    carry=self.tree(weights[x] for x in g if x!=a)
    entries=[self.tree(edge(x,y) for x in g if x!=a for y in groups[j]) for j in others]
    top,avoiding=self.leave_one([carry]+entries);whole[a]=top;strip[a]=dict(zip(others,avoiding[1:]))
  out={p:one[i] for i,g in enumerate(groups) for p in combinations(g,2)}
  single={a:self.plus(one[i],whole[a]) for i,g in enumerate(groups) for a in g}
  for i,j in combinations(ids,2):
   for a in groups[i]:
    partial=self.plus(two[i,j],strip[a][j])
    for b in groups[j]:
     cross=self.tree(edge(x,y) for x in groups[i] if x!=a for y in groups[j] if y!=b)
     out[a,b]=self.plus(partial,self.plus(strip[b][i],cross))
  return total,single,out
 def triples_avoid(self,pts,weights):
  top=self._top;self._top=False
  excluded=list(chain.from_iterable(combinations(pts,k) for k in range(4)))
  if len(pts)<=4:
   return {e:self.tree(w for p,w in weights.items() if not set(p)&set(e)) for e in excluded}
  blocks=[pts[j:j+2] for j in range(0,len(pts),2)];ids=list(range(len(blocks)))
  owner={x:i for i,g in enumerate(blocks) for x in g}
  bag=defaultdict(list)
  for p,w in weights.items():bag[tuple(sorted({owner[x] for x in p}))].append(w)
  coarse={p:self.tree(ws) for p,ws in bag.items() if not(top and len(p)==2)}
  if top:
   for i,j in (p for p in bag if len(p)==2):
    a,b=blocks[i];c,d=blocks[j]
    x=lambda *t:self.variables[tuple(sorted(t))]
    coarse[i,j]=self.plus(self.plus(x(a,c,b),x(a,c,d)),self.plus(x(b,d,a),x(b,d,c)))
  outside=self.triples_avoid(ids,coarse)
  one={}
  for x in pts:
   i=owner[x];others=[j for j in ids if j!=i];bag=defaultdict(list)
   for p,w in weights.items():
    if x not in p:continue
    rest=[a for a in p if a!=x]
    if any(owner[a]==i for a in rest):continue
    bag[tuple(sorted({owner[a] for a in rest}))].append(w)
   coeff={p:self.tree(ws) for p,ws in bag.items()}
   edge={p:coeff.get(p,0) for p in combinations(others,2)};vertex={j:coeff.get((j,),0) for j in others}
   total,single,double=self.edges_avoid(others,edge,vertex)
   constant=coeff.get((),0)
   one[x]={():self.plus(constant,total),**{(j,):self.plus(constant,w) for j,w in single.items()},**{p:self.plus(constant,w) for p,w in double.items()}}
  two={}
  for x,y in combinations(pts,2):
   i,j=owner[x],owner[y]
   if i==j:continue
   others=[k for k in ids if k not in (i,j)]
   entries=[self.tree(weights.get(tuple(sorted((x,y,z))),0) for z in blocks[k]) for k in others]
   total,leave=self.leave_one([weights.get((x,y),0)]+entries)
   two[x,y]={():total,**{(k,):w for k,w in zip(others,leave[1:])}}
  result={}
  for e in excluded:
   omit=set(e);groups=tuple(sorted({owner[x] for x in e}));survivors=[x for i in groups for x in blocks[i] if x not in omit]
   pieces={():outside[groups]}
   for x in survivors:pieces[x,]=one[x][tuple(i for i in groups if i!=owner[x])]
   for x,y in combinations(survivors,2):pieces[x,y]=two[x,y][tuple(i for i in groups if i not in (owner[x],owner[y]))]
   if len(survivors)==3:
    a,b,c=survivors;pieces[tuple(survivors)]=weights.get(tuple(survivors),0)
    order=[(),(a,),(b,),(a,b),(c,),(a,c),(b,c),(a,b,c)]
   else:order=list(chain.from_iterable(combinations(survivors,k) for k in range(len(survivors)+1)))
   result[e]=self.tree(pieces[p] for p in order)
  return result
 def active(self,roots):
  alive=set(roots);todo=list(roots)
  while todo:
   x=todo.pop()
   if self.a[x]:
    for y in self.a[x]:
     if y not in alive:alive.add(y);todo.append(y)
  alive.discard(0);return alive
 def trim(self,roots):
  alive=self.active(roots);mapping={0:0};out=DAG(self.h)
  for x in range(1,self.v+1):mapping[x]=x
  for x in sorted(alive):
   if self.a[x]:mapping[x]=out.plus(*(mapping[y] for y in self.a[x]))
  return out,[mapping[x] for x in roots]

def reconstruct():
 h=24;g=DAG(h);res=g.triples_avoid(list(range(h)),g.variables);pieces=[];centers=[res[(i,)]for i in range(h-1)]+[res[()]];whole=(1<<h)-1
 def emit(t,x,sign):
  if not x:return
  mask=sum(1<<i for i in t)
  if g.u[x]|mask==whole:
   a,b=g.a[x];emit(t,a,sign);emit(t,b,sign)
  else:pieces.append((t,x,sign))
 for t in g.triples:emit(t,res[t],1)
 vec_cache={}
 def leaf(a,b,c):return g.variables[tuple(sorted((a,b,c))) ]
 def pairvec(a,b):
  k=tuple(sorted((a,b)))
  if k not in vec_cache:
   groups=[j for j in range(h//2)if j not in(a//2,b//2)]
   vals=[g.tree(leaf(a,b,c)for c in(2*j,2*j+1))for j in groups]
   total,leave=g.leave_one(vals);vec_cache[k]={():total,**{(j,):x for j,x in zip(groups,leave)}}
  return vec_cache[k]
 for a,b in combinations(range(h),2):
  vv=pairvec(a,b)
  if a//2==b//2:
   for c in range(h):
    if c//2!=a//2:
     t=tuple(sorted((a,b,c)));emit(t,leaf(a,b,c^1),-1);emit(t,vv[(c//2,)],-1)
  else:
   aa,bb=a^1,b^1;p=g.plus(leaf(a,b,aa),leaf(a,b,bb))
   for c in range(h):
    if c in(a,b):continue
    t=tuple(sorted((a,b,c)))
    if c==aa:emit(t,leaf(a,b,bb),-1);emit(t,vv[()],-1)
    elif c==bb:emit(t,leaf(a,b,aa),-1);emit(t,vv[()],-1)
    else:emit(t,leaf(a,b,c^1),-1);emit(t,g.plus(vv[(c//2,)],p),-1)
 roots=[x for t,x,sg in pieces]+centers;alive=g.active(roots)
 # Independent exact support audit of every positive and negative target response.
 point=[sum(1<<j for j,t in enumerate(g.triples)if i in t)for i in range(h)];universe=(1<<g.v)-1;pos=defaultdict(int);neg=defaultdict(int)
 for t,x,sg in pieces:
  dest=pos if sg>0 else neg;assert not dest[t]&g.s[x];dest[t]|=g.s[x]
 for t in g.triples:
  a,b,c=t;assert pos[t]==universe&~(point[a]|point[b]|point[c])
  two=(point[a]&point[b]&~point[c])|(point[a]&point[c]&~point[b])|(point[b]&point[c]&~point[a]);assert neg[t]==two
 for i,x in enumerate(centers[:-1]):assert g.s[x]==universe&~point[i]
 assert g.s[centers[-1]]==universe
 # Both center formulas have coefficient intersection−1 before division by2.
 for overlap in range(4):assert (overlap-1)+(overlap==0)-(overlap==2)==2*(overlap==3)
 uses=Counter(x for x in roots)
 for x in alive:
  for y in g.a[x]or():uses[y]+=1
 H=Counter();c=0
 for x in sorted(alive):
  r=g.r[x]
  if g.a[x]:
   c+=1;H[r]+=uses[x]-1;H[h-r]+=1
   for y in g.a[x]:H[r-g.r[y]]+=1
  else:H[1]+=uses[x]
 for j,x in enumerate(roots):
  r=g.r[x]
  if j<len(pieces):H[h-1-r]+=1;H[1]+=1
  else:H[r]+=1;H[h-r]+=1
 R=c+len(roots);assert R==49208;assert sum(r*n for r,n in H.items())==h*R+553
 return g,roots,alive,pieces,centers,H,dict(c=c,q=len(roots),R=R,pieces=len(pieces),centers=len(centers),histogram=dict(sorted(H.items())))

if __name__=='__main__':
 st=time.monotonic();g,roots,alive,pieces,centers,H,stats=reconstruct()
 src=ROOT.parents[2]/'pr_watch_2240/sources/research/deferred-signed/round6-complex-literal-ledger/result.json'
 # ROOT is this script's directory.
 src=ROOT.parent.parent/'pr_watch_2240/sources/research/deferred-signed/round6-complex-literal-ledger/result.json'
 x=json.loads(src.read_text());expected=Counter({int(r):n for r,n in x['internal_histograms']['aux'].items()})+Counter({int(r):n for r,n in x['internal_histograms']['center'].items()})
 assert {r:n for r,n in H.items()if r}==dict(expected),({r:n for r,n in H.items()if r},dict(expected))
 stats.update(all_side_and_center_supports=True,complete_positive_histogram_matches97=True,seconds=time.monotonic()-st,rss_KiB=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
 (ROOT/'BASELINE_RECONSTRUCTION.json').write_text(json.dumps(stats,indent=2)+'\n');print(json.dumps(stats,indent=2))
