"""Independently certify chart-118 bank aliases and exact pairings."""
from collections import defaultdict
from fractions import Fraction as Q
from functools import cache
from gzip import decompress
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from signal import SIGALRM, alarm, signal
from time import monotonic

ROOT = Path(__file__).resolve().parent
PINS = {
    "inputs/R128-PRICE.json": "8083c540876bbc7c61fc05eaa8e5796cb96d58ea123638931f6cb60ce0507849",
    "inputs/R89-PAIR.json": "4b8f2963ae0ef7bd357c3129e8287f79c5c1fccca6375c41e35fa01c476cb2ae",
    "inputs/OLD-WITNESS.json": "5be60a09485041744919696121ae27e57a1aa9de437a2c4494d5fc569af4cdb4",
    "inputs/R128-two_keys.py": "b6d97bbe22649b18e745ae70cba60542beba1d91e34f9f827b28fe29854265f2",
    "inputs/7334-WORD.json.gz": "4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a",
}
PAYLOAD = "9aa8d6b054ba7eb2289d052c1079b16be518d2f0fbfb244569fa18e3733acdac"
CHART, PIVOT, CASE_CAP = 118, 635, 74
HEAD = "aaeec8c0acf01e99a5f331ef363a698d9c084ace"
CALLER = "07a76c5e2738882c0cb322278e56f6cae3c9885d"


def unique(items):
    result = dict(items)
    if len(result) != len(items):
        raise ValueError("duplicate JSON key")
    return result


def checked(name):
    raw = (ROOT / name).read_bytes()
    if sha256(raw).hexdigest() != PINS[name]:
        raise ValueError(f"changed dependency {name}")
    return raw


@cache
def scalar(value):
    return Q(value)


def axpy(row, other, q):
    if q:
        for j, value in other.items():
            updated = row.get(j, 0) + q*value
            if updated:
                row[j] = updated
            else:
                row.pop(j, None)


def dot(a, b):
    return sum(value*b.get(j, 0) for j, value in a.items())


def stop():
    raise TimeoutError("35-second exact cap")


def hard_stop(*_):
    stop()


def cohorts(word, requests, deadline):
    tape = word["program"]
    n, owned = word["public"], word["owned_fields"]
    state = word["initial"][:] + [None]*owned
    seen, contacts, epoch = {}, [], 0
    lo, hi = min(requests), max(requests)
    for t, event in enumerate(tape):
        if t % 256 == 0 and monotonic() >= deadline:
            stop()
        if t in requests:
            residents = tuple(r for r, frame in enumerate(state) if frame == CHART)
            assert residents == requests[t] and PIVOT in residents and max(residents) < n
            seen[t] = (epoch, residents)
        if t == hi:
            break
        op, d, *args = event
        before = state[d]
        if op == "MOVE":
            assert args[0] == before and args[2] == (d >= n)
            after = args[1]
        elif op == "INIT":
            assert before is None and d >= n
            after = args[0]
        elif op == "CLEAR":
            assert before == args[0] and d >= n
            after = None
        else:
            after = before
            assert op in ("ADD", "COPY", "SCALE") and after == args[-1]
            if op in ("ADD", "COPY"):
                assert state[args[0]] == before and args[0] != d
        if t >= lo and CHART in (before, after):
            invertible = d < n and (op == "SCALE" or (op == "ADD" and args[0] < n)) and bool(scalar(args[-2]))
            if not invertible:
                epoch += 1
            contacts.append({"clock": t, "event": event, "within_epoch": invertible})
        state[d] = after
    assert set(seen) == set(requests)
    grouped = defaultdict(list)
    for t, key in seen.items():
        grouped[key].append(t)
    return list(grouped.items()), contacts


def trace(word, cut, bank, deadline, reverse):
    tape = word["program"]
    n, owned = word["public"], word["owned_fields"]
    values = [{} for _ in range(n+owned)]
    for role in bank:
        values[role] = {role: Q(1)}
    clocks = range(cut-1, -1, -1) if reverse else range(cut, len(tape))
    for t in clocks:
        if t % 256 == 0 and monotonic() >= deadline:
            stop()
        op, d, *args = tape[t]
        if op in ("CLEAR", "INIT"):
            values[d] = {}
        elif op == "SCALE" and values[d]:
            q = scalar(args[0])
            values[d] = {j:q*v for j,v in values[d].items() if q*v}
        elif op in ("ADD", "COPY"):
            source, factor = args[:2]
            q = scalar(factor)
            if reverse:
                axpy(values[source], values[d], q)
                if op == "COPY":
                    values[d] = {}
            elif op == "COPY":
                values[d] = {j:q*v for j,v in values[source].items() if q*v}
            else:
                axpy(values[d], values[source], q)
    responses = {r:{} for r in bank}
    for coordinate, data in enumerate(values[:n]):
        for role, value in data.items():
            responses[role][coordinate] = value
    return responses


def kernel(columns, allowed):
    basis, pure = {}, []
    for role, full in columns.items():
        row = {j:v for j,v in full.items() if j not in allowed}
        combo = {role:Q(1)}
        for pivot, (old, old_combo) in sorted(basis.items()):
            q = -row.get(pivot, 0)
            axpy(row, old, q)
            axpy(combo, old_combo, q)
        if row:
            pivot = min(row)
            q = row[pivot]
            basis[pivot] = ({j:v/q for j,v in row.items()}, {j:v/q for j,v in combo.items()})
        else:
            image = {}
            for j, q in combo.items():
                axpy(image, columns[j], q)
            assert set(image) <= allowed
            pure.append((combo, image))
    assert len(basis) + len(pure) == len(columns)
    return len(basis), pure


def printed(vector):
    return {j:str(v) for j,v in sorted(vector.items())}


def controls(old):
    vectors = {k:{int(j):Q(v) for j,v in old[k].items()} for k in "abcd"}
    assert (old["pivot"], old["frame"], old["cut_before"]) == (635, 118, 37473)
    assert dot(vectors["a"], vectors["b"]) == dot(vectors["c"], vectors["d"]) == 1
    rank, pure = kernel({4:{0:Q(2),5:Q(1)}, 6:{5:Q(1)}}, {0})
    assert rank == 1 and pure == [({6:Q(1),4:Q(-1)}, {0:Q(-2)})]
    assert dot(vectors["c"], {j:2*v for j,v in vectors["d"].items()}) == 2
    return ["historical exact unit pair", "planted exact exterior kernel", "wrong endpoint pairing"]


def main():
    assert __debug__
    signal(SIGALRM, hard_stop)
    alarm(35)
    deadline = monotonic()+32
    price, prior, old, _source, packed = map(checked, PINS)
    price, prior, old = [loads(raw, object_pairs_hook=unique) for raw in (price, prior, old)]
    assert price["head"] == prior["head"] == HEAD and price["caller"] == CALLER
    assert Q(price["complete_probe"][0]) > 0
    tests = controls(old)
    rows = [r for r in prior["results"] if r["key"][1] == CHART and PIVOT in r["pivots"]]
    requests = {r["key"][0]:tuple(r["public"]) for r in rows}
    keys = [r["key"] for r in price["selected"]] + price["unvisited"]
    assert len(requests) == len(rows) == len(keys) == CASE_CAP
    assert set(requests) == {k[0] for k in keys} and all(k[1] == CHART for k in keys)
    assert all(not r["owned"] and r["disposition"] == "rank drop" for r in rows)
    raw = decompress(packed)
    assert sha256(raw).hexdigest() == PAYLOAD
    word = loads(raw, object_pairs_hook=unique)
    assert (word["public"], word["owned_fields"], len(word["program"])) == (1501,68,76466)
    cohort = set(price["endpoint_cohort"])
    assert len(cohort) == 615 and PIVOT in cohort and 631 not in cohort
    assert all((word["initial"][r],word["final"][r]) == (3,127) for r in cohort)
    assert [len(word["frames"][r]) for r in (3,118,127)] == [0,5,9]
    classes, contacts = cohorts(word, requests, deadline)
    results = []
    for (_epoch, bank), aliases in classes:
        cut = aliases[0]
        f = trace(word,cut,bank,deadline,True)
        s = trace(word,cut,bank,deadline,False)
        fp, pure_f = kernel(f,cohort)
        sp, pure_s = kernel(s,cohort)
        local = [[str(dot(a,b)) for b,_ in pure_s] for a,_ in pure_f]
        endpoint = [[str(dot(c,d)) for _,d in pure_s] for _,c in pure_f]
        zero = all(v=="0" for matrix in (local,endpoint) for row in matrix for v in row)
        results.append(dict(representative=[cut,CHART], keys=[[t,CHART] for t in aliases], bank=bank,
            prefix_rank=fp, suffix_rank=sp,
            pure_prefix=[dict(a=printed(a),c=printed(c)) for a,c in pure_f],
            pure_suffix=[dict(b=printed(b),d=printed(d)) for b,d in pure_s],
            local=local, endpoint=endpoint, status="zero pairing" if zero else "requires exact pairing test"))
    excluded = sum(len(row["keys"]) for row in results if row["status"] == "zero pairing")
    alarm(0)
    print(dumps(dict(head=HEAD,caller=CALLER,pins=PINS,controls=tests,cap_cases=CASE_CAP,cap_seconds=35,
        representative_count=len(results),case_count=len(requests),contacts=contacts,results=results,
        excluded=excluded,unresolved=CASE_CAP-excluded,
        scope="Relaxed exact rational normalized prefix and suffix pairing, original fixed paid paths."),
        indent=2,sort_keys=True))


if __name__ == "__main__":
    main()
