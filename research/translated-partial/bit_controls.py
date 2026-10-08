#!/usr/bin/env python3
"""Bounded exact controls for the new partial-swap auxiliary source lemma.

Copyright 2026 Zhihao Chen (jacklightChen). Apache-2.0.
Extends PR18 f2ab41aebad47861caf6316282c1793e5513845e by icekylinx.

These validate endpoint identities, full small physical pivot profiles, and
the actual PR18 prescribed 23-corner.  The rational finite-family proof is
notes/translated-partial-bit.tex; controls alone are not an exponent certificate.
"""
import json
import random
from pathlib import Path
from hashlib import sha256
from matrix_helpers import P, ident, mm, inv, randinv, subtract, pivots


def add(a,b):
    return [[(x+y)%P for x,y in zip(ar,br)] for ar,br in zip(a,b)]


def proj(pair,rank):
    a,b=pair;n=len(a)
    return [[sum(a[i][k]*b[k][j] for k in range(rank))%P for j in range(n)] for i in range(n)]


def partial(p):
    n=len(p);q=subtract(ident(n),p)
    return [q[i]+p[i] for i in range(n)]+[p[i]+q[i] for i in range(n)]


def endpoint_control(n,r0,r1,seed):
    rng=random.Random(seed);base=randinv(n,rng)
    p0,p1=proj(base,r0),proj(base,r1);one=ident(n);zero=[[0]*n for _ in range(n)]
    assert mm(p0,p1)==mm(p1,p0)==p0
    source=partial(p0);sink=partial(subtract(one,p0));full=partial(one)
    assert mm(source,source)==ident(2*n)
    assert mm(sink,source)==full
    residual=add(subtract(one,p1),p0)
    assert mm(residual,residual)==residual
    exit_edge=mm(sink,partial(p1))
    assert exit_edge==partial(residual)
    assert len(pivots(residual))==n-r1+r0
    # Complete first/interior/final telescoping, on every input coordinate.
    entrance=mm(partial(p0),source)
    interior=mm(partial(p1),partial(p0))
    assert entrance==ident(2*n)
    assert mm(mm(exit_edge,interior),entrance)==full
    # Exact dense-vector check with arbitrary nonzero dirty input.
    dirty=[[rng.randrange(P)] for _ in range(2*n)]
    assert mm(mm(mm(exit_edge,interior),entrance),dirty)==mm(full,dirty)
    # Negative controls distinguish the multiplicative identity from two
    # tempting but incorrect additive/end-frame substitutions.
    assert mm(partial(add(one,p0)),source)!=full
    assert partial(subtract(one,p1))!=exit_edge
    return dict(dimension=n,first_rank=r0,last_rank=r1,exit_rank=n-r1+r0,
                arbitrary_input_matrix_identity=True,negative_controls=2)


def small_profile(dims,seed):
    a,b,c=dims;H=a*b;m=H*c;rng=random.Random(seed)
    js=[randinv(a,rng) for _ in range(b)]
    gs=[randinv(c,rng) for _ in range(H)]
    u=[];v=[];bs=[]
    for gamma in range(c):
        for alpha in range(a):
            for beta in range(b):
                j,ji=js[beta];g,gi=gs[alpha*b+beta]
                u.append(g[gamma][0]*j[alpha][0]%P)
                v.append(ji[0][alpha]*gi[0][gamma]%P)
                bs.append(beta)
    assert all(sum(u[i]*v[i] for i in range(m) if bs[i]==beta)%P==1 for beta in range(b))
    if not all(u[:b]) or not all(v[-b:]):return None
    A=[[(int(i==j)-(u[i]*v[j] if bs[i]==bs[j] else 0))%P for j in range(m)] for i in range(m)]
    ps=pivots(A);lookup=dict(ps)
    assert len(ps)==m-b
    assert all(lookup.get(i)==m-b+i for i in range(b))
    assert all(lookup.get(i)==i for i in range(b,m-b))
    return dict(dims=dims,ambient_dimension=m,rank=m-b,blocks=[b,m-2*b],
                full_physical_elimination=True)


def dot(x,y):return sum(a*b for a,b in zip(x,y))%P


def line(n,rng):
    while True:
        p=[rng.randrange(P) for _ in range(n)];q=[rng.randrange(P) for _ in range(n)]
        d=dot(p,q)
        if d:return p,[x*pow(d,-1,P)%P for x in q]


def actual_corner(seed):
    rng=random.Random(seed);a,b,c=25,23,57;H=a*b
    L1,L1i=randinv(a,rng);L0,L0i=randinv(c,rng)
    R=list(range(a))+list(range(7))+list(range(a))*2
    C=list(range(a))*2+list(range(7))+list(range(a))
    perms=[]
    for beta in range(b):
        prescribed={}
        def put(row,col):
            assert row not in prescribed or prescribed[row]==col
            assert col not in prescribed.values() or prescribed.get(row)==col
            prescribed[row]=col
        for i,col in enumerate(R):
            if i%b==beta:put(i//b,col)
        for j,col in enumerate(C):
            i=H-len(C)+j
            if i%b==beta:put(i//b,col)
        unused=iter(k for k in range(a) if k not in prescribed.values())
        perms.append([prescribed[r] if r in prescribed else next(unused) for r in range(a)])
    records=[]
    for case in range(8):
        p,xi=line(a,rng);t,phi=line(c,rng)
        lp=[dot(row,p) for row in L1]
        xli=[dot(xi,col) for col in zip(*L1i)]
        lt=[dot(row,t) for row in L0]
        fli=[dot(phi,col) for col in zip(*L0i)]
        d=[]
        for beta in range(b):
            # The completed M has row alpha=0 equal to e_beta and
            # M^{-1}e_24 equal to e_(beta+2), directly from prescriptions.
            assert perms[beta][0]==beta
            assert perms[beta][24]==beta+2
            actual=lt[beta]*lp[perms[beta][0]]*xli[perms[beta][24]]*fli[beta+34]%P
            expected=lt[beta]*lp[beta]*xli[beta+2]*fli[beta+34]%P
            assert actual==expected
            d.append(actual)
        if not all(d):return None
        corner=[[d[i] if i==j else 0 for j in range(b)] for i in range(b)]
        assert pivots(corner)==[(i,i) for i in range(b)]
        records.append(dict(case=case,corner_size=b,nonzero_diagonal=True))
    return dict(seed=seed,profiles=records,prescribed_completions=len(perms),
                actual_dimensions=[a,b,c],physical_blocks=[23,32729])


def main():
    endpoints=[endpoint_control(n,2,n-3,3000+n) for n in (7,9,13,17)]
    profiles=[]
    for dims in ((3,4,5),(4,3,5),(4,5,6)):
        for trial in range(3):
            seed=10000*sum(dims)+trial
            while True:
                z=small_profile(dims,seed);seed+=100
                if z:profiles.append(z);break
    actual=[]
    for trial in range(3):
        seed=400000+trial
        while True:
            z=actual_corner(seed);seed+=100
            if z:actual.append(z);break
    root=Path(__file__).resolve().parents[2]
    files=[Path(__file__).resolve(),Path(__file__).with_name('matrix_helpers.py'),root/'notes/translated-partial-bit.tex']
    hashes={str(p.relative_to(root)):sha256(p.read_bytes()).hexdigest() for p in files}
    print(json.dumps(dict(source_sha256=hashes,status='BOUNDED EXACT ALGEBRA CONTROLS; NOT A MULTIPLICATION CERTIFICATE',
                         modulus=P,endpoints=endpoints,full_small_profiles=profiles,
                         actual_prescribed_corners=actual),indent=2))


if __name__=='__main__':main()
