#!/usr/bin/env python3
"""Exact finite corroboration of the new Gaussian boundary lower estimate."""
from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction as F
from math import isqrt
from pathlib import Path


def need(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def inverse(matrix: list[list[F]]) -> list[list[F]]:
    n = len(matrix)
    need(1 <= n <= 5 and all(len(row) == n for row in matrix), "matrix size")
    rows = [row[:] + [F(i == j) for j in range(n)]
            for i, row in enumerate(matrix)]
    for col in range(n):
        pivot = next((k for k in range(col, n) if rows[k][col]), None)
        need(pivot is not None, "singular matrix")
        rows[col], rows[pivot] = rows[pivot], rows[col]
        value = rows[col][col]
        rows[col] = [x / value for x in rows[col]]
        for k in range(n):
            if k != col:
                value = rows[k][col]
                rows[k] = [x - value * y for x, y in zip(rows[k], rows[col])]
    return [row[n:] for row in rows]


def inverse_sum(n: int, q: F) -> list[list[F]]:
    """The cited finite q-LDU formula, with no predecessor code import."""
    products = [F(1)]
    for k in range(1, n):
        products.append(products[-1] * (1 - q ** (2 * k)))
    result = [[F(0) for _ in range(n)] for _ in range(n)]
    for i in range(n):
        for j in range(n):
            value = sum((q ** (2 * k - i - j) * products[k]
                         / (products[i] * products[k - i]
                            * products[j] * products[k - j])
                         for k in range(max(i, j), n)), F(0))
            result[i][j] = (-1) ** (i + j) * value
    return result


def fixture(n: int, h: int, r: F) -> dict[str, int]:
    """Rational exact Gaussians with theta=1/h and arbitrary positive b0."""
    need(2 <= n <= 5 and n <= h <= 16, "fixture phase/size")
    need(F(0) < r < F(1), "Gaussian base")
    alpha, degree = F(3, 2), 4 * h * (h + 1)
    q = r ** degree
    gaussian = [[q ** ((i - j) ** 2) for j in range(n)] for i in range(n)]
    exact_g = inverse(gaussian)
    need(exact_g == inverse_sum(n, q), "finite inverse sum")
    matrix = [[r ** ((2 * (h + 1) * i - 2 * h * k - h) ** 2) / alpha
               for i in range(n)] for k in range(n)]
    exact = inverse(matrix)
    for i in range(n):
        col = 4 * (h + 1) * i * i - 4 * h * (h + 1) * i
        for j in range(n):
            row = -4 * h * j * j + 4 * h * h * j + h * h
            signed = (-1) ** (i + j) * exact[i][j]
            need(exact[i][j] == alpha * r ** (-col - row) * exact_g[i][j],
                 "inverse gauge identity")
            need(signed >= alpha * r ** (degree * abs(i - j) - col - row),
                 "positive single-term lower estimate")
    rectangles = 0
    for m in range(1, n // 2 + 1):
        floor = alpha * r ** (4 * (h + 1) * (2 * m - 1) ** 2)
        for i in range(m):
            for j in range(m, 2 * m):
                need((-1) ** (i + j) * exact[i][j] >= floor, "rectangle")
        vector = [F((-1) ** j if m <= j < 2 * m else 0) for j in range(n)]
        output = [sum((x * y for x, y in zip(row, vector)), F(0))
                  for row in exact]
        need(sum(x * x for x in output) >= m * (m * floor) ** 2,
             "explicit alternating test vector")
        rectangles += 1
    return {"entries": n * n, "rectangles": rectangles}


def coefficient_checks() -> dict[str, int]:
    pairs = 0
    for h in (16, 64, 400, 1600):
        theta, rho = F(1, h), F(h + 1, h)
        c, m = 1 / (2 * rho), isqrt(h) // 2
        for i in range(m):
            for j in range(m, 2 * m):
                beta_i, beta_j = theta * i - F(1, 2), theta * j - F(1, 2)
                raw = (theta / rho * i * i - 2 * c * i
                       - theta / rho ** 2 * j * j + 2 * c / rho * j
                       + c * c - abs(i - j) / rho)
                coupled = beta_j ** 2 / rho ** 2 - theta / rho * (j * j - i * i)
                need(raw == coupled, "coupled boundary exponent")
                need(-F(1, 2) <= beta_i <= beta_j <= F(1, 2), "phase")
                need(raw >= -theta / rho * (2 * m - 1) ** 2, "exponent floor")
                pairs += 1
    for h in range(16, 1025):
        m = isqrt(h) // 2
        need(16 * m * m >= h and (2 * m - 1) ** 2 <= h, "floor inequalities")
    # pi < 22/7 and exp(-t) >= 1-t+t^2/2-t^3/6 for 0<t<1.
    t = F(22, 63) * F(361, 400)
    lower = 30 * (1 - t + t * t / 2 - t ** 3 / 6)
    need(lower > F(109, 5), "actual alpha=3, theta=1/400 lower certificate")
    return {"exponent_pairs": pairs, "floor_cases": 1009,
            "first_fixture_lower_numerator": lower.numerator,
            "first_fixture_lower_denominator": lower.denominator}


def controls() -> int:
    rejected = 0
    for n, h, r in ((1, 4, F(1, 2)), (4, 3, F(1, 2)),
                    (6, 8, F(1, 2)), (2, 17, F(1, 2)),
                    (2, 4, F(0)), (2, 4, F(1))):
        try:
            fixture(n, h, r)
        except ValueError:
            rejected += 1
        else:
            raise ValueError("invalid fixture accepted")
    try:
        inverse([[F(1), F(1)], [F(1), F(1)]])
    except ValueError:
        rejected += 1
    else:
        raise ValueError("singular control accepted")
    gi = inverse([[F(1), F(1, 2)], [F(1, 2), F(1)]])
    need(gi[0][1] < 0, "omitting checkerboard signs must fail")
    need((-1) * gi[0][1] >= F(1, 2), "signed positive control")
    need((-1) * gi[0][1] < F(1), "overstated one-term floor must fail")
    return rejected + 2


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()
    entries = rectangles = cases = 0
    for h in (2, 3, 4, 6, 9, 16):
        for n in range(2, min(h, 5) + 1):
            for r in (F(1, 2), F(2, 3)):
                result = fixture(n, h, r)
                entries += result["entries"]
                rectangles += result["rectangles"]
                cases += 1
    report = {"status": "PASS_GAUSSIAN_PHASE_CELL_LOWER", "exact_gaussian_cases": cases,
              "inverse_entries": entries, "rectangle_tests": rectangles,
              "controls": controls(), **coefficient_checks(), "new_kappa": False}
    package = Path(__file__).resolve().parent
    names = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py")
    report["sha256"] = {name: hashlib.sha256((package / name).read_bytes()).hexdigest()
                        for name in names}
    payload = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.receipt:
        target = args.receipt.resolve()
        need(not target.is_relative_to(package), "receipt must be outside package")
        with target.open("x", encoding="utf-8") as handle:
            written = handle.write(payload)
        need(written == len(payload), "complete receipt write")
    print(payload, end="")


if __name__ == "__main__":
    main()
