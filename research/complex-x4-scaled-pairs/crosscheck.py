#!/usr/bin/env python3
"""Independent Fraction/primitive-word census; imports no project code.

ToikY, with substantial AI assistance from OpenAI Codex. Apache-2.0.
"""

import argparse
import gzip
import hashlib
import json
import tarfile
from collections import Counter
from fractions import Fraction
from functools import lru_cache
from pathlib import Path

CANONICAL_SHA256 = "1c0e9da767d4418f70016af599e4a447a3f7777acabe930318459c0fbbd260aa"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def same_json(actual, expected):
    """JSON equality that rejects bool/int and int/float substitutions."""
    if type(actual) is not type(expected):
        return False
    if isinstance(actual, dict):
        return actual.keys() == expected.keys() and all(
            same_json(value, expected[key]) for key, value in actual.items())
    if isinstance(actual, list):
        return len(actual) == len(expected) and all(
            same_json(a, b) for a, b in zip(actual, expected))
    return actual == expected


def primitive_word(coefficient):
    """Original binary Horner lowering on registers S=0, T=1, W=2."""
    if not coefficient:
        return []
    word = [("clear", 2), ("add", 2, 0, 1)]
    # Construct operations, rather than evaluate a bit-count cost formula.
    for bit in bin(abs(coefficient.numerator))[3:]:
        word.append(("add", 2, 2, 1))
        if bit == "1":
            word.append(("add", 2, 0, 1))
    denominator = coefficient.denominator
    while denominator > 1:
        require(denominator % 2 == 0, "only dyadic coefficients are in scope")
        denominator //= 2
        word.append(("half", 2))
    word.extend([("add", 1, 2, 1 if coefficient > 0 else -1), ("clear", 2)])
    return word


def execute(word, registers):
    registers = [Fraction(value) for value in registers]
    for op in word:
        if op[0] == "clear":
            registers[op[1]] = Fraction(0)
        elif op[0] == "half":
            registers[op[1]] /= 2
        else:
            require(op[0] == "add", "unknown primitive operation")
            registers[op[1]] += op[3] * registers[op[2]]
    return registers


def boundary_controls(cost):
    """Exact local identities and concrete deliberately invalid variants."""
    start = [3, 5, 7, 11]  # yi, yj, arbitrary compensation increments u, v
    expected = [10, 16, 7, 11]
    wrapper_checks = inverse_transpose_checks = 0
    for exponent in range(-3, 4):
        for sign in (-1, 1):
            lam = Fraction(sign * 2 ** max(exponent, 0), 2 ** max(-exponent, 0))
            wrapper = [("add", 0, 1, lam), ("add", 0, 2, 1),
                       ("add", 0, 3, lam), ("add", 1, 3, 1),
                       ("add", 0, 1, -lam)]
            # A basis check proves this finite rational linear-map identity.
            for column in range(4):
                basis = [int(k == column) for k in range(4)]
                want = basis[:]
                want[0] += basis[2]
                want[1] += basis[3]
                require(execute(wrapper, basis) == want, "wrapper basis identity")
                wrapper_checks += 1
                inverse_transpose = [("add", op[2], op[1], -op[3]) for op in wrapper]
                want = basis[:]
                want[2] -= basis[0]
                want[3] -= basis[1]
                require(execute(inverse_transpose, basis) == want,
                        "same-order inverse-transpose wrapper identity")
                inverse_transpose_checks += 1
            require(execute(wrapper, start) == expected, "wrapper dirty-target identity")
            require(execute(wrapper[1:], start) != expected, "omitted preparation control")
            require(execute(wrapper[:-1], start) != expected, "omitted restoration control")

    lam = Fraction(2)
    wrapper = [("add", 0, 1, lam), ("add", 0, 2, 1),
               ("add", 0, 3, lam), ("add", 1, 3, 1),
               ("add", 0, 1, -lam)]
    # For chronological A then B, inverse transpose executes A^-T then B^-T.
    forward = [("add", 0, 1, Fraction(2)), ("add", 1, 2, Fraction(3))]
    inverse_transpose = [("add", op[2], op[1], -op[3]) for op in forward]
    transpose_input = [1, 2, 3]
    inverse = [("add", op[1], op[2], -op[3]) for op in reversed(forward)]
    columns = [execute(inverse, [int(k == j) for k in range(3)]) for j in range(3)]
    want_transpose = [sum(columns[j][k] * transpose_input[k] for k in range(3))
                      for j in range(3)]
    correct = execute(inverse_transpose, transpose_input)
    wrong = execute(list(reversed(inverse_transpose)), transpose_input)
    require(correct == want_transpose and wrong != correct, "inverse-transpose order control")
    # Toy coefficients a=2, b=-1 cancel at lambda=2, but pay two shears.
    unpaid = cost(Fraction(2)) - cost(Fraction(0))
    paid = unpaid - 2 * cost(lam)
    require(unpaid > 0 and paid < 0, "unpaid shears control")
    require(not same_json({"cost": 1}, {"cost": True}) and
            not same_json({"cost": 1}, {"cost": 1.0}), "typed receipt control")
    return {
        "wrapper_basis_checks": wrapper_checks,
        "inverse_transpose_wrapper_basis_checks": inverse_transpose_checks,
        "typed_receipts": True,
        "omitted_preparation": {"expected": expected,
                                "actual": list(map(int, execute(wrapper[1:], start)))},
        "omitted_restoration": {"expected": expected,
                                "actual": list(map(int, execute(wrapper[:-1], start)))},
        "unpaid_shears_toy": {"a": 2, "b": -1, "lambda": 2,
                              "unpaid_saving": unpaid, "paid_saving": paid},
        "wrong_inverse_transpose_order": {"input": transpose_input,
                                          "expected": list(map(int, correct)),
                                          "actual": list(map(int, wrong))},
    }


def run(root):
    archive = Path(root) / "research/community-frontier799-audit/integrated799-replay.tar.gz"
    with tarfile.open(archive, "r:gz") as packed:
        member = packed.extractfile("native/local/CANONICAL-WORD.json.gz")
        require(member is not None, "canonical archive member missing")
        payload = gzip.decompress(member.read())
    digest = hashlib.sha256(payload).hexdigest()
    require(digest == CANONICAL_SHA256, "canonical source payload changed")
    compensation = json.loads(payload)["compensation"]
    require(len(compensation) == 6320, "compensation addition count")
    targets = list(range(112, 224))
    rows = {target: {} for target in targets}
    for kind, target, source, numerator, denominator, frame in compensation:
        require(kind == "add" and target in rows and source >= 224 and frame == 0,
                "compensation operation outside scoped panel")
        require(source not in rows[target], "census assumes unique row/source entries")
        coefficient = Fraction(numerator, denominator)
        require(coefficient, "zero coefficient in canonical compensation")
        rows[target][source] = coefficient
    require(all(rows.values()), "missing target row")
    primitive_checks = 0

    @lru_cache(None)
    def cost(coefficient):
        nonlocal primitive_checks
        word = primitive_word(coefficient)
        for source, target, dirty_work in ((1, 0, 0), (0, 1, 0), (0, 0, 1),
                                          (Fraction(3, 7), Fraction(-5, 11), 19)):
            expected_work = 0 if coefficient else dirty_work
            require(execute(word, [source, target, dirty_work]) == [
                source, target + coefficient * source, expected_work], "primitive boundary identity")
            primitive_checks += 1
        return len(word)

    old_costs = {i: sum(cost(a) for a in row.values()) for i, row in rows.items()}
    controls = boundary_controls(cost)
    by_exponent = {str(e): {"cases": 0, "max_saving_per_component": None,
                           "min_saving_per_component": None, "profitable_cases": 0}
                   for e in range(-3, 4)}
    records = []
    for i in targets:
        for j in targets:
            if i == j:
                continue
            # Group equal pairs of exact fractions; this changes no case coverage.
            histogram = Counter((rows[i].get(source, Fraction(0)),
                                 rows[j].get(source, Fraction(0)))
                                for source in rows[i].keys() | rows[j].keys())
            for exponent in range(-3, 4):
                bucket = by_exponent[str(exponent)]
                for sign in (-1, 1):
                    numerator, denominator = sign * 2 ** max(exponent, 0), 2 ** max(-exponent, 0)
                    lam = Fraction(numerator, denominator)
                    changed = sum(multiplicity * cost(a + lam * b)
                                  for (a, b), multiplicity in histogram.items())
                    saving = old_costs[i] - changed - 2 * cost(lam)
                    records.append([saving, i, j, numerator, denominator])
                    bucket["cases"] += 1
                    bucket["profitable_cases"] += int(saving > 0)
                    for key, choose in (("max_saving_per_component", max),
                                        ("min_saving_per_component", min)):
                        bucket[key] = saving if bucket[key] is None else choose(bucket[key], saving)
    require(len(records) == 112 * 111 * 14, "incomplete finite census")
    require(all(bucket["max_saving_per_component"] < 0
                for exponent, bucket in by_exponent.items() if exponent != "0"),
            "nonunit finite exclusion failed")
    return {
        "canonical_sha256": digest,
        "cases": len(records),
        "records_sha256": hashlib.sha256(json.dumps(records, separators=(",", ":")).encode()).hexdigest(),
        "by_exponent": by_exponent,
        "baseline_cost_per_component": sum(old_costs.values()),
        "primitive_lowering": {"distinct_coefficients": cost.cache_info().currsize,
                               "exact_boundary_checks": primitive_checks,
                               "dirty_work_included": True},
        "controls": controls,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="print checked deterministic receipt")
    args = parser.parse_args()
    here = Path(__file__).resolve().parent
    receipt = run(here.parents[1])
    expected = json.loads((here / "INDEPENDENT.json").read_text())
    require(same_json(receipt, expected), "independent receipt mismatch")
    if args.json:
        print(json.dumps(receipt, indent=2, sort_keys=True))
    print("PASS_X4_NONUNIT_INDEPENDENT cases=174048 nonunit=149184 no_new_kappa")


if __name__ == "__main__":
    main()
