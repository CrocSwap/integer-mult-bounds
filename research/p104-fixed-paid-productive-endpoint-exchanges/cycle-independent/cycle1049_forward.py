"""Replay three dirty rows through the old #7481 chart-1049 suffix."""
import argparse
from fractions import Fraction as F
import gzip
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
from signal import alarm
from time import perf_counter

ARCHIVE = "acee323696b18914bd863d55341f92112b48d3d1dc1443c276efb6c396fcc0a9"
NATIVE = "64fca675b91298868e12f09423b47e0c2327cba7095e35c8919c1953b4ed68b8"
CUT, CHART = 36481, 1049
ROLES = (1322, 1352, 1440)
ZERO = (F(0),) * 3


def space(basis):
    xs = {0}
    for x in basis:
        xs |= {x ^ y for y in xs}
    return xs


def replay(word, suppress=None):
    program = word["program"]
    active = dict(enumerate(word["initial"]))
    for op, dest, *args in program[:CUT]:
        if op == "MOVE":
            active[dest] = args[1]
        elif op == "INIT":
            active[dest] = args[0]
        elif op == "CLEAR":
            del active[dest]
    assert all(active[role] == CHART for role in ROLES)
    values = {role: tuple(F(j == i) for j in range(3))
              for i, role in enumerate(ROLES) if role != suppress}
    guards, erasures = {}, {}
    for clock, (op, dest, *args) in enumerate(program[CUT:], CUT):
        value = values.get(dest, ZERO)
        if op == "MOVE":
            assert active[dest] == args[0]
            active[dest] = args[1]
            continue
        if op == "INIT":
            assert dest not in active
            active[dest] = args[0]
            if value != ZERO:
                guards[clock] = value
            values.pop(dest, None)
        elif op == "CLEAR":
            assert active.pop(dest) == args[0]
            if value != ZERO:
                erasures[clock] = value
            values.pop(dest, None)
        elif op == "SCALE":
            assert active[dest] == args[1]
            if value != ZERO:
                values[dest] = tuple(F(args[0]) * x for x in value)
        else:
            assert op in ("COPY", "ADD")
            src, coefficient, chart = args
            assert active[src] == active[dest] == chart
            if op == "COPY" and value != ZERO:
                guards[clock] = value
                value = ZERO
            if src in values or dest in values:
                result = tuple(x + F(coefficient) * y
                               for x, y in zip(value, values.get(src, ZERO)))
                if result != ZERO:
                    values[dest] = result
                else:
                    values.pop(dest, None)
    assert active == dict(enumerate(word["final"]))
    assert all(r in active for r in values)
    return values, guards, erasures


def two_minors(rows):
    for ((kind1, i), a), ((kind2, j), b) in combinations(rows, 2):
        for x, y in combinations(range(3), 2):
            det = a[x] * b[y] - a[y] * b[x]
            if det:
                yield {"constraint_rows": ((kind1, i), (kind2, j)),
                       "carrier_columns": (ROLES[x], ROLES[y]),
                       "matrix": [[a[x], a[y]], [b[x], b[y]]], "determinant": det}


def constraint_rows(values, guards):
    return [(("outside_output", role), row) for role, row in sorted(values.items())
            if role not in ROLES] + [(("clean_guard", clock), row) for clock, row in guards.items()]


def main():
    assert __debug__
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--word", required=True, type=Path)
    args = parser.parse_args()
    start = perf_counter()
    alarm(30)
    archive = args.word.read_bytes()
    assert sha256(archive).hexdigest() == ARCHIVE
    raw = gzip.decompress(archive)
    assert sha256(raw).hexdigest() == NATIVE
    word = json.loads(raw)
    assert word["program"][36480:36484] == [
        ["MOVE", 1322, 3, 1049, False], ["ADD", 1352, 1322, "2", 1049],
        ["ADD", 1440, 1322, "-2", 1049], ["ADD", 679, 1440, "-1/2", 1049],
    ]
    main_roles = set(word["live"]) | {r + 112 for r in word["live"]}
    main_roles.update(word["hosted"]["X2"] + word["hosted"]["Y2"])
    assert not set(ROLES) & main_roles
    old = tuple(word["final"][r] for r in ROLES)
    new = (*old[1:], old[0])
    initial = tuple(word["initial"][r] for r in ROLES)
    frames = word["frames"]
    assert all(space(frames[s]) < space(frames[d]) for s, d in zip(initial, new))
    lengths = lambda endpoints: tuple(len(frames[d]) - len(frames[s])
                                      for s, d in zip(initial, endpoints))
    assert lengths(old) == (9, 5, 2) and lengths(new) == (5, 7, 4)
    values, guards, erasures = replay(word)
    restricted = constraint_rows(values, guards)
    assert all(row[1] == 0 for _, row in restricted)
    witness = next(two_minors(restricted), None)
    mutated, mutated_guards, _ = replay(word, suppress=1440)
    assert next(two_minors(constraint_rows(mutated, mutated_guards)), None) is None
    print(json.dumps({
        "status": "PASS_OUTSIDE_RANK_TWO_EXCLUSION" if witness else "MINOR_NOT_FOUND",
        "native_sha256": NATIVE, "cut_before": CUT, "chart": CHART, "carrier_order": ROLES,
        "old_productive_ranks": lengths(old), "new_productive_ranks": lengths(new),
        "outside_nonzero_responses": {role: row for role, row in sorted(values.items())
                                      if role not in ROLES},
        "copy_init_guard_responses": guards, "inherited_clear_operands": erasures,
        "old_endpoint_responses": {role: values.get(role, ZERO) for role in ROLES},
        "witness": witness, "mutant_removed_carrier": 1440,
        "mutant_has_rank_two_minor": False, "cap_seconds": 30, "cases_completed": 1,
        "seconds": perf_counter() - start,
    }, default=str, sort_keys=True, indent=2))
    alarm(0)


if __name__ == "__main__":
    main()
