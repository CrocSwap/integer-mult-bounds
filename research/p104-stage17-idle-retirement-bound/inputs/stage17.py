"""Exact unit-body necessary gate for redirecting one stage-17 Type B singleton."""
from argparse import ArgumentParser
from fractions import Fraction as Q
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from signal import SIGALRM, alarm, signal

ROOT = Path(__file__).resolve().parent
CALLER_SHA = "255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc"
PRICE_SHA = "2c907dbad96283f0b9d779455e448a3d396c33fe41db443ac5952f7af8a6f8f8"
N, OFFSET, STAGE, DONOR, RAIL = 36, 36, 17, 0, 32
IDLES = (4646, 4660)
J = 4691


def unique(items):
    result = dict(items)
    assert len(result) == len(items), "Duplicate JSON key"
    return result


def timeout(*_):
    raise TimeoutError("20s hard cap")


def gate(event):
    kind, op, *args = event
    if kind == "J":
        r, s, a, b = args[1]
        a, b = Q(a), Q(b)
        return "J", r-OFFSET, s-OFFSET, (Q(1), a, b, 1+a*b)
    if kind != "B":
        assert kind == "A"
        return None
    r, *values = args
    if op in ("IDLE_ONE", "IDLE_ODD", "LAMBDA"):
        return None
    if op == "SCALE":
        return op, r-OFFSET, None, Q(values[0])
    if op == "SWAP":
        return op, r-OFFSET, values[0]-OFFSET, None
    assert op in ("ADD", "QUERY"), op
    return "ADD", r-OFFSET, values[0]-OFFSET, Q(values[1]) if op == "ADD" else Q(1)


def apply(v, step, transpose=False):
    if step is None:
        return
    op, r, s, x = step
    assert 0 <= r < N and (s is None or 0 <= s < N)
    if op == "SCALE":
        v[r] *= x
    elif op == "SWAP":
        v[r], v[s] = v[s], v[r]
    elif op == "ADD":
        if transpose:
            r, s = s, r
        v[r] += x*v[s]
    else:
        assert op == "J"
        a, b, c, d = x
        if transpose:
            b, c = c, b
        v[r], v[s] = a*v[r]+b*v[s], c*v[r]+d*v[s]


def axis(role):
    return [Q(i == role) for i in range(N)]


def transported(gates, clock, role):
    row, col = axis(role), axis(role)
    for step in reversed(gates[:clock+1]):
        apply(row, step, transpose=True)
    for step in gates[clock+1:]:
        apply(col, step)
    return [[x*y for y in row] for x in col]


def sparse(matrix):
    return [[r, s, str(value)] for r, row in enumerate(matrix) for s, value in enumerate(row) if value]


def required(matrix):
    answer = [row[:] for row in matrix]
    answer[DONOR][DONOR] -= 1
    answer[RAIL][RAIL] += 1
    assert answer[RAIL][RAIL] == 1
    assert all(answer[i][RAIL] == answer[RAIL][i] == 0 for i in range(N) if i != RAIL)
    witness = next(((r, s, answer[r][s]) for r in range(32) for s in range(32) if answer[r][s]), None)
    if witness is None:
        return None
    r, s, value = witness
    return {"rows": [r, RAIL], "columns": [s, RAIL], "determinant": str(value)}


def main():
    assert __debug__
    p = ArgumentParser(description=__doc__)
    p.add_argument("caller", type=Path)
    args = p.parse_args()
    signal(SIGALRM, timeout)
    alarm(20)
    assert sha256((ROOT / "PRICE.json").read_bytes()).hexdigest() == PRICE_SHA
    raw = args.caller.read_bytes()
    assert sha256(raw).hexdigest() == CALLER_SHA
    c = loads(raw, object_pairs_hook=unique)
    b = c["types"]["B"]
    events = c["events"]
    assert (b["offset"], b["roles"], len(b["ports"]), len(events), c["stages"]) == (OFFSET, N, 8, 4783, 17)
    assert b["diagonal"][DONOR] == [-1, 0, *([1]*17)]
    assert b["diagonal"][RAIL] == [-1, 0, *[int(i==8) for i in range(1,18)]]
    even = [(i,e) for i,e in enumerate(events) if e[:2] == ["B","IDLE_ONE"]]
    assert sum(len(e[3]) == 1 for _,e in even) == 34
    assert [i for i,e in even if STAGE in e[3]] == list(IDLES)
    for i in IDLES:
        assert events[i] == ["B", "IDLE_ONE", 36, [STAGE]]
    assert events[J] == ["J",17,[17,0,18,35],[36,37,"-1","1/2"]]
    assert [(i,e) for i,e in enumerate(events) if e[:2]==["B","IDLE_ODD"] and STAGE in e[3]] == []
    assert [i for i,e in enumerate(events) if e[:2]==["J",STAGE]] == [J]
    gates = [gate(e) for e in events]
    live = [g for g in gates if g is not None]
    for i in range(N):
        col = axis(i)
        for step in live:
            apply(col, step)
        assert col == axis(i), f"Bad baseline +I column {i}"

    elementary = {i: transported(gates,i,0) for i in IDLES}
    native = [transported(gates,J,r) for r in (0,1)]
    complete = [*elementary.values(), *native]
    expected = [i for i,row in enumerate(b["diagonal"]) if row[STAGE+1]]
    assert expected == [0,1,16,17]
    assert all(sum(m[r][s] for m in complete) == int(r==s and r in expected) for r in range(N) for s in range(N))

    control = [[Q(r==s==DONOR) for s in range(N)] for r in range(N)]
    assert required(control) is None
    control[DONOR][DONOR] = 0
    control[1][1] = 1
    assert required(control) is not None

    rows = [{"slot":i, "old_derivative":sparse(m), "rank_two_minor_of_required":required(m)} for i,m in elementary.items()]
    alarm(0)
    print(dumps({"baseline_control": "all 36 +I columns and complete stage-17 derivative E0+E1+E16+E17",
                 "caps": {"word":1,"stages":[17],"slots":list(IDLES),"runner_seconds":20},
                 "pins":{"caller_payload":CALLER_SHA,"PRICE.json":PRICE_SHA},
                 "cases":rows, "unresolved":[row["slot"] for row in rows if row["rank_two_minor_of_required"] is None],
                 "coverage":"Only q=+1, all bodies=1, first derivative in D17, arbitrary constant even invertible wrappers around one selected slot."},
                sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
