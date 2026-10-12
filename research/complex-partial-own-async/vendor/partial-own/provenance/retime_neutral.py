"""OpenAI Codex fixed-gate frame-component retiming search.
All local scalar operations and selected entrance gauges/kernel remain fixed.
"""
exec(open('/private/tmp/complex484-pooling-frontier/retime_word.py').read().split('out=[finish')[0])
import math,time,random
random.seed(484)
alpha=133385415620840915601/10**23
cost=lambda r:r/73*math.expm1(alpha*math.log(73/r))+32*73/10**16*73**alpha if r else 0.
def optimize(word,tag):
 z=copy.deepcopy(word);labels=[];fixed=[];eventnodes={};seq=[[]for _ in range(n)]
 def node(F,pin,rs,key=None):
  i=len(labels);labels.append(basis(F));fixed.append(pin)
  for r in rs:seq[r].append(i)
  if key:eventnodes[key]=i
  return i
 for r,F in enumerate(start):node(F,True,[r])
 for part in ['A','B']:
  if part=='B':
   for r,F in zip(z['centers'],z['center_frames']):node(F,True,[r])
   for t in range(V):node(z.get('target_levels',{}).get(str(t),[]),True,[V+t])
  for j,e in enumerate(z[part]):node(e[-1],False,registers(e),(part,j))
 for r,F in enumerate(final):node(F,True,[r])
 edges=[(a,b,r)for r,ss in enumerate(seq)for a,b in zip(ss,ss[1:])]
 def total():return sum(cost(len(labels[b])-len(labels[a]))for a,b,r in edges)
 startcost=total();moves=[];t0=time.monotonic();tabu=set();bestcost=startcost;bestlabels=labels.copy()
 for iteration in range(500):
  par=list(range(len(labels)))
  def root(i):
   while par[i]!=i:par[i]=par[par[i]];i=par[i]
   return i
  for a,b,r in edges:
   assert span(labels[a])<=span(labels[b])
   if labels[a]==labels[b]:par[root(a)]=root(b)
  comps={};pins={};incoming={};outgoing={}
  for i in range(len(labels)):
   c=root(i);comps.setdefault(c,[]).append(i);pins[c]=pins.get(c,False)or fixed[i]
  for a,b,r in edges:
   ca,cb=root(a),root(b)
   if ca!=cb:outgoing.setdefault(ca,[]).append((a,b,r));incoming.setdefault(cb,[]).append((a,b,r))
  best=None;neutral=[];state=hash(tuple(labels))
  for c,ns in comps.items():
   if pins[c]:continue
   ins=incoming.get(c,[]);outs=outgoing.get(c,[])
   low=basis([v for a,b,r in ins for v in labels[a]]);up=basis(set.intersection(*(span(labels[b])for a,b,r in outs)))
   cf=labels[ns[0]];old=sum(cost(len(cf)-len(labels[a]))for a,b,r in ins)+sum(cost(len(labels[b])-len(cf))for a,b,r in outs)
   for nf in {low,up}:
    if nf==cf:continue
    new=sum(cost(len(nf)-len(labels[a]))for a,b,r in ins)+sum(cost(len(labels[b])-len(nf))for a,b,r in outs);delta=new-old
    if delta<-1e-13 and(best is None or delta<best[0]):best=(delta,c,nf,len(ns),len(cf))
    if abs(delta)<1e-13:
     trial=hash((state,c,nf))
     if trial not in tabu:neutral.append((delta,c,nf,len(ns),len(cf),trial))
  if best is None:
   if not neutral:break
   chosen=random.choice(neutral);tabu.add(chosen[-1]);best=chosen[:-1]
  delta,c,nf,sz,oldrank=best
  for i in comps[c]:labels[i]=nf
  moves.append(dict(delta=delta,events=sz,oldrank=oldrank,newrank=len(nf),nodes=comps[c],frame=list(nf)))
  currentcost=total()
  if currentcost<bestcost-1e-13:bestcost=currentcost;bestlabels=labels.copy();print('NEW BEST',tag,len(moves),bestcost,flush=True)
  if len(moves)%25==0:print(tag,'moves',len(moves),'cost',total(),'sec',time.monotonic()-t0,flush=True)
 labels=bestlabels
 for(part,j),i in eventnodes.items():z[part][j][-1]=list(labels[i])
 print('DONE',tag,len(moves),'cost',startcost,total(),'seconds',time.monotonic()-t0,flush=True)
 result=finish(tag,z);result.update(moves=moves,cost_before=startcost,cost_after=total(),seconds=time.monotonic()-t0)
 (P/(tag+'-moves.json')).write_text(json.dumps(result,indent=2)+'\n')
 return z
if __name__=='__main__':optimize(w,'neutral-walk')
