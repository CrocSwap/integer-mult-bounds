"""Exact finite controls for the separately proved superunit-tail obstruction."""
from __future__ import annotations

import hashlib
import json
from fractions import Fraction as Q
from pathlib import Path

MAX_N = 64
ETAS = (Q(17, 16), Q(5, 4), Q(3, 2), Q(2), Q(3))
SIZES = (4, 8, 16, 32, 64)


def need(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def parameters(eta: Q, n: int) -> tuple[Q, Q]:
    need(Q(1) < eta <= Q(3), "finite checker requires 1 < eta <= 3")
    need(4 <= n <= MAX_N and n & (n - 1) == 0, "dyadic size in [4, 64]")
    a = (eta + 1) / 2
    b = (eta - 1) / 2
    need(a > 1 and b == a - 1 and a + b == eta, "parameter identities")
    return a, b


def identity(n: int) -> list[list[Q]]:
    return [[Q(i == j) for j in range(n)] for i in range(n)]


def toeplitz(symbol: list[Q]) -> list[list[Q]]:
    n = len(symbol)
    return [[symbol[i - j] if i >= j else Q(0)
             for j in range(n)] for i in range(n)]


def norm(matrix: list[list[Q]]) -> Q:
    return max(sum(map(abs, row)) for row in matrix)


def quotient(numerator: list[Q], denominator: list[Q]) -> list[Q]:
    need(len(numerator) == len(denominator) <= MAX_N, "division lengths")
    need(denominator[0] == 1, "unit denominator")
    out = [Q(0)] * len(numerator)
    for i, value in enumerate(numerator):
        out[i] = value - sum(denominator[j] * out[i - j]
                             for j in range(1, i + 1))
    return out


def shear(matrix: list[list[Q]], k: list[Q], upper: bool) -> list[list[Q]]:
    n, m = len(matrix), len(k)
    need(n == 2 * m <= MAX_N, "shear dimensions")
    out = [row.copy() for row in matrix]
    for i in range(m):
        for j in range(i if upper else i + 1):
            target = 2 * i if upper else 2 * i + 1
            source = 2 * j + 1 if upper else 2 * j
            coefficient = k[i - j - 1] if upper else k[i - j]
            for col in range(n):
                out[target][col] += coefficient * matrix[source][col]
    return out


def middle(matrix: list[list[Q]], e: list[Q], s: list[Q]) -> list[list[Q]]:
    n, m = len(matrix), len(e)
    out = [[Q(0)] * n for _ in range(n)]
    for parity, symbol in enumerate((e, s)):
        for i in range(m):
            for j in range(i + 1):
                for col in range(n):
                    out[2 * i + parity][col] += (
                        symbol[i - j] * matrix[2 * j + parity][col])
    return out


def one_case(eta: Q, n: int) -> dict[str, str | int]:
    a, b = parameters(eta, n)
    m = n // 2
    f = [Q(1), b, a] + [Q(0)] * (n - 3)
    e, o = f[::2], f[1::2]
    k = quotient(o, e)
    need(k == [b * (-a) ** j for j in range(m)], "geometric quotient")
    s = e.copy()
    for i in range(1, m):
        s[i] -= sum(o[j] * k[i - 1 - j] for j in range(i))
    unit = identity(n)
    u = shear(unit, k, upper=True)
    ui = shear(unit, [-value for value in k], upper=True)
    expected = a ** (m - 1)
    need(norm(u) == norm(ui) == expected, "exact prefix norm")
    need(shear(u, [-value for value in k], upper=True) == unit,
         "two-sided square-zero shear inverse")
    need(shear(ui, k, upper=True) == unit, "reverse inverse order")
    completed = shear(middle(u, e, s), k, upper=False)
    target = toeplitz(f)
    need(completed == target, "literal factorization endpoint")
    need(norm(target) == 1 + eta, "bounded completed output")
    row = u[n - 2]
    witness = [Q((value > 0) - (value < 0)) for value in row]
    need(max(map(abs, witness)) == 1, "unit input witness")
    need(sum(x * y for x, y in zip(row, witness)) == expected,
         "attained infinity norm on an explicit input")
    need(norm(u) == 1 + b * sum(a ** j for j in range(m - 1)),
         "row geometric sum")
    return {"eta": str(eta), "n": n, "a": str(a),
            "prefix_norm": str(expected), "completed_norm": str(1 + eta)}


def rejected(call, message: str) -> None:
    try:
        call()
    except ValueError as exc:
        need(message in str(exc), "wrong rejection reason")
    else:
        raise ValueError("control failed to reject: " + message)


def controls() -> int:
    rejected(lambda: parameters(Q(1), 8), "1 < eta")
    rejected(lambda: parameters(Q(4), 8), "1 < eta")
    rejected(lambda: parameters(Q(2), 6), "dyadic size")
    rejected(lambda: parameters(Q(2), 128), "dyadic size")
    rejected(lambda: quotient([Q(1)], [Q(2)]), "unit denominator")
    # Omitting Z incorrectly includes the last quotient coefficient.
    a, b = parameters(Q(3, 2), 8)
    need(1 + b * sum(a ** j for j in range(4)) != a ** 3,
         "unshifted-quotient control distinguishes the exponent")
    f = [Q(1), b, a] + [Q(0)] * 5
    e, o = f[::2], f[1::2]
    k = quotient(o, e)
    wrong = e.copy()
    for i in range(1, 4):
        wrong[i] += sum(o[j] * k[i - 1 - j] for j in range(i))
    result = shear(middle(shear(identity(8), k, True), e, wrong), k, False)
    need(result != toeplitz(f), "wrong Schur sign changes endpoint")
    return 7


def main() -> None:
    results = [one_case(eta, n) for eta in ETAS for n in SIZES]
    need(len(results) == 25, "finite fixture inventory")
    for eta in ETAS:
        a, _ = parameters(eta, 4)
        for n in SIZES[:-1]:
            small = Q(next(r["prefix_norm"] for r in results
                           if r["eta"] == str(eta) and r["n"] == n))
            large = Q(next(r["prefix_norm"] for r in results
                           if r["eta"] == str(eta) and r["n"] == 2 * n))
            need(large == a * small * small, "exact dyadic growth recurrence")
    control_count = controls()
    package = Path(__file__).resolve().parent
    hashes = {name: hashlib.sha256((package / name).read_bytes()).hexdigest()
              for name in ("README.md", "TASK.json", "SOURCES.json",
                           "VERIFY.json", "verify.py")}
    print(json.dumps({"claim_type": "scoped proof with finite controls",
                      "package_sha256": hashes, "fixtures": results,
                      "controls": control_count}, sort_keys=True))
    print(f"PASS_PARITY_TAIL_THRESHOLD fixtures={len(results)} "
          f"controls={control_count} max_n={MAX_N} no_new_kappa")


if __name__ == "__main__":
    main()
