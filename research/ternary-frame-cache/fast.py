"""Opt-in adaptation of the retained historical ternary rational-frame check.

The physical schedule and every require() are copied from the pinned
scripts/experiments/ternary_side.py by Douglas R. Colkitt. Changes: memoize
projection within this call; reuse exact ordered frame-pair arithmetic; expose
an optional observer and cache counters. No source or evidence is rewritten.
Hanson Sun, with substantial OpenAI Codex assistance. Apache-2.0.
"""
from functools import lru_cache
from experiments.ternary_side import small_program, Q, comb, require
from frame_cache import FrameCache


def verify_invocation_frames(result, *, observe=None, statistics=None):
    """Every physical rational edge of both signed invocation directions."""
    from audit_joint_frames import eye,zero,matrix,row_basis,product,inverse,sub,rank
    cache = FrameCache(rank, sub)
    code=small_program(result);g=result['_graph'];n=result['n'];h=result['h']
    S=code['roles'];r=comb(h,2);W=2*n+S+r
    H=matrix([[Q(int(i==j))-Q(2,25) for j in range(h)] for i in range(h)])
    I,Z=eye(h),zero(h)
    require(rank(H)==h,'Degenerate ambient form')
    lines=[(tuple(Q(int(t>>i&1)) for i in range(h)),) for t in g['labels']]
    @lru_cache(maxsize=None)
    def projection(U):
        Ut=matrix(zip(*U));UH=product(U,H)
        P=product(product(Ut,inverse(product(UH,Ut))),UH)
        require(product(P,P)==P,'Non-idempotent frame')
        return P
    P=[projection(U) for U in lines];spans={};E={}
    for x,is_active in enumerate(g['active']):
        if not is_active:continue
        if x<=n:spans[x]=lines[x-1]
        else:spans[x]=row_basis(spans[g['left'][x]]+spans[g['right'][x]])
        require(g['common'][x].bit_count()>=2,'Missing common-pair positivity witness')
        E[x]=projection(spans[x])
    index={t:i for i,t in enumerate(g['labels'])}
    sources={index[t]:slot for t,slot in code['sources'].items()}
    outputs={i:[] for i in range(n)}
    for j,slot in code['outputs'].items():outputs[code['target_indices'][j]].append(slot)
    evidence=[]
    for reverse in (False,True):
        physical=P+[Z]*n+[Z]*(S+r);cost=lost=edges=0
        X=list(range(n));Y=list(range(n,2*n));source,target=(Y,X) if reverse else (X,Y)
        centers=list(range(2*n+S,W))
        def touch(ports,F):
            nonlocal cost,lost,edges
            for slot in set(ports):
                old=physical[slot];a,change=cache.transition(old,F)
                if observe is not None: observe(reverse,slot,old,F,a,change)
                require(a==abs(change),'A physical edge has a non-nested rank charge')
                cost+=a;lost+=max(0,-change);edges+=1;physical[slot]=F
        program=('L','J','l','R','V','G','R','L','J','l','G','V')
        frames=('0','0','0','0','X','1','0','u','Y','1','1','1')
        if reverse:
            program=tuple('l' if op=='L' else 'L' if op=='l' else op for op in reversed(program))
            frames=('0','0','0','X','u','1','0','Y','1','1','1','1')
        for op,label in zip(program,frames):
            if op in ('L','l'):
                sequence=code['gates'] if op=='L' else reversed(code['gates'])
                for node,ins,outs in sequence:
                    F=Z if label=='0' else I if label=='1' else sub(I,E[node]) if reverse else E[node]
                    touch([2*n+i for i in ins+outs],F)
            elif op in ('V','J'):
                for t in range(n):
                    slots=[sources[t]] if op=='V' else outputs[t]
                    data=source if op=='V' else target
                    F=Z if label=='0' else I if label=='1' else P[t] if label=='X' else sub(I,P[t])
                    touch([data[t]]+[2*n+s for s in slots],F)
            else:touch((source if op=='G' else target)+centers,Z if label=='0' else I)
        ends=[I]*n+[sub(I,p) for p in P]+[I]*(S+r)
        for slot,F in enumerate(ends):touch([slot],F)
        require(lost==r*h and cost==W*h-2*n+2*r*h,'Invocation rank ledger failed')
        evidence.append(dict(reverse=reverse,physical_edges=edges,rank_sum=cost,
                             decreasing_dimensions=lost,expected=W*h-2*n+2*r*h))
    if statistics is not None:
        statistics.update(cache.statistics())
        statistics['projection_cache'] = projection.cache_info()._asdict()
    return dict(h=h,ordinary_rational_frame_edges_checked=True,
                common_pair_source_spans_checked=True,orientations=evidence)
