"""Independent exact moment and finite-leaf audit; no optimizer imports."""
from fractions import Fraction as Q
from functools import lru_cache
from math import factorial
ROUND=2**192

def lower(value):
    return Q((value * ROUND).numerator // (value * ROUND).denominator, ROUND)

def upper(value):
    x = value * ROUND
    return Q(-((-x.numerator) // x.denominator), ROUND)

@lru_cache(None)
def logarithm(x):
    """Independent base-two reduction, 64 atanh terms and geometric remainder."""
    assert x >= 1
    power = 0
    while x >= 2:
        x /= 2
        power += 1
    def small(y):
        z = (y - 1) / (y + 1)
        s = 2 * sum((z**(2*j+1) / (2*j+1) for j in range(64)), Q(0))
        return s, s + 2*z**129 / (129*(1-z*z))
    l, u = small(x)
    l2, u2 = small(Q(2))
    return lower(l + power*l2), upper(u + power*u2)

def exponential(l, u):
    assert 0 <= l <= u < Q(1, 4)
    def polynomial(x):
        return sum((x**j / factorial(j) for j in range(17)), Q(0))
    tail = u**17 / (factorial(17)*(1-u/18))
    return lower(polynomial(l)), upper(polynomial(u) + tail)


def moment(row,a,bit):
    m,W=row['m'],row['W'];H={int(r):n for r,n in row['child_multiplicities'].items()}
    assert sum(r*n for r,n in H.items())==row['total_rank']==m*W-row['N']
    lo=hi=Q(0)
    for r,n in H.items():
        l,u=logarithm(Q(m,r));e,f=exponential(a*l,a*u)
        lo+=Q(r*n,m*W)*e;hi+=Q(r*n,m*W)*f
    if bit:
        l,u=logarithm(Q(m));e,f=exponential(a*l,a*u)
        weight=Q(32*m*sum(H.values()),10**16*W)
        lo+=weight*e;hi+=weight*f
    return lo,hi


def run(record,original):
    original=dict(original,child_multiplicities={int(r):n for r,n in original['child_multiplicities'].items()})
    intervals={}
    for name,row,bit in (('complex',record['complex_profile'],False),('bit_before',original,True),('bit_after',record['packed_profile'],True)):
        a=Q(record[name]['saving']);lo,hi=moment(row,a,bit);next_lo,next_hi=moment(row,a+Q(1,10**18),bit)
        assert hi<1<next_lo
        intervals[name]=dict(accepted_lower=lo,accepted_upper=hi,next_lower=next_lo,next_upper=next_hi)
    H={int(r):3*n for r,n in original['child_multiplicities'].items()}
    assert H.pop(60)==6600
    packed=record['packed_profile']
    assert H=={int(r):n for r,n in packed['child_multiplicities'].items()}
    assert packed['W']==3*original['W']-5500==57824
    assert packed['N']==3*original['N']==5808
    c=Q(record['bit_after']['saving']);chain=list(map(Q,record['ordinary_chain']))
    assert len(chain)==4
    for j,a in enumerate(chain[1:],1):
        assert a==(1-c)*c+c*chain[j-1]==c-c**j*(c-chain[0])
        assert chain[j-1]<a<c<1-a
    b=Q(record['complex']['saving']);beta=eta=Q(1,10**24)
    for name,saving in (('before_packing',chain[0]),('after_packing',chain[-1])):
        a=min(saving,(1-beta)*b-Q(1,10**30));q=a*(1-2*eta);ceiling=(1-eta)*q/(1+q)
        k=Q(record[name]['kappa'])
        assert k<ceiling<=k+Q(1,10**18)
        assert a==saving<b
    assert Q(record['after_packing']['kappa'])>Q(record['comparison_pr194_kappa'])
    return dict(status='PASS',moment_intervals=intervals,finite_leaf_levels=3,adjacent_final_grids_checked=2)
