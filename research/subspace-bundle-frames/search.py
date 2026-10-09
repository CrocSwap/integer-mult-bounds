#!/usr/bin/env python3
"""Local ascent and descent of actual operation frames, with fixed word/aliases.
Discovery objective uses floats; the final profile requires exact verification.
"""
from pathlib import Path
from collections import Counter,defaultdict,deque
import argparse,gzip,json,sys,math,time
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
from paired_cube.frames import basis,perp,contained
from functools import lru_cache
_perp=perp
@lru_cache(maxsize=100000)
def cached_perp(rows,h):return _perp(rows,h)
def perp(rows,h):return cached_perp(tuple(rows),h)
CAND=None
def load(n):return json.loads(gzip.decompress((CAND/(n+'.json.gz')).read_bytes()))

def main():
 global CAND
 ap=argparse.ArgumentParser(description=__doc__)
 ap.add_argument('--candidate',type=Path,default=Path(__file__).resolve().parent/'candidate')
 ap.add_argument('--output',type=Path,required=True)
 args=ap.parse_args();CAND=args.candidate.resolve()
 if sys.flags.optimize:raise ValueError('Assertions must be enabled')
 args.output.parent.mkdir(parents=True,exist_ok=True)
 g,w,fw,changes,pairs,row,profile=[load(n) for n in ['graph','word','frames','physical-frames','physical-pairs','profile-before','profile']]
 h=g['h'];R=row['R'];full=basis(1<<i for i in range(h));spans=[]
 for n,ab in enumerate(g['args']):spans.append((g['inputs'][n],) if ab is None else basis(spans[ab[0]]+spans[ab[1]]))
 original=[perp(fw['annihilators'][n],h) for a,b,n in w['ops']];F=original[:]
 for i,U in changes:F[i]=tuple(U)
 initial=F[:]
 aliases={b:a for a,b,t in pairs};donors={a:b for a,b,t in pairs}
 starts=[()]*R;roleops=defaultdict(list)
 for n,s in w['sources'].items():starts[s]=(g['inputs'][int(n)-1],)
 for z in w['selected']:starts[z['role']]=perp(z['annihilator'],h)
 for i,(a,b,n) in enumerate(w['ops']):roleops[a].append(i);roleops[b].append(i)
 roots={s:(spans[r['node']] if r['kind']=='center' else perp((g['inputs'][t] for t in r['targets']),h)) for r,s in zip(g['roots'],w['rootroles'])}
 kinds={s:r['kind'] for r,s in zip(g['roots'],w['rootroles'])}
 def chain(s):return [starts[s]]+roleops[s]+([roots[s]] if s in roots else [])+[full]
 chains=[];neighbors=defaultdict(list)
 for s in range(R):
  if s in aliases:continue
  seq=chain(s)
  if s in donors:seq=seq[:-1]+chain(donors[s])
  chains.append(seq)
  for k,i in enumerate(seq):
   if isinstance(i,int):neighbors[i].append((seq[k-1],seq[k+1]))
 def frame(x):return F[x] if isinstance(x,int) else x
 def recount():
  H=Counter()
  for seq in chains:
   for a,b in zip(seq,seq[1:]):
    A,B=frame(a),frame(b);assert contained(A,B)
    if len(B)>len(A):H[len(B)-len(A)]+=1
  H[1]+=len(w['sources'])
  for s,kind in kinds.items():
   if kind=='center':H[len(roots[s])]+=1
  return H
 before=recount();assert {str(k):v for k,v in before.items() if v}==profile['local_histogram']
 a=0.000662323931899052
 cost=[0.]+[t*math.expm1(-a*math.log(t)) for t in range(1,h+1)]
 def score(i,U):
  return sum(cost[len(U)-len(frame(p))]+cost[len(frame(q))-len(U)] for p,q in neighbors[i])
 history=[];start=time.monotonic()
 for sweep in range(6):
  count=0;gain=0.
  order=range(len(F)) if sweep%2==0 else reversed(range(len(F)))
  for i in order:
   assert len(neighbors[i])==2
   low=basis(spans[w['ops'][i][2]-1]+tuple(x for p,q in neighbors[i] for x in frame(p)))
   high=perp(basis(x for p,q in neighbors[i] for x in perp(frame(q),h)),h)
   assert contained(low,F[i]) and contained(F[i],high)
   best=F[i];oldscore=score(i,best);newscore=oldscore
   for U in (low,high):
    z=score(i,U)
    if z<newscore-1e-13:best,newscore=U,z
   if best!=F[i]:F[i]=best;count+=1;gain+=oldscore-newscore
  history.append(dict(sweep=sweep,changes=count,cost_gain=gain))
  print(history[-1],flush=True)
  if count==0:break
 # Equal-frame plateaus can trap single-operation descent/ascent. Move an
 # entire connected plateau together, charging every external boundary.
 for sweep in range(4):
  parent=list(range(len(F)))
  def find(i):
   while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
   return i
  for i in range(len(F)):
   for p,q in neighbors[i]:
    for j in (p,q):
     if isinstance(j,int) and F[i]==F[j]:parent[find(i)]=find(j)
  groups=defaultdict(list)
  for i in range(len(F)):groups[find(i)].append(i)
  count=0;gain=0.;moved=0
  for group in sorted(groups.values(),key=lambda x:(-len(x),x[0])):
   if len(group)<2:continue
   ids=set(group)
   if any(F[i]!=F[group[0]] for i in group):continue
   prev=[p for i in group for p,q in neighbors[i] if not isinstance(p,int) or p not in ids]
   nxt=[q for i in group for p,q in neighbors[i] if not isinstance(q,int) or q not in ids]
   low=basis(tuple(x for i in group for x in spans[w['ops'][i][2]-1])+tuple(x for p in prev for x in frame(p)))
   high=perp(basis(x for q in nxt for x in perp(frame(q),h)),h)
   U=F[group[0]];assert contained(low,U) and contained(U,high)
   def blockscore(U):return sum(cost[len(U)-len(frame(p))] for p in prev)+sum(cost[len(frame(q))-len(U)] for q in nxt)
   oldscore=blockscore(U);best=U;newscore=oldscore
   for candidate in (low,high):
    z=blockscore(candidate)
    if z<newscore-1e-13:best,newscore=candidate,z
   if best!=U:
    for i in group:F[i]=best
    count+=1;moved+=len(group);gain+=oldscore-newscore
  history.append(dict(plateau_sweep=sweep,blocks=count,changes=moved,cost_gain=gain));print(history[-1],flush=True)
  if count==0:break
 # Global expansion by a coordinate direction is a minimum-weight closure:
 # if the predecessor acquires a direction absent from the successor, the
 # successor must acquire it too. The remaining edge costs are unary.
 def closure(weights,arcs):
  n=len(weights);src=n;dst=n+1;graph=[[] for _ in range(n+2)]
  def edge(u,v,c):graph[u].append([v,c,len(graph[v])]);graph[v].append([u,0,len(graph[u])-1])
  ints=[round(x*10**12) for x in weights];infty=sum(map(abs,ints))+1
  for u,wgt in enumerate(ints):
   if wgt<0:edge(src,u,-wgt)
   elif wgt>0:edge(u,dst,wgt)
  for u,v in arcs:
   if v is None:edge(u,dst,infty)
   else:edge(u,v,infty)
  while True:
   dist=[-1]*(n+2);dist[src]=0;q=deque([src])
   while q:
    u=q.popleft()
    for v,c,r in graph[u]:
     if c and dist[v]<0:dist[v]=dist[u]+1;q.append(v)
   if dist[dst]<0:break
   cursor=[0]*(n+2)
   def dfs(u,flow):
    if u==dst:return flow
    while cursor[u]<len(graph[u]):
     e=graph[u][cursor[u]];v,c,r=e
     if c and dist[v]==dist[u]+1:
      f=dfs(v,min(flow,c))
      if f:e[1]-=f;graph[v][r][1]+=f;return f
     cursor[u]+=1
    return 0
   while dfs(src,infty):pass
  seen={src};q=deque([src])
  while q:
   for v,c,r in graph[q.popleft()]:
    if c and v not in seen:seen.add(v);q.append(v)
  return seen-{src,dst}
 sys.setrecursionlimit(100000)
 from itertools import combinations
 # Add a fixed subspace V to each chosen frame. The number of added
 # dimensions may differ across frames, but the implication remains valid.
 catalogue=[basis((1<<i,1<<j)) for i,j in combinations(range(h),2)]
 frequency=Counter(perp(U,h) for U in F if 2<=h-len(U)<=3)
 catalogue += [U for U,n in sorted(frequency.items(),key=lambda item:(-item[1],item[0]))[:96]]
 catalogue=list(dict.fromkeys(catalogue))
 print('bundle catalogue',len(catalogue),flush=True)
 def checkpoint():
  current=recount()
  result=dict(scope='Discovery checkpoint; exact physical verification pending',history=history,
   changed_from_baseline=sum(A!=B for A,B in zip(initial,F)),before=dict(before),after=dict(current),
   physical_frames=[[i,list(U)] for i,U in enumerate(F) if U!=original[i]],seconds=time.monotonic()-start)
  args.output.with_suffix('.progress.json').write_text(json.dumps(result)+'\n')
 checkpoint()
 for dual in (True,False):
  for number,V in enumerate(catalogue):
   view=[perp(U,h) for U in F] if dual else F
   fixed={};allframes=list(view);edges=[]
   def node(x):
    if isinstance(x,int):return x
    U=perp(x,h) if dual else x
    if U not in fixed:fixed[U]=len(allframes);allframes.append(U)
    return fixed[U]
   for seq0 in chains:
    seq=list(reversed(seq0)) if dual else seq0
    edges.extend((node(p),node(q)) for p,q in zip(seq,seq[1:]))
   increments={}
   for U in set(allframes):
    residuals=[]
    for v in V:
     for u in U:v=min(v,v^u)
     residuals.append(v)
    increments[U]=len(basis(residuals))
   t=[increments[U] for U in allframes]
   weights=[0.]*len(F);arcs=[]
   if dual:
    forbidden={S:any((u&v).bit_count()%2 for u in S for v in V) for S in set(spans)}
    arcs.extend((i,None) for i in range(len(F)) if t[i] and forbidden[spans[w['ops'][i][2]-1]])
   for p,q in edges:
    d=len(allframes[q])-len(allframes[p]);tp=t[p];tq=t[q]
    assert tp>=tq
    pv=p<len(F) and tp>0;qv=q<len(F) and tq>0
    if tp and tq:
     if qv:weights[q]+=cost[d+tq]-cost[d]
     if pv:weights[p]+=cost[d+tq-tp]-cost[d+tq];arcs.append((p,q if qv else None))
    elif tp and pv:weights[p]+=cost[d-tp]-cost[d]
   selected={i for i in closure(weights,arcs) if t[i]}
   gain=-sum(weights[i] for i in selected)
   if gain>1e-10:
    before_move=recount();old_cost=sum(cost[k]*v for k,v in before_move.items())
    for i in selected:
     expanded=basis(view[i]+V)
     assert len(expanded)-len(view[i])==t[i]
     F[i]=perp(expanded,h) if dual else expanded
     assert contained(spans[w['ops'][i][2]-1],F[i])
    after_move=recount();new_cost=sum(cost[k]*v for k,v in after_move.items())
    assert abs(old_cost-new_cost-gain)<1e-8 and new_cost<old_cost
    move=dict(dual=dual,bundle=list(V),changes=len(selected),cost_gain=gain)
    history.append(move);print(move,flush=True);checkpoint()
   if number%25==0:print('progress',dual,number,len(catalogue),round(time.monotonic()-start,2),flush=True)
 print('Final local/group polish',flush=True)
 for sweep in range(6):
  count=0;gain=0.
  order=range(len(F)) if sweep%2==0 else reversed(range(len(F)))
  for i in order:
   assert len(neighbors[i])==2
   low=basis(spans[w['ops'][i][2]-1]+tuple(x for p,q in neighbors[i] for x in frame(p)))
   high=perp(basis(x for p,q in neighbors[i] for x in perp(frame(q),h)),h)
   assert contained(low,F[i]) and contained(F[i],high)
   best=F[i];oldscore=score(i,best);newscore=oldscore
   for U in (low,high):
    z=score(i,U)
    if z<newscore-1e-13:best,newscore=U,z
   if best!=F[i]:F[i]=best;count+=1;gain+=oldscore-newscore
  history.append(dict(sweep=sweep,changes=count,cost_gain=gain))
  print(history[-1],flush=True)
  if count==0:break
 # Equal-frame plateaus can trap single-operation descent/ascent. Move an
 # entire connected plateau together, charging every external boundary.
 for sweep in range(4):
  parent=list(range(len(F)))
  def find(i):
   while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
   return i
  for i in range(len(F)):
   for p,q in neighbors[i]:
    for j in (p,q):
     if isinstance(j,int) and F[i]==F[j]:parent[find(i)]=find(j)
  groups=defaultdict(list)
  for i in range(len(F)):groups[find(i)].append(i)
  count=0;gain=0.;moved=0
  for group in sorted(groups.values(),key=lambda x:(-len(x),x[0])):
   if len(group)<2:continue
   ids=set(group)
   if any(F[i]!=F[group[0]] for i in group):continue
   prev=[p for i in group for p,q in neighbors[i] if not isinstance(p,int) or p not in ids]
   nxt=[q for i in group for p,q in neighbors[i] if not isinstance(q,int) or q not in ids]
   low=basis(tuple(x for i in group for x in spans[w['ops'][i][2]-1])+tuple(x for p in prev for x in frame(p)))
   high=perp(basis(x for q in nxt for x in perp(frame(q),h)),h)
   U=F[group[0]];assert contained(low,U) and contained(U,high)
   def blockscore(U):return sum(cost[len(U)-len(frame(p))] for p in prev)+sum(cost[len(frame(q))-len(U)] for q in nxt)
   oldscore=blockscore(U);best=U;newscore=oldscore
   for candidate in (low,high):
    z=blockscore(candidate)
    if z<newscore-1e-13:best,newscore=candidate,z
   if best!=U:
    for i in group:F[i]=best
    count+=1;moved+=len(group);gain+=oldscore-newscore
  history.append(dict(plateau_sweep=sweep,blocks=count,changes=moved,cost_gain=gain));print(history[-1],flush=True)
  if count==0:break
 after=recount();assert sum(k*v for k,v in after.items())==sum(k*v for k,v in before.items())
 output=dict(scope='Discovery, same exact word and alias schedule; full physical replay pending',history=history,
  changed_from_baseline=sum(A!=B for A,B in zip(initial,F)),before=dict(before),after=dict(after),
  physical_frames=[[i,list(U)] for i,U in enumerate(F) if U!=original[i]],seconds=time.monotonic()-start)
 args.output.write_text(json.dumps(output)+'\n')
 print('changed',output['changed_from_baseline'],'seconds',output['seconds'],flush=True)

if __name__=='__main__':main()
