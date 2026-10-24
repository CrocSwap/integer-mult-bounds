#!/usr/bin/env python3
"""Exact finite checks of minimum weighted-reversal rescaling.

Produced by Nick Petalas. Apache-2.0. Python managed allocation is used.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from math import gcd
from pathlib import Path

HERE = Path(__file__).resolve().parent


def need(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def units(modulus: int) -> tuple[int, ...]:
    need(type(modulus) is int and 2 <= modulus <= 16, "finite modulus domain")
    return tuple(x for x in range(modulus) if gcd(x, modulus) == 1)


def validate(weights: tuple[int, ...], modulus: int) -> tuple[int, ...]:
    group = units(modulus)
    need(1 <= len(weights) <= 6, "finite length domain")
    need(all(type(x) is int and x in group for x in weights), "unit weights")
    return group


def polynomial(weights: tuple[int, ...], modulus: int) -> list[int]:
    """The exponent counts nonidentity scales on both output banks."""
    group = validate(weights, modulus)
    phi = len(group)
    rho = sum(x * x % modulus == 1 for x in group)
    result = [1]
    n = len(weights)
    for i in range((n + 1) // 2):
        j = n - 1 - i
        good = weights[i] * weights[j] % modulus == 1
        if i == j:
            factor = [1, 0, rho - 1] if good else [0, 0, rho]
        else:
            factor = [1, 0, 0, 0, phi - 1] if good else [0, 0, 2, 0, phi - 2]
        combined = [0] * (len(result) + len(factor) - 1)
        for a, value in enumerate(result):
            for b, coefficient in enumerate(factor):
                combined[a + b] += value * coefficient
        result = combined
    return result + [0] * (2 * n + 1 - len(result))


def predicted_minimum(weights: tuple[int, ...], modulus: int) -> tuple[int, int]:
    group = validate(weights, modulus)
    rho = sum(x * x % modulus == 1 for x in group)
    pairs = center = 0
    for i in range((len(weights) + 1) // 2):
        j = len(weights) - 1 - i
        if weights[i] * weights[j] % modulus != 1:
            center += i == j
            pairs += i != j
    return 2 * (pairs + center), 2 ** pairs * rho ** center


def predicted_common(weights: tuple[int, ...], modulus: int) -> tuple[int | None, int]:
    validate(weights, modulus)
    defects = set()
    pairs = 0
    for i in range((len(weights) + 1) // 2):
        j = len(weights) - 1 - i
        defect = weights[i] * weights[j] % modulus
        if defect == 1:
            continue
        if i == j:
            return None, 0
        defects.add(defect)
        pairs += 1
    if not defects:
        return 0, 1
    if len(defects) != 1:
        return None, 0
    scalar = next(iter(defects))
    if scalar * scalar % modulus != 1:
        return None, 0
    return 2 * pairs, 2 ** pairs


def literal_accepts(weights: tuple[int, ...], u: tuple[int, ...],
                    v: tuple[int, ...], modulus: int) -> bool:
    """Compare actual monomial bank maps, then square the first bank map."""
    n = len(weights)
    first = tuple(u[i] * weights[i] % modulus for i in range(n))
    second = tuple(v[i] * pow(weights[n - 1 - i], -1, modulus) % modulus
                   for i in range(n))
    return first == second and all(first[i] * first[n - 1 - i] % modulus == 1
                                   for i in range(n))


def exhaustive(weights: tuple[int, ...], modulus: int) -> tuple[list[int], tuple[int | None, int], int]:
    group = validate(weights, modulus)
    n = len(weights)
    need(len(group) ** (2 * n) <= 4096, "dual-scale enumeration cap")
    candidates = tuple(itertools.product(group, repeat=n))
    histogram = [0] * (2 * n + 1)
    common = [0] * (2 * n + 1)
    for u in candidates:
        for v in candidates:
            if literal_accepts(weights, u, v, modulus):
                support = sum(x != 1 for x in u + v)
                histogram[support] += 1
                if len(set(u + v) - {1}) <= 1:
                    common[support] += 1
    minimum = next((i for i, value in enumerate(common) if value), None)
    return histogram, (minimum, 0 if minimum is None else common[minimum]), len(candidates) ** 2


def callee(h: tuple[int, ...], d: tuple[int, ...], weights: tuple[int, ...],
           u: tuple[int, ...], v: tuple[int, ...], modulus: int) -> tuple[tuple[int, ...], tuple[int, ...]]:
    n = len(weights)
    first = tuple(u[i] * weights[i] * d[n - 1 - i] % modulus for i in range(n))
    second = tuple(v[i] * pow(weights[n - 1 - i], -1, modulus)
                   * h[n - 1 - i] % modulus for i in range(n))
    return first, second


def wrapper_basis(weights: tuple[int, ...], u: tuple[int, ...],
                  v: tuple[int, ...], modulus: int) -> int:
    n = len(weights)
    for column in range(2 * n):
        original_h = tuple(int(i == column) for i in range(n))
        original_d = tuple(int(n + i == column) for i in range(n))
        h = original_h
        d = tuple((original_d[i] - h[i]) % modulus for i in range(n))
        h, d = callee(h, d, weights, u, v, modulus)
        d = tuple((d[i] + h[i]) % modulus for i in range(n))
        h, d = callee(h, d, weights, u, v, modulus)
        d = tuple((-d[i] + h[i]) % modulus for i in range(n))
        need((h, d) == (original_d, original_h), "literal dirty wrapper")
    return 2 * n


def minimum_repairs(weights: tuple[int, ...], modulus: int) -> list[tuple[tuple[int, ...], tuple[int, ...]]]:
    group = validate(weights, modulus)
    n = len(weights)
    choices = []
    for i in range((n + 1) // 2):
        j = n - 1 - i
        defect = weights[i] * weights[j] % modulus
        if defect == 1:
            choices.append(((i, j, 1, 1),))
        elif i != j:
            inverse = pow(defect, -1, modulus)
            choices.append(((i, j, inverse, 1), (i, j, 1, inverse)))
        else:
            choices.append(tuple((i, j, root * pow(weights[i], -1, modulus) % modulus,
                                  root * pow(weights[i], -1, modulus) % modulus)
                                 for root in group if root * root % modulus == 1))
    repairs = []
    for selection in itertools.product(*choices):
        u = [1] * n
        for i, j, left, right in selection:
            u[i], u[j] = left, right
        v = tuple(pow(u[n - 1 - i], -1, modulus) for i in range(n))
        repairs.append((tuple(u), v))
    return repairs


def controls() -> int:
    rejected = 0
    for weights, modulus in [((0, 1), 5), ((True,), 3), ((), 3), ((1,), 1)]:
        try:
            validate(weights, modulus)
        except ValueError:
            rejected += 1
    need(rejected == 4, "input controls")
    weights, modulus = (2, 1), 15
    u, v = minimum_repairs(weights, modulus)[0]
    need(literal_accepts(weights, u, v, modulus), "positive repair")
    need(not literal_accepts(weights, u, (1, 1), modulus), "omitted D-bank scale")
    need(not literal_accepts(weights, u, tuple(reversed(v)), modulus), "wrong D support")
    need(not literal_accepts(weights, u, u, modulus), "equal diagonal maps")
    need(predicted_common((2,), 15) == (None, 0), "central common-scale obstruction")
    need(predicted_common((4, 1), 15) == (2, 2), "common involution attains")
    need(predicted_common((4, 11, 1, 1), 15) == (None, 0), "different pair defects")
    return rejected + 6


def build() -> dict:
    records = []
    cases = [(m, n) for m in range(2, 9) for n in (1, 2)]
    cases += [(m, 3) for m in (2, 3, 4, 5, 6, 8)]
    cases += [(3, 4), (4, 4), (3, 5)]
    assignments = 0
    for modulus, n in cases:
        group = units(modulus)
        totals = [0] * (2 * n + 1)
        for weights in itertools.product(group, repeat=n):
            actual, common, checked = exhaustive(weights, modulus)
            need(actual == polynomial(weights, modulus), "full support polynomial")
            minimum = next(i for i, value in enumerate(actual) if value)
            need((minimum, actual[minimum]) == predicted_minimum(weights, modulus), "minimum")
            need(common == predicted_common(weights, modulus), "common-scalar criterion")
            assignments += checked
            totals = [a + b for a, b in zip(totals, actual)]
        records.append({"modulus": modulus, "length": n, "weight_lists": len(group) ** n,
                        "accepted_support_histogram": totals})
    fixtures = []
    basis_columns = 0
    for modulus, weights in [(15, (2, 2, 2, 1, 1, 1)), (15, (1, 2, 1)),
                              (15, (4, 4, 1, 1)), (8, (3, 5, 1, 1)),
                              (9, (4, 1, 1, 1)), (2, (1,))]:
        repairs = minimum_repairs(weights, modulus)
        minimum, count = predicted_minimum(weights, modulus)
        need(len(repairs) == len(set(repairs)) == count, "distinct minimum repairs")
        for u, v in repairs:
            need(literal_accepts(weights, u, v, modulus), "constructed endpoint")
            need(sum(x != 1 for x in u + v) == minimum, "constructed minimum support")
            basis_columns += wrapper_basis(weights, u, v, modulus)
        fixtures.append({"modulus": modulus, "weights": weights, "minimum_support": minimum,
                         "repairs": repairs, "common_minimum": predicted_common(weights, modulus)})
    return {"enumeration": records, "scale_assignments": assignments,
            "weight_lists": sum(row["weight_lists"] for row in records), "fixtures": fixtures,
            "wrapper_basis_columns": basis_columns, "controls": controls()}


def serialized(value: object) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def receipt() -> dict:
    names = ("README.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py")
    hashes = {name: hashlib.sha256((HERE / name).read_bytes()).hexdigest() for name in names}
    return {"schema_version": 1, "source_sha256": hashes, "results": build()}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit-to", type=Path, help="exclusive-create a fresh external receipt")
    args = parser.parse_args()
    fresh = receipt()
    if args.emit_to is not None:
        destination = args.emit_to.resolve()
        need(not destination.is_relative_to(HERE), "emit outside package")
        with destination.open("x", encoding="utf-8") as stream:
            stream.write(serialized(fresh))
    else:
        stored = json.loads((HERE / "RESULT.json").read_text(encoding="utf-8"))
        need(serialized(stored) == serialized(fresh), "typed receipt/source mismatch")
    result = fresh["results"]
    print("PASS_WEIGHTED_REVERSAL_RESCALING", "weights=" + str(result["weight_lists"]),
          "assignments=" + str(result["scale_assignments"]),
          "wrapper_columns=" + str(result["wrapper_basis_columns"]),
          "controls=" + str(result["controls"]), "no_new_kappa")


if __name__ == "__main__":
    main()
