"""Exact native map simultaneously preserving a line and matching a subspace.

Apache-2.0. Cao Yifan, with substantial OpenAI Codex assistance.
"""
from pathlib import Path
import sys
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'research/scalar-reorder-20261022'))
from intervals import basis,closure


def line_matching_map(A,cap,a,b):
    """Return invertible columns G and B with G(A)=B<=cap and G(a)=b."""
    k=len(A);SA=closure(A);SC=closure(cap)
    if a in SA:
        assert b in SC
        AB=[a];BB=[b]
        for x in A:
            if len(basis(AB+[x]))>len(AB):AB.append(x)
        for y in cap:
            if len(BB)==k:break
            if len(basis(BB+[y]))>len(BB):BB.append(y)
        output=BB[:]
    else:
        assert k<len(cap) or b not in SC
        AB=A[:];BB=[];quotient=[b]
        for y in cap:
            if len(BB)==k:break
            if len(basis(quotient+[y]))>len(quotient):
                BB.append(y);quotient.append(y)
        assert len(BB)==k
        output=BB[:];AB.append(a);BB.append(b)
    assert len(AB)==len(BB)==len(basis(AB))==len(basis(BB))
    for X in (AB,BB):
        for j in range(9):
            if len(basis(X+[1<<j]))>len(X):X.append(1<<j)
    images={0:0}
    for x,y in zip(AB,BB):images.update({z^x:w^y for z,w in list(images.items())})
    assert len(images)==len(set(images.values()))==512
    assert images[a]==b and {images[x] for x in SA}==set(closure(output)) and closure(output)<=SC
    return [images[1<<j] for j in range(9)],output
