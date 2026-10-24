"""Exact finite binary-subspace intervals for the local discovery screens."""
from itertools import combinations


def basis(vectors):
    pivots={}
    for value in vectors:
        v=value
        while v:
            p=v.bit_length()-1
            if p in pivots:v^=pivots[p]
            else:pivots[p]=v;break
    return [pivots[k] for k in sorted(pivots)]


def closure(vectors):
    s={0}
    for v in basis(vectors):s|={x^v for x in tuple(s)}
    return frozenset(s)


def subspaces(q):
    """All subspaces in their unique reduced row-echelon coordinates."""
    for d in range(q+1):
        for pivots in combinations(range(q),d):
            free=[(i,j) for i,p in enumerate(pivots) for j in range(p+1,q) if j not in pivots]
            for mask in range(1<<len(free)):
                rows=[1<<p for p in pivots]
                for k,(i,j) in enumerate(free):
                    if mask>>k&1:rows[i]|=1<<j
                yield rows


def complete_interval(spans,dims,frame_bases,lo,hi,stats,max_gap=5):
    lower=closure(set().union(*(spans[x] for x in lo)))
    upper=set.intersection(*(set(spans[x]) for x in hi))
    if not lower<=upper:return []
    lb=basis(lower)
    joined=lb[:];quotient=[]
    for v in basis(upper):
        if len(basis(joined+[v]))>len(joined):joined.append(v);quotient.append(v)
    q=len(quotient)
    stats['gap_'+str(q)]=stats.get('gap_'+str(q),0)+1
    if q>max_gap:
        stats['skipped_large_interval']=stats.get('skipped_large_interval',0)+1
        return [i for i,s in enumerate(spans) if lower<=s<=upper]
    labels={s:i for i,s in enumerate(spans)}
    result=[]
    for qb in subspaces(q):
        vb=lb[:]
        for row in qb:
            v=0
            for k,x in enumerate(quotient):
                if row>>k&1:v^=x
            vb.append(v)
        space=closure(vb)
        if space not in labels:
            labels[space]=len(spans);spans.append(space);dims.append(len(vb));frame_bases.append(vb)
        result.append(labels[space])
    assert len(result)==len(set(result))
    return result
