# Copyright 2026 icekylinx. Apache-2.0.
# Developed with GPT-6 Astra assistance; integrated with Codex assistance.
# Modified 2026 by Joel Pulikkan (GamingPuzzled) with Anthropic Claude assistance: compile_graph(g, None) now builds
# its own monotone carrier matching (maximum cardinality, Hopcroft-Karp) instead of requiring frozen arcs, and
# basis() is memoized. With frozen arcs supplied, behaviour is PR161's scripts/paired_cube/frames.py.
"""Actual monotone carrier matching and binary frame profile for a signed DAG.

Signs are recorded in the construction's scalar ledger. This compiler uses
the safe union of operand address spans, never cancellation of a fresh value
to justify a physical frame. New work for icekylinx, OpenAI GPT-6 Astra assistance.
"""
from pathlib import Path
from collections import Counter
import json, math, sys, functools

def _basis_raw(rows):
    b={}
    for x in rows:
        for p,y in sorted(b.items(),reverse=True):
            if x>>p&1:x^=y
        if x:
            p=x.bit_length()-1
            for k,y in list(b.items()):
                if y>>p&1:b[k]=y^x
            b[p]=x
    return tuple(b[p] for p in sorted(b,reverse=True))

@functools.lru_cache(maxsize=None)
def _basis_c(rows):return _basis_raw(rows)
def basis(rows):return _basis_c(tuple(rows))

def perp(rows,h):
    rows=basis(rows); piv={r.bit_length()-1:r for r in rows}; out=[]
    for j in range(h):
        if j in piv:continue
        x=1<<j
        for p,r in piv.items():
            if r>>j&1:x|=1<<p
        out.append(x)
    return basis(out)

@functools.lru_cache(maxsize=500000)
def contained(A,B):
    for x in A:
        for y in B:x=min(x,x^y)
        if x:return False
    return True

def hopcroft_karp(left, adj):
    """maximum bipartite matching; adj[x] = sorted list of right vertices."""
    INF = 1 << 60
    mate_l = {x: None for x in left}; mate_r = {}
    while True:
        dist = {}; queue = []
        for x in left:
            if mate_l[x] is None: dist[x] = 0; queue.append(x)
            else: dist[x] = INF
        found = INF; head = 0
        while head < len(queue):
            x = queue[head]; head += 1
            if dist[x] >= found: continue
            for r in adj[x]:
                y = mate_r.get(r)
                if y is None: found = min(found, dist[x] + 1)
                elif dist[y] == INF: dist[y] = dist[x] + 1; queue.append(y)
        if found == INF: break
        gained = 0
        for x0 in left:
            if mate_l[x0] is not None: continue
            stack = [(x0, iter(adj[x0]))]; path = []
            while stack:
                x, it = stack[-1]
                advanced = False
                for r in it:
                    y = mate_r.get(r)
                    if (y is None and dist[x] + 1 == found) or (y is not None and dist[y] == dist[x] + 1):
                        path.append((x, r))
                        if y is None:
                            for xx, rr in path: mate_l[xx] = rr; mate_r[rr] = xx
                            gained += 1; stack = []; break
                        stack.append((y, iter(adj[y]))); advanced = True; break
                else:
                    dist[x] = INF; stack.pop()
                    if path: path.pop()
                    continue
                if not advanced: break
        if not gained: break
    return mate_l


def compile_graph(g, frozen_arcs):
    if g['args'][len(g['inputs'])] is not None:
        # Accept the construction's compact zero-based node convention.
        g=dict(g)
        g['args']=[None]+[None if a is None else [x+1 for x in a] for a in g['args']]
        g['roots']=[dict(r,node=r['node']+1) for r in g['roots']]
    h=g['h']; inputs=g['inputs']; v=len(inputs); args=g['args']; n=len(args)
    roots=g['roots']; q=len(roots); spans=[()]*n
    # Node zero is reserved. Input node i+1 carries the corresponding source.
    for i,u in enumerate(inputs):spans[i+1]=(u,)
    for x in range(v+1,n):
        a,b=args[x]
        assert 0<a<x and 0<b<x
        spans[x]=basis(spans[a]+spans[b])
    rframe=[]; rann=[]; Y=[() for _ in inputs]; targetH=Counter(); ell=0
    for r in roots:
        x=r['node']
        if r.get('kind','side')=='center':
            U=spans[x]; A=perp(U,h); ell+=len(U)
        else:
            A=basis(inputs[t] for t in r['targets'])
            U=perp(A,h)
            for t in r['targets']:
                assert contained(Y[t],U),('target retreat',t,Y[t],U)
                targetH[len(U)-len(Y[t])]+=1
                Y[t]=U
        assert contained(spans[x],U),('root physical incompatibility',x)
        rframe.append(U);rann.append(A)
    for t in range(v):
        cap=perp((inputs[t],),h)
        assert contained(Y[t],cap)
        targetH[h-1-len(Y[t])]+=1
    active=set(range(1,v+1)); todo=[r['node'] for r in roots]
    while todo:
        x=todo.pop()
        if x in active:continue
        active.add(x)
        if args[x]:todo.extend(args[x])
    # The scalar word may list dead intermediates, but they allocate no role.
    initial=spans
    if g.get('matching_frames','maximal') in ('maximal','coordinate'):
        initial=[()]*n;preann=[None]*n;successors=[[] for _ in args];constraints=[[] for _ in args]
        for x in sorted(active):
            if args[x]:
                for y in args[x]:successors[y].append(x)
        for j,r in enumerate(roots):constraints[r['node']].extend(rann[j])
        for x in sorted(active,reverse=True):
            preann[x]=basis(constraints[x]+[z for y in successors[x] for z in preann[y]])
            initial[x]=perp(preann[x],h)
            if g.get('matching_frames')=='coordinate':
                # Explicit unused orthogonal address directions may be added
                # to side caps. Center annihilators still exclude them.
                cover=g.get('side_padding_mask',0)
                for u in spans[x]:cover|=u
                initial[x]=perp(preann[x]+tuple(1<<j for j in range(h) if not cover>>j&1),h)
            assert contained(spans[x],initial[x])
    order=sorted(active,key=lambda x:(len(initial[x]),x)); position={x:i for i,x in enumerate(order)}
    uses=[[] for _ in args]; usevalue=[]; usetarget=[]; useframe=[]; usecode=[]
    for x in order:
        if args[x]:
            for j,y in enumerate(args[x]):
                uses[y].append(len(usevalue));usevalue.append(y);usetarget.append(x)
                useframe.append(initial[x]);usecode.append(2*x+j)
    for j,r in enumerate(roots):
        x=r['node'];uses[x].append(len(usevalue));usevalue.append(x);usetarget.append(n+j)
        useframe.append(rframe[j]);usecode.append((1<<31)|j)
    donors=[x for x in order if args[x]]
    bycode={code:u for u,code in enumerate(usecode)}
    if frozen_arcs is None:
        left=[];adj={}
        for x in donors:
            cand=[]
            for y in args[x]:
                for u in uses[y]:
                    t=usetarget[u]
                    if t==x:continue
                    if (t>=n or position[t]>position[x]) and contained(initial[x],useframe[u]):cand.append(u)
            if cand:left.append(x);adj[x]=sorted(set(cand))
        mate=hopcroft_karp(left,adj)
        frozen_arcs=[[x,usecode[u]] for x,u in mate.items() if u is not None]
    arcs={x:bycode[code] for x,code in frozen_arcs}
    assert len(arcs)==len(frozen_arcs)==len(set(arcs.values()))
    donors_set=set(donors)
    for x,u in arcs.items():
        assert x in donors_set and usevalue[u] in args[x]
        t=usetarget[u]
        assert t>=n or position[t]>position[x]
        assert contained(initial[x],useframe[u])
    succ=[[] for _ in args]; direct=[[] for _ in args]
    for x in order:
        if args[x]:
            for y in args[x]:succ[y].append(x)
    for j,r in enumerate(roots):direct[r['node']].extend(rann[j])
    for x,u in arcs.items():
        t=usetarget[u]
        if t<n:succ[x].append(t)
        else:direct[x].extend(rann[t-n])
    ann=[None]*n; rank=[0]*n
    for x in reversed(order):
        ann[x]=basis(direct[x]+[z for y in succ[x] for z in ann[y]])
        rank[x]=h-len(ann[x])
        assert contained(spans[x],perp(ann[x],h))
    H=Counter()
    for x in order:
        r=rank[x];degree=len(uses[x]);assert degree>0,('unused input',x)
        H[r]+=degree-1
        if args[x]:
            H[h-r]+=1
            for y in args[x]:
                assert contained(ann[x],ann[y])
                H[r-rank[y]]+=1
        else:H[1]+=1;H[r-1]+=1
    for j,root in enumerate(roots):
        x=root['node'];r=rank[x];rt=len(rframe[j]);assert r<=rt
        if root.get('kind','side')=='center':
            assert r==rt
            H[r]+=1;H[h-r]+=1
        else:H[rt-r]+=1;H[h-rt]+=1
    for x,u in arcs.items():
        value=usevalue[u];t=usetarget[u];rv=rank[value];rd=rank[x]
        rt=rank[t] if t<n else len(rframe[t-n])
        assert rt>=rd>=rv
        H[h-rd]-=1;H[rv]-=1;H[rt-rv]-=1;H[rt-rd]+=1
    assert min(H.values())>=0
    R=len(donors)+q-len(arcs)
    mass=sum(r*c for r,c in H.items());assert mass==h*R+ell,(mass,h*R+ell)
    source=Counter({2:v,h-4:v,1:v})
    if g.get('source_data_histogram') is not None:source=Counter({int(r):c for r,c in g['source_data_histogram'].items()})
    assert sum(r*c for r,c in source.items())==v*(h-1)
    m=3*h;W=2*v+R
    children=Counter({r:3*c for r,c in H.items() if r})
    children.update({r:3*c for r,c in source.items() if r})
    children.update({r:3*c for r,c in targetH.items() if r})
    children[2]+=2*v
    cmass=sum(r*c for r,c in children.items());deficit=W*m-cmass
    assert deficit==2*v-3*ell
    lo=0.;hi=.1
    if deficit>0:
        for _ in range(75):
            a=(lo+hi)/2
            if math.fsum(c*r*math.exp(a*math.log(m/r)) for r,c in children.items())<W*m:lo=a
            else:hi=a
    profile=dict(h=h,v=v,R=R,q=q,c=len(donors),matched=len(arcs),loss=ell,selected_roles=0,
        selected_rank_histogram={},remaining_internal_histogram=[H[r] for r in range(h+1)],
        source_data_histogram=dict(source),target_data_histogram=dict(targetH),copied_centers_already=True,
        m=m,W_per_vertex=W,rank_per_vertex=cmass,deficit_per_vertex=deficit,
        numerical_complex_root=lo if deficit>0 else None,child_histogram=dict(children),
        matching_frames=g.get('matching_frames','maximal'),
        status='Concrete zero-gauge signed DAG, actual monotone carrier matching and complete rank profile; numerical moment, not yet a strict assembled supplier')
    witness=dict(matching_arcs=[[x,usecode[u]] for x,u in arcs.items()],annihilators=ann,order=order)
    return profile,witness
