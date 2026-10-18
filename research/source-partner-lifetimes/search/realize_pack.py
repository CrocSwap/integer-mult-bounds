# SPDX-License-Identifier: Apache-2.0
# Nomination only; build.py independently verifies the emitted witness.
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
 if w==9:
  B=[(g,p) for g in bins for p,b in enumerate(bins[g]) if b[j]];sink=667+len(B);E=[(0,1+t,inv[w]) for t in range(666)]
  for k,(g,p) in enumerate(B):
   E.append((667+k,sink,bins[g][p][j]))
   E.extend((1+t,667+k,1) for t in windows[groups[g]][1] if t not in used[g][p])
  print('DIRECT_EDGES',len(E),flush=True);ff=flow(sink+1,E,0,sink);print('DIRECT_FLOW',ff.flow_value,666*inv[w],flush=True);assert ff.flow_value==666*inv[w]
  co=ff.flow.tocoo()
  mask=(co.data>0)&(co.row>=1)&(co.row<=666)&(co.col>=667)&(co.col<sink)
  for a,b,v in zip(co.row[mask],co.col[mask],co.data[mask]):
   if v>0 and 1<=a<=666 and 667<=b<sink:
    g,p=B[b-667];used[g][p].add(int(a-1));assigned.append([int(a-1),w,g,p])
  continue
 edges=[];sink=1+666+len(groups)
 for t in range(666):edges.append((0,1+t,inv[w]))
 for g in bins:
  need=sum(b[j] for b in bins[g]);edges.append((667+g,sink,need))
  if not need:continue
  ports=[p for p,b in enumerate(bins[g]) if b[j]]
  for t in windows[groups[g]][1]:
   cap=sum(t not in used[g][p] for p in ports)
   if cap:edges.append((1+t,667+g,cap))
 F=flow(sink+1,edges,0,sink);print('FLOW',w,F.flow_value,666*inv[w],flush=True);assert F.flow_value==666*inv[w]
 for g in bins:
  if not any(b[j] for b in bins[g]):continue
  times=windows[groups[g]][1];counts={t:int(F.flow[1+t,667+g]) for t in times};counts={t:n for t,n in counts.items() if n}
  E=[];T=113+len(counts);tt=list(counts)
  for p,b in enumerate(bins[g]):
   E.append((0,1+p,b[j]))
   if b[j]:
    for k,t in enumerate(tt):
     if t not in used[g][p]:E.append((1+p,113+k,1))
  for k,t in enumerate(tt):E.append((113+k,T,counts[t]))
  ff=flow(T+1,E,0,T);need=sum(counts.values())
  if ff.flow_value!=need:
   print('BIN_FAIL',w,g,groups[g],ff.flow_value,need,counts,flush=True);raise RuntimeError('bin distribution')
  for p,b in enumerate(bins[g]):
   if not b[j]:continue
   for k,t in enumerate(tt):
    if ff.flow[1+p,113+k]>0:used[g][p].add(t);assigned.append([t,w,g,p])
 print('BINS_PASS',w,flush=True)
 (BASE/'realized-partial.json').write_text(json.dumps(assigned))
# Name helpers and pack prefixes; exact upstream verifier subsequently checks all claims.
nw=json.load(gzip.open(BASE/'eight-alias-base.json.gz','rt'));oldw=json.load(gzip.open(BASE/'pr2462/research/gmx-t74-borrow43-handoff/new/borrow/words/BORROW-WORD-43base.json.gz','rt'));oldpv=json.load(open(BASE/'pr2462/research/gmx-t74-borrow43-handoff/new/BORROW-PROVIDERS.json'));live=sorted(set(range(224,704))-set(oldw['removed']));nlive=sorted(set(range(224,704))-set(nw['removed']));widths=[oldpv['gauge44']['widths'][live.index(r)] for r in nlive];helpers=defaultdict(list)
for h,w in enumerate(widths):helpers[w].append(h)
cursor=Counter();offset=Counter();rows=[]
for t,w,g,p in sorted(assigned):
 h=helpers[w][cursor[t,w]];cursor[t,w]+=1;rep,ch=map(int,groups[g].split(','));rows.append([t,h,rep,ch,p,offset[g,p]]);offset[g,p]+=w
out=dict(columns=['time','helper','owner_replica','child','port','offset'],dispatch_overrides=[],rows=rows)
(BASE/'eight-fill.json.gz').write_bytes(gzip.compress(json.dumps(out,separators=(',',':')).encode(),mtime=0))
(BASE/'eight-order.json').write_text(json.dumps(D['order']))
(BASE/'eight-providers.json').write_text(json.dumps({p:dict(widths=widths,actual_paid_profile=nw['report']['local_profile']) for p in oldpv}))
print('DONE',len(rows),Counter(windows[groups[g]][0]-offset[g,p] for g in bins for p in range(112)),flush=True)
