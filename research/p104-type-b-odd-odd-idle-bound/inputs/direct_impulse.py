"""Independent exact direct interval projector comparison for R85."""
from argparse import ArgumentParser
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from time import monotonic

PRICE = "33aad506112912ddf0721a2b007d9194eaa02e5792aceda2f9774f8838511262"
ADMISSION = "c95300e9bca27e44a25c82d794f88cbf70757c142806b0e4c590ea29feb81a13"
CALLER = "255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc"
HEAD = "aaeec8c0acf01e99a5f331ef363a698d9c084ace"
CAP, SECONDS = 180, 20


class Capped(Exception):
    pass


def need(condition, text):
    if not condition:
        raise ValueError(text)


def read(path, expected):
    raw = path.read_bytes()
    need(sha256(raw).hexdigest() == expected, "changed input " + path.name)
    return loads(raw)


def gates(event, offset, q):
    family, op, *a = event
    if family == "J":
        u, v, l, r = a[1]
        u, v = u - offset, v - offset
        return [("add", u, v, q * Q(l)), ("add", v, u, Q(r) / q)]
    if family != "B":
        need(family == "A", "unknown event family")
        return []
    dest, *tail = a
    dest -= offset
    if op == "ADD":
        return [("add", dest, tail[0] - offset, Q(tail[1]))]
    if op == "QUERY":
        return [("add", dest, tail[0] - offset, q ** tail[1])]
    if op == "SWAP":
        return [("swap", dest, tail[0] - offset, Q(1))]
    if op == "SCALE":
        return [("scale", dest, dest, Q(tail[0]))]
    if op == "IDLE_ODD":
        return [("scale", dest, dest, q ** tail[1])]
    need(op in ("IDLE_ONE", "LAMBDA"), "unknown Type B op")
    return []


def basis(n, i):
    return [Q(k == i) for k in range(n)]


def apply(op, vector, transpose=False):
    kind, d, s, c = op
    if kind == "add":
        if transpose:
            d, s = s, d
        if vector[s]:
            vector[d] += c * vector[s]
    elif kind == "scale":
        vector[d] *= c
    else:
        need(kind == "swap", "bad gate")
        vector[d], vector[s] = vector[s], vector[d]


def between(items, early_role, late_role, n):
    column = basis(n, early_role)
    for op in items:
        apply(op, column)
    for i, x in enumerate(column):
        if i != late_role and x:
            return "column", i, x
    row = basis(n, late_role)
    for op in reversed(items):
        apply(op, row, True)
    for i, x in enumerate(row):
        if i != early_role and x:
            return "row", i, x
    need(column[late_role] == row[early_role] and column[late_role], "singular interval action")
    return None


def controls():
    need(between([("swap", 0, 1, Q(1))], 0, 1, 2) is None, "valid swapped projector rejected")
    need(between([("add", 1, 0, Q(-2))], 0, 0, 2) == ("column", 1, Q(-2)),
         "mixed impulse column not rejected")
    need(between([("add", 0, 1, Q(-3, 2))], 0, 0, 2) == ("row", 1, Q(-3, 2)),
         "mixed covector row not rejected")
    return ["swapped projector", "negative column shear", "fractional row shear"]


def literal_stock(events, offset):
    odd, even = {}, {}
    for i, e in enumerate(events):
        if e[:2] == ["B", "IDLE_ODD"]:
            need(len(e[3]) == 1 and e[4:] == [-1], "unexpected signed odd idle")
            odd[i] = [e[2] - offset, sorted(e[3])]
        if e[:2] == ["B", "IDLE_ONE"]:
            even[i] = [e[2] - offset, sorted(e[3])]
    return odd, even


def main(args):
    tests = controls()
    price, admission = read(args.price, PRICE), read(args.admission, ADMISSION)
    need(price["head"] == admission["head"] == HEAD and admission["exit"] == 0 and
         price["caller_sha256"] == CALLER and price["limits"]["first_cases"] == CAP and
         price["limits"]["first_seconds"] == SECONDS, "price mismatch")
    started = monotonic()
    caller = read(args.caller, CALLER)
    data = caller["types"]["B"]
    n, off = data["roles"], data["offset"]
    need((caller["stages"], n, off, len(data["ports"])) == (17, 36, 36, 8), "wrong Type B contract")
    old, new = literal_stock(caller["events"], off)
    need({str(k): v for k, v in old.items()} == price["odd_jobs"] and
         {str(k): v for k, v in new.items()} == price["even_jobs"], "exact literal census differs")
    keys = [{"odd": o, "even": e, "size": len(b)} for o, (_, a) in sorted(old.items())
            for e, (_, b) in sorted(new.items()) if set(a).isdisjoint(b)]
    need(keys == price["keys"] and len(keys) == CAP, "exact key stock differs")
    q = Q(1)
    flattened = []
    offsets = [0]
    for event in caller["events"]:
        flattened.extend(gates(event, off, q))
        offsets.append(len(flattened))
    for i in range(n):
        vector = basis(n, i)
        for op in flattened:
            apply(op, vector)
        need(vector == basis(n, i), "old exact unit endpoint differs")
    roles = {t: v[0] for t, v in (old | new).items()}
    outcomes = []
    for key in keys:
        if monotonic() - started >= SECONDS - 2:
            break
        a, b = sorted((key["odd"], key["even"]))
        # Original old idles are identity at q=+1, unit body, so both boundaries can be omitted.
        interval = flattened[offsets[a + 1]:offsets[b]]
        witness = between(interval, roles[a], roles[b], n)
        result = {"key": [key["odd"], key["even"]], "mask_size": key["size"],
                  "chronological_roles": [roles[a] + off, roles[b] + off]}
        if witness is None:
            result |= {"status": "provisional_projectors_equal"}
        else:
            side, role, value = witness
            result |= {"status": "excluded", "exact_off_axis": [side, role + off, str(value)]}
        outcomes.append(result)
    unvisited = keys[len(outcomes):]
    return {"status": "CAPPED" if unvisited else "EXHAUSTED", "head": HEAD, "price_sha256": PRICE,
            "caller_sha256": CALLER, "admission_sha256": ADMISSION, "case_cap": CAP,
            "runner_cap_seconds": SECONDS, "q": 1, "body": "unit", "old_endpoint_columns": n,
            "controls": tests, "tested": len(outcomes), "outcomes": outcomes,
            "counts": dict(Counter(row["status"] for row in outcomes)), "unvisited": unvisited,
            "survivors": [row["key"] for row in outcomes if row["status"] != "excluded"]}


if __name__ == "__main__":
    p = ArgumentParser()
    for name in ("price", "admission", "caller"):
        p.add_argument("--" + name, type=Path, required=True)
    print(dumps(main(p.parse_args()), sort_keys=True, indent=2))
