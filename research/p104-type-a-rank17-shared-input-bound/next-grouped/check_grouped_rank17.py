"""Test same-mask rank-17 input mixing by exact sector kernels."""
import argparse
from fractions import Fraction as Q
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from runpy import run_path
from signal import SIGALRM, alarm, signal
from time import perf_counter

PINS = {
    "inputs/7113-CALLER.json": "255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc",
    "next-root28/7398/engines/forward.py": "1043c6cb86af5c3fe348e62e5e7f89c2148e1273f1456382907a1a77a739b0df",
}
PAIRS = {(7, 25): (7, 8), (10, 28): (9, 10)}
EVENTS = 4783
ROLES = 36
CAP = 30
TOTAL = len(PAIRS) * (EVENTS + 1) * 2 * 2
ZERO = (Q(0), Q(0))
ONE = (Q(1), Q(0))


def emit(record):
    print(dumps(record, sort_keys=True, default=str, separators=(",", ":")), flush=True)


def gadd(x, y, scale=1):
    return x[0] + scale*y[0], x[1] + scale*y[1]


def gmul(x, y):
    return x[0]*y[0] - x[1]*y[1], x[0]*y[1] + x[1]*y[0]


def gneg(x):
    return -x[0], -x[1]


def sector_rows(columns, sign):
    rows = {}
    for col, vectors in enumerate(columns):
        for role, vector in enumerate(vectors):
            for (phase, stages), coefficient in vector.items():
                key = (role, stages, phase % 2)
                line = rows.setdefault(key, [ZERO, ZERO])
                line[col] = gadd(line[col], coefficient, sign**(phase//2))
    return sorted(rows.items())


def dot(line, column):
    return gadd(gmul(line[0], column[0]), gmul(line[1], column[1]))


def forbidden_kernel(rows, desired):
    first = None
    for (role, stages, parity), line in rows:
        if (stages, parity) == desired or not any(x != ZERO for x in line):
            continue
        key = (role, stages, parity)
        if first is None:
            first = (key, line)
            continue
        determinant = gadd(gmul(first[1][0], line[1]), gmul(first[1][1], line[0]), -1)
        if determinant != ZERO:
            return {"rank": 2, "minor_keys": [first[0], key],
                    "minor_rows": [first[1], line], "determinant": determinant}
    kernel = (ONE, ZERO) if first is None else (gneg(first[1][1]), first[1][0])
    assert any(v != ZERO for v in kernel)
    assert all(dot(line, kernel) == ZERO for (_, mask, parity), line in rows
               if (mask, parity) != desired)
    allowed = [(key, dot(line, kernel)) for key, line in rows if key[1:] == desired]
    allowed = [(key, value) for key, value in allowed if value != ZERO]
    assert allowed
    return {"rank": int(first is not None), "kernel": kernel, "allowed_terms": allowed}


def controls():
    first = {(0, (7,)): ONE, (0, ()): ONE, (2, ()): ONE}
    second = {(0, ()): ONE}
    columns = [[first], [second]]
    plus, minus = (sector_rows(columns, sign) for sign in (1, -1))
    assert forbidden_kernel(plus, ((7,), 0))["kernel"] == (gneg(ONE), (Q(2), Q(0)))
    assert forbidden_kernel(minus, ((7,), 0))["kernel"] == (gneg(ONE), ZERO)
    failed = sector_rows([[first, {}], [second, {(0, (8,)): ONE}]], 1)
    assert forbidden_kernel(failed, ((7,), 0))["determinant"] == (Q(2), Q(0))


def main():
    assert __debug__
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("handoff_root", type=Path)
    args = parser.parse_args()
    started = perf_counter()
    finished = 0
    current = None
    survivors = []

    def cap(_signal, _frame):
        emit({"status": "UNRESOLVED_CAP", "completed": finished, "remaining": TOTAL-finished,
              "first_unresolved": current, "survivors": survivors, "seconds": perf_counter()-started})
        raise SystemExit(124)

    signal(SIGALRM, cap)
    alarm(CAP)
    raw = {path: (args.handoff_root / path).read_bytes() for path in PINS}
    assert {path: sha256(data).hexdigest() for path, data in raw.items()} == PINS
    caller = loads(raw["inputs/7113-CALLER.json"])
    kind, tape = caller["types"]["A"], caller["events"]
    assert (caller["stages"], kind["roles"], kind["offset"], len(kind["ports"]), len(tape)) == (
        17, ROLES, 0, 96, EVENTS)
    source = args.handoff_root / "next-root28/7398/engines/forward.py"
    propagate = run_path(str(source))["propagate"]
    alpha = Q(kind["alpha2"])
    controls()
    emit({"status": "START", "pins": PINS, "total_cases": TOTAL, "runner_cap_seconds": CAP,
          "pairs": [{"roles": p, "body_orders": [s, s[::-1]]} for p, s in PAIRS.items()]})
    for pair, stages in PAIRS.items():
        body_mask = [int(j in stages) for j in range(1, 18)]
        assert all(kind["diagonal"][r] == [-1, 0, *body_mask] for r in pair)
        columns = [[{(0, ()): ONE} if i == r else {} for i in range(ROLES)] for r in pair]
        for cut in range(EVENTS + 1):
            current = {"roles": pair, "cut": cut, "first_body_stage": stages[0], "first_parity": 0}
            data = {sign: sector_rows(columns, sign) for sign in (1, -1)}
            for stage in stages:
                for parity in (0, 1):
                    current = {"roles": pair, "cut": cut, "first_body_stage": stage, "first_parity": parity}
                    sectors = {}
                    for sign, rows in data.items():
                        result = forbidden_kernel(rows, ((stage,), parity))
                        sectors[sign] = result
                        if result["rank"] == 2:
                            emit(dict(current, status="EXCLUDED_RANK_TWO", sector=sign, **result))
                            break
                    else:
                        survivors.append(current)
                        emit(dict(current, status="NECESSARY_GATE_SURVIVES", sectors=sectors))
                    finished += 1
            if cut < EVENTS:
                for column in columns:
                    propagate(column, tape[cut], alpha)
        for r, column in zip(pair, columns, strict=True):
            assert column[r] == {(3, stages): ONE}
            assert all(not vector for i, vector in enumerate(column) if i != r)
    assert finished == TOTAL
    emit({"status": "PASS_COMPLETE_GROUPED_RANK17_PREFIX_CENSUS", "completed": finished, "remaining": 0,
          "survivors": survivors, "seconds": perf_counter()-started})
    alarm(0)


if __name__ == "__main__":
    main()
