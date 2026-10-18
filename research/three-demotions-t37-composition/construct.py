#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Rebuild literal owners from the exact pattern-flow certificate."""
import argparse,json,gzip,hashlib
from collections import Counter,defaultdict
from pathlib import Path
HERE=Path(__file__).resolve().parent
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--out',type=Path,required=True)
parser.add_argument('--flow',type=Path,required=True)
parser.add_argument('--plan',type=Path,required=True)
args=parser.parse_args()
if not __debug__:raise ValueError('Construction checks require assertions')
if args.out.exists():raise ValueError('Choose a new construction directory')
D=json.loads(args.flow.read_text())
assert D['T']==37 and sorted(D['order'])==[[s,r] for s in range(9) for r in range(37)]
P=json.loads(gzip.decompress(args.plan.read_bytes()) if args.plan.suffix=='.gz' else args.plan.read_bytes())
widths=P['provider_registry']['gauge44']['widths'];ws=(4,5,7,8,9)
xs={};ys=defaultdict(Counter)
for entry,n in D['entries']:
 assert type(n) is int and n>0
 if entry[0]=='x':_,g,p=entry;xs[g,p]=n
 else:_,g,p,t,w=entry;ys[g,p][t,w]+=n
assign=defaultdict(list);global_count=Counter();idle=Counter();offsets=defaultdict(int)
for gi,(r,cap,ts,children) in enumerate(D['groups']):
 port_index=0
 for pi,pat in enumerate(D['patterns'][str(cap)]):
  N=xs.get((gi,pi),0)
  if not N:continue
  v=ys[gi,pi]
  assert all(t in ts for t,w in v)
  assert Counter({w:sum(n for (t,ww),n in v.items() if w==ww) for w,num in enumerate(pat) if num})==Counter({w:N*num for w,num in enumerate(pat) if num})
  assert all(sum(n for (tt,w),n in v.items() if tt==t)<=N for t in ts)
  slot_width=[w for w,n in enumerate(pat) for _ in range(n)]
  graph=[Counter() for _ in slot_width]
  # Split each width vertex into vertices of degree N.
  for w in set(slot_width):
   slots=[s for s,ww in enumerate(slot_width) if ww==w];j=0;used=0
   for (t,ww),n in sorted(v.items()):
    if ww!=w:continue
    while n:
     count=min(n,N-used);graph[slots[j]][t]+=count;used+=count;n-=count
     if used==N:used=0;j+=1
   assert j==len(slots) and used==0
  assert all(sum(a.values())==N for a in graph)
  for remaining in range(N,0,-1):
   degree=Counter()
   for adj in graph:degree.update(adj)
   assert max(degree.values(),default=0)<=remaining
   required=sorted(t for t,n in degree.items() if n==remaining)
   st={};tt={}
   def match_time(t,seen):
    for s,adj in enumerate(graph):
     if adj[t]==0 or s in seen:continue
     seen.add(s)
     if s not in st or match_time(st[s],seen):
      st[s]=t;tt[t]=s;return True
    return False
   for t in required:assert match_time(t,set())
   def match_slot(s,seen):
    for t,n in sorted(graph[s].items()):
     if not n or t in seen:continue
     seen.add(t)
     if t not in tt or match_slot(tt[t],seen):
      tt[t]=s;st[s]=t;return True
    return False
   for s in range(len(graph)):
    if s not in st:assert match_slot(s,set())
   assert len(st)==len(tt)==len(graph) and all(t in tt for t in required)
   child=children[port_index//112];port=port_index%112;port_index+=1
   offset=0
   for s,t in sorted(st.items(),key=lambda it:(it[1],it[0])):
    w=ws[slot_width[s]];graph[s][t]-=1
    assign[t,w].append((r,child,port,offset))
    offset+=w;global_count[w]+=1
   assert offset<=cap
   idle[cap-offset]+=1
  assert all(not any(adj.values()) for adj in graph)
 assert port_index==112*len(children)
roles=[]
for t,(stage,replica) in enumerate(D['order']):
 for h,w in enumerate(widths):
  owner,child,port,offset=assign[t,w].pop()
  family=896*owner+112*(2*P['pairs'][str(child)]+P['sides'][str(child)])+port
  roles.append(dict(time=t,stage=stage,replica=replica,helper=h,width=w,owner_replica=owner,child=child,port=port,offset=offset,copy=112*owner+port,family=family))
assert not any(assign.values());assert len(roles)==37*9*480
print('literal roles',len(roles),'idle',dict(sorted(idle.items())))
# Separate direct check from the aggregate model.
used=defaultdict(set);seen=defaultdict(set);coverage=defaultdict(set)
windows={(r,ch):(cap,set(ts)) for r,cap,ts,chs in D['groups'] for ch in chs}
for z in roles:
 t=z['time'];key=z['owner_replica'],z['child'];cap,ts=windows[key]
 assert t in ts and z['family'] not in seen[t];seen[t].add(z['family'])
 g=key+(z['port'],);cells=set(range(z['offset'],z['offset']+z['width']))
 assert not cells&used[g] and all(0<=x<cap for x in cells);used[g]|=cells;coverage[t].add(z['helper'])
for t,hh in coverage.items():assert hh==set(range(480))
left=Counter()
for key,(cap,ts) in windows.items():
 for port in range(112):
  cell=used[key+(port,)];assert cell==set(range(len(cell)));left[cap-len(cell)]+=1
assert left==idle
raw=json.dumps(roles,sort_keys=True,separators=(',',':')).encode()
# Discovery constructor: freeze the derived map for a later strict replay.
out=args.out;out.mkdir(parents=True)
(out/'OWNERS.json.gz').write_bytes(gzip.compress(raw,mtime=0))
(out/'ORDER.json').write_text(json.dumps(D['order'])+'\n')
(out/'GEOMETRY-CHECK.json').write_text(json.dumps({'roles':len(roles),'idle':dict(sorted(idle.items())),'owner_content_sha256':hashlib.sha256(raw).hexdigest(),'status':'PASS_LITERAL_WHOLE_HELPER_GEOMETRY'},indent=2)+'\n')
print('PASS_LITERAL_WHOLE_HELPER_GEOMETRY',hashlib.sha256(raw).hexdigest())
