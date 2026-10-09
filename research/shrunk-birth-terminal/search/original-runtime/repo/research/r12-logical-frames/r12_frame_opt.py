"""R12 logical-frame endpoint descent, Chafik Boukhalfa with OpenAI Codex.

Adapts Joel Pulikkan's PR125 logical-frame shrinking to complete degenerate
lower spans and alternate lower/upper endpoint moves. The radical-dual
completion principle is retained from icekylinx PR115 and DanieleCorso PR126;
PR125/eumemic F2 operations and original notices are retained. Apache-2.0.
Search scores select candidates only; physical words and exact moments remain
separate verification obligations. No global optimality claim.
"""
from collections import defaultdict
from functools import lru_cache
import math, os, time


def optimize(U, order, args, succ, holds, role_root, envelope, h, algebra):
    start=time.monotonic()
    basis=algebra['sat_basis']; cap=algebra['sat_cap']; nondeg=algebra['sat_nondeg']
    inside=algebra['sat_contained']; nonsingular=algebra['sat_nonsingular_part']
    kernel=algebra['kernel']; dot=algebra['sat_dot']
    frames={x:basis(B) for x,B in U.items()}; original=dict(frames)
    rounds=int(os.environ.get('R12_FRAME_ROUNDS','1'))
    mode=os.environ.get('R12_FRAME_MODE','radical_min')
    assert mode in ('radical_min','both_endpoints','minimal_repeat') and 1<=rounds<=12
    pred=defaultdict(list);occ=defaultdict(list)
    for x,ts in succ.items():
        for t in ts:pred[t].append(x)
    for s,hs in enumerate(holds):
        for i,x in enumerate(hs):occ[x].append((s,i))
    @lru_cache(None)
    def perp(A):return basis(kernel(A,h))
    @lru_cache(None)
    def minimum(L,C):
        assert inside(L,C) and nondeg(C)
        radical=cap(L,perp(L)); expected=len(L)+len(radical)
        while not nondeg(L):
            radical=cap(L,perp(L));r=radical[0]
            y=next(v for v in C if dot(v,r))
            L=basis(L+(y,))
        assert len(L)==expected and inside(L,C)
        return L
    weight=[0]+[round(d*math.log(d)*10**9) for d in range(1,h+1)]
    def score(x,d):
        total=0
        for s,i in occ[x]:
            hs=holds[s];a=len(frames[hs[i-1]]) if i else 0
            b=len(frames[hs[i+1]]) if i+1<len(hs) else h-1 if s in role_root else h
            assert a<=d<=b,(x,a,d,b)
            total+=weight[d-a]+weight[b-d]
        return total
    stats=[]
    for cycle in range(rounds):
        counts=dict(pass_index=cycle,moves=0,shrink=0,grow=0,radical_completions=0,integer_score_gain=0)
        walk=order if cycle%2==0 else list(reversed(order))
        for x in walk:
            if not args[x][0]:continue
            old=frames[x];lower=basis(tuple(envelope(x))+tuple(b for p in pred[x] for b in frames[p]))
            assert inside(lower,old)
            if mode=='minimal_repeat' and not nondeg(lower):small=old
            else:small=minimum(lower,old)
            candidates=[old,small]
            if mode=='both_endpoints':
                upper=old
                # Logical frame must remain within all successor frames and
                # its original lifted kernel. Original frame is a safe cap.
                # Growth is limited to that immutable cap, so root obligations
                # remain discharged even for nodes without a successor.
                upper=original[x]
                for t in succ[x]:upper=cap(upper,frames[t])
                extra=cap(upper,perp(old))
                large=basis(old+nonsingular(extra))
                assert nondeg(large) and inside(large,upper)
                candidates.append(large)
            best=max(candidates,key=lambda B:score(x,len(B)))
            gain=score(x,len(best))-score(x,len(old))
            if gain>0:
                assert nondeg(best) and inside(lower,best)
                assert inside(best,original[x]) and all(inside(best,frames[t]) for t in succ[x])
                frames[x]=best;counts['moves']+=1;counts['integer_score_gain']+=gain
                counts['shrink' if len(best)<len(old) else 'grow']+=1
                counts['radical_completions']+=int(best==small and not nondeg(lower))
        stats.append(counts);print('R12 frame optimization',counts,flush=True)
        if not counts['moves']:break
    for x,B in frames.items():
        assert nondeg(B) and inside(B,original[x]) and inside(basis(envelope(x)),B)
        assert all(inside(B,frames[t]) for t in succ[x])
    receipt=dict(mode=mode,requested_rounds=rounds,passes=stats,changed_frames=sum(frames[x]!=original[x] for x in frames),shrunk_frames=sum(len(frames[x])<len(original[x]) for x in frames),scope='Heuristic integer rank-moment score; fresh complete physical word and exact arithmetic remain required.')
    return {x:list(B) for x,B in frames.items()},{x:len(B) for x,B in frames.items()},receipt
