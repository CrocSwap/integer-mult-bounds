"""Price a fixed affine chart after the two-return parity bypass."""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from runpy import run_path
from signal import SIGALRM, alarm, signal

ROOT=Path(__file__).resolve().parent
PINS={
    "inputs/CALLER.json":"255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc",
    "inputs/PROJECTOR.json":"c36cb8d3fae7bccd15566c2f83f2d2bd8abeeb334381cbf3212d5d9b3d965c35",
    "inputs/R92-PRICE.json":"05d7a5ebdd2eeedd6c8f534e8e2eeac22484daf9f387f4a6b88cc9eed22a6b8f",
    "inputs/pricing.py":"f4d0b6c9314b838d882d6d06020f24881c19a3fda97a7c00df87b1e920785182",
}


def rank(vectors):
    basis={}
    for x in vectors:
        while x:
            p=x.bit_length()-1
            if p not in basis:
                basis[p]=x
                break
            x ^= basis[p]
    return len(basis)


def mul(a,b):
    return [[sum(x*y for x,y in zip(row,col,strict=True)) for col in zip(*b,strict=True)] for row in a]


def stop(*_):
    raise TimeoutError("20-second affine hull gate")


def main():
    assert __debug__
    signal(SIGALRM,stop)
    alarm(20)
    for path,digest in PINS.items():
        assert sha256((ROOT/path).read_bytes()).hexdigest()==digest
    c=loads((ROOT/"inputs/CALLER.json").read_bytes())
    p=loads((ROOT/"inputs/PROJECTOR.json").read_bytes())
    price=loads((ROOT/"inputs/R92-PRICE.json").read_bytes())
    clocks=(4646,4660)
    assert p["inclusive_window"]==list(clocks) and p["events"]==15
    assert p["head"]==price["head"] and p["caller"]==price["caller_head"]
    assert all(c["events"][k]==["B","IDLE_ONE",36,[17]] for k in clocks)
    ports=c["types"]["B"]["ports"]
    assert ports==[15,17,27,34,35,42,47,55]
    a,b=([[Q(x) for x in row] for row in mat] for mat in p["projectors"])
    assert mul(a,a)==a and mul(b,b)==b and mul(a,b)==mul(b,a)==[[0]*4 for _ in range(4)]
    assert sum(a[i][i] for i in range(4))==sum(b[i][i] for i in range(4))==1
    cost=run_path(str(ROOT/"inputs/pricing.py"))["cost"]
    k=Q(price["old_crossing_upper"])
    ideal=cost(Counter({8:16,16:-8}),k)
    actual=cost(Counter({8:16,16:-16}),k)
    p8=cost(Counter({8:2}),k)
    p16=cost(Counter({16:1}),k)
    assert 0<ideal[0]<=ideal[1] and actual[1]<0
    affordable=[p8[0]/p16[1],p8[1]/p16[0]]
    assert 1<affordable[0]<=affordable[1]<Q(1003,1000)
    m=8
    phases=Counter(x.bit_count()%4 for x in range(1<<m))
    assert phases=={0:72,1:64,2:56,3:64}
    active=[x for x in range(1<<(m+1)) if (x & ((1<<m)-1)).bit_count()%4 in (2,3)]
    assert len(active)==240
    # Weight-two points span all even differences. A weight-three point
    # supplies an odd difference. Duplicating the base in the other lane
    # supplies the independent selector direction.
    base=3
    points=[base]+[1|(1<<j) for j in range(2,m)]+[6,7,base|(1<<m)]
    assert all(x in active for x in points)
    assert len(points)==m+2
    assert rank(x^base for x in points)==rank(x^base for x in active)==m+1
    assert rank(x^base for x in active if (x&255).bit_count()==2)==m
    alarm(0)
    print(dumps({"pins":PINS,"head":p["head"],"caller":p["caller"],"clocks":clocks,"ports":ports,
                 "width_one_addresses":512,"active_width_one":len(active),"phase_counts":phases,
                 "selected_bits":m,"affine_points":points,"affine_hull_dimension":m+1,
                 "all_width_active_volume_fraction_of_one_lane":"1-2^(-4f)",
                 "affine_minimum_volume_fraction":2,"rank16_affordability":affordable,
                 "ideal_one_lane_raw_gain":ideal,"affine_chart_raw_gain":actual,
                 "runner_cap_seconds":20},default=str,indent=2,sort_keys=True))


if __name__=="__main__":
    main()
