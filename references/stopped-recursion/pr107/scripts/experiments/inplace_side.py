"""In-place binary side maps and exact disjoint-path excess witnesses.

The rejection is scoped to lexicographic, smallest-row Gauss--Jordan,
exactly n side roles, retained invocation boundaries and central frames.
"""
from itertools import combinations
from fractions import Fraction as Q
from certify import require


def triple_side(h):
    require(type(h) is int and h>=6 and h%2==0,'Use even h >= 6')
    triples=list(combinations(range(h),3));n=len(triples);points=[0]*h
    for i,S in enumerate(triples):
        for p in S:points[p]|=1<<i
    rows=[points[a]^points[b]^points[c]^(1<<i) for i,(a,b,c) in enumerate(triples)]
    return triples,points,rows


def central_type(h):
    triples,points,rows=triple_side(h)
    # The point incidence Gram has diagonal binom(h-1,2) and off-diagonal h-2.
    q=((h-1)*(h-2)//2)%2
    require(all((points[i]&points[j]).bit_count()%2==(q if i==j else 0)
                for i in range(h) for j in range(h)), 'Wrong binary incidence Gram')
    return dict(h=h,n=len(triples),gram_diagonal=q,side_invertible=q==0,
                reason='C^2=0 and (I+C)^2=I' if q==0 else 'C^2=C and (I+C)U=0 with U nonzero')


def compile_side(h):
    triples,points,rows=triple_side(h);n=len(rows);work=list(rows);unused=set(range(n));ops=[]
    require(h%4==2,'The n-role side matrix is singular for h divisible by four')
    pivots=[]
    for col in range(n):
        p=next(i for i in sorted(unused) if work[i]>>col&1)
        unused.remove(p);pivots.append(p)
        for i in range(n):
            if i!=p and work[i]>>col&1:work[i]^=work[p];ops.append((i,p))
    require(set(work)=={1<<i for i in range(n)},'Incomplete elimination')
    initial=[row.bit_length()-1 for row in work]
    values=[1<<j for j in initial]
    gates=list(reversed(ops))
    for t,s in gates:values[t]^=values[s]
    require(values==rows,'Input matching and in-place mixer do not give the side map')
    return dict(h=h,triples=triples,points=points,rows=rows,pivots=pivots,
                initial=initial,gates=gates,roles=n)


def verify_prefix(h,pivots,swaps):
    """Check disjoint one-switch routes without materializing the large graph.

    swaps contains pairs of pivot COLUMN indices j<c. The actual gate is
    row[pivots[j]] += row[pivots[c]] at elimination step c.
    """
    triples,points,rows=triple_side(h);n=len(rows)
    require(h%4==2 and 0<len(pivots)<=n,'Need an invertible side and nonempty prefix')
    require(all(type(p) is int and 0<=p<n for p in pivots) and len(set(pivots))==len(pivots),
            'Pivot roles must be distinct')
    masks=[sum(1<<x for x in T) for T in triples]
    partners={};at_step={}
    for j,c in swaps:
        require(type(j) is int and type(c) is int and 0<=j<c<len(pivots), 'Invalid switch indices')
        require(j not in partners and c not in partners,'Switch paths reuse a physical role')
        partners[j]=c;partners[c]=j;at_step[c]=j
    unused=set(range(n));verified=[]
    for col,p in enumerate(pivots):
        expected=next(i for i in sorted(unused) if rows[i]>>col&1)
        require(p==expected,'Not the specified lexicographic elimination prefix')
        unused.remove(p)
        if col in at_step:
            j=at_step[col]
            require(rows[pivots[j]]>>col&1,'Claimed switch gate is absent')
            verified.append((j,col))
        if col+1<len(pivots):
            row=rows[p]
            for i in range(n):
                if i!=p and rows[i]>>col&1:rows[i]^=row
    bad=[]
    for j,p in enumerate(pivots):
        target=pivots[partners[j]] if j in partners else p
        if (masks[j]&masks[target]).bit_count()!=1:bad.append((j,target))
    k=len(bad)
    # Each selected path contributes at least two units of edge excess in
    # every invocation. The three n^2 copies give at least 6kn^2 extra.
    deficit_upper=n*n*(n-6*h*h-6*k)
    return dict(h=h,n=n,prefix_columns=len(pivots),disjoint_switches=len(swaps),
                certified_nonorthogonal_paths=k,bad_endpoints=bad,
                excess_per_invocation_lower=2*k,deficit_upper=deficit_upper,
                no_positive_deficit=deficit_upper<=0,
                all_internal_rational_frames_allowed=True,
                scope='Fixed data-copy/injection boundaries, central frames, lexicographic elimination and exactly n side roles')


def invoke(x,y,side,center,code,inverse=False):
    n=code['roles'];h=code['h']
    require(len(x)==len(y)==len(side)==n and len(center)==h,'Wrong role dimensions')
    def mix(reverse=False):
        for t,s in (reversed(code['gates']) if reverse else code['gates']):side[t]^=side[s]
    def copy():
        for slot,i in enumerate(code['initial']):side[slot]^=x[i]
    def inject():
        for i in range(n):y[i]^=side[i]
    def gather():
        for i,T in enumerate(code['triples']):
            for p in T:center[p]^=x[i]
    def scatter():
        for i,T in enumerate(code['triples']):
            for p in T:y[i]^=center[p]
    ops=((mix,False),(inject,None),(mix,True),(scatter,None),(copy,None),(gather,None),
         (scatter,None),(mix,False),(inject,None),(mix,True),(gather,None),(copy,None))
    if inverse:ops=tuple((f,not arg if f==mix else arg) for f,arg in reversed(ops))
    for f,arg in ops:
        if f==mix:f(arg)
        else:f()
