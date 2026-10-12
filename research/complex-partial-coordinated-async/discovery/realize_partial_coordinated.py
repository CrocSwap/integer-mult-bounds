"""Realize an async allocation nomination with literal whole owners.
Each pattern is colored independently; call colors enforce distinct families.
"""
from pathlib import Path
from collections import Counter,defaultdict,deque
import json,gzip,sys,hashlib,time
import numpy as np
from scipy.optimize import milp,Bounds,LinearConstraint
from scipy.sparse import lil_matrix
R=Path(__file__).resolve().parent;N=Path(sys.argv[1]);O=Path(sys.argv[2]);O.mkdir(exist_ok=False);n=json.loads(N.read_text());D=json.load(open(R/'partial-coordinated-screen/PLAN-SEED.json'));win={tuple(map(int,k.split(','))):v for k,v in n['windows'].items()};widths=D['baseline_widths'];xs=defaultdict(list);quota=defaultdict(Counter)
for k,i,a,count in n['selection']:
 i=tuple(i)
 if k=='x':xs[i].append((tuple(a),count))
 elif k=='y':t,w=a;quota[i][t,w]+=count
 else:raise AssertionError(k)
roles=[];ledger=[];remainders=[]
for group,patterns in sorted(xs.items()):
 rep,child=group;assert sum(count for p,count in patterns)==120;qs=quota[group];vars=[(pi,t,w)for pi,(pat,count)in enumerate(patterns)for (t,w),v in qs.items()if w in pat];rows=[('slots',pi,w)for pi,(pat,count)in enumerate(patterns)for w in set(pat)]+[('quota',t,w)for t,w in qs]+[('distinct',pi,t)for pi,(pat,count)in enumerate(patterns)for t in sorted({t for t,w in qs})];ri={v:j for j,v in enumerate(rows)};A=lil_matrix((len(rows),len(vars)),dtype=float)
 for j,(pi,t,w)in enumerate(vars):A[ri['slots',pi,w],j]=1;A[ri['quota',t,w],j]=1;A[ri['distinct',pi,t],j]=1
 rhs=np.array([patterns[row[1]][1]*patterns[row[1]][0].count(row[2])if row[0]=='slots'else qs[row[1],row[2]]if row[0]=='quota'else patterns[row[1]][1]for row in rows]);lo=rhs.astype(float)
 for j,row in enumerate(rows):
  if row[0]=='distinct':lo[j]=-np.inf
 start=time.monotonic()
 if vars:
  A=A.tocsr();res=milp(np.zeros(len(vars)),integrality=np.ones(len(vars)),bounds=Bounds(0,np.inf),constraints=LinearConstraint(A,lo,rhs),options={'time_limit':15});assert res.x is not None,(group,res.message);x=np.rint(res.x).astype(int);assert np.all(A@x<=rhs)and np.all(A@x>=lo)
 else:x=[]
 alloc=defaultdict(Counter)
 for val,(pi,t,w)in zip(x,vars):
  if val:alloc[pi][t,w]+=int(val)
 portstart=0
 for pi,(pat,count)in enumerate(patterns):
  edges=[];colors=[];at=defaultdict(dict);slotleft={w:deque(s for s,v in enumerate(pat)if v==w for _ in range(count))for w in set(pat)};metadata=[]
  for (t,w),val in sorted(alloc[pi].items()):
   for _ in range(val):
    slot=slotleft[w].popleft();u=('slot',slot);v=('call',t);a=next(c for c in range(count)if c not in at[u]);b=next(c for c in range(count)if c not in at[v])
    if a!=b:
     path=[];node=u;color=b
     while color in at[node]:
      e=at[node][color];path.append(e);l,r=edges[e];node=r if node==l else l;color=a if color==b else b
     assert node!=v
     for e in path:
      l,r=edges[e];old=colors[e];del at[l][old];del at[r][old]
     for e in path:
      l,r=edges[e];colors[e]=a if colors[e]==b else b;assert colors[e]not in at[l]and colors[e]not in at[r];at[l][colors[e]]=at[r][colors[e]]=e
    e=len(edges);edges.append((u,v));colors.append(b);assert b not in at[u]and b not in at[v];at[u][b]=at[v][b]=e;metadata.append((slot,t,w))
  assert all(not v for v in slotleft.values())
  for (slot,t,w),color in zip(metadata,colors):
   port=portstart+color;stage,invrep=n['order'][t];family=rep*960+(2*int(D['pairs'][str(child)])+int(D['sides'][str(child)]))*120+port
   roles.append(dict(owner_replica=rep,child=child,port=port,time=t,width=w,offset=sum(pat[:slot]),stage=stage,replica=invrep,copy=rep*120+port,family=family))
  for port in range(portstart,portstart+count):
   left=win[group][0]-sum(pat)
   if left:remainders.append(dict(owner_replica=rep,child=child,port=port,rank=left))
  portstart+=count
 ledger.append(dict(group=group,patterns=len(patterns),variables=len(vars),seconds=time.monotonic()-start));print('MATCHED',group,flush=True)
bycall=defaultdict(list)
for z in roles:bycall[z['time']].append(z)
for t,zs in bycall.items():
 helpers={w:deque(h for h,v in enumerate(widths)if v==w)for w in set(widths)}
 for z in sorted(zs,key=lambda z:(z['family'],z['offset'])):z['helper']=helpers[z['width']].popleft()
 assert all(not h for h in helpers.values())and len(zs)==560 and len({z['family']for z in zs})==560
assert len(roles)==40320
D.update(order=n['order'],windows=n['windows'],profile=n['profile'],patterns=[[i,a,count]for k,i,a,count in n['selection']if k=='x'],stage_assignments=[[i,a[1],a[0],count]for k,i,a,count in n['selection']if k=='y'],status='EXPLICIT_NEW_ASYNC_WHOLE_OWNER_NOMINATION',mode=n['label'],numeric_saving=n['float_root'],solver_status=n['status'],gap=n['gap'])
(O/'PLAN.json').write_text(json.dumps(D,indent=2)+'\n');raw=json.dumps(sorted(roles,key=lambda z:(z['time'],z['helper'])),sort_keys=True,separators=(',',':')).encode();(O/'OWNERS.json.gz').write_bytes(gzip.compress(raw,mtime=0));(O/'MATCHING.json').write_text(json.dumps(dict(status='PASS_LITERAL_WHOLE_OWNER_MATCHING',roles=len(roles),groups=ledger,owners_json_sha256=hashlib.sha256(raw).hexdigest(),scope='Literal matching only; controller, chart, invoice and exact assembly checks remain required.'),indent=2)+'\n')
