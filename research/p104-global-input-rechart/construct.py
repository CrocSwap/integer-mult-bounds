"""Rechart public scalar contacts and reconstruct every causal transport.

Fresh-helper-boundary alpha-expansion supplied the nomination. This generator
does not trust its floating score. Rohan Arun/OpenAI Codex, Apache-2.0.
"""
from copy import deepcopy
def span(basis):
    out={0}
    for x in basis:
        assert x not in out;out|={x^v for v in tuple(out)}
    return frozenset(out)
def construct(source,changes):
    w=deepcopy(source);n=w['public'];spaces=list(map(span,w['frames']))
    main=set(w['live'])|{r+112 for r in w['live']}|set(w['hosted']['X2'])|set(w['hosted']['Y2'])
    for r,old,new in changes['initial']:
        assert r<n and r not in main and w['initial'][r]==old
        assert spaces[new]<spaces[w['final'][r]];w['initial'][r]=new
    edits={i:(old,new) for i,old,new in changes['scalar']};assert len(edits)==len(changes['scalar'])
    cur=w['initial']+[None]*w['owned_fields'];program=[];seen=set()
    def move(r,to):
        old=cur[r]
        if old==to:return
        assert old is not None and (spaces[old]<spaces[to] or (r>=n and spaces[to]<spaces[old]))
        program.append(['MOVE',r,old,to,r>=n]);cur[r]=to
    for i,e in enumerate(source['program']):
        op,r=e[:2]
        if op=='MOVE':
            if r>=n:assert cur[r]==e[2];move(r,e[3])
        elif op=='INIT':assert r>=n and cur[r] is None;program.append(e.copy());cur[r]=e[2]
        elif op=='CLEAR':assert r>=n and cur[r]==e[2];program.append(e.copy());cur[r]=None
        else:
            assert op in ('ADD','COPY','SCALE');roles=e[1:3] if op in ('ADD','COPY') else e[1:2];frame=e[-1]
            if i in edits:
                old,frame=edits[i];assert old==e[-1] and all(r<n for r in roles);seen.add(i)
            for r in roles:move(r,frame)
            program.append([*e[:-1],frame])
    assert seen==set(edits)
    for r,f in enumerate(w['final']):move(r,f)
    assert cur==w['final']+[None]*w['owned_fields'];w['program']=program;return w
