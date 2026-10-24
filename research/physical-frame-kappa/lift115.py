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
