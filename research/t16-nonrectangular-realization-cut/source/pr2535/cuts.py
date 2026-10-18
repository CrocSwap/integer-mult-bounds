"""Exact necessary realization cuts. ywz65 / OpenAI Codex; Apache-2.0."""
from itertools import combinations

def require(ok,message):
    if not ok: raise ValueError(message)

def validate(patterns,flows,widths,capacity=None,bin_count=None):
    require(bool(widths) and len(set(widths))==len(widths) and all(type(w) is int and w>0 for w in widths),'widths')
    require(all(type(t) is int and t>=0 for t in flows),'calls')
    for p,n in patterns.items():
        require(len(p)==len(widths) and all(type(a) is int and a>=0 for a in p) and type(n) is int and n>=0,'pattern')
        if n:
            require(sum(p)<=len(flows),'pattern exceeds available calls')
            if capacity is not None: require(sum(a*w for a,w in zip(p,widths))<=capacity,'capacity')
    require(all(len(r)==len(widths) and all(type(a) is int and a>=0 for a in r) for r in flows.values()),'flow')
    if bin_count is not None: require(sum(patterns.values())==bin_count,'bin count')
    for i in range(len(widths)):
        require(sum(r[i] for r in flows.values())==sum(p[i]*n for p,n in patterns.items()),'width balance')

def separate(patterns,flows,widths):
    """One maximizing call subset per width subset/cardinality; all violated prefixes.
    Passing is NOT sufficient for realization. Ties use numeric call order.
    """
    validate(patterns,flows,widths);out=[];ordered_patterns=sorted(patterns)
    for size in range(1,len(widths)+1):
        for indices in combinations(range(len(widths)),size):
            loads={t:sum(r[i] for i in indices) for t,r in flows.items()}
            order=sorted(loads,key=lambda t:(-loads[t],t));lhs=0
            for k,t in enumerate(order,1):
                lhs+=loads[t]
                coeff=[(p,min(k,sum(p[i] for i in indices))) for p in ordered_patterns]
                rhs=sum(patterns[p]*a for p,a in coeff)
                if lhs>rhs:
                    out.append({'widths':[widths[i] for i in indices],'calls':sorted(order[:k]),
                                'lhs':lhs,'rhs':rhs,'deficit':lhs-rhs,
                                'pattern_coefficients':[[list(p),a] for p,a in coeff]})
    return out

def source_hall_and_gr(patterns,flows,widths):
    """Eliminate glob.py's optional auxiliary mt exactly: max mt=min(y,h)."""
    validate(patterns,flows,widths)
    for size in range(1,len(widths)+1):
        for ix in combinations(range(len(widths)),size):
            hit=sum(n for p,n in patterns.items() if any(p[i] for i in ix))
            if any(sum(r[i] for i in ix)>hit for r in flows.values()): return False
    for i in range(len(widths)):
        for j in range(2,max((p[i] for p in patterns),default=0)+1):
            high=[(p,n) for p,n in patterns.items() if p[i]>=j];h=sum(n for _,n in high)
            if sum(p[i]*n for p,n in high)>sum(min(r[i],h) for r in flows.values()): return False
    return True
