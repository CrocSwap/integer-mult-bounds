"""Independent reverse suffix rank on the 2,128 frozen R89 bank keys."""
from argparse import ArgumentParser
from collections import Counter, defaultdict
from fractions import Fraction
from functools import cache
from gzip import decompress
from hashlib import sha256
from json import dumps, loads
from math import isqrt
from pathlib import Path
from signal import SIGALRM, alarm, signal
from time import monotonic

HEAD = "aaeec8c0acf01e99a5f331ef363a698d9c084ace"
PRIME = 65537
PINS = {
    "keys": "a131ec5bf96baac89f0f6623cf7d9dff06601b36ea720474311ee7ecb394f6e2",
    "price": "b4bf8e00a8289f03b1da731fb3ab563a771d88d875e0da73acf70954df2f2c56",
    "word": "4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a",
}
PAYLOAD = "9aa8d6b054ba7eb2289d052c1079b16be518d2f0fbfb244569fa18e3733acdac"
PROTECTED = {319,863,1355,1568}


def unique(pairs):
    result = dict(pairs)
    if len(result) != len(pairs):
        raise ValueError("Duplicate JSON key")
    return result


def checked(path, name):
    raw = path.read_bytes()
    if sha256(raw).hexdigest() != PINS[name]:
        raise ValueError(f"Changed input {name}")
    if name == "word":
        raw = decompress(raw)
        assert sha256(raw).hexdigest() == PAYLOAD
    return loads(raw, object_pairs_hook=unique)


@cache
def scalar(value):
    q = Fraction(value)
    if q.denominator % PRIME == 0:
        raise ValueError("Nonunit native denominator")
    assert q
    return q.numerator * pow(q.denominator, -1, PRIME) % PRIME, q.denominator


def add(target, other, coefficient):
    if not coefficient:
        return
    for i,v in other.items():
        x = (target.get(i,0)+coefficient*v) % PRIME
        if x:
            target[i]=x
        else:
            target.pop(i,None)


def scale(row, coefficient):
    return {i:x for i,v in row.items() if (x:=v*coefficient%PRIME)}


def column_rank(bank, suffix):
    """Eliminate columns over live role coordinates and retain the original minor."""
    n = len(bank)
    columns = defaultdict(dict)
    for row, role in enumerate(bank):
        for output, coefficient in suffix[role].items():
            columns[output][row]=coefficient
    echelon = []
    used = []
    determinant = 1
    for output in sorted(columns,reverse=True):
        column=columns[output].copy()
        for pivot,inverse,earlier in echelon:
            add(column,earlier,-column.get(pivot,0)*inverse)
        if not column:
            continue
        pivot=max(column)
        diagonal=column[pivot]
        echelon.append((pivot,pow(diagonal,-1,PRIME),column))
        used.append(output)
        determinant=determinant*diagonal%PRIME
        if len(echelon)==n:
            break
    rank=len(echelon)
    rows=[bank[p] for p,_,_ in echelon]
    if rank<n:
        return {"suffix_exterior_rank":rank,"status":"modular_suffix_rank_drop",
                "rank_pivot_rows":rows,"rank_pivot_output_columns":used}
    assert determinant
    # Order the original minor's rows by pivot insertion, and its columns by
    # their acceptance. The column additions give a triangular matrix.
    return {"suffix_exterior_rank":rank,"status":"no_nonzero_pure_suffix",
            "minor_role_rows":rows,"minor_exterior_output_columns":used,
            "minor_determinant_mod_prime":determinant}


def reverse_event(event, columns, n):
    op,d,*args=event
    if op in ("INIT","CLEAR"):
        assert d>=n
        columns[d]={}
        return (d,),None
    if op=="MOVE":
        return (),None
    coefficient,denom=scalar(args[-2])
    if op=="SCALE":
        columns[d]=scale(columns[d],coefficient)
        return (d,),denom
    assert op in ("ADD","COPY") and args[0]!=d
    s=args[0]
    add(columns[s],columns[d],coefficient)
    if op=="COPY":
        assert d>=n
        columns[d]={}
        return (s,d),denom
    return (s,),denom


def controls():
    assert all(PRIME%d for d in range(2,isqrt(PRIME)+1))
    full=column_rank([5,7],{5:{2:2,8:3},7:{2:5,8:7}})
    assert full["minor_exterior_output_columns"]==[8,2] and full["minor_role_rows"]==[7,5]
    assert full["minor_determinant_mod_prime"]==PRIME-1
    deficient=column_rank([5,7],{5:{2:2,8:3},7:{2:4,8:6}})
    assert deficient["suffix_exterior_rank"]==1 and deficient["status"]=="modular_suffix_rank_drop"
    tape=[["INIT",3,0],["COPY",3,1,"-3/2",0],["ADD",0,3,"1",0],
          ["SCALE",1,"2/5",0],["CLEAR",3,0]]
    columns=[{0:1},{1:1},{2:1},{}]
    for event in reversed(tape):
        reverse_event(event,columns,3)
    assert columns==[{0:1},{0:scalar("-3/2")[0],1:scalar("2/5")[0]},{2:1},{}]
    try:
        scalar("1/65537")
    except ValueError:
        pass
    else:
        raise AssertionError("Nonunit denominator was admitted")
    return ["column_order_determinant","planted_suffix_rank_drop","signed_COPY_ADD_SCALE_CLEAR_adjoint",
            "nonunit_denominator_rejected"]


def admission(keys, price):
    assert keys["head"]==price["head"]==HEAD
    assert keys["source_sha256"]["inputs/PRICE.json"]==PINS["price"]
    assert keys["source_sha256"]["inputs/7334-WORD.json.gz"]==price["word_sha256"]==PINS["word"]
    assert keys["reverse_case_cap"]==keys["cases"]==2128 and keys["reverse_runner_seconds_cap"]==35
    new={tuple(r["key"]):r for r in keys["keys"]}
    known={tuple(r["key"]):r for r in keys["controls"]}
    assert len(new)==len(keys["keys"])==2128 and len(known)==len(keys["controls"])==6
    assert not new.keys() & known.keys()
    assert all(r["disposition"]=="rank drop" for r in new.values())
    assert len({t for t,c in new})==2128 and len({c for t,c in new})==27
    assert {p for r in new.values() for p in r["pivots"]}==set(keys["possible_literal_pivots"])
    assert len(keys["possible_literal_pivots"])==keys["one_split_per_literal_pivot_cap"]==129
    return new,known


def sweep(word, cohort, keys, prior, deadline, out, old_out, progress):
    n,owned = word["public"],word["owned_fields"]
    tape=word["program"]
    assert (n,owned,len(tape))==(1501,68,76466)
    mains=set(word["live"])|{r+112 for r in word["live"]}
    mains.update(word["hosted"]["X2"],word["hosted"]["Y2"])
    assert cohort=={i for i,az in enumerate(zip(word["initial"],word["final"],strict=True))
                    if az==(3,127) and i not in mains|PROTECTED}
    assert len(cohort)==615
    frames=word["frames"]

    @cache
    def space(chart):
        span={0}
        for v in frames[chart]:
            assert v not in span
            span.update(v^x for x in tuple(span))
        return span

    requests=defaultdict(list)
    for t,c in [*keys,*prior]:
        assert len(frames[c]) in (4,5) and space(3)<space(c)<space(127)
        requests[t].append(c)
    states=list(word["final"])+[None]*owned
    banks=defaultdict(set)
    for r,c in enumerate(states[:n]):
        banks[c].add(r)
    suffix=[({r:1} if r not in cohort else {}) for r in range(n)]+[{} for _ in range(owned)]
    revision=[0]*(n+owned)
    rank_cache={}
    denoms=set()
    histogram=Counter()
    for t in range(len(tape),-1,-1):
        progress["first_unvisited_reverse_event"]=t-1 if t else None
        if (t%128==0 or t in requests) and monotonic()>=deadline:
            raise TimeoutError("bounded suffix replay")
        for c in requests.get(t,()):
            k=t,c
            pinned=keys[k] if k in keys else prior[k]
            roles=sorted(banks[c])
            public=[r for r in roles if r<n]
            owner=[r for r in roles if r>=n]
            pivots=sorted(set(public)&cohort)
            assert public==pinned["public"] and owner==pinned["owned"] and pivots==pinned["pivots"]
            assert pivots
            if t:
                event=tape[t-1]
                incident=event[2:4] if event[0]=="MOVE" else event[-1:]
                assert c in incident
            signature=tuple((r,revision[r]) for r in public)
            if signature not in rank_cache:
                rank_cache[signature]=column_rank(public,suffix)
            result=dict(key=list(k),chart_rank=len(frames[c]),public=public,owned=owner,pivots=pivots,
                        **rank_cache[signature])
            if k in prior:
                expected=len(public)-pinned["pure_suffix_dimension"]
                result["prior_exact_suffix_rank"]=expected
                old_out[k]=result
            else:
                out[k]=result
        if not t:
            break
        event=tape[t-1]
        op,d,*args=event
        if op=="MOVE":
            a,b,is_owned=args
            assert states[d]==b and is_owned==(d>=n)
            assert space(a)<space(b) or is_owned and space(b)<space(a)
            histogram[abs(len(frames[b])-len(frames[a]))]+=1
            states[d]=a
            banks[b].remove(d)
            banks[a].add(d)
        elif op=="INIT":
            chart=args[0]
            assert d>=n and states[d]==chart
            states[d]=None
            banks[chart].remove(d)
        elif op=="CLEAR":
            chart=args[0]
            assert d>=n and states[d] is None and not suffix[d]
            states[d]=chart
            banks[chart].add(d)
        else:
            chart=args[-1]
            assert states[d]==chart and op in ("ADD","COPY","SCALE")
            if op!="SCALE":
                assert states[args[0]]==chart
        changed,denominator=reverse_event(event,suffix,n)
        for r in changed:
            revision[r]+=1
        if denominator is not None:
            denoms.add(denominator)
    assert states==list(word["initial"])+[None]*owned and not any(suffix[n:])
    assert dict(histogram)=={1:4000,2:853,3:829,4:223,5:345,6:14,7:10,8:5}
    progress.update(first_unvisited_reverse_event=None,events_replayed=len(tape),
                    denominator_units=sorted(denoms),native_paid_histogram=dict(histogram),
                    distinct_suffix_exterior_row_sets=len(rank_cache))


def main():
    parser=ArgumentParser(description=__doc__)
    for n in PINS:
        parser.add_argument("--"+n,type=Path)
    parser.add_argument("--controls-only",action="store_true")
    args=parser.parse_args()
    if not __debug__:
        raise RuntimeError("Run with assertions")
    if args.controls_only:
        print(dumps(controls()))
        return
    if not all(getattr(args,n) for n in PINS):
        parser.error("Require all three pinned input paths")

    def stop(*_):
        raise TimeoutError("hard 35-second cap")

    checks=[]
    keys,prior,results,prior_results,progress={},{},{},{},{}
    interruption=None
    signal(SIGALRM,stop)
    alarm(35)
    deadline=monotonic()+33
    try:
        checks=controls()
        document=checked(args.keys,"keys")
        price=checked(args.price,"price")
        keys,prior=admission(document,price)
        word=checked(args.word,"word")
        sweep(word,set(price["endpoint_cohort"]),keys,prior,deadline,results,prior_results,progress)
    except TimeoutError as error:
        interruption=str(error)
    finally:
        alarm(0)
    rows=[results[k] for k in keys if k in results]
    olds=[prior_results[k] for k in prior if k in prior_results]
    unvisited=[list(k) for k in keys if k not in results]
    control_unvisited=[list(k) for k in prior if k not in prior_results]
    control_discrepancies=[r["key"] for r in olds if r["suffix_exterior_rank"]!=r["prior_exact_suffix_rank"]]
    drops=[r["key"] for r in rows if r["status"]=="modular_suffix_rank_drop"]
    print(dumps(dict(head=HEAD,pins=PINS,prime=PRIME,case_cap=2128,runner_cap_seconds=35,
        controls=checks,prior_exact_controls=olds,control_unvisited=control_unvisited,
        control_discrepancies=control_discrepancies,tested=rows,unvisited=unvisited,suffix_rank_drops=drops,
        status_counts=dict(Counter(r["status"] for r in rows)),timeout=interruption,**progress),
        indent=2,sort_keys=True))
    if interruption or control_unvisited or control_discrepancies:
        raise SystemExit(2)


if __name__=="__main__":
    main()
