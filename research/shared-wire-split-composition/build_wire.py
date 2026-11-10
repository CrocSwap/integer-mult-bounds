import json,gzip,collections,copy,heapq,pathlib
from fractions import Fraction as Q
from compose import access
HERE=pathlib.Path(__file__).resolve().parent
ROOT=HERE/'build'

def build(w,p):
 n=w['public'];hp=n;ef=p['F'];er=p['R'];q=Q(ef['q']);y,x,u,v=ef['dest'],ef['src'],er['dest'],er['src'];a,c,b,d=p['frames']
 def shift(e):
  e=e.copy();e[1]+=e[1]>=n
  if e[0]in('ADD','COPY'):e[2]+=e[2]>=n
  return e
 removed={ef['index'],er['index'],*ef['moves'],*er['moves']}
 ev=[];positions=[]
 for i,e in enumerate(w['program']):
  if i not in removed:ev.append(shift(e));positions.append((i,0))
 for f in (ef,er):
  for i,j in zip(f['moves'][::2],f['moves'][1::2]):
   e=w['program'][i];z=w['program'][j];assert e[1]==z[1]
   ev.append(['MOVE',e[1],e[2],z[3],False]);positions.append((i,0))
 new=[['ADD',y,hp,'1',a],['ADD',hp,v,'1',a],['MOVE',hp,a,c,False],['ADD',u,hp,str(-q),c],['ADD',hp,x,str(-q),c],['MOVE',hp,c,b,False],['ADD',hp,v,'-1',b],['ADD',y,hp,'-1',b],['MOVE',hp,b,d,False],['ADD',hp,x,str(q),d],['ADD',u,hp,str(q),d]]
 starts={y:0,v:1,u:3,x:4};ends={v:6,y:7,x:9,u:10};newidx=[]
 for j,e in enumerate(new):
  idx=len(ev);newidx.append(idx);ev.append(e)
  if e[0]=='MOVE':positions.append((0,0));continue
  r=e[2]if e[1]==hp else e[1];slot=p['slots'][r][0 if j in starts.values() else 1];pos,after=slot
  positions.append((pos,1 if after else -1))
 regs=collections.defaultdict(list)
 for i,e in enumerate(ev):
  for r,c_ in access(e):
   if r!=hp:regs[r].append((positions[i],c_,i))
 adj=[set()for _ in ev];indeg=[0]*len(ev)
 def edge(i,j):
  if j not in adj[i]:adj[i].add(j);indeg[j]+=1
 for r,rs in regs.items():
  rs.sort();runs=[]
  for _,c_,i in rs:
   if runs and runs[-1][0]==c_ and c_ in 'AR':runs[-1][1].append(i)
   else:runs.append((c_,[i]))
  for(_,aa),(_,bb)in zip(runs,runs[1:]):
   for i in aa:
    for j in bb:edge(i,j)
 for i,j in zip(newidx,newidx[1:]):edge(i,j)
 ready=[(positions[i],i)for i,d_ in enumerate(indeg)if not d_];heapq.heapify(ready);order=[]
 while ready:
  _,i=heapq.heappop(ready);order.append(i)
  for j in adj[i]:
   indeg[j]-=1
   if not indeg[j]:heapq.heappush(ready,(positions[j],j))
 if len(order)!=len(ev):return None,{'ordered':len(order),'total':len(ev),'blocked':[[i,ev[i]]for i,d_ in enumerate(indeg)if d_][:25]}
 z=copy.deepcopy(w);z['initial'].append(a);z['final'].append(d);z['public']+=1;z['program']=[ev[i]for i in order]
 return z,{'ordered':len(order),'gain_model':p['gain']}
if __name__=='__main__':
 w=json.load(gzip.open(ROOT/'composed.json.gz'));ps=[json.load(open(HERE/'data/extra_wire_spec.json'))]
 for p in ps:p['slots']={int(r):v for r,v in p['slots'].items()}
 for i,p in enumerate(ps):
  if p['gain']<=0:break
  z,r=build(w,p);print('CANDIDATE',i,r)
  if z:
   with gzip.open(ROOT/f'extra_wire_{i}.json.gz','wt')as f:json.dump(z,f,separators=(',',':'))
