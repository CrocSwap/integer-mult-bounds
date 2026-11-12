"""Independent directed arithmetic for the separately tariffed nonuniform mask bound."""
from collections import Counter
from fractions import Fraction as Q
from functools import cache
from hashlib import sha256
import json
from pathlib import Path
import sys

TARGET=Q(10018846261809,2500000000000000)
RESULT_SHA="a46b6c6040f75184cab5467656811ad988c216e3bc8e44d595a5015b6e49620b"
SCALE=10**29


def directed(x,up):
    n,d=(x*SCALE).as_integer_ratio()
    return Q(-(-n//d) if up else n//d,SCALE)


@cache
def log_unit(x):
    z=(x-1)/(x+1)
    lo=2*sum(z**(2*j+1)/Q(2*j+1) for j in range(34))
    return lo,lo+2*z**69/(69*(1-z*z))


@cache
def h(r):
    e=r.bit_length()-1
    a,b=log_unit(Q(r,1<<e))
    c,d=log_unit(Q(2))
    lo,hi=(a+e*c)*TARGET,(b+e*d)*TARGET

    def exp_minus(z):
        t=s=Q(1)
        for i in range(1,23):
            t=-t*z/i
            s+=t
        return s-t,s

    return directed(r*exp_minus(hi)[0],False),directed(r*exp_minus(lo)[1],True)


def plus(x,y):
    return x[0]+y[0],x[1]+y[1]


def times(x,k):
    return (x[0]*k,x[1]*k) if k>=0 else (x[1]*k,x[0]*k)


def run(source):
    blob=source.read_bytes()
    assert sha256(blob).hexdigest()==RESULT_SHA
    r=json.loads(blob)
    signed=Counter({int(k):n for k,n in r["targets"].items()})
    signed.subtract({int(k):n for k,n in r["paid"].items()})
    margin=Q(0),Q(0)
    for rank,c in signed.items():
        margin=plus(margin,times(h(rank),c))
    delta=plus(times(h(7),2),times(h(14),-1))
    body_floor=plus(h(63),times(h(56),-1))
    penalty=plus(plus(body_floor,(Q(-5),Q(-5))),times(delta,-9))
    assert delta[0]>0 and 48*delta[0]>1
    assert penalty[0]>Q("1.51")
    head_free=plus(margin,(Q(444),Q(444)))

    def bound(k):
        return plus(plus(head_free,times(h(444+k),-1)),times(delta,min(64*k,1776)))

    k=28
    best=bound(k)
    assert best[1]<0
    left,right=bound(k-1),bound(k+1)
    assert left[1]<best[0] and right[1]<best[0]
    return {"status":"PASS_NONUNIFORM_TARGET_PRICE","target":str(TARGET),
            "source_sha256":RESULT_SHA,"maximizing_K":k,
            "old_target_margin":list(map(str,margin)),"delta":list(map(str,delta)),
            "minimum_cross_credit_growth_before_K28":list(map(str,times(delta,48))),
            "within_half_body_floor_per_excess_incidence":list(map(str,body_floor)),
            "excess_penalty_lower":list(map(str,penalty)),
            "optimistic_target_upper":list(map(str,best)),
            "adjacent_K27_upper":list(map(str,left)),"adjacent_K29_upper":list(map(str,right))}


if __name__=="__main__":
    assert __debug__
    print(json.dumps(run(Path(sys.argv[1])),sort_keys=True,indent=2))
