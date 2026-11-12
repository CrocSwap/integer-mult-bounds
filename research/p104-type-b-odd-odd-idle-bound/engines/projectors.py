"""Check single and simultaneous distinct-mask odd idle unions at q=+1."""
from collections import defaultdict
from fractions import Fraction as Q
from gzip import decompress
from hashlib import sha256
from itertools import combinations, product
from json import dumps, loads
from pathlib import Path
from runpy import run_path
from signal import SIGALRM, alarm, signal

ROOT = Path(__file__).resolve().parents[1]
PINS = {
    "inputs/PRICE.json": "cca4b82a9b7b1670705373a245282043e32527f453cd24ba4500794857686872",
    "inputs/direct_impulse.py": "d04426aed9528aedc6400d384d7fd13c6531e5e3e6592a7eea4faee46c61e004",
    "inputs/7113-CALLER.json.gz": "7e8038559cd158f6e32ef6d1a3bf15ab6a8ecc2239af32ab1699511ac28e26d9",
}
CAP, SECONDS = 16, 20


def checked(path):
    raw = (ROOT / path).read_bytes()
    if sha256(raw).hexdigest() != PINS[path]:
        raise ValueError(f"changed dependency {path}")
    return raw


def inverse(gate):
    kind, dest, source, coeff = gate
    return kind, dest, source, -coeff if kind == "add" else 1 / coeff


def outer(left, right):
    return {(i, j): a * b for i, a in enumerate(left) for j, b in enumerate(right) if a and b}


def add(dest, source, coefficient):
    for position, value in source.items():
        updated = dest.get(position, 0) + coefficient * value
        if updated:
            dest[position] = updated
        else:
            dest.pop(position, None)


def stop(*_):
    raise TimeoutError("20-second hard cap")


def main():
    assert __debug__
    signal(SIGALRM, stop)
    alarm(SECONDS)
    price = loads(checked("inputs/PRICE.json"))
    assert Q(price["cases"]["18"]["1"]["complete"]["probe"][0]) > 0
    assert Q(price["cases"]["18"]["2"]["gross"]["incumbent"][1]) < 1
    raw = decompress(checked("inputs/7113-CALLER.json.gz"))
    assert sha256(raw).hexdigest() == price["caller_sha256"]
    caller = loads(raw)
    checked("inputs/direct_impulse.py")
    ref = run_path(str(ROOT / "inputs/direct_impulse.py"))
    checks = ref["controls"]()
    events = caller["events"]
    typ = caller["types"]["B"]
    size, offset = typ["roles"], typ["offset"]
    assert caller["stages"] == 17 and size == 36 and len(typ["ports"]) == 8
    jobs, _ = ref["literal_stock"](events, offset)
    assert {str(t): job for t, job in jobs.items()} == price["odd_jobs"]
    gate, apply, basis = (ref[k] for k in ("gates", "apply", "basis"))
    flattened, prefix = [], {}
    for clock, event in enumerate(events):
        if clock in jobs:
            prefix[clock] = len(flattened)
        flattened.extend(gate(event, offset, Q(1)))
    for role in range(size):
        vector = basis(size, role)
        for primitive in flattened:
            apply(primitive, vector)
        assert vector == basis(size, role)
    projectors = {}
    for clock, (role, _) in jobs.items():
        column, row = basis(size, role), basis(size, role)
        for primitive in reversed(flattened[:prefix[clock]]):
            apply(inverse(primitive), column)
            apply(primitive, row, True)
        assert sum(a * b for a, b in zip(column, row)) == 1
        projectors[clock] = outer(column, row)

    pairs = [tuple(pair) for pair in price["pairs"]]
    assert pairs == [(a, b) for a in jobs for b in jobs if jobs[a][1] == [8] and jobs[b][1] == [9]]
    schedules = []
    for k in (1, 2):
        for edges in combinations(pairs, k):
            if len(set(sum(edges, ()))) != 2 * k:
                continue
            for kept in product(*edges):
                defects = defaultdict(dict)
                for edge, dst in zip(edges, kept):
                    src = next(t for t in edge if t != dst)
                    stage, = jobs[src][1]
                    add(defects[stage], projectors[dst], 1)
                    add(defects[stage], projectors[src], -1)
                witnesses = {}
                for stage, defect in sorted(defects.items()):
                    if defect:
                        i, j = min(defect)
                        witnesses[stage] = [i, j, str(defect[i, j])]
                schedules.append(dict(pairs=edges, kept=kept, witnesses=witnesses,
                                      decision="derivative excluded" if witnesses else "unresolved"))
    assert len(schedules) == CAP
    encode = lambda matrix: [[i, j, str(q)] for (i, j), q in sorted(matrix.items())]
    good = {(0, 0): Q(1)}
    control = good.copy()
    add(control, good, -1)
    assert not control
    checks += ["full original unit-body endpoint", "equal projector cancellation"]
    alarm(0)
    receipt = dict(pins=PINS, head=price["head"], caller=price["caller"], caps=[4, CAP, SECONDS],
                   events=len(events), projectors={t: encode(m) for t, m in projectors.items()},
                   controls=checks, schedules=schedules,
                   unresolved=sum(row["decision"] == "unresolved" for row in schedules))
    print(dumps(receipt, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
