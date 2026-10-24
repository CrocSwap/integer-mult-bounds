#!/usr/bin/env python3
"""Check the new capped-rank schedule, its exact price, and rejection controls."""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from fractions import Fraction
from pathlib import Path

# Each tuple is one chronological invocation, not a recursive child profile.
SCHEDULE = (("a", (0, 1)), ("b", (0, 2)), ("a", (2,)),
            ("b", (1, 2)), ("a", (0, 1)))
PACKAGE = Path(__file__).resolve().parent
MAX_ROLES = 6  # Finite corroboration only; the proof allows any finite count.


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def identity(n: int) -> tuple[int, ...]:
    return tuple(1 << i for i in range(n))


def multiply(a: tuple[int, ...], b: tuple[int, ...]) -> tuple[int, ...]:
    n = len(a)
    require(n == len(b) and 1 <= n <= MAX_ROLES, "matrix dimensions")
    return tuple(xor_rows(b, row) for row in a)


def xor_rows(rows: tuple[int, ...], mask: int) -> int:
    out = 0
    for i, row in enumerate(rows):
        if mask >> i & 1:
            out ^= row
    return out


def rank(rows: tuple[int, ...]) -> int:
    work = list(rows)
    pivot = 0
    for col in range(len(rows)):
        found = next((i for i in range(pivot, len(rows)) if work[i] >> col & 1), None)
        if found is None:
            continue
        work[pivot], work[found] = work[found], work[pivot]
        for i in range(pivot + 1, len(rows)):
            if work[i] >> col & 1:
                work[i] ^= work[pivot]
        pivot += 1
    return pivot


def inverse(rows: tuple[int, ...]) -> tuple[int, ...]:
    n = len(rows)
    work = [row | (1 << (n + i)) for i, row in enumerate(rows)]
    for col in range(n):
        found = next((i for i in range(col, n) if work[i] >> col & 1), None)
        require(found is not None, "singular gauge")
        work[col], work[found] = work[found], work[col]
        for i in range(n):
            if i != col and work[i] >> col & 1:
                work[i] ^= work[col]
    require(tuple(row & ((1 << n) - 1) for row in work) == identity(n), "inverse left block")
    return tuple(row >> n for row in work)


def coordinate_projector(n: int, support: tuple[int, ...]) -> tuple[int, ...]:
    require(3 <= n <= MAX_ROLES, "corroboration role bound")
    require(len(support) == len(set(support)) and all(0 <= i < n for i in support), "support")
    return tuple((1 << i) if i in support else 0 for i in range(n))


def group_table() -> tuple[list[tuple[int, ...]], list[list[int]], int, dict[str, int]]:
    group = [(x, y) for x in range(4) for y in range(4) if rank((x, y)) == 2]
    table = [[group.index(multiply(g, h)) for h in group] for g in group]
    labels = {"a": group.index((3, 2)), "b": group.index((1, 3))}
    labels["s"] = table[labels["a"]][table[labels["b"]][labels["a"]]]
    require(len(group) == 6 and group[labels["s"]] == (2, 1), "GL2 labels")
    return group, table, group.index((1, 2)), labels


def gates(n: int, gauge: tuple[int, ...]) -> list[tuple[str, tuple[int, ...]]]:
    inv = inverse(gauge)
    result = []
    for label, support in SCHEDULE:
        p = coordinate_projector(n, support)
        q = multiply(multiply(gauge, p), inv)
        require(rank(q) == len(support) and multiply(q, q) == q, "projector rank/idempotence")
        result.append((label, q))
    return result


def formal_endpoint(n: int, program: list[tuple[str, tuple[int, ...]]],
                    gauge: tuple[int, ...]) -> tuple[tuple[int, ...], ...]:
    _, table, unit, labels = group_table()
    zero = (0,) * n
    state = [zero for _ in range(6)]
    state[unit] = gauge  # Free entrance map, followed by conjugated paid gates.
    for label, q in program:
        require(label in ("a", "b") and 1 <= rank(q) <= 2, "paid alphabet/rank cap")
        products = [multiply(q, coeff) for coeff in state]
        out = [list(coeff) for coeff in state]
        for h in range(6):
            for row in range(n):
                out[h][row] ^= products[h][row]
                out[table[labels[label]][h]][row] ^= products[h][row]
        state = [tuple(coeff) for coeff in out]
    return tuple(multiply(inverse(gauge), coeff) for coeff in state)


def expected_formal(n: int) -> tuple[tuple[int, ...], ...]:
    _, _, unit, labels = group_table()
    out = [[0] * n for _ in range(6)]
    for i in range(n):
        out[labels["s"] if i < 3 else unit][i] = 1 << i
    return tuple(tuple(coeff) for coeff in out)


def permutation_compose(p: tuple[int, ...], q: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(p[q[i]] for i in range(3))


def regular_scalar(vector: int, matrix: tuple[int, ...]) -> int:
    out = 0
    for row, mask in enumerate(matrix):
        for col in range(len(matrix)):
            if mask >> col & 1:
                out ^= ((vector >> (6 * col)) & 63) << (6 * row)
    return out


def regular_endpoint(n: int, program: list[tuple[str, tuple[int, ...]]],
                     gauge: tuple[int, ...]) -> tuple[int, ...]:
    # Independent group construction: permutations of three points, no GL2 table.
    group = list(itertools.permutations(range(3)))
    permutations = {"a": (1, 0, 2), "b": (0, 2, 1)}
    action = {name: tuple(group.index(permutation_compose(p, h)) for h in group)
              for name, p in permutations.items()}
    outputs = []
    for column in range(6 * n):
        value = regular_scalar(1 << column, gauge)
        for label, q in program:
            new_value = value
            for source in range(n):
                for h in range(6):
                    if value >> (6 * source + h) & 1:
                        for target in range(n):
                            if q[target] >> source & 1:
                                new_value ^= 1 << (6 * target + h)
                                new_value ^= 1 << (6 * target + action[label][h])
            value = new_value
        outputs.append(regular_scalar(value, inverse(gauge)))
    return tuple(outputs)


def expected_regular(n: int) -> tuple[int, ...]:
    group = list(itertools.permutations(range(3)))
    swap = (2, 1, 0)
    return tuple(1 << (6 * role + (group.index(permutation_compose(swap, h)) if role < 3 else j))
                 for role in range(n) for j, h in enumerate(group))


def gauges(n: int) -> list[tuple[int, ...]]:
    if n == 3:
        return [tuple(rows) for rows in itertools.product(range(8), repeat=3)
                if rank(tuple(rows)) == 3]
    out = [identity(n)]
    for i in range(n):
        for j in range(n):
            if i != j:
                rows = list(identity(n))
                rows[i] ^= 1 << j
                out.append(tuple(rows))
    # A dense, invertible gauge also couples successive dirty roles.
    dense = identity(n)
    for i in range(n):
        rows = list(identity(n))
        rows[i] ^= 1 << ((i + 1) % n)
        dense = multiply(tuple(rows), dense)
    out.append(dense)
    return out


def tariff(c1: Fraction, c2: Fraction) -> Fraction:
    require(0 <= c1 <= c2 <= 2 * c1, "require 0 <= c1 <= c2 <= 2*c1")
    return c1 + 4 * c2


def check_prices() -> dict[str, int]:
    prices = [(Fraction(0), Fraction(0))]
    for denominator in range(1, 5):
        for numerator in range(1, 5):
            c1 = Fraction(numerator, denominator)
            prices.extend((c1, c1 * ratio) for ratio in (Fraction(1), Fraction(5, 4), Fraction(3, 2), Fraction(2)))
    comparisons = 0
    for c1, c2 in prices:
        optimum = tariff(c1, c2)
        attained = sum(c1 if len(support) == 1 else c2 for _, support in SCHEDULE)
        require(optimum == attained, "price attained by the actual schedule")
        require(optimum <= 3 * c1 + 3 * c2, "saving over disjoint batching")
        for q1 in range(13):
            for q2 in range(13):
                if q1 + 2 * q2 >= 9:
                    require(q1 * c1 + q2 * c2 >= optimum, "integer rank-profile price bound")
                    comparisons += 1
    invalid = [(Fraction(-1), Fraction(0)), (Fraction(1), Fraction(1, 2)),
               (Fraction(1), Fraction(3))]
    for c1, c2 in invalid:
        try:
            tariff(c1, c2)
        except ValueError:
            continue
        raise ValueError("invalid price accepted")
    return {"price_cases": len(prices), "integer_profile_comparisons": comparisons,
            "invalid_price_controls": len(invalid)}


def check_schedule() -> dict[str, int]:
    cases = columns = omissions = flips = leaks = 0
    for n in range(3, MAX_ROLES + 1):
        expected = expected_formal(n)
        for gauge in gauges(n):
            program = gates(n, gauge)
            require(formal_endpoint(n, program, gauge) == expected, "full formal endpoint")
            require(regular_endpoint(n, program, gauge) == expected_regular(n), "regular endpoint")
            for i in range(5):
                omitted = program[:i] + program[i + 1:]
                require(formal_endpoint(n, omitted, gauge) != expected, "omitted call undetected")
                require(regular_endpoint(n, omitted, gauge) != expected_regular(n),
                        "regular omitted call undetected")
                flipped = list(program)
                label, p = flipped[i]
                flipped[i] = ("b" if label == "a" else "a", p)
                require(formal_endpoint(n, flipped, gauge) != expected, "wrong label undetected")
                omissions += 1
                flips += 1
            if n > 3:
                broken = list(gauge)
                broken[3] ^= gauge[0]  # An unmatched free-map change leaks a target into dirt.
                require(formal_endpoint(n, program, tuple(broken)) != expected, "dirty leak undetected")
                leaks += 1
            cases += 1
            columns += 6 * n
    require(tuple(len(s) for _, s in SCHEDULE) == (2, 2, 1, 2, 2), "rank profile")
    require(sum(len(s) for _, s in SCHEDULE) == 9, "rank mass")
    bad = [("a", identity(3))]
    try:
        formal_endpoint(3, bad, identity(3))
    except ValueError:
        pass
    else:
        raise ValueError("rank-three paid call accepted")
    return {"gauged_endpoints": cases, "regular_basis_columns": columns,
            "omitted_call_controls": omissions, "wrong_label_controls": flips,
            "dirty_leak_controls": leaks, "rank_cap_controls": 1}


def receipt() -> dict[str, object]:
    names = ("README.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py")
    hashes = {name: hashlib.sha256((PACKAGE / name).read_bytes()).hexdigest() for name in names}
    return {"schema_version": 1, "claim_type": "scoped proof", "minimum_invocations": 5,
            "rank_profile": [2, 2, 1, 2, 2], "rank_mass": 9,
            "tariff": "c1+4*c2 for 0<=c1<=c2<=2*c1", "source_sha256": hashes,
            "schedule_checks": check_schedule(), "price_checks": check_prices()}


def canonical(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit-receipt", action="store_true")
    args = parser.parse_args()
    actual = receipt()
    if args.emit_receipt:
        print(json.dumps(actual, indent=2, sort_keys=True))
        return
    expected = json.loads((PACKAGE / "RESULT.json").read_text())
    require(canonical(actual) == canonical(expected), "receipt mismatch")
    print("PASS_RANK2_SWAP_BATCHING minimum=5 rank_profile=2,2,1,2,2 rank_mass=9 no_new_kappa")
    print(canonical(actual))


if __name__ == "__main__":
    main()
