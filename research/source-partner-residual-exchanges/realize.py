# SPDX-License-Identifier: Apache-2.0
# Nomination only; the immutable predecessor reconstruct.py checks the witness.
from common import *
from collections import Counter,defaultdict
import numpy as np
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import maximum_flow
D=json.load(open(BASE/'order-screen.json'));P=json.load(open(BASE/'interval-packing-neworder.json'));assert P['added']==0
ws=D['widths'];inv={int(k):v for k,v in D['inventory'].items()};groups=P['groups'];pat=P['patterns'];windows=D['windows'];bins=defaultdict(list)
for g,p,n in P['solution']:
 for _ in range(n):bins[g].append(pat[p][1])
assert all(len(bins[g])==112 for g in range(len(groups)))
used={g:[set() for _ in range(112)] for g in bins};assigned=[]
def flow(N,edges,src,sink):
 rows,cols,vals=zip(*edges);mat=coo_matrix((np.array(vals,dtype=np.int64),(rows,cols)),shape=(N,N)).tocsr();return maximum_flow(mat,src,sink)
for w in [8,5,4,7,9]:
 j=ws.index(w)
 # Aggregate bins with identical demand and occupied times. This is the same
 # literal bipartite problem as the predecessor's port expansion, with
 # interchangeable bins represented by one capacity class.
 import heapq
 classes=defaultdict(list)
 for g in bins:
  for p,b in enumerate(bins[g]):
   if b[j]:classes[g,b[j],tuple(sorted(used[g][p]))].append(p)
 C=list(classes);sink=667+len(C);E=[(0,1+t,inv[w]) for t in range(666)]
 for k,(g,demand,banned) in enumerate(C):
  count=len(classes[C[k]]);E.append((667+k,sink,count*demand));ban=set(banned)
  E.extend((1+t,667+k,count) for t in windows[groups[g]][1] if t not in ban)
 print('CLASS_EDGES',len(E),'classes',len(C),flush=True)
 ff=flow(sink+1,E,0,sink);print('CLASS_FLOW',ff.flow_value,666*inv[w],flush=True)
 assert ff.flow_value==666*inv[w]
 co=ff.flow.tocoo();demands=defaultdict(list)
 mask=(co.data>0)&(co.row>=1)&(co.row<=666)&(co.col>=667)&(co.col<sink)
 for a,b,value in zip(co.row[mask],co.col[mask],co.data[mask]):demands[int(b-667)].append((int(value),int(a-1)))
 for k,(g,demand,banned) in enumerate(C):
  heap=[(-demand,p) for p in classes[C[k]]];heapq.heapify(heap)
  for count,t in sorted(demands[k],reverse=True):
   picked=[heapq.heappop(heap) for _ in range(count)]
   for remain,p in picked:
    assert remain<0 and t not in used[g][p]
    used[g][p].add(t);assigned.append([t,w,g,p]);heapq.heappush(heap,(remain+1,p))
  assert all(remain==0 for remain,p in heap)
# Name helpers and pack prefixes; exact upstream verifier subsequently checks all claims.
nw=json.load(gzip.open(BASE/'eight-alias-base.json.gz','rt'));oldw=json.load(gzip.open(Path(os.environ['SOURCE_PARTNER_PREPARED'])/'new/borrow/words/BORROW-WORD-43base.json.gz','rt'));oldpv=json.load(open(Path(os.environ['SOURCE_PARTNER_PREPARED'])/'new/BORROW-PROVIDERS.json'));live=sorted(set(range(224,704))-set(oldw['removed']));nlive=sorted(set(range(224,704))-set(nw['removed']));widths=[oldpv['gauge44']['widths'][live.index(r)] for r in nlive];helpers=defaultdict(list)
for h,w in enumerate(widths):helpers[w].append(h)
cursor=Counter();offset=Counter();rows=[]
for t,w,g,p in sorted(assigned):
 h=helpers[w][cursor[t,w]];cursor[t,w]+=1;rep,ch=map(int,groups[g].split(','));rows.append([t,h,rep,ch,p,offset[g,p]]);offset[g,p]+=w
out=dict(columns=['time','helper','owner_replica','child','port','offset'],dispatch_overrides=[],rows=rows)
(BASE/'eight-fill.json.gz').write_bytes(gzip.compress(json.dumps(out,separators=(',',':')).encode(),mtime=0))
(BASE/'eight-order.json').write_text(json.dumps(D['order']))
(BASE/'eight-providers.json').write_text(json.dumps({p:dict(widths=widths,actual_paid_profile=nw['report']['local_profile']) for p in oldpv}))
print('DONE',len(rows),Counter(windows[groups[g]][0]-offset[g,p] for g in bins for p in range(112)),flush=True)
