#!/usr/bin/env python3
"""Float discovery pricing for README section 4 (auxiliary re-gauging under banks; target entrance gauges).

Copyright 2026 Joel Pulikkan (GamingPuzzled). Apache-2.0. Prepared with Anthropic Claude assistance.
Reads the PR173 package research/paired-cube-bit-rl-module (set PR173 to its path). Discovery only; no certificate.
"""
import os
import sys,math
from collections import Counter,defaultdict
sys.path.insert(0,os.environ.get('PR173','research/paired-cube-bit-rl-module'))
from word import Candidate
c=Candidate([]);C=c.C;C.decoder();C.geometry();M=c.module;h=c.h;w,g=c.w,c.g
rf=w['root_frame']
# target events in time order: gauge reads (by readtime), side roots, deliveries
ev=defaultdict(list)
for b in sorted(c.order,key=lambda b:c.readtime[b]):
    for t in c.gauge[b]['targets']: ev[t].append(c.gauge[b]['frame'])
dl=defaultdict(list)
for e in C.k['entries']: dl[e['deliver_after_root']].append(e)
for j,r in enumerate(g['roots']):
    if r['kind']=='center': continue
    for t in r['targets']: ev[t].append(rf[j])
    for e in dl.get(j,[]):
        for t in e['receivers']: ev[t].append(e['deliver_frame'])
adj=c.adjoint()
first_op={}
for i,(a,b,x) in enumerate(c.ops):
    for s in (a,b): first_op.setdefault(s,i)
src=set(c.source.values());p1=set()
for i in c.phase1: p1.update(c.ops[i][:2])
cand=[s for s in range(c.R) if s not in c.gauge and s not in src and s not in p1 and s in first_op and adj[s]]
cache={}
def inter(fs):
    k=tuple(sorted(set(fs)))
    if k not in cache:
        A=[r for f in k for r in C.A[f]];B,_=M.kernel(A,h);cache[k]=len(B)
    return cache[k]
dims=Counter();firstd=Counter();gain_rank=0
for s in cand:
    F=c.opframe[first_op[s]]
    fs=[F]+[ev[t][0] for t in adj[s] if ev[t]]
    f=inter(fs);dims[f]+=1;firstd[C.dimf[F]]+=1
print('ungauged non-source roles with targets',len(cand),'of R',c.R,'| existing gauges',len(c.gauge))
print('first-op dims',sorted(firstd.items()))
print('feasible sigma dims (read before all target events)',sorted(dims.items()))
print('targets per role',Counter(min(len(adj[s]),9) for s in cand).most_common(6))
empty=[s for s in range(c.R) if s not in c.gauge and s not in src and s in first_op and not adj[s]]
print('ungauged roles with EMPTY adjoint',len(empty),'in phase1',sum(s in p1 for s in empty),'root roles',sum(s in c.rootroles for s in empty))
print('their first-op dims',sorted(Counter(C.dimf[c.opframe[first_op[s]]] for s in empty).items()))
print('sources',len(src),'gauges',len(c.gauge),'phase1 roles',len(p1),'roots',len(c.rootroles))
import math
row=c.row();H={int(k):n for k,n in row['child_histogram'].items()};W=row['W_per_vertex'];m=72
def sav(H,W):
    g=lambda a:math.fsum(n*r*math.exp(a*math.log(m/r)) for r,n in H.items() if n)-W*m
    lo,hi=0.,2e-2
    for _ in range(80):
        mid=(lo+hi)/2;lo,hi=(mid,hi) if g(mid)<0 else (lo,mid)
    return lo
# 1) bank existing gauges: remove 5720 exterior children of width 60, W -= 5720*60/72
Hb=dict(H);Hb[60]-=5720;Wb=W-5720*60/72;ab=sav(Hb,Wb);print('banked existing gauges: %.6e (vs unbanked %.6e)'%(ab,sav(H,W)))
# 2) regauge candidates at sigma f: first transition r->r-f (3 copies), exterior 3f banked (free): mass -3f, W -3f/72
Hr=dict(Hb);Wr=Wb
for s in cand:
    F=c.opframe[first_op[s]];r=C.dimf[F];f=inter([F]+[ev[t][0] for t in adj[s] if ev[t]])
    if f<=0: continue
    # previous increment into first op frame from start (0) is r
    Hr[r]-=3
    if r-f: Hr[r-f]=Hr.get(r-f,0)+3
    Wr-=3*f/72
assert all(n>=0 for n in Hr.values())
print('regauge upper bound (no target-split cost): %.6e  gain %+.3f%%'%(sav(Hr,Wr),100*(sav(Hr,Wr)/ab-1)))
# exact-ish: frames per role sigma (actual subspace), nested chains on targets
def interF(fs):
    A=[r for f in set(fs) for r in C.A[f]];B,_=M.kernel(A,h)
    return c.register(B) if B else None
info=[]
for s in cand:
    F=c.opframe[first_op[s]];r=C.dimf[F]
    sg=interF([F]+[ev[t][0] for t in adj[s] if ev[t]])
    if sg is None: continue
    f=C.dimf[sg];info.append((f,s,sg,r))
info.sort(key=lambda z:-z[0])
chains=defaultdict(list)   # target -> accepted sigma frames
acc=[]
for f,s,sg,r in info:
    ok=all(all(C.sub(sg,o) or C.sub(o,sg) for o in chains[t]) for t in adj[s])
    if ok:
        acc.append((f,s,sg,r))
        for t in adj[s]: chains[t].append(sg)
print('accepted',len(acc),'of',len(info))
# rebuild: role side
Hx=dict(Hb);Wx=Wb
for f,s,sg,r in acc:
    Hx[r]-=3
    if r-f: Hx[r-f]=Hx.get(r-f,0)+3
    Wx-=3*f/72
# target side: first increment d1 of each touched target split along its distinct sigma dims
for t,fs in chains.items():
    d1=C.dimf[ev[t][0]];ds=sorted(set(C.dimf[x] for x in fs))
    Hx[d1]-=3;prev=0
    for d in ds+[d1]:
        if d>prev: Hx[d-prev]=Hx.get(d-prev,0)+3
        prev=d
assert all(n>=0 for n in Hx.values())
ax=sav(Hx,Wx);print('regauge with nested target splits: %.6e gain %+.3f%% over banked'%(ax,100*(ax/ab-1)))
# marginal greedy: accept only if exact saving improves
def tsplit(d1,ds):
    out=Counter();prev=0
    for d in sorted(set(ds))+[d1]:
        if d>prev: out[d-prev]+=3
        prev=d
    return out
Hg=Counter(Hb);Wg=Wb;cur=ab;chains2=defaultdict(list);n=0
for f,s,sg,r in info:
    if not all(all(C.sub(sg,o) or C.sub(o,sg) for o in chains2[t]) for t in adj[s]): continue
    H2=Counter(Hg);H2[r]-=3
    if r-f: H2[r-f]+=3
    for t in adj[s]:
        d1=C.dimf[ev[t][0]];old=[C.dimf[x] for x in chains2[t]]
        if old: H2.subtract(tsplit(d1,old))
        else: H2[d1]-=3
        H2.update(tsplit(d1,old+[f]))
    W2=Wg-3*f/72;a2=sav(+H2,W2)
    if a2>cur:
        Hg,Wg,cur=+H2,W2,a2;n+=1
        for t in adj[s]: chains2[t].append(sg)
print('marginal greedy accepted',n,'saving %.6e gain %+.3f%% over banked'%(cur,100*(cur/ab-1)))
# target entrance gauges: tau_t = first event frame E_t; first increment d1 (3 copies) -> one fused child 3*d1
v=c.v;Ht=Counter(Hb);n=0;d1s=Counter()
for t in range(v):
    if not ev[t]: continue
    d1=C.dimf[ev[t][0]];Ht[d1]-=3;Ht[3*d1]+=1;n+=1;d1s[d1]+=1
print('targets',n,'first-event dims',sorted(d1s.items()))
at=sav(+Ht,Wb);print('target gauges, fused correction child (unbanked): %+.3f%%'%(100*(at/ab-1)))
# variant: correction merged into the existing rank-2 final complement child of each data bank target
Hm=Counter(Ht)
for t in range(v):
    if not ev[t]: continue
    d1=C.dimf[ev[t][0]];Hm[3*d1]-=1;Hm[2]-=1;Hm[3*d1+2]+=1
am=sav(+Hm,Wb);print('  ... merged with final rank-2 complement: %+.3f%%'%(100*(am/ab-1)))
