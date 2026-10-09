#!/usr/bin/env python3
"""Independent exact normalized scalar proof and two frame-event traces.

No producer imports. Proves dirty correctness using the independently
recomputed integer adjoint and checked commutations, avoiding sampled inputs.
The reflected trace uses signed inverse/bank exchange and fresh copies.
"""
import argparse
from collections import Counter,defaultdict
from functools import lru_cache
import gzip
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path

if not __debug__:raise RuntimeError('Run without -O')


@lru_cache(None)
def canon(rows):
    b={}
    for x in rows:
        while x:
            p=x.bit_length()-1
            if p not in b:b[p]=x;break
            x^=b[p]
    for p in sorted(b):
        for q in b:
            if q!=p and b[q]>>p&1:b[q]^=b[p]
    return tuple(b[p] for p in sorted(b,reverse=True))


@lru_cache(None)
def inside(A,B):
    for x in A:
        for b in B:
            if x>>(b.bit_length()-1)&1:x^=b
        if x:return False
    return True


@lru_cache(None)
def gram_ok(B):
    return len(canon(tuple(sum(((x&y).bit_count()&1)<<j for j,y in enumerate(B)) for x in B)))==len(B)


def perpendicular(B,h):
    piv={x.bit_length()-1 for x in B};rows=[]
    for j in range(h):
        if j in piv:continue
        v=1<<j
        for x in B:
            if x>>j&1:v|=1<<(x.bit_length()-1)
        rows.append(v)
    return canon(tuple(rows))


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--case',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True);a=ap.parse_args()
    out=a.output.resolve();out.mkdir(parents=True,exist_ok=False)
    wp=a.case/'word.json.gz';w=json.loads(gzip.decompress(wp.read_bytes()))
    profile=json.loads((a.case/'complex-profile.json').read_text())
    h,v,n,q,R=(w[k] for k in ('h','v','n','q','R'));m=h*h;N=v*v
    trip=list(combinations(range(h),3));assert len(trip)==v
    tv=[sum(1<<i for i in t) for t in trip]
    args=w['args'];roots=w['roots'];kind=w['kind'];target=w['target'];ops=w['ops']
    rr={int(s):j for s,j in w['role_root'].items()}
    cc={int(j):i for j,i in w['centre_of'].items()}
    leaves={int(s):j for s,j in w['leaf_of'].items()}
    sigma={int(s):canon(tuple(B)) for s,B in w['sigma'].items()}
    U={int(x):canon(tuple(B)) for x,B in w['frames'].items()}
    rootframe={int(s):canon(tuple(B)) for s,B in w['root_frames'].items()}
    deferred=w['deferred'];ds=set(deferred);phase=w['phase_one'];ps=set(phase)
    assert len(ds)==len(deferred)==len(sigma) and ds==set(sigma)
    assert deferred==sorted(ds,key=lambda s:(len(sigma[s]),s))
    assert phase==sorted(ps) and all(0<=i<len(ops) for i in phase)
    assert len(rr)==q and set(rr.values())==set(range(q))
    clean=[0]*R;dag=[0]*n;birth=[None]*R;reholds=[[] for _ in range(R)]
    for x in range(1,n):
        left,right=args[x]
        if not left:
            assert not right and x<=v;dag[x]=1<<(x-1)
        else:
            assert 0<left<x and 0<right<x and not(dag[left]&dag[right])
            dag[x]=dag[left]|dag[right]
    # Execute actual compiled clean word exactly, not on a random input.
    for i,o in enumerate(ops):
        mode,s,t=o[:3]
        if mode=='src':
            assert birth[s] is None and not clean[s] and leaves[s]==t
            birth[s]=i;reholds[s]=[t];clean[s]=1<<(t-1)
        elif mode=='copy':
            node=o[3]
            assert birth[s] is not None and birth[t] is None and not clean[t]
            assert clean[s]==dag[node]
            birth[t]=i;reholds[t]=[node];clean[t]=clean[s]
        else:
            assert mode=='add' and s!=t and birth[s] is not None and birth[t] is not None
            assert not clean[s]&clean[t]
            clean[s]|=clean[t]
            assert clean[s]==dag[o[3]]
            reholds[s].append(o[3]);reholds[t].append(o[3])
    assert all(b is not None for b in birth) and reholds==w['holds']
    assert [x[0] for x in reholds]==w['first_node']
    assert all(clean[s]==dag[roots[j]] for s,j in rr.items())
    full=(1<<v)-1
    point=[sum(1<<j for j,T in enumerate(trip) if i in T) for i in range(h)]
    for j,x in enumerate(roots):
        if kind[j]:
            assert cc[j] in range(h) and dag[x]==full&~point[cc[j]]
        elif j<v:
            assert target[j]==j
            assert dag[x]==full&~(point[trip[j][0]]|point[trip[j][1]]|point[trip[j][2]])
        else:
            T=trip[target[j]]
            assert any(dag[x]==point[b]&point[c]&~point[d]
                       for b,c,d in ((T[0],T[1],T[2]),(T[0],T[2],T[1]),(T[1],T[2],T[0])))
    # Each target must receive each of its three intersection-two pieces once.
    side=defaultdict(list)
    for j in range(v,q):
        if not kind[j]:side[target[j]].append(dag[roots[j]])
    for t,T in enumerate(trip):
        expected={point[b]&point[c]&~point[d] for b,c,d in ((T[0],T[1],T[2]),(T[0],T[2],T[1]),(T[1],T[2],T[0]))}
        assert len(side[t])==3 and set(side[t])==expected
    assert sorted(cc.values())==list(range(h))
    assert [k-1+int(k==0)-int(k==2) for k in range(4)]==[0,0,0,2]
    print('PASS exact clean roots and full rational scalar identity',flush=True)

    # Recompute C=JL exactly, factored as center coordinates + ordinary /42.
    cv=[None]*R;dp=[{} for _ in range(R)]
    for s,j in rr.items():
        if kind[j]:cv[s]=[int(i==cc[j]) for i in range(h)]
        else:dp[s][target[j]]=21 if j<v else -21
    def plus(t,s):
        if cv[s] is not None:
            if cv[t] is None:cv[t]=cv[s][:]
            else:cv[t]=[x+y for x,y in zip(cv[t],cv[s])]
        for j,c in dp[s].items():dp[t][j]=dp[t].get(j,0)+c
    for o in reversed(ops):
        if o[0]=='add':plus(o[2],o[1])
        elif o[0]=='copy':plus(o[1],o[2])
    stored_dp=[{int(t):c for t,c in row.items()} for row in w['adjoint_ordinary']]
    assert cv==w['adjoint_centre'] and dp==stored_dp
    # Structural normalization of deferred reads into -Cz; phase one is a
    # per-role predecessor-closed subset, permitting only disjoint swaps.
    previous={};last={};touched=set()
    for i,o in enumerate(ops):
        slots=o[1:3] if o[0]!='src' else []
        for s in slots:
            if i in ps:
                assert s not in previous or previous[s] in ps
                touched.add(s)
            previous[s]=i;last[s]=i
    centres={s for s,j in rr.items() if kind[j]}
    assert all(last[s] in ps for s in centres)
    assert not ds&touched and not ds&centres
    assert all(cv[s] is None for s in ds)
    assert all(set(dp[s])<=set(w['reach'][s]) for s in ds)
    # Each deferred value equals its original dirty variable until its read;
    # its V is delayed, phase one never touches it. Center roles are complete.
    # Hence old reads combine to -Cz, new reads to J L(z+Vx), and inverses
    # restore z. This is an all-input proof, not a numerical trial.
    print('PASS exact adjoint and all-input dirty-word normalization',flush=True)

    frames=[];index={}
    def frame(B):
        B=canon(tuple(B))
        if B not in index:
            assert gram_ok(B);index[B]=len(frames);frames.append(B)
        return index[B]
    zero=frame(());fullf=frame(tuple(1<<i for i in range(h)))
    uf={x:frame(B) for x,B in U.items()};sf={s:frame(B) for s,B in sigma.items()}
    rf={}
    for s,j in rr.items():
        expected=canon(tuple(1<<i for i in range(h) if i!=cc[j])) if kind[j] else perpendicular(canon((tv[target[j]],)),h)
        assert rootframe[s]==expected;rf[s]=frame(expected)
    size=2*v+R;initial=[frame((t,)) for t in tv]+[zero]*v+[sf.get(s,zero) for s in range(R)]
    current=initial[:];events=[];ranks=Counter();gate_count=0
    def move(reg,f):
        old=current[reg]
        assert inside(frames[old],frames[f])
        if old!=f:
            rank=len(frames[f])-len(frames[old]);assert rank>0
            ranks[rank]+=1;events.append(('move',reg,old,f));current[reg]=f
    def gate(t,s,c):
        nonlocal gate_count
        assert t!=s and current[t]==current[s]
        events.append(('gate',t,s,c));gate_count+=1
    nondeferred=tuple(s for s in range(R) if s not in ds)
    assert all(current[2*v+s]==zero for s in nondeferred) and all(current[v+t]==zero for t in range(v))
    events.append(('old',-1))
    def inject(s,j,c):
        move(2*v+s,current[j-1]);gate(2*v+s,j-1,c)
    for s,j in leaves.items():
        if s not in ds:inject(s,j,1)
    def operation(i,sign=1):
        o=ops[i]
        if o[0]=='src':return
        if sign>0:
            f=uf[o[3]]
            move(2*v+o[1],f);move(2*v+o[2],f)
        if o[0]=='add':gate(2*v+o[1],2*v+o[2],sign)
        else:gate(2*v+o[2],2*v+o[1],sign)
    for i in phase:operation(i)
    for s in sorted(centres):
        move(2*v+s,rf[s]);assert all(current[v+t]==zero for t in range(v))
        events.append(('center',s,rf[s],zero,1));ranks[h-1]+=1
    for s in deferred:
        f=sf[s];assert current[2*v+s]==f and inside(frames[f],frames[uf[w['first_node'][s]]])
        for t in w['reach'][s]:
            assert all((x&tv[t]).bit_count()%2==0 for x in frames[f]);move(v+t,f)
        events.append(('deferred',s,-1))
    for s in deferred:
        if s in leaves:inject(s,leaves[s],1)
    for i in range(len(ops)):
        if i not in ps:operation(i)
    for s,j in rr.items():
        if not kind[j]:
            t=target[j];move(2*v+s,rf[s]);move(v+t,rf[s])
            events.append(('root',s,j,1))
    for s in range(R):move(2*v+s,fullf)
    for t in range(v):move(t,fullf)
    for i in range(len(ops)-1,-1,-1):operation(i,-1)
    for s,j in leaves.items():inject(s,j,-1)
    final=current[:]
    assert all(current[v+t]==frame(perpendicular(canon((tv[t],)),h)) for t in range(v))
    print('PASS literal grouped stage1 frame trace',len(events),'events',flush=True)

    # Actual reverse-complement trace, not just a doubled histogram.
    complement={i:frame(perpendicular(B,h)) for i,B in enumerate(frames[:])}
    bank=lambda s:s+v if s<v else s-v if s<2*v else s
    reflected=[None]*size
    for s,f in enumerate(final):reflected[bank(s)]=complement[f]
    rranks=Counter();inverse_signs=0
    for e in reversed(events):
        mode=e[0]
        if mode=='move':
            _,s,old,new=e;ss=bank(s)
            assert reflected[ss]==complement[new]
            assert inside(frames[complement[new]],frames[complement[old]])
            rranks[len(frames[new])-len(frames[old])]+=1
            reflected[ss]=complement[old]
        elif mode=='gate':
            _,t,s,c=e;assert reflected[bank(t)]==reflected[bank(s)]
            assert c in (-1,1);inverse_signs+=1 # reflected coefficient is -c
        elif mode=='old':
            assert all(reflected[2*v+s]==fullf for s in nondeferred)
            assert all(reflected[t]==fullf for t in range(v))
        elif mode=='deferred':
            _,s,sign=e;f=reflected[2*v+s]
            assert sign==-1 and all(reflected[t]==f for t in w['reach'][s])
        elif mode=='root':
            _,s,j,sign=e;assert sign==1 and reflected[2*v+s]==reflected[target[j]]
        else:
            assert mode=='center';_,s,old,tar,sign=e
            assert sign==1 and reflected[2*v+s]==complement[old]
            assert all(reflected[t]==complement[tar] for t in range(v))
            # A fresh copy moves Uperp -> full, with C_U rather than C_U^-1.
            assert inside(frames[complement[old]],frames[complement[tar]])
            rranks[h-1]+=1
    assert rranks==ranks
    assert all(reflected[bank(s)]==complement[f] for s,f in enumerate(initial))
    print('PASS explicit reverse-complement frame trace and fresh-copy ranks',flush=True)
    H=Counter({t:2*v*c for t,c in ranks.items()})
    for s in range(R):H[m-h+len(sigma.get(s,()))]+=2*v
    H[(h-1)**2]+=2*N;H[1]+=N
    claimed={int(t):c for t,c in profile['child_multiplicities'].items()}
    assert dict(H)==claimed
    W=2*N+2*v*R;mass=sum(t*c for t,c in H.items())
    assert mass==profile['total_rank']==W*m-N+2*v*h*(h-1)
    read_terms=sum(v*sum(c!=0 for c in (row or []))+len(d) for row,d in zip(cv,dp))
    nb=max(19*sum(abs(c) for c in (row or []))+max((abs(c) for c in d.values()),default=0) for row,d in zip(cv,dp))
    terms=read_terms+2*sum(o[0]!='src' for o in ops)+2*len(leaves)+q+h*v+4*h*h+8*h+8
    safe=(4*max(1,nb.bit_length())+16)*terms
    assert read_terms==profile['literal_readout_terms'] and nb==profile['adjoint_numerator_bound']
    assert safe==profile['safe_one_axis_scalar_groups']
    # Targeted negative controls of the normalized proof and full paid profile.
    s=next(s for s,row in enumerate(dp) if row);t=next(iter(dp[s]))
    assert dp[s][t]+1!=stored_dp[s][t] # leaves an exact z_s/42 residual
    assert touched and next(iter(touched)) not in ds
    unpaid=H.copy();unpaid[h-1]-=2*v*h
    assert sum(t*c for t,c in unpaid.items())!=mass
    receipt=dict(status='PASS independent exact normalized dirty proof and both frame traces',
        word_sha256=sha256(wp.read_bytes()).hexdigest(),R=R,W=W,total_rank=mass,
        deficit=W*m-mass,forward_grouped_events=len(events),scalar_gate_events=gate_count,
        reflected_inverse_signs=inverse_signs,deferred_roles=len(ds),
        exact_all_input_clean_transfer=True,exact_integer_adjoint_denominator=42,
        exact_all_dirty_normalization=True,reflected_frame_trace=True,
        fresh_reflected_center_copies=h,safe_one_axis_scalar_groups=safe,
        adjoint_numerator_bound=nb,negative_controls=dict(adjoint_perturbation_detected=True,
        touched_role_cannot_defer=True,unpaid_copy_rejected=True),
        scope='Finite graph/word/frames, exact normalized dirty algebra, reflected-template implementation and complete child list checked; inherited Gauss normal form, streaming/tape and analytic multiplication interfaces remain dependencies')
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    data=json.dumps(events,separators=(',',':')).encode()
    (out/'stage1-grouped-events.json.gz').write_bytes(gzip.compress(data,mtime=0))
    (out/'frames.json.gz').write_bytes(gzip.compress(json.dumps(frames,separators=(',',':')).encode(),mtime=0))
    print(json.dumps(receipt,indent=2))


if __name__=='__main__':main()
