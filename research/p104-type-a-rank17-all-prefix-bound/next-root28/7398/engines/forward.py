"""Independent forward Gaussian-Laurent column for the two frozen cuts."""
from fractions import Fraction as Q
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from signal import SIGALRM, alarm, signal

ROOT = Path(__file__).resolve().parent
PINS = {
    "inputs/CALLER.json": "255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc",
    "inputs/PRICE.json": "e076ac34017cc3c86c185a3f5982857dd70325012e196a2dcdd8d2d85a3957dc",
}
CUTS = (1743, 1744)
ROLE = 10
ONE = (Q(1), Q(0))


def verify(path):
    raw = (ROOT / path).read_bytes()
    if sha256(raw).hexdigest() != PINS[path]:
        raise ValueError(f"changed dependency {path}")
    return loads(raw)


def add_scaled(dest, src, a, b, exponent=0, factors=()):
    for (phase, stages), (x, y) in src.items():
        key = ((phase + exponent) % 4, tuple(sorted(stages + factors)))
        u, v = dest.get(key, (0, 0))
        value = (u + a * x - b * y, v + a * y + b * x)
        if any(value):
            dest[key] = value
        else:
            dest.pop(key, None)


def scaled(src, a=Q(1), b=Q(0), exponent=0, factors=()):
    dest = {}
    add_scaled(dest, src, a, b, exponent, factors)
    return dest


def propagate(rows, event, alpha):
    if event[0] == "J":
        _, stage, (u, v, x, y), _ = event
        add_scaled(rows[v], rows[u], Q(1), Q(0), exponent=-1)
        add_scaled(rows[x], rows[y], alpha, Q(0), exponent=1)
        for role in (u, v, x, y):
            rows[role] = scaled(rows[role], factors=(stage,))
        return
    if event[0] != "A":
        return
    _, op, role, *args = event
    if op == "ADD":
        add_scaled(rows[role], rows[args[0]], Q(args[1]), Q(0))
    elif op == "QUERY":
        add_scaled(rows[role], rows[args[0]], Q(1), Q(0), exponent=args[1])
    elif op == "SWAP":
        peer, = args
        rows[role], rows[peer] = rows[peer], rows[role]
    elif op == "SCALE":
        rows[role] = scaled(rows[role], a=Q(args[0]))
    elif op == "IDLE_ONE":
        rows[role] = scaled(rows[role], factors=tuple(args[0]))
    else:
        assert op == "LAMBDA" and args[0] in (-1, 1)
        source = rows[role]
        sign = args[0]
        rows[role] = scaled(source, Q(1, 2), Q(sign, 2))
        add_scaled(rows[role], source, Q(1, 2), Q(-sign, 2), exponent=2)


def classify(rows, cut):
    entries = [[i, phase, list(stages), str(a), str(b)]
               for i, vector in enumerate(rows) for (phase, stages), (a, b) in sorted(vector.items())]
    wrong = [item for item in entries if item[1] % 2 or item[2] != [9]]
    assert entries
    return dict(cut=cut, entries=entries, bad_terms=wrong,
                status="prefix excluded" if wrong else "paired support needed")


def stop(*_):
    raise TimeoutError("25-second exact cap")


def main():
    assert __debug__
    signal(SIGALRM, stop)
    alarm(25)
    c = verify("inputs/CALLER.json")
    price = verify("inputs/PRICE.json")
    assert c["stages"] == 17 and len(c["events"]) == 4783
    assert c["events"][1742] == ["A", "IDLE_ONE", ROLE, [9]]
    assert c["events"][3377][0:3] == ["J", 10, [10, 0, 18, 28]]
    A = c["types"]["A"]
    assert A["offset"] == 0 and len(A["ports"]) == 96
    rows = [{} for _ in range(A["roles"])]
    rows[ROLE] = {(0, ()): ONE}
    alpha = Q(A["alpha2"])
    checks = []
    for clock, event in enumerate(c["events"], 1):
        propagate(rows, event, alpha)
        if clock in CUTS:
            checks.append(classify(rows, clock))
    assert rows[ROLE] == {(3, (9, 10)): ONE}
    assert all(not vector for r, vector in enumerate(rows) if r != ROLE)
    bad = [{(1, (9,)): ONE}]
    assert classify(bad, 0)["status"] == "prefix excluded"
    wrong_stage = [{(2, (10,)): ONE}]
    assert classify(wrong_stage, 0)["status"] == "prefix excluded"
    good = [{(2, (9,)): ONE}]
    assert classify(good, 0)["status"] == "paired support needed"
    alarm(0)
    print(dumps(dict(pins=PINS, head=price["head"], caller=price["caller"], tested_role=ROLE,
                     events=len(c["events"]), cuts=checks, controls=["full original column", "wrong phase",
                     "foreign stage", "valid prefix only"]), sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
