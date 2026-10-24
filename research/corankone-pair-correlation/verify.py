"""Exact corroboration of the new correlation inequality; no file writes."""

from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path


def need(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def multiply(left: tuple[int, ...], right: tuple[int, ...]) -> tuple[int, ...]:
    need(1 <= len(left) <= 4 and 1 <= len(right) <= 4, "polynomial degree")
    result = [0] * (len(left) + len(right) - 1)
    for i, first in enumerate(left):
        for j, second in enumerate(right):
            result[i + j] += first * second
    return tuple(result)


def polynomial_check() -> dict[str, list[int]]:
    square = multiply((1, -1, 1), (1, -1, 1))
    qb = (0, 1, -1, 0, 1)
    difference = tuple(qb[i] - square[i] for i in range(5))
    factorization = multiply((-1, 1), (1, -2, 2)) + (0,)
    need(difference == factorization, "q beta - alpha factorization")
    need(difference != (0, -1, 3, -2, 0), "reversed-sign control")
    return {"alpha": list(square), "q_beta_minus_alpha": list(difference)}


def probabilities(q: int, m: int) -> tuple[Fraction, Fraction]:
    need(type(q) is int and 2 <= q <= 64, "q outside finite replay domain")
    need(type(m) is int and 2 <= m <= 65, "m outside finite replay domain")
    n = m - 1
    s, beta, gamma = q * q - q + 1, q**3 - q + 1, q**3 - q * q + 1
    marginal = Fraction((q - 1) * s**n, q**n * (q**m - 1))
    joint = Fraction(
        (q - 1) ** 2 * (s ** (2 * n) - 2 * beta**n + gamma**n),
        q ** (2 * n) * (q**m - 1) * (q**m - q),
    )
    return marginal, joint


def compare(q: int, m: int) -> Fraction:
    marginal, joint = probabilities(q, m)
    n, total = m - 1, q**m
    alpha = (q * q - q + 1) ** 2
    beta, gamma = q**3 - q + 1, q**3 - q * q + 1
    need(beta - gamma == q * (q - 1) > 0, "ordered correction bases")
    need(q * beta - alpha == (q - 1) * (2 * q * q - 2 * q + 1) > 0,
         "positive factored polynomial")
    need(q**n * (2 * beta**n - gamma**n) > alpha**n, "power comparison")
    ratio = joint / marginal**2
    expression = Fraction(
        (total - 1) * (alpha**n - 2 * beta**n + gamma**n),
        (total - q) * alpha**n,
    )
    need(ratio == expression, "ratio algebra")
    need(0 <= joint <= marginal <= 1, "probability ranges")
    need(ratio < Fraction(total - 1, total) < 1, "strict quantitative bound")
    return ratio


def controls() -> int:
    q, m = 5, 2
    marginal, joint = probabilities(q, m)
    upper = Fraction(q**m - 1, q**m) * marginal**2
    need(not marginal**2 < upper, "independence control")
    alpha, beta, gamma = 441, 121, 101
    denominator = q**2 * (q**m - 1) * (q**m - q)
    for wrong_sum in (alpha + gamma, alpha - 2 * gamma + beta):
        mutant = Fraction((q - 1) ** 2 * wrong_sum, denominator)
        need(not mutant < upper, "correction-term mutation")
    header, inverse = ((1, 1), (1, 2)), ((2, 2), (2, 1))
    for i in range(2):
        for j in range(2):
            entry = sum(header[i][k] * inverse[k][j] for k in range(2)) % 3
            need(entry == int(i == j), "restricted-header inverse")
    for kernel in range(2):
        diagonal = header[0][1 - kernel] * inverse[1 - kernel][0] % 3
        need(diagonal == 2, "singleton full guard")
    need(not Fraction(1) < Fraction(8, 9), "restricted-header control")
    rejected = 0
    for args in ((1, 2), (5, 1), (65, 2), (5, 66), (2.0, 2)):
        try:
            probabilities(*args)
        except ValueError:
            rejected += 1
    need(rejected == 5, "finite-domain rejection controls")
    need(joint == Fraction(2, 5), "cited q=5,m=2 fixture")
    return 4 + rejected


def main() -> None:
    polynomials = polynomial_check()
    cases = 0
    for q in range(2, 65):
        for m in range(2, 66):
            compare(q, m)
            cases += 1
    fixtures = ((2, 3, Fraction(28, 243)), (3, 2, Fraction(24, 49)),
                (5, 2, Fraction(40, 49)))
    examples = []
    for q, m, expected in fixtures:
        ratio = compare(q, m)
        need(ratio == expected, "published overlap fixture")
        examples.append({"q": q, "m": m, "joint_to_product": str(ratio)})
    control_count = controls()
    package = Path(__file__).resolve().parent
    names = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json",
             "VERIFY.json", "verify.py")
    hashes = {name: sha256((package / name).read_bytes()).hexdigest() for name in names}
    print(json.dumps({"status": "PASS_CORANKONE_PAIR_CORRELATION",
                      "claim_type": "scoped proof with finite corroboration",
                      "integer_parameter_cases": cases, "q_range": [2, 64],
                      "m_range": [2, 65], "controls": control_count,
                      "polynomial_identities": polynomials, "examples": examples,
                      "sha256": hashes}, sort_keys=True))


if __name__ == "__main__":
    main()
