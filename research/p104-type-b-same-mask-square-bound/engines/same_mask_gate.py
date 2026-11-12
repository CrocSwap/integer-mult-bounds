"""Exact chronological rank-one projector gate for repeated Type B singleton idles."""

from argparse import ArgumentParser
from collections import Counter, defaultdict
from fractions import Fraction
from hashlib import sha256
from itertools import combinations
from json import dumps, loads
from pathlib import Path
from signal import alarm
from time import monotonic

PRICE = "price/PRICE.json"
CALLER = "lead/inputs/7113-CALLER.json"
ADMISSION = "lead/inputs/7334-ADMITTED.json"
PINS = {
    PRICE: "57687d0cdb758cacaff681497c6d4834ec071749156c05b1d74d326cda9c958d",
    CALLER: "255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc",
    ADMISSION: "c95300e9bca27e44a25c82d794f88cbf70757c142806b0e4c590ea29feb81a13",
}
HEAD = "aaeec8c0acf01e99a5f331ef363a698d9c084ace"
CALLER_HEAD = "07a76c5e2738882c0cb322278e56f6cae3c9885d"
CASE_CAP, HARD_SECONDS, SOFT_SECONDS = 9, 20, 18
Q = Fraction


def unique(pairs):
    result = dict(pairs)
    if len(result) != len(pairs):
        raise ValueError("duplicate JSON key")
    return result


def authenticate(root):
    inputs = {}
    for rel, pin in PINS.items():
        inputs[rel] = (root / rel).read_bytes()
        if sha256(inputs[rel]).hexdigest() != pin:
            raise ValueError(f"changed dependency {rel}")
    return inputs


def identity(n):
    return [[Q(i == j) for j in range(n)] for i in range(n)]


def axpy(a, b, c):
    return [x + c*y for x, y in zip(a,b,strict=True)]


def add(rows, inverse_columns, d, s, c):
    assert d != s
    rows[d] = axpy(rows[d], rows[s], c)
    inverse_columns[s] = axpy(inverse_columns[s], inverse_columns[d], -c)


def scale(rows, inverse_columns, d, c):
    assert c
    rows[d] = [c*x for x in rows[d]]
    inverse_columns[d] = [x/c for x in inverse_columns[d]]


def update(rows, inverse_columns, event, offset):
    family = event[0]
    n = len(rows)
    if family == "J":
        _, stage, roles_a, (a, b, left, right) = event
        assert 1 <= stage <= 17 and len(roles_a) == 4
        a, b = a-offset, b-offset
        assert 0 <= a < n and 0 <= b < n
        add(rows, inverse_columns, a, b, Q(left))
        add(rows, inverse_columns, b, a, Q(right))
        return
    if family == "A":
        return
    assert family == "B"
    _, op, d, *tail = event
    d -= offset
    assert 0 <= d < n
    if op in ("ADD","QUERY","SWAP"):
        s = tail[0] - offset
        assert 0 <= s < n and s != d
        if op == "SWAP":
            assert len(tail) == 1
            rows[d], rows[s] = rows[s], rows[d]
            inverse_columns[d], inverse_columns[s] = inverse_columns[s], inverse_columns[d]
        elif op == "ADD":
            add(rows, inverse_columns, d, s, Q(tail[1]))
        else:
            assert tail[1] in (-1, 1)
            add(rows, inverse_columns, d, s, Q(1))
    elif op == "SCALE":
        scale(rows, inverse_columns, d, Q(tail[0]))
    elif op == "LAMBDA":
        assert tail in ([1], [-1])
    else:
        assert op in ("IDLE_ONE", "IDLE_ODD")
        mask = tail[0]
        assert mask and len(mask) == len(set(mask)) and all(1 <= j <= 17 for j in mask)
        assert tail[1:] == ([-1] if op == "IDLE_ODD" else [])


def projector(rows, inverse_columns, r):
    # Snapshot the covector e_r^T F and vector F^-1 e_r.
    column, row = inverse_columns[r], rows[r]
    assert sum(a*b for a,b in zip(row,column,strict=True)) == 1
    return column.copy(), row.copy()


def difference(early, late):
    ec, er = early
    lc, lr = late
    for i, (x,y) in enumerate(zip(ec,lc,strict=True)):
        if not (x or y):
            continue
        for j, (u,v) in enumerate(zip(er,lr,strict=True)):
            a,b = x*u,y*v
            if a != b:
                return {
                    "matrix_coordinate": [i,j], "earlier_projector_entry": str(a),
                    "later_projector_entry": str(b), "later_minus_earlier": str(b-a),
                }
    return None


def sparse(v):
    return [[i,str(x)] for i,x in enumerate(v) if x]


def controls():
    rows, inv = identity(3), identity(3)
    baseline = projector(rows,inv,0)
    scale(rows,inv,0,Q(-3,2))
    assert difference(baseline,projector(rows,inv,0)) is None
    rows, inv = identity(3), identity(3)
    add(rows,inv,1,0,Q(-2))
    assert difference(baseline,projector(rows,inv,0)) == {
        "matrix_coordinate":[1,0], "earlier_projector_entry":"0",
        "later_projector_entry":"2", "later_minus_earlier":"2",
    }
    rows, inv = identity(3), identity(3)
    add(rows,inv,0,2,Q(3,2))
    assert difference(baseline,projector(rows,inv,0)) == {
        "matrix_coordinate":[0,2], "earlier_projector_entry":"0",
        "later_projector_entry":"3/2", "later_minus_earlier":"3/2",
    }
    rows, inv = identity(36), identity(36)
    update(rows, inv, ["J",1,[0,1,2,3],[36,37,"-1","1/2"]], 36)
    assert rows[0][:2] == [1,-1] and rows[1][:2] == [Q(1,2),Q(1,2)]
    assert inv[0][:2] == [Q(1,2),Q(-1,2)] and inv[1][:2] == [1,1]
    return ["reciprocal_prefix_scaling_preserves_projector", "pure_column_obstruction",
            "pure_row_obstruction", "signed_J_and_inverse_columns"]


def stock(caller, offset):
    sites = defaultdict(list)
    for clock, event in enumerate(caller["events"]):
        if event[:2] == ["B", "IDLE_ONE"] and len(event[3]) == 1:
            sites[event[2]-offset,event[3][0]].append(clock)
    repeated = {k:v for k,v in sites.items() if len(v)>1}
    assert len(repeated) == CASE_CAP and all(len(v) == 2 for v in repeated.values())
    keys = [dict(earlier=a,later=b,role=role,stage=stage)
            for (role,stage), clocks in repeated.items() for a,b in combinations(clocks,2)]
    return sorted(keys,key=lambda row:(row["later"]-row["earlier"],row["earlier"]))


def audit(raw, deadline):
    price, admission = [loads(raw[key],object_pairs_hook=unique) for key in (PRICE,ADMISSION)]
    assert price["head"] == admission["head"] == HEAD
    assert admission["exit"] == 0 and admission["status"] == "independently_reproduced_comparable"
    assert price["caller_head"] == admission["caller"] == CALLER_HEAD
    assert price["source_sha256"]["inputs/7113-CALLER.json"] == admission["caller_sha256"] == PINS[CALLER]
    assert price["limits"]["projector_keys"] == CASE_CAP and price["limits"]["projector_seconds"] == HARD_SECONDS
    cases = price["cases"]
    assert len(cases) == CASE_CAP and cases[0] == {"earlier":4646,"later":4660,"role":0,"stage":17}
    caller = loads(raw[CALLER],object_pairs_hook=unique)
    kind = caller["types"]["B"]
    n, offset = kind["roles"], kind["offset"]
    assert (caller["stages"], n, offset, len(kind["ports"])) == (17,36,36,8)
    assert stock(caller,offset) == cases
    assert all(case["role"] == 0 for case in cases)
    wanted = {}
    for case in cases:
        r, s = case["role"], case["stage"]
        for clock in (case["earlier"], case["later"]):
            assert clock not in wanted
            assert caller["events"][clock] == ["B","IDLE_ONE",r+offset,[s]]
            wanted[clock] = r

    rows, inverse_columns = identity(n), identity(n)
    certificates = {}
    prefix_count = 0
    for clock, event in enumerate(caller["events"]):
        if (clock % 128 == 0 or clock in wanted) and monotonic() >= deadline:
            break
        if clock in wanted:
            certificates[clock] = projector(rows, inverse_columns, wanted[clock])
        update(rows, inverse_columns, event, offset)
        prefix_count += 1
    old_endpoint = prefix_count == len(caller["events"])
    if old_endpoint:
        assert rows == inverse_columns == identity(n)
        assert len(kind["diagonal"]) == n and len(certificates) == 2*CASE_CAP

    decisions, survivors, unvisited = [], [], []
    for case in cases:
        a,b = case["earlier"],case["later"]
        if monotonic() >= deadline or not old_endpoint or not {a,b} <= certificates.keys():
            unvisited.append(case)
            continue
        early, late = certificates[a],certificates[b]
        bad = difference(early,late)
        status = "excluded" if bad else "projector_survives"
        decisions.append({
            "key":case, "status":status, "obstruction":bad,
            "earlier":{"inverse_column":sparse(early[0]),"prefix_row":sparse(early[1])},
            "later":{"inverse_column":sparse(late[0]),"prefix_row":sparse(late[1])},
        })
        if bad is None:
            survivors.append(case)
    return {
        "head":HEAD, "caller_head":CALLER_HEAD, "input_sha256":PINS,
        "price_sha256":PINS[PRICE], "caller_sha256":PINS[CALLER],
        "case_cap":CASE_CAP, "hard_seconds":HARD_SECONDS, "cooperative_seconds":SOFT_SECONDS,
        "specialization":{"q":1,"body":"all one"},
        "prefix_literal_events":prefix_count, "old_endpoint_basis_columns":n if old_endpoint else 0,
        "counts":dict(Counter(row["status"] for row in decisions)),
        "status":"CAPPED" if unvisited else "EXHAUSTED",
        "decisions":decisions, "survivors":survivors, "unvisited":unvisited,
        "scope":"Exact two-clock projector test for nine repeated fixed-role and fixed-mask Type B singleton squares. No changed-provider replay.",
    }


def main():
    assert __debug__
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("root",type=Path,nargs="?")
    parser.add_argument("--controls-only",action="store_true")
    args = parser.parse_args()
    if args.controls_only:
        print(dumps({"controls":controls()},sort_keys=True))
        return
    if args.root is None:
        parser.error("the evidence root is required")
    alarm(HARD_SECONDS)
    deadline = monotonic() + SOFT_SECONDS
    raw = authenticate(args.root)
    checked = controls()
    result = audit(raw,deadline)
    result["controls"] = checked
    print(dumps(result,sort_keys=True,indent=2))
    alarm(0)


if __name__ == "__main__":
    main()
