"""Census of literal paired BIT invoice and directed raw price crossings."""
from collections import Counter
from fractions import Fraction as Q
from functools import cache
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path
import sys

TARGET = Q("0.0040075385047236")
SCALE = 10**25


def enc_q(x, ceil):
    p = x*SCALE
    n,d = p.numerator,p.denominator
    return Q(-((-n)//d) if ceil else n//d, SCALE)


def out(interval):
    return list(map(str, interval))


def round_out(lo, hi):
    return enc_q(lo, False), enc_q(hi, True)


@cache
def log_reduced(x):
    z = (x-1)/(x+1)
    lo = 2*sum(z**(2*i+1)/(2*i+1) for i in range(31))
    return round_out(lo, lo+2*z**63/(63*(1-z*z)))


@cache
def log_rank(r):
    e = r.bit_length()-1
    l2,h2 = log_reduced(Q(2))
    l,h = log_reduced(Q(r, 2**e))
    return l+e*l2, h+e*h2


def alternating(x):
    assert 0 <= x < 1
    t = s = Q(1)
    for i in range(1,19):
        t = -t*x/i
        s += t
    return s-t, s


@cache
def power(r,k):
    l,h = log_rank(r)
    return round_out(r*alternating(k*h)[0], r*alternating(k*l)[1])


def dot(coefficients, evaluator):
    lo = hi = Q(0)
    for rank,count in coefficients.items():
        a,b = evaluator(rank)
        if count < 0:
            a,b = b,a
        lo += count*a
        hi += count*b
    return lo,hi


def crossing(signed, lo, hi):
    assert dot(signed, lambda r:power(r,lo))[0]>0
    assert dot(signed, lambda r:power(r,hi))[1]<0
    def derivative_bound(r):
        ll,lh = log_rank(r)
        return -lh*power(r,lo)[1], -ll*power(r,hi)[0]
    derivative = dot(signed, derivative_bound)
    assert derivative[1] < 0
    while hi-lo > Q(1,10**13):
        m = (lo+hi)/2
        a,b = dot(signed,lambda r:power(r,m))
        if a>0:
            lo=m
        elif b<0:
            hi=m
        else:
            raise RuntimeError("insufficient interval separation")
    assert dot(signed,lambda r:power(r,lo))[0]>0
    assert dot(signed,lambda r:power(r,hi))[1]<0
    # Outward decimal grid also gets independent sign checks.
    grid=10**13
    lo=Q((lo*grid).numerator//(lo*grid).denominator,grid)
    hi=Q(-((-hi*grid).numerator//(hi*grid).denominator),grid)
    assert dot(signed,lambda r:power(r,lo))[0]>0
    assert dot(signed,lambda r:power(r,hi))[1]<0
    return out((lo,hi)),out(round_out(*derivative))


def integer_hist(d):
    return Counter({int(r): n for r,n in d.items()})


def price(root):
    spec=spec_from_file_location("endpoint", Path(__file__).with_name("HEAD-REPLAY.py"))
    endpoint=module_from_spec(spec)
    spec.loader.exec_module(endpoint)
    caller=endpoint.load(root, "EFREE-CALLER.json.gz")
    result=endpoint.load(root, "EFREE-RESULT.json")
    source=endpoint.load(root, "retained/inputs/BIT-NATIVE-WORD.json.gz")
    dims={int(i): c["dim"] for i,c in source["frames"].items()}
    paid0=Counter(abs(dims[a]-dims[b]) for op,_,*rest in source["program"]
                  if op=="MOVE" for a,b in (rest,))
    helper0=Counter(abs(dims[a]-dims[b]) for a,b in
                    zip(source["start"][222:], source["final"][222:], strict=True))
    assert paid0==integer_hist(result["native_paid"])
    assert helper0==integer_hist(result["native_helpers"])
    n=caller["ports"]
    count=Counter(e[0] for e in caller["events"])
    paid=Counter({r:c*count["LOCAL"] for r,c in paid0.items()})
    productive=Counter({r:c*count["LOCAL"] for r,c in helper0.items()})
    for op,*rest in caller["events"]:
        if op=="QUERY":
            paid[1]+=n
        elif op=="IDLE_ONE":
            paid[caller["body_rank"]*len(rest[1])]+=n
    for spec in caller["diagonal"]:
        productive[spec["q"]+caller["body_rank"]*len(spec["stages"])]+=n
    assert paid==integer_hist(result["paid"])
    assert productive==integer_hist(result["targets"])
    signed=productive.copy()
    signed.subtract(paid)
    base=crossing(signed,Q(".0038"),Q(".0043"))
    old_cert=tuple(map(Q,result["raw_crossing"]))
    assert Q(base[0][0])<=old_cert[1] and old_cert[0]<=Q(base[0][1])
    cases={}
    for extra in range(4):
        new=signed.copy()
        new[1]+=n-extra*caller["stages"]
        interval,derivative=crossing(new,Q(".0038"),Q(".0043"))
        cases[extra]={"net_removed_rank_one":new[1]-signed[1],
                      "raw_crossing_bracket":interval,
                      "derivative_bound_on_initial_bracket":derivative,
                      "target_margin":out(dot(new,lambda r:power(r,TARGET)))}
    return {"pins":endpoint.PINS,"target":str(TARGET),"native_paid":paid0,"native_helpers":helper0,
            "paid":paid,"productive":productive,"predecessor_crossing_bracket":base[0],
            "predecessor_target_margin":out(dot(signed,lambda r:power(r,TARGET))),
            "predecessor_crossing_overlaps_public_receipt":True,
            "cases_extra_rank_one_per_changed_native":cases,
            "scope":"Raw paid-profile crossing only; excludes any unpriced costs of literal changed native word, compiler/tape, and full theorem."}


if __name__=="__main__":
    print(json.dumps(price(Path(sys.argv[1])),sort_keys=True,indent=2))
