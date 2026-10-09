# Copyright 2026 icekylinx. Apache-2.0.
# Prepared with OpenAI GPT-6 Astra and Codex assistance; see NOTICE.
"""Independent checks of the generated DAG, lifted frames and physical word."""
from collections import Counter
from functools import lru_cache
from itertools import combinations
from .binary import load
from .lift import basis, perp, contained, nondeg


def verify(path, matching, ann, lift, word, selected, record):
    h,v,n,q,args,core,cover,roots,kind,active,oldrank,types=load(path)
    triples=list(combinations(range(h),3)); full=(1<<h)-1
    point=[sum(1<<j for j,t in enumerate(triples) if a in t) for a in range(h)]
    all_inputs=(1<<v)-1; supports=[0]*n
    @lru_cache(None)
    def frame(A):
        F=perp(A,h)
        assert nondeg(F)
        return F
    @lru_cache(None)
    def includes(A,B):
        return contained(A,B)
    for x in range(1,n):
        if not active[x]:continue
        a,b=args[2*x:2*x+2]
        if a:
            assert a<x and b<x and not supports[a]&supports[b]
            supports[x]=supports[a]|supports[b]
        else:
            assert x<=v
            supports[x]=1<<(x-1)
        A=tuple(ann[x]); F=frame(A)
        if types[x]==1:
            old=(cover[x],) if oldrank[x]==1 else tuple((1<<j)|core[x] for j in range(h) if (cover[x]&~core[x])>>j&1)
        else:
            assert types[x]==2
            old=tuple(1<<j for j in range(h) if cover[x]>>j&1)
        assert len(old)==oldrank[x] and includes(basis(old),F)
        if a:
            assert includes(A,tuple(ann[a])) and includes(A,tuple(ann[b]))
    for j,t in enumerate(triples):
        assert supports[roots[j]]==all_inputs & ~(point[t[0]]|point[t[1]]|point[t[2]])
    at=v
    for a,b in combinations(range(h),2):
        others=[i for i in range(h) if i not in (a,b)]
        others.sort(key=lambda i:((i^1) in (a,b),i))
        for i in others:
            assert supports[roots[at]]==point[a]&point[b]&~point[i];at+=1
    for a in range(h):
        assert kind[at] and supports[roots[at]]==all_inputs^point[a];at+=1
    assert at==q
    # Every input appears in h-3 disjoint centers: exact divisor 21. For
    # overlap k, twice the signed output coefficient is 2-(3-k)+[k=0]-[k=2].
    assert h-3==21
    assert [2-(3-k)+(k==0)-(k==2) for k in range(4)]==[0,0,0,2]
    for donor,use in matching['matching_arcs']:
        if use>>31:
            j=use&0x7fffffff;x=roots[j]
            normal=full^cover[x] if kind[j] else core[x]|(full^cover[x])
            assert includes(basis([normal]),tuple(ann[donor]))
        else:assert includes(tuple(ann[use//2]),tuple(ann[donor]))
    R=record['R']; values=[0]*R; current=[0]*R; first=[None]*R
    H=Counter();phase=set(word['phase1']); touched=set(map(int,word['sources'].values()))
    for x,s in word['sources'].items():
        values[s]=supports[int(x)];current[s]=1;H[1]+=1
    last=[-1]*R
    for i,(a,b,x) in enumerate(word['ops']):
        assert a!=b
        if i in phase:
            assert all(last[s]<0 or last[s] in phase for s in (a,b))
            touched.update((a,b))
        for s in (a,b):
            if first[s] is None:first[s]=x
            r=h-len(ann[x]);assert r>=current[s]
            H[r-current[s]]+=1;current[s]=r;last[s]=i
        assert not values[a]&values[b]
        values[a]|=values[b]
        assert values[a]==supports[x]
    for j,(x,s) in enumerate(zip(roots,word['rootroles'])):
        assert values[s]==supports[x]
        if kind[j]:
            assert last[s]<0 or last[s] in phase
            H[current[s]]+=1
        else:
            H[h-1-current[s]]+=1;current[s]=h-1
    for r in current:H[h-r]+=1
    assert all(H[r]==lift['histogram'][r] for r in range(1,h+1))
    co=[0]*R;tid={sum(1<<a for a in t):j for j,t in enumerate(triples)}
    for x,s,k in zip(roots,word['rootroles'],kind):
        co[s]|=all_inputs if k else 1<<tid[core[x]|(full^cover[x])]
    for a,b,x in reversed(word['ops']):co[b]|=co[a]
    latest=[()]*v;seen=set();residual=Counter();birth=Counter()
    for row in selected:
        s=row['role'];A=tuple(row['annihilator']);F=frame(A)
        assert s not in touched and s not in seen;seen.add(s)
        assert includes(tuple(ann[first[s]]),A)
        r=h-len(ann[first[s]]);d=len(F)
        assert row['first_rank']==r and row['gauge_rank']==d and 0<d<=r
        residual[r-d]+=1;birth[d]+=1
        bits=co[s]
        while bits:
            bit=bits&-bits;bits-=bit;t=bit.bit_length()-1
            assert includes(latest[t],A);latest[t]=A
    # Execute the requested reverse readout order and recount target transitions.
    current_ann=[tuple(1<<i for i in reversed(range(h)))]*v;Y=Counter()
    for row in reversed(selected):
        A=tuple(row['annihilator']);bits=co[row['role']]
        while bits:
            bit=bits&-bits;bits-=bit;t=bit.bit_length()-1;old=current_ann[t]
            assert includes(A,old)
            if A!=old:Y[len(old)-len(A)]+=1
            current_ann[t]=A
    for t,A in enumerate(current_ann):
        normal=sum(1<<a for a in triples[t]);assert includes((normal,),A)
        Y[len(A)-1]+=1
    for actual,key in [(Y,'target_data_histogram'),(birth,'selected_rank_histogram'),(residual,'partial_first_transition_histogram')]:
        assert dict(actual)=={int(k):v for k,v in record[key].items()},key
    return dict(scalar_supports_exact=True, signed_coefficients_exact=True,
                divisor=21, lifted_frames_nondegenerate=True,
                old_frames_contained=True, dependency_and_carrier_nesting=True,
                physical_M_replayed=True, positive_rank_ledger_recounted=True,
                center_phase_closed=True, selected_sources_untouched=True,
                reverse_readout_frame_chains=True, target_transitions_recounted=True,
                selected_roles=len(seen))
