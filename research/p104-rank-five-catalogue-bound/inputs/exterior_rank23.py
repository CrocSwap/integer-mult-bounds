"""Exact modular exterior minors for the frozen rank-four/five banks."""
from collections import Counter, defaultdict
from fractions import Fraction
from functools import cache
from gzip import decompress
from hashlib import sha256
import json
from math import isqrt
from pathlib import Path
import sys
from time import monotonic

HEAD = "aaeec8c0acf01e99a5f331ef363a698d9c084ace"
P = 65521
PINS = {
    "inputs/GEOMETRY.json": "238135413a5646cb39b34dd65dad73b3032f28352f114da9d67b854ffff39250",
    "inputs/PRICE.json": "b4bf8e00a8289f03b1da731fb3ab563a771d88d875e0da73acf70954df2f2c56",
    "inputs/7334-WORD.json.gz": "4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a",
}


def unique(items):
    d = dict(items)
    if len(d) != len(items):
        raise ValueError("duplicate JSON key")
    return d


def checked(root, name):
    raw = (root / name).read_bytes()
    if sha256(raw).hexdigest() != PINS[name]:
        raise ValueError(f"changed dependency: {name}")
    return json.loads(decompress(raw) if name.endswith(".gz") else raw,
                      object_pairs_hook=unique)


@cache
def scalar(x):
    q = Fraction(x)
    if q.denominator % P == 0:
        raise ValueError("nonunit native denominator")
    return q.numerator * pow(q.denominator, -1, P) % P


def plus(row, other, c):
    if c:
        for k, x in other.items():
            y = (row.get(k, 0) + c * x) % P
            if y:
                row[k] = y
            else:
                row.pop(k, None)


def exterior_minor(bank, rows, allowed):
    """Use the discovered pivot order as the column order of the minor."""
    basis = []
    determinant = 1
    for role in bank:
        row = {i: x for i, x in rows[role].items() if i not in allowed}
        for k, vector in basis:
            plus(row, vector, -row.get(k, 0))
        if row:
            k = min(row)
            pivot = row[k]
            determinant = determinant * pivot % P
            scale = pow(pivot, -1, P)
            basis.append((k, {i: x * scale % P for i, x in row.items()}))
    rank = len(basis)
    full = rank == len(bank)
    return dict(exterior_rank=rank, columns=[k for k, _ in basis],
                determinant=determinant if full else None,
                disposition="excluded" if full else "rank drop")


def controls():
    bank = [0, 1]
    rows = [{0: 2, 1: 3}, {0: 5, 1: 7}]
    x = exterior_minor(bank, rows, set())
    assert x["determinant"] == P - 1 and x["columns"] == [0, 1]
    rows = [{0: 1, 2: 1}, {1: 1, 2: 1}]
    assert exterior_minor(bank, rows, {0, 1})["disposition"] == "rank drop"
    try:
        scalar(f"1/{P}")
    except ValueError:
        pass
    else:
        raise AssertionError("nonunit denominator admitted")
    return ["determinant sign", "planted nonzero pure prefix", "nonunit denominator rejection"]


def sweep(word, keys, allowed, deadline):
    n = word["public"]
    active = word["initial"] + [None] * word["owned_fields"]
    rows = [{i: 1} for i in range(n)] + [None] * word["owned_fields"]
    requests = defaultdict(list)
    for t, c in keys:
        requests[t].append(c)
    requested = set(keys)
    out = {}
    finished = 0
    for t, e in enumerate(word["program"]):
        if (t % 128 == 0 or t in requests) and monotonic() >= deadline:
            break
        for c in requests.get(t, ()):
            public = [i for i in range(n) if active[i] == c]
            owned = [i for i in range(n, len(active)) if active[i] == c]
            pivots = sorted(set(public) & allowed)
            assert pivots and len(word["frames"][c]) in (2, 3)
            if t:
                prior = word["program"][t - 1]
                charts = prior[2:4] if prior[0] == "MOVE" else prior[-1:]
                assert c in charts
            out[t, c] = dict(key=[t, c], public=public, owned=owned, pivots=pivots,
                             **exterior_minor(public, rows, allowed))
        op, r, *a = e
        if op == "MOVE":
            assert active[r] == a[0] and a[2] == (r >= n)
            active[r] = a[1]
        elif op == "INIT":
            assert active[r] is None and r >= n and rows[r] is None
            active[r], rows[r] = a[0], {}
        elif op == "CLEAR":
            assert active[r] == a[0] and r >= n and rows[r] is not None
            active[r] = rows[r] = None
        elif op == "SCALE":
            assert active[r] == a[1]
            c = scalar(a[0])
            rows[r] = {i: c * x % P for i, x in rows[r].items()} if c else {}
        else:
            s, c, f = a
            assert active[r] == active[s] == f and r != s and op in ("ADD", "COPY")
            if op == "COPY":
                assert r >= n and not rows[r]
            plus(rows[r], rows[s], scalar(c))
        finished = t + 1
    if finished == len(word["program"]):
        assert active == word["final"] + [None] * word["owned_fields"]
        assert requested == out.keys()
    return out, finished


def main():
    deadline = monotonic() + 32
    root = Path(sys.argv[1])
    geom = checked(root, "inputs/GEOMETRY.json")
    price = checked(root, "inputs/PRICE.json")
    word = checked(root, "inputs/7334-WORD.json.gz")
    assert geom["head"] == price["head"] == HEAD
    assert geom["price_sha256"] == PINS["inputs/PRICE.json"]
    assert all(P % i for i in range(2, isqrt(P) + 1))
    allowed = set(price["endpoint_cohort"])
    assert len(allowed) == 615
    chosen = {tuple(r["key"]): r for r in geom["selected"]}
    keys = [tuple(k) for k in geom["unvisited_keys"]]
    assert len(chosen) == 24 and len(set(keys)) == len(keys) == 4183
    assert set(keys) | chosen.keys() == {tuple(k) for k in geom["all_representative_keys"]}
    checks = controls()
    out, finished = sweep(word, list(chosen) + keys, allowed, deadline)
    control_records = []
    for k, earlier in chosen.items():
        if k in out:
            r = out[k]
            assert r["disposition"] == "excluded"
            assert all(r[f] == earlier[f] for f in ("public", "owned", "pivots"))
            control_records.append(r)
    tested = [out[k] for k in keys if k in out]
    missing = [k for k in keys if k not in out]
    print(json.dumps(dict(head=HEAD, pins=PINS, prime=P, phase="normalized rational cocharts",
        limit_cases=4183, limit_seconds=32, events_processed=finished,
        status="CAPPED" if missing or len(control_records) != 24 else "EXHAUSTED",
        controls=checks, prior_controls=control_records, results=tested,
        counts=Counter(r["disposition"] for r in tested), unvisited=missing,
        rank_drops=[r["key"] for r in tested if r["disposition"] == "rank drop"]),
        separators=(",", ":"), sort_keys=True))


if __name__ == "__main__":
    main()
