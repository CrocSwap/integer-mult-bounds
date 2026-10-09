#!/usr/bin/env python3
"""Open generator for physical frame descent and late-read compensated reuse on a paired-cube complex word.

Copyright 2026 Joel Pulikkan (GamingPuzzled). Apache-2.0. Prepared with Anthropic Claude assistance.

It writes the frozen-input format that PR161's scripts/paired_cube_physical.py checks (operation frames and
donor/recipient pairs), and then runs that unchanged checker on its own output.  Frame descent and
compensated reuse follow PR130/PR131 (general Clifford frames, physical descent), jamesyc's PR124 (birth-read
reuse) and PR143 (deadline reads); the paired-cube word is icekylinx's PR144 and eumemic's PR161.

Frames: alternating forward/backward passes choose, per operation, the lower bound (span of both roles'
previous frames and the node's value span) or the upper bound (intersection of both roles' next frames),
whichever lowers the local child cost; a move is taken only when lower <= upper.  Pairs: a maximum-weight
assignment of ungauged non-root donors to gauged recipients, with the donor's last operation before the
recipient's first and the donor's last frame inside the recipient gauge.

The search is discovery only.  Every result is accepted or rejected by PR161's checker, which with
replay=True also runs its exact numeric replay of the aliased signed word.
"""
import functools
import math
from collections import defaultdict
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
import paired_cube.frames as _FR
# basis() returns the unique reduced row-echelon form of a span, so memoizing on the input tuple is exact.
# Patched before any importer binds the name, so the gauge selector and the checker share the cache.
if not hasattr(_FR, '_basis_raw'):
    _FR._basis_raw = _FR.basis
    _basis_c = functools.lru_cache(maxsize=None)(_FR._basis_raw)
    _FR.basis = lambda rows: _basis_c(tuple(rows))
import paired_cube_physical as PP
from paired_cube.frames import basis, contained
perp = functools.lru_cache(maxsize=None)(lambda rows, h: _FR.perp(tuple(rows), h))


@functools.lru_cache(maxsize=None)
def _cap(A, B, h):
    return perp(basis(perp(A, h) + perp(B, h)), h)


def float_saving(res):
    """Float root a of sum_r n_r r (m/r)^a = W m for a checker result (discovery score, not a certificate)."""
    C = {int(k): n for k, n in res['child_histogram'].items()}; W = res['W_per_vertex']; m = res['m']
    gap = lambda a: math.fsum(n * r * math.exp(a * math.log(m / r)) for r, n in C.items()) - W * m
    lo, hi = 0.0, 1e-2
    for _ in range(70):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if gap(mid) < 0 else (lo, mid)
    return lo


def optimize(g,witness,word,record,passes=6,replay=True,log=lambda *a:None):
    """Return (float complex saving, checker result) for the generated frames and pairs."""
    h,v,R=g['h'],g['v'],record['R'];m=3*h
    full=basis(1<<i for i in range(h))
    args=[None]+[None if a is None else (a[0]+1,a[1]+1) for a in g['args']]
    inputs=g['inputs'];roots=[dict(r,node=r['node']+1) for r in g['roots']]
    ann=witness['annihilators'];ops=[tuple(o) for o in word['ops']]
    phase1=sorted(word['phase1']);pset=set(phase1);rest=[i for i in range(len(ops)) if i not in pset]
    position={i:k for k,i in enumerate(phase1+rest)}
    sources={int(x):s for x,s in word['sources'].items()}
    spans=[()]*len(args)
    for x in range(1,len(args)):spans[x]=(inputs[x-1],) if args[x] is None else basis(spans[args[x][0]]+spans[args[x][1]])
    base=[perp(tuple(ann[x]),h) for _,_,x in ops];frames=list(base)
    start=[()]*R
    for x,s in sources.items():start[s]=(inputs[x-1],)
    gauge={}
    for z in word['selected']:gauge[z['role']]=perp(tuple(z['annihilator']),h);start[z['role']]=gauge[z['role']]
    rootframe={}
    for r,s in zip(roots,word['rootroles']):
        rootframe[s]=spans[r['node']] if r['kind']=='center' else perp(basis(inputs[t] for t in r['targets']),h)
    role_ops=defaultdict(list)
    for i,(a,b,_) in enumerate(ops):role_ops[a].append(i);role_ops[b].append(i)
    idx={}
    for s,l in role_ops.items():
        for k,i in enumerate(l):idx[(s,i)]=k
    f=lambda t:t*math.log(m/t) if t>0 else 0.0
    def prevF(s,i):
        k=idx[(s,i)];return frames[role_ops[s][k-1]] if k else start[s]
    def nextF(s,i):
        k=idx[(s,i)];l=role_ops[s]
        if k+1<len(l):return frames[l[k+1]]
        return rootframe.get(s,full)
    cap=lambda A,B:_cap(A,B,h) if A<=B else _cap(B,A,h)
    def cost(i,F):
        a,b,_=ops[i];c=0.0
        for s in (a,b):c+=f(len(F)-len(prevF(s,i)))+f(len(nextF(s,i))-len(F))
        return c
    for p in range(passes):
        changes=0;gain=0.0
        order=range(len(ops)) if p%2==0 else reversed(range(len(ops)))
        for i in order:
            a,b,x=ops[i]
            lo=basis(list(prevF(a,i))+list(prevF(b,i))+list(spans[x]))
            up=cap(nextF(a,i),nextF(b,i))
            if not contained(lo,up):continue
            cur=frames[i];best=cur;bc=cost(i,cur)
            for F in (lo,up):
                if F!=cur:
                    c=cost(i,F)
                    if c<bc-1e-12:best,bc=F,c
            if best!=cur:gain+=cost(i,cur)-bc;frames[i]=best;changes+=1
        log('pass',p,'changes',changes,'gain %.2f'%gain)
        if not changes:break
    frames_in=[[i,list(F)] for i,F in enumerate(frames) if F!=base[i]]
    # pairs: donors ungauged non-root roles; recipients gauged; late deadline = recipient's first op
    first={s:l[0] for s,l in role_ops.items()};lastop={s:l[-1] for s,l in role_ops.items()}
    donors=[s for s in role_ops if s not in gauge and s not in rootframe]
    recips=[s for s in gauge if s in role_ops and first[s] not in pset]
    phi=lambda r:r*((m/r)**5.9e-4-1)/5.9e-4 if r else 0.0
    import numpy as np
    from scipy.optimize import linear_sum_assignment
    # Containment is tested once per distinct (donor end frame, gauge frame); edge weights depend only on dims,
    # and the timing mask is filled per block with numpy.  Same matrix as the per-edge loop.
    gk=defaultdict(list)
    for b in recips:gk[gauge[b]].append(b)
    dk=defaultdict(list)
    for a in donors:dk[frames[lastop[a]]].append(a)
    # E is inside G iff every row of E is orthogonal over F2 to every annihilator row of G: one parity matrix.
    Es=list(dk);Gs=list(gk);ann=[perp(G,h) for G in Gs]
    X=np.array([x for E in Es for x in E],dtype=np.int64);P=np.array([y for Y in ann for y in Y],dtype=np.int64)
    odd=(np.bitwise_count(X[:,None]&P[None,:])&1).astype(bool) if len(X) and len(P) else np.zeros((len(X),len(P)),bool)
    erow=np.repeat(np.arange(len(Es)),[len(E) for E in Es]);pcol=np.repeat(np.arange(len(Gs)),[len(Y) for Y in ann])
    bad=np.zeros((len(Es),len(P)),bool);np.logical_or.at(bad,erow,odd)
    badG=np.zeros((len(Es),len(Gs)),bool);np.logical_or.at(badG.T,pcol,bad.T)
    blocks=[]
    for i,j in zip(*np.nonzero(~badG)):
        E,G=Es[i],Gs[j];e=len(E)
        if len(G)>=e:blocks.append((dk[E],gk[G],3*phi(h-e)+phi(3*len(G))-3*phi(len(G)-e)))
    ds=sorted({a for as_,_,_ in blocks for a in as_});rs=sorted({b for _,bs,_ in blocks for b in bs})
    di={a:k for k,a in enumerate(ds)};ri={b:k for k,b in enumerate(rs)}
    A=np.zeros((len(ds),len(rs)));nedge=0
    for as_,bs,w in blocks:
        ia=np.array([di[a] for a in as_]);ib=np.array([ri[b] for b in bs])
        pa=np.array([position[lastop[a]] for a in as_]);pb=np.array([position[first[b]] for b in bs])
        mask=pa[:,None]<pb[None,:];nedge+=int(mask.sum())
        sub=A[np.ix_(ia,ib)];A[np.ix_(ia,ib)]=np.where(mask,np.maximum(sub,w),sub)
    log('edges',nedge,'donors',len(donors),'recips',len(recips))
    r_,c_=linear_sum_assignment(A,maximize=True)
    pairs=[(ds[i],rs[j]) for i,j in zip(r_,c_) if A[i,j]>0]
    pairs_in=[[a,b,first[b]] for a,b in pairs]
    log('pairs',len(pairs))
    if not replay:
        _orig=PP.scalar_replay;PP.scalar_replay=lambda *a,**k:None
        try:res=PP.physical(g,witness,word,record,frames_in,pairs_in)
        finally:PP.scalar_replay=_orig
    else:res=PP.physical(g,witness,word,record,frames_in,pairs_in)
    log('CHECKER PASS',res['checks'],'changed frames',res['changed_operation_frames'],'pairs',res['pairs'],'W',res['W_per_vertex'])
    lo_=float_saving(res)
    res['generated']=dict(frames=frames_in,pairs=pairs_in)
    return lo_,res
