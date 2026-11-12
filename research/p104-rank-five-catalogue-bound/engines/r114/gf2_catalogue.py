"""Verify R114 chart inclusions using exact GF(2) elimination and reverse liveness."""
from argparse import ArgumentParser
from collections import Counter
from fractions import Fraction
from functools import cache
from gzip import decompress
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from signal import SIGALRM, alarm, signal
from time import monotonic

ROOT = Path(__file__).resolve().parent
HEAD = "aaeec8c0acf01e99a5f331ef363a698d9c084ace"
CALLER = "07a76c5e2738882c0cb322278e56f6cae3c9885d"
PINS = {
    "inputs/PRICE.json":"86fa60a067496a276d911fd3cb56b78fbb2388138be6e438b754e1573f9cd077",
    "inputs/GEOMETRY.json":"00c49b4bd76005b34a60f639b4a7ed8742d36239bb37aa4d8f026b4450e0cf31",
    "inputs/7334-WORD.json.gz":"4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a",
}
PAYLOAD = "9aa8d6b054ba7eb2289d052c1079b16be518d2f0fbfb244569fa18e3733acdac"
LOW,HIGH = 1090,127
RANKS = (6,7)
EVENTS,SECONDS = 76466,20


def unique(pairs):
    value = dict(pairs)
    if len(value) != len(pairs):
        raise ValueError("Duplicate JSON key")
    return value


def read(root,name):
    raw = (root/name).read_bytes()
    if sha256(raw).hexdigest() != PINS[name]:
        raise ValueError("Changed input " + name)
    if name.endswith(".gz"):
        raw = decompress(raw)
        assert sha256(raw).hexdigest() == PAYLOAD
    return loads(raw,object_pairs_hook=unique)


def normal(v,pivots):
    for j in range(8,-1,-1):
        if v & (1<<j):
            v ^= pivots[j]
    return v


def basis(rows):
    pivots = [0]*9
    for value in rows:
        assert type(value) is int and 0 < value < 512
        residual = normal(value,pivots)
        if residual:
            pivots[residual.bit_length()-1] = residual
    return pivots


def rank(rows):
    return sum(bool(v) for v in basis(rows))


def missed(rows,other):
    return [[v,r] for v in rows if (r:=normal(v,other))]


def controls():
    a,b,c = (1,2),(1,2,4),(1,2,4,8)
    assert rank(a+b)==len(b) and rank(b+c)==len(c)
    assert missed(a,basis(b))==[] and missed(b,basis(c))==[]
    assert missed((1,16),basis(b))==[[16,16]]
    assert rank((1,2,3))==2
    return ["strict nested positive","out-of-span vector certificate","dependent basis"]


def catalogue(frames,progress,deadline):
    ranks = [rank(row) for row in frames]
    assert ranks == list(map(len,frames))
    assert ranks[LOW]==4 and ranks[HIGH]==9
    low,high = frames[LOW],frames[HIGH]
    top = basis(high)
    assert not missed(low,top)
    data = []
    for chart,r in enumerate(ranks):
        if r not in RANKS:
            continue
        if monotonic() >= deadline:
            raise TimeoutError("chart catalogue cap")
        middle = frames[chart]
        inner = missed(low,basis(middle))
        outer = missed(middle,top)
        joined1,joined2 = rank(low+middle),rank(middle+high)
        assert (joined1==r)==(not inner) and (joined2==9)==(not outer)
        data.append(dict(chart=chart,rank=r,union_with_low_rank=joined1,union_with_high_rank=joined2,
            low_generator_residues=inner,middle_generator_residues=outer,
            nested=not inner and not outer))
        progress["catalogue_checked"] += 1
    return data


def reverse(word,price,progress,deadline):
    n,owned = word["public"],word["owned_fields"]
    assert (n,owned,len(word["program"])) == (1501,68,EVENTS)
    frames = word["frames"]

    @cache
    def strict(a,b):
        return len(frames[a])<len(frames[b]) and not missed(frames[a],basis(frames[b]))

    roles = set(price["cohort"])
    assert len(roles)==9 and all((word["initial"][r],word["final"][r])==(LOW,HIGH) for r in roles)
    state = word["final"]+[None]*owned
    require_init = set()
    transitions = []
    for t in range(EVENTS-1,-1,-1):
        progress["first_unvisited_event"] = t
        if t%128 == 0 and monotonic()>=deadline:
            raise TimeoutError("reverse liveness cap")
        op,d,*args = word["program"][t]
        assert 0<=d<len(state) and (d not in require_init or op=="INIT")
        if op=="MOVE":
            a,b,owned_flag=args
            assert state[d]==b and owned_flag==(d>=n)
            assert strict(a,b) or (owned_flag and strict(b,a))
            state[d]=a
            if d in roles:
                transitions.append([t,d,a,b])
        elif op=="INIT":
            assert d>=n and state[d]==args[0]
            state[d]=None
            require_init.discard(d)
        elif op=="CLEAR":
            assert d>=n and state[d] is None
            state[d]=args[0]
        else:
            assert op in ("ADD","COPY","SCALE") and state[d]==args[-1]
            assert Fraction(args[-2])
            if op!="SCALE":
                assert d!=args[0] and state[args[0]]==args[-1]
            if op=="COPY":
                assert d>=n
                require_init.add(d)
        progress["events_checked"]+=1
    assert state==word["initial"]+[None]*owned and not require_init
    progress["first_unvisited_event"]=None
    return list(reversed(transitions))


def main():
    assert __debug__
    p = ArgumentParser(description=__doc__)
    p.add_argument("--root",type=Path,default=ROOT)
    p.add_argument("--controls-only",action="store_true")
    args=p.parse_args()
    checks=controls()
    if args.controls_only:
        print(dumps(checks))
        return
    progress=dict(events_checked=0,catalogue_checked=0,first_unvisited_event=EVENTS-1)
    failure=None
    records,transitions=[],[]

    def stop(*_):
        raise TimeoutError("Hard 20-second cap")

    signal(SIGALRM,stop)
    alarm(SECONDS)
    deadline=monotonic()+SECONDS-2
    try:
        price=read(args.root,"inputs/PRICE.json")
        primary=read(args.root,"inputs/GEOMETRY.json")
        assert price["head"]==primary["head"]==HEAD and price["caller"]==CALLER
        assert price["word_sha256"]==primary["word_sha256"]==PINS["inputs/7334-WORD.json.gz"]
        assert primary["price_sha256"]==PINS["inputs/PRICE.json"]
        assert price["endpoint_charts"]==[LOW,HIGH] and price["cut_ranks"]==list(RANKS)
        assert price["event_cap"]==EVENTS and price["geometry_runner_seconds"]==SECONDS
        assert primary["status"]=="EXHAUSTED" and primary["visited_events"]==EVENTS
        word=read(args.root,"inputs/7334-WORD.json.gz")
        records=catalogue(word["frames"],progress,deadline)
        assert [r["chart"] for r in records if r["nested"]]==primary["intermediate_charts"]==[]
        assert primary["eligible_bank_count"]==primary["eligible_chart_count"]==0
        assert primary["all_representative_keys"]==primary["selected"]==primary["unvisited_keys"]==[]
        transitions=reverse(word,price,progress,deadline)
    except TimeoutError as exc:
        failure=str(exc)
    finally:
        alarm(0)
    print(dumps(dict(head=HEAD,caller=CALLER,pins=PINS,controls=checks,progress=progress,timeout=failure,
        endpoints=[LOW,HIGH],endpoint_ranks=[4,9],tested_rank_counts=dict(Counter(r["rank"] for r in records)),
        catalogue=records,cohort_paid_moves=transitions,nested_charts=[r["chart"] for r in records if r["nested"]],
        primary_agreement=failure is None),indent=2,sort_keys=True))
    if failure:
        raise SystemExit(2)


if __name__=="__main__":
    main()
