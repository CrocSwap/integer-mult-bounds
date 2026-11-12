"""Verify the 24 frozen rank-four/five banks by backward modular covectors."""
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
PINS = {
    "price": "b4bf8e00a8289f03b1da731fb3ab563a771d88d875e0da73acf70954df2f2c56",
    "geometry": "238135413a5646cb39b34dd65dad73b3032f28352f114da9d67b854ffff39250",
    "primary": "4000abaf88ad7ecb1f76a59b9eb5bafc64d0c3db75e6af159826a4431ca8f884",
    "word": "4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a",
}
PAYLOAD = "9aa8d6b054ba7eb2289d052c1079b16be518d2f0fbfb244569fa18e3733acdac"
PRIME = 65521
PROTECTED = {319, 863, 1355, 1568}


def unique(pairs):
    value = dict(pairs)
    assert len(value) == len(pairs), "Duplicate JSON key"
    return value


def checked(path, name):
    raw = path.read_bytes()
    if sha256(raw).hexdigest() != PINS[name]:
        raise ValueError(f"Changed dependency {name}")
    if name == "word":
        raw = decompress(raw)
        assert sha256(raw).hexdigest() == PAYLOAD
    return loads(raw, object_pairs_hook=unique)


@cache
def coefficient(value):
    q = Fraction(value)
    assert q and q.denominator % PRIME, "Nonunit native denominator"
    return q.numerator * pow(q.denominator, -1, PRIME) % PRIME, q.denominator


def chart_audit(word, chosen, cohort, deadline):
    n = word["public"]
    frames = word["frames"]
    states = list(word["initial"]) + [None] * word["owned_fields"]
    fresh = set()
    moves = Counter()
    denoms = set()
    requests = defaultdict(list)

    @cache
    def span(chart):
        space = {0}
        for v in frames[chart]:
            assert v not in space
            space.update(v ^ w for w in tuple(space))
        return space

    at_cut = defaultdict(list)
    for k, row in enumerate(chosen):
        t, chart = row["key"]
        assert len(frames[chart]) in (4, 5) and span(3) < span(chart) < span(127)
        at_cut[t].append((k, row))
    tape = word["program"]
    for t in range(len(tape) + 1):
        if t % 128 == 0 and monotonic() >= deadline:
            raise TimeoutError("literal selected-bank occupancy")
        for k, row in at_cut.get(t, ()):
            chart = row["key"][1]
            public = [r for r in range(n) if states[r] == chart]
            owned = [r for r in range(n, len(states)) if states[r] == chart]
            assert public == row["public"] == row["pivots"] and len(public) == 2
            assert owned == row["owned"] == [] and all(r in cohort for r in public)
            if t:
                prev = tape[t-1]
                touched = prev[2:4] if prev[0] == "MOVE" else prev[-1:]
                assert chart in touched
            for i, r in enumerate(public):
                requests[t].append((r, 2*k+i))
        if t == len(tape):
            break
        op, d, *args = tape[t]
        assert 0 <= d < len(states)
        if op == "INIT":
            assert d >= n and states[d] is None
            states[d] = args[0]
            fresh.add(d)
        elif op == "CLEAR":
            assert d >= n and states[d] == args[0]
            states[d] = None
            fresh.discard(d)
        elif op == "MOVE":
            a,b,owned = args
            assert states[d] == a and owned == (d >= n)
            assert span(a) < span(b) or owned and span(b) < span(a)
            moves[abs(len(frames[a])-len(frames[b]))] += 1
            states[d] = b
            fresh.discard(d)
        else:
            assert states[d] == args[-1] and op in ("ADD","COPY","SCALE")
            _, denominator = coefficient(args[-2])
            denoms.add(denominator)
            if op != "SCALE":
                s = args[0]
                assert s != d and states[s] == args[-1]
            if op == "COPY":
                assert d >= n and d in fresh
            fresh.discard(d)
    assert states == word["final"] + [None] * word["owned_fields"] and not fresh
    assert sum(map(len, requests.values())) == 2*len(chosen)
    return requests, dict(moves), sorted(denoms)


def axpy(dst, src, scale):
    for j, value in src.items():
        updated = (dst.get(j, 0) + scale * value) % PRIME
        if updated:
            dst[j] = updated
        else:
            dst.pop(j, None)


def reverse_rows(word, requests, count, deadline):
    n = word["public"]
    active = [{} for _ in range(n + word["owned_fields"])]
    for t in range(max(requests), -1, -1):
        if t % 128 == 0 and monotonic() >= deadline:
            raise TimeoutError("reverse modular prefix")
        if t < len(word["program"]):
            op,d,*args = word["program"][t]
            if op in ("INIT","CLEAR"):
                active[d] = {}
            elif op == "SCALE" and active[d]:
                scale,_ = coefficient(args[0])
                active[d] = {j: value*scale%PRIME for j,value in active[d].items() if value*scale%PRIME}
            elif op in ("ADD","COPY"):
                if active[d]:
                    scale,_ = coefficient(args[-2])
                    axpy(active[args[0]], active[d], scale)
                if op == "COPY":
                    active[d] = {}
        for r,k in requests.get(t, ()):
            axpy(active[r], {k:1}, 1)
    assert not any(active[n:])
    rows = [{} for _ in range(count)]
    for coordinate, weights in enumerate(active[:n]):
        for k,value in weights.items():
            rows[k][coordinate] = value
    return rows


def exterior_minor(rows, cohort):
    assert len(rows) == 2
    a,b = rows
    coords = sorted((a.keys() | b.keys()) - cohort)
    if not coords:
        return None
    j = coords[0]
    for k in coords[1:]:
        matrix = [[a.get(j,0),a.get(k,0)], [b.get(j,0),b.get(k,0)]]
        det = (matrix[0][0]*matrix[1][1]-matrix[0][1]*matrix[1][0]) % PRIME
        if det:
            return {"outside_input_coordinates":[j,k],"modular_matrix":matrix,"determinant_mod_prime":det}
    return None


def controls():
    toy = {"public":3, "owned_fields":1,
           "program":[["INIT",3,0],["COPY",3,1,"-3/2",0],["ADD",0,3,"1",0],
                      ["SCALE",1,"2/5",0],["CLEAR",3,0]]}
    rows = reverse_rows(toy, {5:[(0,0),(1,1)]}, 2, float("inf"))
    assert rows == [{0:1,1:coefficient("-3/2")[0]}, {1:coefficient("2/5")[0]}]
    witness = exterior_minor(rows,{2})
    assert witness["outside_input_coordinates"] == [0,1]
    assert witness["determinant_mod_prime"] == coefficient("2/5")[0]
    assert exterior_minor(rows,{0,2}) is None
    assert exterior_minor([{0:1,1:2},{0:3,1:6}],set()) is None
    try:
        coefficient("1/65521")
    except AssertionError:
        pass
    else:
        raise AssertionError("Nonunit scalar was accepted")
    return ["signed_owned_COPY_and_backward_ADD_SCALE_CLEAR","full_exterior_minor",
            "pure_prefix_survivor_and_dependent_exterior","nonunit_denominator_rejected"]


def main():
    parser = ArgumentParser(description=__doc__)
    for name in PINS:
        parser.add_argument("--"+name, type=Path)
    parser.add_argument("--controls-only", action="store_true")
    args = parser.parse_args()
    assert __debug__
    if args.controls_only:
        print(dumps(controls()))
        return
    assert all(getattr(args,name) for name in PINS)
    start = monotonic()
    deadline = start+23
    tests, chosen, results, denoms = [], [], [], []
    geometry = {}
    compared = False
    interruption = None

    def stop(*_):
        raise TimeoutError("hard 25-second runner cap")
    signal(SIGALRM, stop)
    alarm(25)
    try:
        assert all(PRIME%d for d in range(2,isqrt(PRIME)+1))
        tests = controls()
        price = checked(args.price,"price")
        geometry = checked(args.geometry,"geometry")
        assert price["head"] == geometry["head"] == HEAD and geometry["status"] == "EXHAUSTED"
        assert geometry["price_sha256"] == PINS["price"] and geometry["word_sha256"] == price["word_sha256"] == PINS["word"]
        chosen = geometry["selected"]
        all_keys = {tuple(k) for k in geometry["all_representative_keys"]}
        chosen_keys = {tuple(row["key"]) for row in chosen}
        unvisited = {tuple(k) for k in geometry["unvisited_keys"]}
        assert len(chosen_keys) == len(chosen) == 24 and len(unvisited) == 4183
        assert len(all_keys) == 4207 and all_keys == chosen_keys | unvisited and not chosen_keys & unvisited
        word = checked(args.word,"word")
        assert (word["public"],word["owned_fields"],len(word["program"])) == (1501,68,76466)
        main_roles = set(word["live"]) | {r+112 for r in word["live"]} | set(word["hosted"]["X2"]) | set(word["hosted"]["Y2"])
        cohort = {r for r, ends in enumerate(zip(word["initial"],word["final"],strict=True))
                  if ends == (3,127) and r not in main_roles | PROTECTED}
        assert len(cohort) == 615 and cohort == set(price["endpoint_cohort"])
        requests,hist,denoms = chart_audit(word,chosen,cohort,deadline)
        assert hist == {1:4000,2:853,3:829,4:223,5:345,6:14,7:10,8:5}
        rows = reverse_rows(word,requests,48,deadline)
        for k, bank in enumerate(chosen):
            if monotonic() >= deadline:
                raise TimeoutError("selected exterior minor check")
            row_pair = rows[2*k:2*k+2]
            proof = exterior_minor(row_pair,cohort)
            results.append(bank | {"chart_rank":len(word["frames"][bank["key"][1]]),
                "row_nnz_mod_prime":[len(row) for row in row_pair],
                "status":"no nonzero pure prefix" if proof else "unresolved_modular_rank", "minor":proof})
        primary = checked(args.primary,"primary")
        assert primary["head"] == HEAD and primary["geometry_sha256"] == PINS["geometry"]
        assert primary["price_sha256"] == PINS["price"] and primary["word_sha256"] == PINS["word"]
        by_key = {tuple(row["key"]):row for row in primary["results"]}
        assert len(by_key) == 24 and set(by_key) == chosen_keys
        for row in results:
            expected = by_key[tuple(row["key"])]
            assert all(row[k] == expected[k] for k in ("key","public","owned","pivots"))
            assert expected["prefix_kernel"] == 0 and expected["status"] == "no nonzero pure prefix"
        compared = True
    except TimeoutError as exc:
        interruption = str(exc)
    finally:
        alarm(0)

    unverified = [r["key"] for r in chosen[len(results):]]
    counts = dict(Counter(r["status"] for r in results))
    unresolved = unverified+[r["key"] for r in results if r["minor"] is None]
    print(dumps(dict(head=HEAD, pins=PINS, prime=PRIME, selected_cap=24, runner_cap_seconds=25,
        geometry_banks=geometry.get("eligible_bank_count"), outside_selected_unvisited=len(geometry.get("unvisited_keys",[])),
        selected_unresolved=unresolved, status_counts=counts, denominator_units=denoms,
        independently_checked_public_banks_and_lifetimes=compared, controls=tests, results=results,
        primary_comparison_passed=compared, timeout=interruption),sort_keys=True,indent=2))
    if interruption:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
