# Copyright 2026 icekylinx. Apache-2.0.
# Prepared with OpenAI GPT-6 Astra and Codex assistance; see NOTICE.
#!/usr/bin/env python3
"""Construct maximal nondegenerate backward frames containing every old frame.
Existing carrier dependencies are included before the backward pass. Exact F2
linear algebra only; the general Gauss compiler permits alternating residuals.
"""
from pathlib import Path
from collections import Counter
import json,argparse
from .binary import load

def basis(rows):
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

def perp(rows,h):
    rows=basis(rows);piv={r.bit_length()-1:r for r in rows};out=[]
    for j in range(h):
        if j in piv:continue
        x=1<<j
        for p,r in piv.items():
            if r>>j&1:x|=1<<p
        out.append(x)
    return basis(out)

def dot(a,b):return (a&b).bit_count()&1

def nondeg(rows):
    return len(basis(sum(dot(x,y)<<j for j,y in enumerate(rows)) for x in rows))==len(rows)

def contained(A,B):
    for x in A:
        for y in B:x=min(x,x^y)
        if x:return False
    return True

def safe_subspace(cap,old):
    # Old has a supplied orthonormal basis. Orthogonally remove old from cap.
    others=[]
    for x in cap:
        for u in old:
            if dot(x,u):x^=u
        others.append(x)
    others=list(basis(others));chosen=[]
    while others:
        i=next((i for i,x in enumerate(others) if dot(x,x)),None)
        if i is not None:
            u=others.pop(i);chosen.append(u)
            others=list(basis(x^(u if dot(x,u) else 0) for x in others));continue
        pair=next(((i,j) for i in range(len(others)) for j in range(i) if dot(others[i],others[j])),None)
        if pair is None:break
        i,j=pair;u=others[i];v=others[j];chosen.extend((u,v))
        others=list(basis(x^(u if dot(x,v) else 0)^(v if dot(x,u) else 0) for k,x in enumerate(others) if k not in (i,j)))
    result=basis(list(old)+chosen)
    assert nondeg(result) and contained(basis(old),result)
    return result

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
        if ok:A=capann;d=len(C)
        else:
            if types[x]==1:
                if oldrank[x]==1:U=(cover[x],)
                else:U=tuple((1<<j)|core[x] for j in range(h) if (cover[x]&~core[x])>>j&1)
            elif types[x]==2:U=tuple(1<<j for j in range(h) if cover[x]>>j&1)
            else:raise ValueError('Unselected center type')
            key=(capann,U)
            if key not in repaircache:
                M=safe_subspace(C,U);repaircache[key]=perp(M,h)
            A=repaircache[key];d=h-len(A);repairs+=1
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
        dimension_gains=dict(dimhist),lift='Backward chosen-successor intersection; maximal nondegenerate complement containing old orthonormal frame; old matched dependencies preserved')
    return out,ann
