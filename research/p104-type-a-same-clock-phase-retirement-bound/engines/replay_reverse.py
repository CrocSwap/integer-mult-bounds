"""Independent exact reverse-covector replay of the fixed erased Type A caller."""
import argparse
import hashlib
import json
import signal
from fractions import Fraction
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


def phase(q, exponent):
    return q if exponent % 2 else 1


def specialized(events, q, query_factor=None, omitted=None):
    """List nonidentity primal operations after every body specializes to 1."""
    operations = []
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
            if clock != omitted:
                factor = phase(q, args[1]) if query_factor is None else query_factor
                operations.append(("ADD", dest, args[0], factor))
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


def rank_witness(matrix):
    """Track original row and column IDs through exact rational elimination."""
    reduced = [list(map(Fraction, row)) for row in matrix]
    ids = list(range(ROLES))
    cols = []
    for j in range(ROLES):
        step = len(cols)
        pivot = next((i for i in range(step, ROLES) if reduced[i][j]), None)
        if pivot is None:
            continue
        cols.append(j)
        reduced[step], reduced[pivot] = reduced[pivot], reduced[step]
        ids[step], ids[pivot] = ids[pivot], ids[step]
        for i in range(step + 1, ROLES):
            if reduced[i][j]:
                factor = reduced[i][j] / reduced[step][j]
                for k in range(j, ROLES):
                    reduced[i][k] -= factor * reduced[step][k]
    return len(cols), ids[:len(cols)], cols


def determinant3(rows):
    (a, b, c), (d, e, f), (g, h, i) = rows
    return a * (e * i - f * h) - b * (d * i - f * g) + c * (d * h - e * g)


def main():
    assert __debug__
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--caller", type=Path, default=Path(__file__).resolve().parent / "inputs" / "CALLER.json"
    )
    args = parser.parse_args()
    signal.signal(signal.SIGALRM, alarm_handler)
    signal.alarm(LIMIT)

    source = args.caller.read_bytes()
    assert hashlib.sha256(source).hexdigest() == CALLER_SHA256
    caller = json.loads(source)
    events = caller["events"]
    typ = caller["types"]["A"]
    assert len(events) == 4783 and typ["roles"] == ROLES and typ["offset"] == 0
    assert typ["alpha2"] == "-1" and typ["beta2"] == "0" and len(typ["ports"]) == 96
    assert [e[1] for e in events if e[0] == "J"] == list(range(1, 18))
    assert tuple(i for i, e in enumerate(events) if e[:2] == ["A", "QUERY"]) == QUERY_CLOCKS

    plus = pullback(specialized(events, 1))
    minus = pullback(specialized(events, -1))
    assert plus == diagonal([1] * ROLES) and minus == diagonal([-1] * ROLES)
    corrupted = pullback(specialized(events, 1, omitted=QUERY_CLOCKS[0]))
    assert rank_witness(difference(plus, corrupted))[0] == 1

    erased_plus = pullback(specialized(events, 1, query_factor=1))
    erased_minus = pullback(specialized(events, -1, query_factor=1))
    assert erased_plus == plus
    target = diagonal([1 if i in ROOTS else -1 for i in range(ROLES)])
    delta = difference(target, erased_minus)
    rank, row_ids, col_ids = rank_witness(delta)
    witness = None
    if rank >= 3:
        rows = row_ids[:3]
        cols = col_ids[:3]
        minor = [[delta[i][j] for j in cols] for i in rows]
        determinant = determinant3(minor)
        assert determinant
        witness = dict(rows=rows, columns=cols, matrix=minor, determinant=determinant)

    receipt = dict(
        head=HEAD, caller_head=CALLER_HEAD,
        pins={"inputs/CALLER.json": CALLER_SHA256},
        roles=ROLES, roots=ROOTS, phase_signs=[1, -1],
        events=len(events), fixed_J_stages=17, zero_based_query_clocks=QUERY_CLOCKS,
        unit_body=True, even_query_factor=1, allowed_rank_one_insertions=2,
        rank=rank, pivot_rows=row_ids, pivot_columns=col_ids, witness=witness,
        nonzero_delta_entries=[[i, j, x] for i, row in enumerate(delta) for j, x in enumerate(row) if x],
        disposition="fixed-erased class excluded" if rank > 2 else "necessary gate passed, feasibility unresolved",
        controls=["original +I and -I", "one missing QUERY changes +I by rank one", "erased +I unchanged"],
        hard_cap_seconds=LIMIT,
    )
    signal.alarm(0)
    print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
