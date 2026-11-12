"""Exact reverse covectors and stage-17 derivative for the fixed Type B caller."""
import argparse
import hashlib
import json
import signal
from fractions import Fraction as Q
from itertools import combinations
from pathlib import Path

HEAD = "aaeec8c0acf01e99a5f331ef363a698d9c084ace"
CALLER_HEAD = "07a76c5e2738882c0cb322278e56f6cae3c9885d"
PIN = "255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc"
OFFSET = 36
ORDER = 36
STAGE = 17
IDLES = (4646, 4660)
HOST = 4691
MARKS = (*IDLES, HOST)
LIMIT = 20
ZERO = Q(0)
ONE = Q(1)


def timeout(_signal, _frame):
    raise TimeoutError("20-second reverse-covector cap")


def reverse_program(events):
    instructions = []
    hits = []
    for clock, event in enumerate(events):
        family, *args = event
        if family == "A":
            continue
        if family == "J":
            stage, _, (s, t, alpha, beta) = args
            if stage == STAGE:
                hits.append(clock)
            a, b = Q(alpha), Q(beta)
            instructions.append((clock, "host", s - OFFSET, t - OFFSET, a, b, ONE + a*b))
            continue
        assert family == "B"
        op, role, *rest = args
        dest = role - OFFSET
        assert 0 <= dest < ORDER
        if op == "ADD":
            peer, coefficient = rest
            instructions.append((clock, "add", dest, peer - OFFSET, Q(coefficient)))
        elif op == "SWAP":
            peer, = rest
            instructions.append((clock, "swap", dest, peer - OFFSET))
        elif op == "SCALE":
            coefficient, = rest
            instructions.append((clock, "scale", dest, Q(coefficient)))
        elif op in ("IDLE_ONE", "IDLE_ODD"):
            if STAGE in rest[0]:
                assert op == "IDLE_ONE" and rest == [[STAGE]]
                hits.append(clock)
                instructions.append((clock, "idle", dest))
        else:
            assert op == "LAMBDA" and rest in ([1], [-1])
    assert tuple(hits) == MARKS
    return instructions[::-1]


def pull_back(vector, op, d, args):
    if op == "add":
        peer, c = args
        vector[peer] += c*vector[d]
    elif op == "swap":
        peer, = args
        vector[d], vector[peer] = vector[peer], vector[d]
    elif op == "scale":
        c, = args
        vector[d] *= c
    else:
        assert op == "host"
        peer, a, b, c = args
        x, y = vector[d], vector[peer]
        vector[d], vector[peer] = x + b*y, a*x + c*y


def evaluate(program):
    endpoint = []
    marked = {clock: [] for clock in MARKS}
    for output in range(ORDER):
        value = [Q(i == output) for i in range(ORDER)]
        deriv = {clock: [ZERO]*ORDER for clock in MARKS}
        for clock, op, d, *args in program:
            if op == "idle":
                deriv[clock][d] += value[d]
                continue
            pull_back(value, op, d, args)
            for row in deriv.values():
                pull_back(row, op, d, args)
            if clock == HOST:
                peer = args[0]
                deriv[clock][d] += value[d]
                deriv[clock][peer] += value[peer]
        endpoint.append(value)
        for clock in MARKS:
            marked[clock].append(deriv[clock])
    return endpoint, marked


def entries(matrix):
    return [[i, j, str(value)] for i, row in enumerate(matrix)
            for j, value in enumerate(row) if value]


def rank(matrix):
    a = [row[:] for row in matrix]
    k = 0
    for j in range(len(a[0])):
        pivot = next((i for i in range(k, len(a)) if a[i][j]), None)
        if pivot is None:
            continue
        a[k], a[pivot] = a[pivot], a[k]
        for i in range(k+1, len(a)):
            if a[i][j]:
                factor = a[i][j] / a[k][j]
                a[i] = [x-factor*y for x,y in zip(a[i], a[k], strict=True)]
        k += 1
    return k


def nonzero_minor(a):
    for i,k in combinations(range(ORDER), 2):
        for j,l in combinations(range(ORDER), 2):
            d = a[i][j]*a[k][l] - a[i][l]*a[k][j]
            if d:
                return dict(rows=[i,k], columns=[j,l],
                            matrix=[[str(a[i][j]),str(a[i][l])],[str(a[k][j]),str(a[k][l])]],
                            determinant=str(d))
    return None


def main():
    if not __debug__:
        raise RuntimeError("assertions required")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--caller", type=Path, default=Path(__file__).resolve().parent / "inputs/CALLER.json")
    path = parser.parse_args().caller
    signal.signal(signal.SIGALRM, timeout)
    signal.alarm(LIMIT)
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != PIN:
        raise ValueError("changed caller bytes")
    caller = json.loads(raw)
    body = caller["types"]["B"]
    events = caller["events"]
    assert len(events) == 4783 and caller["stages"] == STAGE
    assert body["roles"] == ORDER and body["offset"] == OFFSET and len(body["ports"]) == 8
    assert all(events[clock] == ["B", "IDLE_ONE", OFFSET, [STAGE]] for clock in IDLES)
    assert events[HOST] == ["J", STAGE, [17, 0, 18, 35], [36, 37, "-1", "1/2"]]
    endpoint, contributions = evaluate(reverse_program(events))
    assert endpoint == [[Q(i == j) for j in range(ORDER)] for i in range(ORDER)]
    original = [[Q(body["diagonal"][i][STAGE+1] if i == j else 0)
                 for j in range(ORDER)] for i in range(ORDER)]
    observed = [[sum(m[i][j] for m in contributions.values()) for j in range(ORDER)]
                for i in range(ORDER)]
    assert observed == original
    assert original[0][0] == ONE and original[32][32] == ZERO
    assert rank(contributions[HOST]) == 2
    assert any(x for row in contributions[HOST] for x in row)

    cases = []
    for clock in IDLES:
        old = contributions[clock]
        assert rank(old) == 1
        required = [row[:] for row in old]
        required[0][0] -= ONE
        required[32][32] += ONE
        required_rank = rank(required)
        minor = nonzero_minor(required)
        assert (minor is not None) == (required_rank > 1)
        assert nonzero_minor(old) is None
        cases.append(dict(clock=clock, old_rank=1, required_rank=required_rank,
                          old_entries=entries(old), required_entries=entries(required),
                          excluding_minor=minor))

    receipt = dict(comparator=HEAD, caller_head=CALLER_HEAD, pins={"inputs/CALLER.json":PIN},
                   events=len(events), roles=ORDER, body_stage=STAGE, q=1, all_body_values=1,
                   host_clock=HOST, host_entries=entries(contributions[HOST]), source_role=36,
                   destination_role=68, expected_derivative_entries=entries(original),
                   cases=cases, survivors=[c["clock"] for c in cases if c["required_rank"] <= 1],
                   cap_seconds=LIMIT,
                   controls=["original +I", "original exact full stage-17 derivative",
                             "fixed J derivative rank two", "old idle ranks one"])
    signal.alarm(0)
    print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
