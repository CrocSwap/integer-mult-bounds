"""Exact first-derivative necessity for two fixed Type B idle fusions."""
from collections import Counter
from fractions import Fraction
from gzip import decompress
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from runpy import run_path
from signal import SIGALRM, alarm, signal
from sys import argv
from time import monotonic

ROOT = Path(__file__).resolve().parents[1]
PINS = {
    "plan/PRICE.json": "3633b57cc096fe511daac7c23ead578f839096df8b6ef62651844c2e62a3f2a6",
    "inputs/7113-CALLER.json.gz": "7e8038559cd158f6e32ef6d1a3bf15ab6a8ecc2239af32ab1699511ac28e26d9",
    "inputs/direct_impulse.py": "d04426aed9528aedc6400d384d7fd13c6531e5e3e6592a7eea4faee46c61e004",
}


def unique(items):
    result = dict(items)
    if len(result) != len(items):
        raise ValueError("duplicate JSON key")
    return result


def checked(rel):
    data = (ROOT / rel).read_bytes()
    if sha256(data).hexdigest() != PINS[rel]:
        raise ValueError(f"changed dependency {rel}")
    return data


def identity(n):
    return [[Fraction(i == j) for j in range(n)] for i in range(n)]


def update(gate, rows, inverse_columns):
    op, d, s, value = gate
    if op == "add":
        rows[d] = [x + value * y for x, y in zip(rows[d], rows[s])]
        inverse_columns[s] = [x - value * y for x, y in zip(inverse_columns[s], inverse_columns[d])]
    elif op == "scale":
        assert value
        rows[d] = [value * x for x in rows[d]]
        inverse_columns[d] = [x / value for x in inverse_columns[d]]
    else:
        assert op == "swap"
        rows[d], rows[s] = rows[s], rows[d]
        inverse_columns[d], inverse_columns[s] = inverse_columns[s], inverse_columns[d]


def projector(column, row):
    return {(i, j): x * y for i, x in enumerate(column) if x for j, y in enumerate(row) if y}


def difference(projectors, pairs):
    total = {}
    for odd, even in pairs:
        for site, sign in ((odd, 1), (even, -1)):
            for key, value in projectors[site].items():
                total[key] = total.get(key, 0) + sign * value
    return {k: v for k, v in total.items() if v}


def controls():
    ident = identity(3)
    rows, columns = identity(3), identity(3)
    for op in [("add", 0, 1, Fraction(-3, 2)), ("swap", 1, 2, Fraction(1)),
               ("scale", 0, 0, Fraction(2, 3))]:
        update(op, rows, columns)
    assert [[sum(a * b for a, b in zip(row, col)) for col in columns] for row in rows] == ident
    p, q = projector(ident[0], ident[0]), projector(ident[1], ident[1])
    values = {1: p, 2: q, 3: q, 4: p}
    assert difference(values, [(1, 2)]) and not difference(values, [(1, 2), (3, 4)])
    assert set([1, 2]) ^ set([2, 3]) == {1, 3}
    return ["exact inverse conjugation", "two nonzero differences that cancel", "unequal mask variable"]


def walk(caller, engine, requested, deadline):
    data = caller["types"]["B"]
    n, offset = data["roles"], data["offset"]
    assert (caller["stages"], n, offset, len(data["ports"])) == (17, 36, 36, 8)
    events = caller["events"]
    odd, even = engine["literal_stock"](events, offset)
    assert len(odd) == 4 and len(even) == 60
    roles = odd | even
    for item in requested:
        masks = [even[e][1] for _, e in item["fusions"]]
        assert masks[0] == masks[1] == item["even_mask"]
        assert len({c for pair in item["fusions"] for c in pair}) == 4
        assert all(set(odd[o][1]).isdisjoint(even[e][1]) for o, e in item["fusions"])
    rows, columns = identity(n), identity(n)
    values = {}
    q = Fraction(1)
    for t, event in enumerate(events):
        if t % 128 == 0 and monotonic() >= deadline:
            raise TimeoutError("literal projector walk cap")
        if t in roles:
            role = roles[t][0]
            values[t] = projector(columns[role], rows[role])
        for gate in engine["gates"](event, offset, q):
            update(gate, rows, columns)
    assert rows == columns == identity(n) and len(values) == 64
    return values, len(events)


def stop(*_):
    raise TimeoutError("hard 25-second cap")


def main():
    assert __debug__
    price = loads(checked("plan/PRICE.json"), object_pairs_hook=unique)
    keys = price["equal_mask_keys"]
    assert len(keys) == 210 and len(keys[0]["even_mask"]) == len(keys[1]["even_mask"]) == 8
    tests = controls()
    checked("inputs/direct_impulse.py")
    if argv[1:] == ["--controls-only"]:
        print(dumps({"controls": tests, "cases": len(keys), "priority": keys[:2]}, sort_keys=True))
        return 0
    assert not argv[1:]
    signal(SIGALRM, stop)
    alarm(25)
    deadline = monotonic() + 23
    results, events, reason = [], None, None
    try:
        payload = decompress(checked("inputs/7113-CALLER.json.gz"))
        assert sha256(payload).hexdigest() == price["caller_sha256"]
        caller = loads(payload, object_pairs_hook=unique)
        engine = run_path(str(ROOT / "inputs/direct_impulse.py"))
        projections, events = walk(caller, engine, keys, deadline)
        for item in keys:
            if monotonic() >= deadline:
                raise TimeoutError("paired matrix cap")
            values = difference(projections, item["fusions"])
            witness = None
            if values:
                row, column = min(values)
                witness = [row + 36, column + 36, str(values[row, column])]
            results.append(item | {"status": "exact derivative exclusion" if witness else "first derivative zero",
                                   "witness": witness, "nonzero_coordinates": len(values)})
    except TimeoutError as error:
        reason = str(error)
    finally:
        alarm(0)
    print(dumps({
        "pins": PINS, "head": price["head"], "caller": price["caller"], "q": 1, "body": "unit",
        "controls": tests, "events": events, "cap_cases": 210, "cap_seconds": 25,
        "counts": Counter(r["status"] for r in results), "results": results,
        "unvisited": keys[len(results):], "timeout": reason,
    }, sort_keys=True, indent=2))
    return 124 if reason else 0


if __name__ == "__main__":
    raise SystemExit(main())
