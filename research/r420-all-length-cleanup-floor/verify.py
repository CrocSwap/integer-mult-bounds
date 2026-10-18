#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Cinna Davis (@1337isnot1337), with substantial OpenAI Codex assistance.
"""Check the exact instance of the all-length positive-cleanup lower bound.

PROOF.md proves the bound for every finite word. This script checks source
pins, the target inverse, the lower-bound matrix and the attaining witness;
it does not infer an all-length theorem from a finite word enumeration.
"""
import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent


def need(condition, message):
    if not condition:
        raise ValueError(message)


def identity(n):
    return tuple(tuple(int(i == j) for j in range(n)) for i in range(n))


def word(operations, n):
    need(isinstance(operations, (tuple, list)), "word must be an operation list")
    out = []
    for op in operations:
        need(isinstance(op, (tuple, list)) and len(op) == 2, "only binary ADDs are permitted")
        dst, src = op
        need(type(dst) is int and type(src) is int, "register indices must be integers")
        need(0 <= dst < n and 0 <= src < n and dst != src, "invalid distinct-register ADD")
        out.append((dst, src))
    return tuple(out)


def multiply(a, b):
    n = len(a)
    return tuple(tuple(sum(a[i][k] * b[k][j] for k in range(n))
                       for j in range(n)) for i in range(n))


def elementary(n, dst, src):
    rows = [list(row) for row in identity(n)]
    rows[dst][src] += 1
    return tuple(tuple(row) for row in rows)


def product(n, operations):
    result = identity(n)
    for dst, src in word(operations, n):
        result = multiply(elementary(n, dst, src), result)
    return result


def inverse(matrix):
    """Rational elimination, with an exact integral-inverse check."""
    n = len(matrix)
    rows = [[Fraction(x) for x in matrix[i]] +
            [Fraction(int(i == j)) for j in range(n)] for i in range(n)]
    for col in range(n):
        pivot = next((i for i in range(col, n) if rows[i][col]), None)
        need(pivot is not None, "singular target")
        rows[col], rows[pivot] = rows[pivot], rows[col]
        scale = rows[col][col]
        rows[col] = [x / scale for x in rows[col]]
        for i in range(n):
            if i == col:
                continue
            scale = rows[i][col]
            rows[i] = [x - scale * y for x, y in zip(rows[i], rows[col])]
    need(all(x.denominator == 1 for row in rows for x in row[n:]), "nonintegral inverse")
    result = tuple(tuple(int(x) for x in row[n:]) for row in rows)
    need(multiply(matrix, result) == identity(n) == multiply(result, matrix), "inverse identity failed")
    return result


def column_replay(n, operations, sign=1):
    """Separate primitive interpreter: run numerical basis columns."""
    operations = word(operations, n)
    columns = []
    for col in range(n):
        registers = [int(i == col) for i in range(n)]
        for dst, src in operations:
            registers[dst] += sign * registers[src]
        columns.append(registers)
    return tuple(tuple(columns[j][i] for j in range(n)) for i in range(n))


def floor_from_inverse(r):
    """Smallest entrywise floor from |R|, Q >= I and Q == R (mod 2)."""
    n = len(r)
    result = []
    for i in range(n):
        row = []
        for j in range(n):
            value = max(abs(r[i][j]), int(i == j))
            if value % 2 != r[i][j] % 2:
                value += 1
            row.append(value)
        result.append(tuple(row))
    return tuple(result)


def row_sums(matrix):
    return tuple(map(sum, matrix))


def norm_inf(matrix):
    return max(sum(abs(x) for x in row) for row in matrix)


def admissible_bound(r, q):
    n = len(r)
    return (all(q[i][j] >= abs(r[i][j]) for i in range(n) for j in range(n))
            and all(q[i][i] >= 1 for i in range(n))
            and all((q[i][j] - r[i][j]) % 2 == 0 for i in range(n) for j in range(n)))


def load_inputs():
    manifest = json.loads((HERE / "SOURCES.json").read_text())
    by_path = {}
    for item in manifest["archives"]:
        path = Path(item["local_path"])
        need(not path.is_absolute() and ".." not in path.parts, "invalid archive path")
        data = (HERE / path).read_bytes()
        need(hashlib.sha256(data).hexdigest() == item["sha256"], "source pin mismatch: " + str(path))
        by_path[str(path)] = data
    source = json.loads(by_path["inputs/PR1058-CIRCUIT.json"])
    predecessor = json.loads(by_path["inputs/PR1266-RESULT.json"])
    return manifest, source, predecessor


def calculate():
    manifest, source, predecessor = load_inputs()
    n = len(source["registers"])
    need(n == 6, "wrong register count")
    baseline = word(source["operations"], n)
    witness = word(predecessor["best_shortest_word"]["forward_add_word"], n)
    target = product(n, baseline)
    r = inverse(target)
    q = product(n, tuple(reversed(witness)))
    bound = floor_from_inverse(r)

    # Numerical column interpretation is separate from matrix multiplication
    # and Fraction elimination. Subtraction is an oracle for the signed
    # inverse here, not a gate in the factorization class being optimized.
    need(column_replay(n, baseline) == target, "baseline engines disagree")
    need(column_replay(n, witness) == target == product(n, witness), "witness changed target")
    need(column_replay(n, tuple(reversed(baseline)), -1) == r, "inverse engines disagree")
    need(column_replay(n, tuple(reversed(witness))) == q, "cleanup engines disagree")
    need([list(row) for row in q] == predecessor["best_shortest_word"]["cleanup_matrix"], "witness receipt mismatch")
    need(admissible_bound(r, q), "witness violates a necessary invariant")
    need(all(q[i][j] >= bound[i][j] for i in range(n) for j in range(n)), "witness below floor")
    need(r[1][1] == 0 and bound[1][1] == 2, "critical zero diagonal changed")
    need(norm_inf(bound) == norm_inf(q) == 9, "attainment of norm-nine floor failed")
    need(len(witness) == 11, "witness length changed")
    longer = word(source["old_operations"], n)
    longer_q = product(n, tuple(reversed(longer)))
    need(len(longer) == 19 and product(n, longer) == target, "longer source word changed target")
    need(admissible_bound(r, longer_q), "longer source word violated invariant")

    boolean_cases = 0
    for bits in range(1 << n):
        initial = [(bits >> i) & 1 for i in range(n)]
        a, b = list(initial), list(initial)
        for dst, src in baseline:
            a[dst] ^= a[src]
        for dst, src in witness:
            b[dst] ^= b[src]
        need(a == b, "Boolean forward endpoints differ")
        for dst, src in reversed(witness):
            b[dst] ^= b[src]
        need(b == initial, "literal Boolean inverse failed")
        boolean_cases += 1

    wrong = list(witness)
    dst, src = wrong[0]
    wrong[0] = (dst, next(s for s in range(n) if s not in (dst, src)))
    controls = {
        "dropped_gate_reaches_target": product(n, witness[:-1]) == target,
        "wrong_source_reaches_target": product(n, wrong) == target,
        "forward_order_is_cleanup": product(n, witness) == q,
    }
    need(not any(controls.values()), "malformed-word control accepted")
    swap = ((0, 1), (1, 0))
    need(not admissible_bound(swap, swap), "permutation scope control lost")
    try:
        word(((0, 0),), 2)
    except ValueError:
        illegal_gate_rejected = True
    else:
        illegal_gate_rejected = False
    need(illegal_gate_rejected, "same-register gate accepted")

    # A small positive fixture exercises the zero-diagonal parity step.
    cycle = ((0, 1), (1, 2), (2, 0))
    cycle_r = inverse(product(3, cycle))
    cycle_q = product(3, tuple(reversed(cycle)))
    cycle_b = floor_from_inverse(cycle_r)
    need(cycle_r[0][0] == 0 and cycle_b[0][0] == 2, "cycle fixture lost zero diagonal")
    need(norm_inf(cycle_q) == norm_inf(cycle_b) == 4, "cycle fixture not tight")
    need(floor_from_inverse(identity(2)) == identity(2), "identity floor inflated")

    return {
        "status": "PASS_R420_ALL_LENGTH_CLEANUP_FLOOR",
        "base_commit": manifest["base_commit"],
        "assignment_seed": 0,
        "domain": "Every finite positive ADD word on these six ordered registers, with distinct operands and the fixed exact integer target; no auxiliary registers or permutations.",
        "objective": "Infinity norm of the reverse-positive bound map, not the signed integer inverse norm.",
        "target_forward_integer_matrix": target,
        "signed_inverse": r,
        "absolute_inverse_row_sums": row_sums(tuple(tuple(abs(x) for x in row) for row in r)),
        "diagonal_parity_floor": bound,
        "floor_row_sums": row_sums(bound),
        "all_length_lower_bound": norm_inf(bound),
        "critical_register_zero_based": 1,
        "critical_inverse_row": r[1],
        "critical_cleanup_diagonal_minimum": 2,
        "attaining_forward_word": witness,
        "attaining_reverse_positive_matrix": q,
        "attaining_row_sums": row_sums(q),
        "attaining_norm": norm_inf(q),
        "witness_adds": len(witness),
        "baseline_reverse_positive_norm": norm_inf(product(n, tuple(reversed(baseline)))),
        "longer_same_target_fixture": {"adds": len(longer), "reverse_positive_norm": norm_inf(longer_q)},
        "unit_input_attains_norm": row_sums(q),
        "boolean_inputs_replayed": boolean_cases,
        "negative_controls": {**controls, "same_register_gate_rejected": illegal_gate_rejected,
                              "excluded_swap_violates_positive_diagonal": True},
        "small_zero_diagonal_fixture": {"forward_word": cycle, "inverse": cycle_r,
                                         "floor": cycle_b, "reverse_positive": cycle_q,
                                         "lower_bound_and_attainment": 4},
        "proof_scope": "PROOF.md supplies the arbitrary-length argument. Exact replay instantiates it and checks an upper-bound witness; no enumeration cutoff proves the theorem.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-receipt", type=Path, help="write a new receipt; refuse overwrite")
    args = parser.parse_args()
    try:
        result = calculate()
        data = json.dumps(result, indent=2, sort_keys=True) + "\n"
        if args.write_receipt:
            with args.write_receipt.open("x") as output:
                output.write(data)
        else:
            expected = json.loads((HERE / "CERTIFICATE.json").read_text())
            need(json.loads(data) == expected, "committed certificate differs from recomputed result")
        print("PASS_R420_ALL_LENGTH_CLEANUP_FLOOR lower=9 attained=9 adds=11 columns=6 boolean=64 controls=5")
    except (OSError, ValueError, KeyError, TypeError, StopIteration) as exc:
        print("REJECT_R420_ALL_LENGTH_CLEANUP_FLOOR: " + str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
