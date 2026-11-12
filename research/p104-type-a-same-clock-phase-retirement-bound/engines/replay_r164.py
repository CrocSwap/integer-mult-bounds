"""Independent exact reverse-covector replay with exact integer rank of the same-clock Type A variants."""
import argparse
import hashlib
import json
import signal
from itertools import combinations, permutations
from math import gcd, prod
from pathlib import Path

HEAD = "aaeec8c0acf01e99a5f331ef363a698d9c084ace"
CALLER_HEAD = "07a76c5e2738882c0cb322278e56f6cae3c9885d"
CALLER_SHA256 = "255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc"
QUERY_CLOCKS = (1516, 1580, 1659, 1721)
ROOTS = (0, 18)
ROLES = 36
LIMIT = 20


def alarm_handler(_signum, _frame):
    raise TimeoutError("20-second exact replay cap")


def specialized(events, q, constants):
    """List nonidentity primal operations after every body specializes to 1."""
    operations = []
    replacements = dict(zip(QUERY_CLOCKS, constants, strict=True))
    for clock, event in enumerate(events):
        if event[0] == "B":
            continue
        if event[0] == "J":
            _, _, (u, v, x, y), _ = event
            assert len({u, v, x, y}) == 4
            # The pinned Type A alpha2 is -1.
            operations.extend((("ADD", v, u, q), ("ADD", x, y, -q)))
            continue
        family, operation, dest, *args = event
        assert family == "A"
        if operation == "QUERY":
            assert clock in QUERY_CLOCKS and args == [1, -1]
            operations.append(("ADD", dest, args[0], replacements[clock]))
        elif operation == "ADD":
            source, factor = args
            operations.append(("ADD", dest, source, int(factor)))
        elif operation == "SCALE":
            operations.append(("SCALE", dest, int(args[0])))
        elif operation == "SWAP":
            operations.append(("SWAP", dest, args[0]))
        else:
            assert operation in ("LAMBDA", "IDLE_ONE")
            if operation == "LAMBDA":
                # Both projectors reduce to the identity because q^2=1.
                assert args == [1] or args == [-1]
    return operations


def diagonal(signs):
    return [[sign if i == j else 0 for j in range(ROLES)] for i, sign in enumerate(signs)]


def pullback(operations):
    rows = diagonal([1] * ROLES)
    for output in rows:
        for operation, dest, *args in reversed(operations):
            if operation == "ADD":
                source, factor = args
                output[source] += factor * output[dest]
            elif operation == "SWAP":
                peer, = args
                output[dest], output[peer] = output[peer], output[dest]
            else:
                assert operation == "SCALE"
                output[dest] *= args[0]
    return rows


def difference(left, right):
    return [[x - y for x, y in zip(a, b, strict=True)] for a, b in zip(left, right, strict=True)]


def rank(matrix):
    """Fraction-free elimination with primitive integer row normalization."""
    rows = [row[:] for row in matrix]
    ids = list(range(len(rows)))
    cols = []
    for j in range(len(rows[0])):
        k = len(cols)
        pivot = next((i for i in range(k, len(rows)) if rows[i][j]), None)
        if pivot is None:
            continue
        ids[k], ids[pivot] = ids[pivot], ids[k]
        rows[k], rows[pivot] = rows[pivot], rows[k]
        weight = rows[k][j]
        for i in range(k + 1, len(rows)):
            factor = rows[i][j]
            if factor:
                row = [weight * x - factor * y for x, y in zip(rows[i], rows[k], strict=True)]
                content = gcd(*row)
                rows[i] = [x // content for x in row] if content else row
        cols.append(j)
    return len(cols), ids[:len(cols)], cols


def determinant(matrix):
    n = len(matrix)
    return sum(
        (-1) ** sum(p[i] > p[j] for i in range(n) for j in range(i + 1, n))
        * prod(matrix[i][p[i]] for i in range(n))
        for p in permutations(range(n))
    )


def witness(matrix, rows, cols):
    minor = [[matrix[i][j] for j in cols] for i in rows]
    d = determinant(minor)
    assert d
    return dict(rows=rows, columns=cols, matrix=minor, determinant=d)


def main():
    assert __debug__
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--caller", type=Path, default=Path(__file__).resolve().parent / "inputs/CALLER.json"
    )
    args = parser.parse_args()
    signal.signal(signal.SIGALRM, alarm_handler)
    signal.alarm(LIMIT)

    source = args.caller.read_bytes()
    if hashlib.sha256(source).hexdigest() != CALLER_SHA256:
        raise ValueError("changed signed caller")
    caller = json.loads(source)
    events = caller["events"]
    typ = caller["types"]["A"]
    assert len(events) == 4783 and typ["roles"] == ROLES and typ["offset"] == 0
    assert typ["alpha2"] == "-1" and typ["beta2"] == "0" and len(typ["ports"]) == 96
    assert [e[1] for e in events if e[0] == "J"] == list(range(1, 18))
    assert tuple(i for i, e in enumerate(events) if e[:2] == ["A", "QUERY"]) == QUERY_CLOCKS

    base_plus = diagonal([1] * ROLES)
    base_minus = diagonal([-1] * ROLES)
    target = diagonal([1 if i in ROOTS else -1 for i in range(ROLES)])
    all_plus = (1,) * len(QUERY_CLOCKS)
    all_minus = (-1,) * len(QUERY_CLOCKS)
    balanced = [
        tuple(1 if i in positive else -1 for i in range(len(QUERY_CLOCKS)))
        for positive in combinations(range(len(QUERY_CLOCKS)), 2)
    ]
    configs = [all_plus, all_minus, *balanced]
    assert len(configs) == len(set(configs)) == 8
    maps = {(s, q): pullback(specialized(events, q, s)) for s in configs for q in (1, -1)}
    assert maps[all_plus, 1] == base_plus and maps[all_minus, -1] == base_minus

    plus_delta = difference(base_plus, maps[all_minus, 1])
    plus_rank, plus_rows, plus_cols = rank(plus_delta)
    assert plus_rank == 4
    plus_control = witness(plus_delta, plus_rows, plus_cols)
    rows = (0, 1, 18, 19)
    cols = (2, 9, 20, 27)
    assert set(rows).isdisjoint(cols)
    minus_control = witness(difference(base_minus, maps[all_plus, -1]), rows, cols)
    assert minus_control["determinant"] == 64
    assert minus_control == witness(difference(target, maps[all_plus, -1]), rows, cols)
    damaged = minus_control["matrix"][:-1] + [[0] * 4]
    assert rank(damaged)[0] == 3 and determinant(damaged) == 0

    cases = []
    for constants in balanced:
        plus = difference(base_plus, maps[constants, 1])
        minus = difference(target, maps[constants, -1])
        minus_rank, row_ids, col_ids = rank(minus)
        plus_rank = rank(plus)[0]
        assert plus_rank == 2
        minor = witness(minus, row_ids[:3], col_ids[:3]) if minus_rank > 2 else None
        cases.append(dict(constants=constants, residual_ranks=[plus_rank, minus_rank], minus_exclusion=minor))

    receipt = dict(
        head=HEAD, caller_head=CALLER_HEAD, pins={"inputs/CALLER.json": CALLER_SHA256},
        roots=ROOTS, events=len(events), fixed_J_stages=17, roles=ROLES,
        zero_based_query_clocks=QUERY_CLOCKS, phase_signs=[1, -1], unit_body=True,
        rank_one_correction_budget=2, evaluated_erased_words=len(configs), hard_cap_seconds=LIMIT,
        plus_full_rank_control=plus_control, minus_offdiagonal_full_rank_control=minus_control,
        balanced_cases=cases, unresolved=[c["constants"] for c in cases if max(c["residual_ranks"]) <= 2],
        controls=["original +I and -I", "minus control independent of target diagonal",
                  "one damaged control row reduces rank from four to three"],
    )
    signal.alarm(0)
    print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
