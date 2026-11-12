"""Independent full exterior rank for the 4,183 frozen R86 bank keys."""
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

PRIME = 65537
HEAD = "aaeec8c0acf01e99a5f331ef363a698d9c084ace"
PINS = {
    "price": "b4bf8e00a8289f03b1da731fb3ab563a771d88d875e0da73acf70954df2f2c56",
    "geometry": "238135413a5646cb39b34dd65dad73b3032f28352f114da9d67b854ffff39250",
    "prior": "60ccc6007510c1125a5dee8612f0a3474c2d7e5c21f931745a58a8d4e2077d7b",
    "word": "4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a",
}
PAYLOAD = "9aa8d6b054ba7eb2289d052c1079b16be518d2f0fbfb244569fa18e3733acdac"
PROTECTED = {319, 863, 1355, 1568}


def unique(pairs):
    values = dict(pairs)
    if len(values) != len(pairs):
        raise ValueError("Duplicate JSON key")
    return values


def checked(path, name):
    raw = path.read_bytes()
    if sha256(raw).hexdigest() != PINS[name]:
        raise ValueError(f"Changed input {name}")
    if name == "word":
        raw = decompress(raw)
        assert sha256(raw).hexdigest() == PAYLOAD
    return loads(raw, object_pairs_hook=unique)


@cache
def coefficient(value):
    q = Fraction(value)
    if not q or not q.denominator % PRIME:
        raise ValueError("Zero native scalar or nonunit denominator")
    return q.numerator * pow(q.denominator, -1, PRIME) % PRIME, q.denominator


def axpy(dst, src, scalar):
    for column, value in src.items():
        current = (dst.get(column, 0) + scalar * value) % PRIME
        if current:
            dst[column] = current
        else:
            dst.pop(column, None)


def rank_witness(rows):
    """Use greatest available columns, preserving the order of accepted rows."""
    basis = []
    determinant = 1
    for row in rows:
        reduced = row.copy()
        for pivot, inverse, earlier in basis:
            if (value := reduced.get(pivot, 0)):
                axpy(reduced, earlier, -value*inverse)
        if reduced:
            pivot = max(reduced)
            diagonal = reduced[pivot]
            determinant = determinant * diagonal % PRIME
            basis.append((pivot, pow(diagonal, -1, PRIME), reduced))
    rank = len(basis)
    if rank != len(rows):
        return {"status":"modular_rank_drop","modular_rank":rank}
    # In pivot insertion order, the selected original columns become upper
    # triangular under the same determinant-preserving row additions.
    assert determinant
    columns = [p for p,_,_ in basis]
    return {"status":"no_nonzero_pure_prefix","modular_rank":rank,
            "minor_columns":columns,"minor_determinant_mod_prime":determinant}


def controls():
    assert all(PRIME % divisor for divisor in range(2, isqrt(PRIME)+1))
    # The first selected column is 8, so the minor order swaps the natural axes.
    proof = rank_witness([{3:2,8:1},{3:3,8:4}])
    assert proof["minor_columns"] == [8,3] and proof["minor_determinant_mod_prime"] == PRIME-5
    assert rank_witness([{3:2,8:1},{3:6,8:3}]) == {"status":"modular_rank_drop","modular_rank":1}
    assert rank_witness([{},{}])["modular_rank"] == 0
    row = {1:1, 2:3}
    axpy(row,{2:1,9:2},coefficient("-3")[0])
    assert row == {1:1,9:PRIME-6}
    try:
        coefficient("1/65537")
    except ValueError:
        pass
    else:
        raise AssertionError("Nonunit denominator was accepted")
    return ["nontrivial_signed_minor","planted_rank_drop","zero_rows","signed_cancellation","nonunit_denominator_rejected"]


def admission(price, geometry, prior):
    assert price["head"] == geometry["head"] == prior["head"] == HEAD
    assert geometry["word_sha256"] == price["word_sha256"] == prior["pins"]["word"] == PINS["word"]
    assert geometry["price_sha256"] == prior["pins"]["price"] == PINS["price"]
    assert prior["pins"]["geometry"] == PINS["geometry"] and prior["prime"] == 65521
    assert geometry["status"] == "EXHAUSTED" and geometry["visited_events"] == 76466
    assert geometry["ranks"] == [4,5] and geometry["bank_cap"] == 24
    chosen = {tuple(x["key"]):x for x in geometry["selected"]}
    keys = [tuple(k) for k in geometry["unvisited_keys"]]
    entire = {tuple(k) for k in geometry["all_representative_keys"]}
    assert len(chosen) == 24 and len(keys) == len(set(keys)) == 4183
    assert len(entire) == 4207 and not chosen.keys() & set(keys) and entire == chosen.keys() | set(keys)
    previous = {tuple(r["key"]):r for r in prior["results"]}
    assert previous.keys() == chosen.keys() and not prior["selected_unresolved"]
    for k, row in chosen.items():
        record = previous[k]
        assert all(record[field] == row[field] for field in ("key","public","owned","pivots"))
        assert record["status"] == "no nonzero pure prefix" and record["minor"]["determinant_mod_prime"]
    return keys, chosen


def exterior_rows(word, cohort, keys, chosen, deadline, results, previous, progress):
    n = word["public"]
    owners = word["owned_fields"]
    initial, final = word["initial"], word["final"]
    assert (n, owners, len(word["program"])) == (1501,68,76466)
    mains = set(word["live"]) | {r+112 for r in word["live"]}
    mains.update(word["hosted"]["X2"],word["hosted"]["Y2"])
    expected = {r for r,(a,z) in enumerate(zip(initial,final,strict=True))
                if (a,z)==(3,127) and r not in mains | PROTECTED}
    assert expected == cohort and len(cohort) == 615
    frames = word["frames"]

    @cache
    def space(chart):
        values = {0}
        for v in frames[chart]:
            assert v not in values
            values.update(v ^ x for x in tuple(values))
        return values

    banks = defaultdict(set)
    states = list(initial) + [None]*owners
    revision = [0]*len(states)
    for r,c in enumerate(initial):
        banks[c].add(r)
    rows = [({r:1} if r not in cohort else {}) for r in range(n)] + [None]*owners
    requests = defaultdict(list)
    for t,c in [*keys,*chosen]:
        assert len(frames[c]) in (4,5) and space(3) < space(c) < space(127)
        requests[t].append(c)

    fresh = set()
    cache_by_rows = {}
    denoms = set()
    moves = Counter()
    tape = word["program"]
    for t in range(len(tape)+1):
        if t % 128 == 0 and monotonic() >= deadline:
            raise TimeoutError("normalized exterior replay")
        progress["first_unvisited_event"] = t
        for c in requests.get(t,()):
            if monotonic() >= deadline:
                raise TimeoutError("frozen bank rank")
            key = (t,c)
            public = sorted(r for r in banks[c] if r<n)
            owned = sorted(r for r in banks[c] if r>=n)
            eligible = sorted(set(public)&cohort)
            assert public and eligible
            if t:
                op = tape[t-1]
                incident = op[2:4] if op[0]=="MOVE" else op[-1:]
                assert c in incident
            signature = tuple((r,revision[r]) for r in public)
            if signature not in cache_by_rows:
                cache_by_rows[signature] = rank_witness([rows[r] for r in public])
            rank = cache_by_rows[signature]
            record = dict(key=list(key),chart_rank=len(frames[c]),public=public,owned=owned,pivots=eligible,**rank)
            if key in chosen:
                assert all(record[k] == chosen[key][k] for k in ("key","public","owned","pivots"))
                previous[key] = record
            else:
                results[key] = record
        if t == len(tape):
            break
        op,d,*args = tape[t]
        assert 0 <= d < len(states)
        old = states[d]
        if op=="MOVE":
            a,b,owned = args
            assert old == a and owned == (d>=n)
            assert space(a)<space(b) or owned and space(b)<space(a)
            moves[abs(len(frames[a])-len(frames[b]))] += 1
            banks[a].remove(d)
            states[d]=b
            banks[b].add(d)
            fresh.discard(d)
            continue
        if op=="INIT":
            assert d>=n and old is None and rows[d] is None
            states[d]=args[0]
            banks[args[0]].add(d)
            rows[d]={}
            fresh.add(d)
        elif op=="CLEAR":
            assert d>=n and old==args[0] and rows[d] is not None
            banks[old].remove(d)
            states[d]=rows[d]=None
            fresh.discard(d)
        else:
            assert old==args[-1] and rows[d] is not None and op in ("SCALE","ADD","COPY")
            scale,denominator=coefficient(args[-2])
            denoms.add(denominator)
            if op=="SCALE":
                rows[d]={i:v*scale%PRIME for i,v in rows[d].items() if v*scale%PRIME}
            else:
                s=args[0]
                assert d!=s and states[s]==old and rows[s] is not None
                if op=="COPY":
                    assert d>=n and d in fresh and not rows[d]
                axpy(rows[d],rows[s],scale)
            fresh.discard(d)
        revision[d]+=1

    assert states == list(final)+[None]*owners and not fresh
    assert dict(moves)=={1:4000,2:853,3:829,4:223,5:345,6:14,7:10,8:5}
    progress.update(first_unvisited_event=None, literal_events_replayed=len(tape),
                    distinct_exterior_row_sets=len(cache_by_rows), denominator_units=sorted(denoms),
                    native_paid_histogram=dict(moves))


def main():
    parser=ArgumentParser(description=__doc__)
    for k in PINS:
        parser.add_argument("--"+k,type=Path)
    parser.add_argument("--controls-only",action="store_true")
    args=parser.parse_args()
    if not __debug__:
        raise RuntimeError("Run with assertions")
    if args.controls_only:
        print(dumps(controls()))
        return
    if not all(getattr(args,k) for k in PINS):
        parser.error("All four explicit inputs are required")

    def stop(*_):
        raise TimeoutError("hard 35-second cap")

    keys, chosen, results, previous = [], {}, {}, {}
    progress = {}
    checks = []
    timed_out = None
    signal(SIGALRM,stop)
    alarm(35)
    deadline=monotonic()+33
    try:
        checks = controls()
        price = checked(args.price,"price")
        geometry = checked(args.geometry,"geometry")
        prior = checked(args.prior,"prior")
        keys,chosen = admission(price,geometry,prior)
        word = checked(args.word,"word")
        exterior_rows(word,set(price["endpoint_cohort"]),keys,chosen,deadline,results,previous,progress)
    except TimeoutError as exc:
        timed_out = str(exc)
    finally:
        alarm(0)
    tested = [results[k] for k in keys if k in results]
    tested_prior = [previous[k] for k in chosen if k in previous]
    unvisited = [list(k) for k in keys if k not in results]
    control_unvisited = [list(k) for k in chosen if k not in previous]
    drops = [r["key"] for r in tested if r["status"]=="modular_rank_drop"]
    control_drops = [r["key"] for r in tested_prior if r["status"]=="modular_rank_drop"]
    print(dumps(dict(head=HEAD,pins=PINS,prime=PRIME,case_cap=4183,runner_cap_seconds=35,
        controls=checks,prior_24=tested_prior,prior_unvisited=control_unvisited,prior_rank_drops=control_drops,
        tested=tested,unvisited=unvisited,rank_drops=drops,disposition_counts=dict(Counter(r["status"] for r in tested)),
        actual_full_rank_only=True,timeout=timed_out,**progress),indent=2,sort_keys=True))
    if timed_out or control_drops or control_unvisited:
        raise SystemExit(2)


if __name__=="__main__":
    main()
