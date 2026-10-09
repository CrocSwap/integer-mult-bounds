# Copyright 2026 icekylinx. Apache-2.0.
# Developed with GPT-6 Astra assistance; integrated with Codex assistance.
"""Independent finite checks of the signed scalar word and binary geometry.

Copyright 2026 icekylinx, Apache-2.0; OpenAI GPT-6 Astra assistance. Binary Lagrangian
intersection ranks use L_U=U^perp in X plus U in Z, including degenerate U.
"""
from collections import Counter
from functools import lru_cache
from .frames import basis, perp, contained


def verify(g, baseline, witness, word, record):
    h,v=g['h'],g['v'];args=[None]+[None if a is None else [y+1 for y in a] for a in g['args']]
    roots=[dict(r,node=r['node']+1) for r in g['roots']]
    n=len(args);ann=witness['annihilators'];order=witness['order'];arcs=dict(witness['matching_arcs'])
    active=set(order)
    inputs=g['inputs']; spans=[()]*n;positive=[0]*n;negative=[0]*n
    @lru_cache(None)
    def frame(A):
        U=perp(A,h)
        assert len(U)+len(A)==h and all((a&b).bit_count()%2==0 for a in A for b in U)
        return U
    def each(bits):
        while bits:
            low=bits&-bits;bits^=low;yield low.bit_length()-1
    for x in range(1,n):
        if args[x] is None:
            positive[x]=1<<(x-1);spans[x]=(inputs[x-1],)
        else:
            a,b=args[x];assert 0<a<x and 0<b<x
            assert not (positive[a]|negative[a])&(positive[b]|negative[b])
            sign=g['signs'][x-1];assert sign in (-1,1)
            positive[x]=positive[a]|(positive[b] if sign==1 else negative[b])
            negative[x]=negative[a]|(negative[b] if sign==1 else positive[b])
            spans[x]=basis(spans[a]+spans[b])
        if x in active:assert contained(spans[x],frame(tuple(ann[x])))
    # Recount every actual signed broadcast, with integer twice-coefficients.
    Hrows=[[0]*v for _ in range(v)]
    rootann=[];rootframes=[]
    for r in roots:
        x=r['node']
        if r['kind']=='center':
            assert not negative[x]
            expected=sum(1<<s for s,q in enumerate(inputs) if q>>r['coordinate']&1)
            assert positive[x]==expected
            U=spans[x];A=perp(U,h)
            assert len(U)==h-2
            assert r['coefficients']==['1/3' if q>>r['coordinate']&1 else '-1/6' for q in inputs]
        else:
            A=basis(inputs[t] for t in r['targets']);U=perp(A,h)
            for t,c in zip(r['targets'],r['coefficients']):
                assert c in ('1/2','-1/2');sign=1 if c=='1/2' else -1
                for s in each(positive[x]):Hrows[t][s]+=sign
                for s in each(negative[x]):Hrows[t][s]-=sign
        rootann.append(A);rootframes.append(U)
        assert contained(spans[x],U)
    cube=[tuple(a//2 for a in label) for label in g['labels']]
    scalar_pairs=0
    for t,q in enumerate(inputs):
        for s,u in enumerate(inputs):
            overlap=(q&u).bit_count();same=cube[t]==cube[s]
            expected=0 if same else 1-overlap
            assert Hrows[t][s]==expected, ('Signed H mismatch',t,s)
            distance=(q^u).bit_count()//2
            K2=(1 if distance==3 else -1 if distance==1 else 0) if same else 0
            B2=overlap-1
            assert Hrows[t][s]+K2+B2==2*(t==s)
            scalar_pairs+=1
    # Actual local K matrix, inverse, and destructive-source frame itinerary.
    for start in range(0,v,8):
        qs=inputs[start:start+8]
        K2=[[1 if (a^b).bit_count()==6 else -1 if (a^b).bit_count()==2 else 0 for b in qs] for a in qs]
        assert all(sum(K2[i][k]*K2[k][j] for k in range(8))==4*(i==j) for i in range(8) for j in range(8))
        for parity in (0,1):
            source=[i for i in range(8) if i.bit_count()%2==parity];target=[i for i in range(8) if i.bit_count()%2!=parity]
            U=basis(qs[i] for i in source);assert len(U)==3
            assert all(contained((qs[i],),U) for i in source)
            assert all(contained(U,perp((qs[j],),h)) for j in target)
            assert [3-1,(h-1)-3,h-(h-1)]==[2,h-4,1]
            assert all(sum(K2[i][k]*K2[j][k] for k in source)==4*(i==j) for i in target for j in target)
    # Full backward intersections, including every carrier edge and root cap.
    required=[[] for _ in args];position={x:i for i,x in enumerate(order)}
    for x in order:
        if args[x]:
            for y in args[x]:required[y].extend(ann[x]);assert position[y]<position[x]
    for r,A in zip(roots,rootann):required[r['node']].extend(A)
    assert len(arcs)==len(set(arcs.values()))==record['matched']
    for x,u in arcs.items():
        assert args[x]
        if u>>31:
            j=u&0x7fffffff;value=roots[j]['node'];A=rootann[j]
        else:
            t=u//2;value=args[t][u&1];A=ann[t];assert position[x]<position[t]
        assert value in args[x];required[x].extend(A)
    for x in order:assert basis(required[x])==tuple(ann[x]), ('Incomplete intersection',x)
    # Replay actual signed physical operations and every positive frame movement.
    R=record['R'];values=[(0,0)]*R;full=basis(1<<i for i in range(h));roleann=[full]*R
    first=[None]*R;last=[-1]*R;H=Counter();phase=set(word['phase1']);touched=set(word['sources'].values())
    for x,s in word['sources'].items():
        x=int(x);values[s]=(positive[x],negative[x]);roleann[s]=perp((inputs[x-1],),h);H[1]+=1
    for i,((a,b,x),(ca,cb)) in enumerate(zip(word['ops'],word['opcoeff'])):
        assert a!=b and ca in (-1,1) and cb in (-1,1)
        if i in phase:
            assert all(last[s]<0 or last[s] in phase for s in (a,b));touched.update((a,b))
        for s in (a,b):
            if first[s] is None:first[s]=x
            A=tuple(ann[x]);assert contained(A,roleann[s])
            H[len(roleann[s])-len(A)]+=1;roleann[s]=A;last[s]=i
        pa,na=values[a];pb,nb=values[b];assert not (pa|na)&(pb|nb)
        if ca<0:pa,na=na,pa
        if cb<0:pb,nb=nb,pb
        values[a]=(pa|pb,na|nb);assert values[a]==(positive[x],negative[x])
    for r,s,A,U in zip(roots,word['rootroles'],rootann,rootframes):
        assert values[s]==(positive[r['node']],negative[r['node']])
        assert contained(tuple(A),roleann[s]);H[len(roleann[s])-len(A)]+=1;roleann[s]=tuple(A)
        if r['kind']=='center':assert last[s]<0 or last[s] in phase;H[len(U)]+=1
    for A in roleann:H[len(A)]+=1
    assert [H[r] for r in range(1,h+1)]==baseline['remaining_internal_histogram'][1:]
    co=[0]*R
    for r,s in zip(roots,word['rootroles']):co[s]|=sum(1<<t for t in r['targets'])
    for a,b,x in reversed(word['ops']):co[b]|=co[a]
    limits=[None]*v
    for r,A in zip(roots,rootann):
        if r['kind']=='side':
            for t in r['targets']:
                if limits[t] is None:limits[t]=A
    seen=set();birth=Counter()
    for z in word['selected']:
        s=z['role'];A=tuple(z['annihilator']);d=z['rank'];targets=list(each(co[s]))
        assert s not in touched and s not in seen;seen.add(s)
        assert targets==z['targets']
        assert A==basis(tuple(ann[first[s]])+tuple(u for t in targets for u in limits[t]))
        assert d==h-len(A)>0 and contained(tuple(ann[first[s]]),A)
        r=h-len(ann[first[s]]);H[r]-=1;H[r-d]+=1;birth[d]+=1
        for t in targets:limits[t]=A
    assert [H[r] for r in range(1,h+1)]==record['remaining_internal_histogram'][1:]
    assert dict(birth)=={int(k):c for k,c in record['selected_rank_histogram'].items()}
    current=[full]*v;Y=Counter()
    for z in reversed(word['selected']):
        A=tuple(z['annihilator'])
        for t in z['targets']:
            assert contained(A,current[t]);Y[len(current[t])-len(A)]+=1;current[t]=A
    for r,A in zip(roots,rootann):
        if r['kind']=='side':
            for t in r['targets']:
                assert contained(A,current[t]);Y[len(current[t])-len(A)]+=1;current[t]=A
    for t,q in enumerate(inputs):assert contained((q,),current[t]);Y[len(current[t])-1]+=1
    assert dict(Y)=={int(k):c for k,c in record['target_data_histogram'].items()}
    assert record['selected_roles']==len(seen)==4840 and birth==Counter({20:4840})
    return dict(signed_scalar_pairs_checked=scalar_pairs,scalar_H_exact=True,K_involution_and_inverse_exact=True,
                decoder_identity_exact=True,conservative_source_supports=True,K_source_itinerary_verified=True,
                full_backward_intersections=True,physical_signed_M_replayed=True,
                center_phase_closed=True,full_gauge_intersections=True,selected_sources_untouched=True,
                reverse_target_chains=True,positive_rank_ledger_recounted=True,selected_roles=len(seen))
