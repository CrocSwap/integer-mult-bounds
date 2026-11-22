"""Exact primal and dual prices for the eight upward dimension cuts.

Pass the pinned #8027 gzip graph. The incidence inequality itself and the
restricted ranks are checked by dimension_cuts.py in the scientific package.
No native realization of the optimal relaxed interval cover is assumed.
"""
import gzip
import json
from collections import Counter
from fractions import Fraction
from hashlib import sha256
from math import isqrt
from pathlib import Path
import sys

SHA='74e93daf2b7acf794ffb51f92f03f51556f68126d41ee13a8969bddb4cbe6326'
F=Fraction
UNIT=1<<128


def price(rank,t):
    """Enclose rank^t with monotone dyadic exponents and outward sqrt."""
    bits=72
    assert 0<t<1
    def one(n,upper):
        lower=higher=rank*UNIT
        v=UNIT
        for b in range(bits-1,-1,-1):
            lower=isqrt(lower*UNIT)
            higher=isqrt(higher*UNIT-1)+1
            if n & (1<<b):
                v=(v*higher+UNIT-1)//UNIT if upper else (v*lower)//UNIT
        return F(v,UNIT)
    return one((t*2**bits).__floor__(),False),one((t*2**bits).__ceil__(),True)


def check(source):
    raw=Path(source).read_bytes()
    assert sha256(raw).hexdigest()==SHA
    g=json.loads(gzip.decompress(raw))
    dim={int(j):v['dim'] for j,v in g['frames'].items()}
    covers=Counter()
    tariff=Counter()
    for row in g['program']:
        if row[0]!='MOVE':
            continue
        source,target=(dim[c] for c in row[2:])
        if target>source:
            covers.update(range(source+1,target+1))
            tariff[target-source]+=1
    need=[covers[j] for j in range(1,9)]
    assert need==[516,627,627,627,616,616,616,505]
    order=sorted(range(1,9),key=lambda j:(-need[j-1],j))
    layers=Counter()
    for height in range(1,max(need)+1):
        inside=tuple(j for j in range(1,9) if need[j-1]>=height)
        assert set(inside)==set(order[:len(inside)])
        assert inside==tuple(range(inside[0],inside[-1]+1))
        layers[inside]+=1
    optimum=Counter()
    recovered=Counter()
    for interval,count in layers.items():
        optimum[len(interval)]+=count
        for j in interval:
            recovered[j]+=count
    assert recovered==covers
    assert optimum=={8:505,7:11,6:100,3:11}
    assert sum(r*n for r,n in optimum.items())==sum(r*n for r,n in tariff.items())==4750
    t=1-F('0.00389046')
    prices={0:(F(0),F(0)),**{r:price(r,t) for r in range(1,9)}}
    weights={j:(prices[i][0]-prices[i-1][1],prices[i][1]-prices[i-1][0]) for i,j in enumerate(order,1)}
    # Certify all non-tight interval constraints numerically; the tight rows
    # telescope symbolically because the interval is the corresponding prefix.
    for a in range(1,9):
        for b in range(a,9):
            interval=list(range(a,b+1))
            if set(interval)!=set(order[:len(interval)]):
                assert sum(weights[j][1] for j in interval)<prices[len(interval)][0]
    def total(h):
        return tuple(sum(n*prices[r][i] for r,n in h.items()) for i in (0,1))
    primal,old=total(optimum),total(tariff)
    dual=tuple(sum(need[j-1]*weights[j][i] for j in order) for i in (0,1))
    assert max(primal[0],dual[0])<=min(primal[1],dual[1])
    deficient=dict(recovered); deficient[4]-=1
    assert deficient!=dict(covers)
    def bounds(x):
        scale=10**15
        def fmt(n):
            whole,rem=divmod(n,scale)
            return f'{whole}.{rem:015d}'
        return [fmt((x[0]*scale).__floor__()),fmt((x[1]*scale).__ceil__())]
    return {'upward_native_histogram':dict(tariff),'levels_in_dual_order':order,'required':need,
            'optimal_relaxed_intervals':[{'dimensions':[i[0],i[-1]],'count':n} for i,n in layers.items()],
            'both_unit_totals':4750,'native_upward_price':bounds(old),'minimum_cut_relaxation_price':bounds(primal),
            'difference':bounds((old[0]-primal[1],old[1]-primal[0]))}


if __name__=='__main__':
    print(json.dumps(check(sys.argv[1]),indent=2))
