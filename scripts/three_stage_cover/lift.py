# Copyright 2026 icekylinx. Apache-2.0.
# Integration with OpenAI Codex assistance; see NOTICE.
"""Full backward intersections, including degenerate subspaces.
Adapted from partial_gauge.lift; copyright 2026 icekylinx, Apache-2.0.
"""
from pathlib import Path
from collections import Counter
import json
from partial_gauge.binary import load
from partial_gauge.lift import basis, perp, nondeg

def run(path,matchfile):
    h,v,n,q,args,core,cover,roots,kind,active,oldrank,types=load(path)
    meta=json.loads(Path(matchfile).read_text());arcs=dict(meta['matching_arcs']);full=(1<<h)-1
    succ=[[] for _ in range(n)];direct=[[] for _ in range(n)]
    for x in range(1,n):
        if active[x] and args[2*x]:
            for y in (args[2*x],args[2*x+1]):succ[y].append(x)
    for j,(x,k) in enumerate(zip(roots,kind)):
        normal=(full^cover[x]) if k else (core[x]|(full^cover[x]))
        assert normal.bit_count()==(1 if k else 3)
        direct[x].append(normal)
    for donor,use in arcs.items():
        if use>>31:
            j=use&0x7fffffff;x=roots[j];k=kind[j]
            normal=(full^cover[x]) if k else (core[x]|(full^cover[x]))
            direct[donor].append(normal)
        else:succ[donor].append(use//2)
    order=sorted((x for x in range(1,n) if active[x]),key=lambda x:(oldrank[x],x))
    place={x:i for i,x in enumerate(order)}
    assert all(place[x]<place[y] for x in order for y in succ[x])
    ann=[None]*n;nr=[0]*n;repairs=0;capcache={};repaircache={};dimhist=Counter()
    for at,x in enumerate(reversed(order)):
        rows=direct[x][:]
        for y in succ[x]:rows.extend(ann[y])
        capann=basis(rows)
        if capann not in capcache:
            C=perp(capann,h);capcache[capann]=(C,nondeg(C))
        C,ok=capcache[capann]
        A=capann;d=len(C)
        ann[x]=A;nr[x]=d;assert d>=oldrank[x]
        dimhist[d-oldrank[x]]+=1
    degree=[0]*n
    for x in order:
        if args[2*x]:
            degree[args[2*x]]+=1;degree[args[2*x+1]]+=1
    for x in roots:degree[x]+=1
    H=Counter()
    for x in order:
        r=nr[x]
        if args[2*x]:
            H[r]+=degree[x]-1;H[h-r]+=1
            for y in (args[2*x],args[2*x+1]):assert r>=nr[y];H[r-nr[y]]+=1
        else:
            H[r]+=degree[x]-1;H[1]+=1;H[r-1]+=1
    loss=0
    for x,k in zip(roots,kind):
        r=nr[x]
        if k:H[r]+=1;H[h-r]+=1;loss+=r
        else:assert r<=h-1;H[h-1-r]+=1;H[1]+=1
    for donor,use in arcs.items():
        target=roots[use&0x7fffffff] if use>>31 else use//2
        value=target if use>>31 else args[2*target+(use&1)]
        ru,rv=nr[donor],nr[value]
        rt=(h-1 if use>>31 else nr[target])
        # Root uses have a direct physical edge to their output frame, not
        # necessarily to the value's newly lifted producer frame.
        old_target_rank=nr[target]
        H[h-ru]-=1;H[rv]-=1
        if use>>31:
            H[h-1-rv]-=1;H[h-1-ru]+=1
        else:H[rt-rv]-=1;H[rt-ru]+=1
    assert min(H.values())>=0
    R=meta['R'];mass=sum(r*c for r,c in H.items());assert mass==h*R+loss,(mass,h*R+loss)
    out={k:meta[k] for k in ['h','v','c','q','R','matched']}
    out.update(loss=loss,histogram=[H[i] for i in range(h+1)],rank_sum=mass,
        copied_centers_already=True,repairs=repairs,distinct_caps=len(capcache),distinct_repairs=len(repaircache),
        dimension_gains=dict(dimhist),lift='Full backward intersections using generalized Lagrangian frames, including degenerate subspaces')
    return out,ann
