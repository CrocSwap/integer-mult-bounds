"""Forward exact Type A endpoint replay for fixed even QUERY coefficients."""

from fractions import Fraction
from hashlib import sha256
from itertools import permutations
from json import dumps, loads
from math import prod
from pathlib import Path
from signal import SIGALRM, alarm, signal

ROOT = Path(__file__).resolve().parent
CALLER_SHA256 = "255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc"
QUERY_INDICES = (1516, 1580, 1659, 1721)
ROLES = 36
FLIPS = (0, 18)


def diagonal(q):
    return [[Fraction(q if i == j else 0) for j in range(ROLES)] for i in range(ROLES)]


def transfer(events, alpha, q, query_coefficient=None, omit_query=None):
    rows = diagonal(1)

    def add(dest, source, coefficient):
        rows[dest] = [
            a + coefficient * b for a, b in zip(rows[dest], rows[source], strict=True)
        ]

    for index, event in enumerate(events):
        if event[0] == "J":
            _, _, (u, v, x, y), _ = event
            add(v, u, q)
            add(x, y, alpha * q)
            continue
        if event[0] == "B":
            continue
        kind, op, dest, *args = event
        assert kind == "A"
        if op == "ADD":
            add(dest, args[0], Fraction(args[1]))
        elif op == "QUERY":
            assert index in QUERY_INDICES and args[1] == -1
            if index != omit_query:
                factor = q if query_coefficient is None else query_coefficient
                if isinstance(factor, tuple):
                    factor = factor[QUERY_INDICES.index(index)]
                add(dest, args[0], factor)
        elif op == "SWAP":
            peer, = args
            rows[dest], rows[peer] = rows[peer], rows[dest]
        elif op == "SCALE":
            coefficient, = args
            rows[dest] = [Fraction(coefficient) * x for x in rows[dest]]
        else:
            # LAMBDA has q²=1 and the IDLE_ONE bodies are all unit at this test.
            assert op in ("LAMBDA", "IDLE_ONE")
    return rows


def difference(a, b):
    return [[x - y for x, y in zip(u, v, strict=True)] for u, v in zip(a, b, strict=True)]


def rank(matrix):
    rows = [r.copy() for r in matrix if any(r)]
    pivot_row = 0
    for col in range(ROLES):
        pivot = next((i for i in range(pivot_row, len(rows)) if rows[i][col]), None)
        if pivot is None:
            continue
        rows[pivot_row], rows[pivot] = rows[pivot], rows[pivot_row]
        for i in range(pivot_row + 1, len(rows)):
            ratio = rows[i][col] / rows[pivot_row][col]
            rows[i] = [a - ratio * b for a, b in zip(rows[i], rows[pivot_row], strict=True)]
        pivot_row += 1
    return pivot_row


def minor(matrix, row_ids, col_ids):
    entries = [[matrix[i][j] for j in col_ids] for i in row_ids]
    size = len(entries)
    determinant = sum(
        (-1) ** sum(p[i] > p[j] for i in range(size) for j in range(i + 1, size))
        * prod(entries[i][p[i]] for i in range(size))
        for p in permutations(range(size))
    )
    return {"rows": row_ids, "columns": col_ids, "entries": entries, "determinant": determinant}


def stop(*_):
    raise TimeoutError("20-second exact cap")


def main():
    assert __debug__
    signal(SIGALRM, stop)
    alarm(20)
    raw = (ROOT / "inputs/CALLER.json").read_bytes()
    assert sha256(raw).hexdigest() == CALLER_SHA256
    caller = loads(raw)
    events = caller["events"]
    assert len(events) == 4783
    assert [event[1] for event in events if event[0] == "J"] == list(range(1, 18))
    assert [i for i, e in enumerate(events) if e[:2] == ["A", "QUERY"]] == list(QUERY_INDICES)
    assert all(events[i] == ["A", "QUERY", 0, 1, -1] for i in QUERY_INDICES)
    type_a = caller["types"]["A"]
    assert type_a["roles"] == ROLES and len(type_a["ports"]) == 96
    alpha = Fraction(type_a["alpha2"])
    for q in (-1, 1):
        assert transfer(events, alpha, q) == diagonal(q)

    erased_plus = transfer(events, alpha, 1, query_coefficient=1)
    assert erased_plus == diagonal(1)
    missing = transfer(events, alpha, 1, omit_query=QUERY_INDICES[0])
    assert rank(difference(missing, erased_plus)) == 1
    erased_minus = transfer(events, alpha, -1, query_coefficient=1)
    target = diagonal(-1)
    for i in FLIPS:
        target[i][i] = 1
    residual = difference(target, erased_minus)
    residual_rank = rank(residual)
    universal = minor(residual, (0, 1, 18, 19), (2, 9, 20, 27))
    assert residual_rank == 4 and universal["determinant"] == 64
    assert set(universal["rows"]).isdisjoint(universal["columns"])
    entries = [[i, j, v] for i, row in enumerate(residual) for j, v in enumerate(row) if v]
    alarm(0)
    print(dumps({
        "caller_sha256": CALLER_SHA256,
        "head": "aaeec8c0acf01e99a5f331ef363a698d9c084ace",
        "caller_head": "07a76c5e2738882c0cb322278e56f6cae3c9885d",
        "roles": ROLES, "events": len(events), "query_indices_zero_based": QUERY_INDICES,
        "fixed_j": 17, "target_phase_retirements": FLIPS, "even_query_factor": 1,
        "candidate_rank": residual_rank, "off_diagonal_minor": universal,
        "nonzero_delta_entries": entries, "hard_cap_seconds": 20,
        "controls": ["original +I and -I", "erased +I unchanged", "one omitted QUERY gives rank one"],
    }, indent=2, sort_keys=True, default=str))


if __name__ == "__main__":
    main()
