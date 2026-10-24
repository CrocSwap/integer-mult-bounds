"""Exact checks of the one-way correlation inequality; standard library only."""

from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path


MAX_Q = 64
MAX_M = 65


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def convolution(left: tuple[int, ...], right: tuple[int, ...]) -> tuple[int, ...]:
    require(1 <= len(left) <= 4 and 1 <= len(right) <= 4, "polynomial capacity")
    result = [0] * (len(left) + len(right) - 1)
    for i, a in enumerate(left):
        for j, b in enumerate(right):
            result[i + j] += a * b
    return tuple(result)


def check_polynomial() -> list[int]:
    alpha = convolution((1, -1, 1), (1, -1, 1))
    q_gamma = (0, 1, 0, -1, 1)
    difference = tuple(a - b for a, b in zip(q_gamma, alpha, strict=True))
    cube = convolution(convolution((-1, 1), (-1, 1)), (-1, 1)) + (0,)
    require(difference == cube, "q gamma - alpha = (q-1)^3")
    require(difference != tuple(-a for a in cube), "reversed-sign control")
    return list(difference)


def probabilities(q: int, m: int) -> tuple[Fraction, Fraction]:
    require(type(q) is int and 2 <= q <= MAX_Q, "q outside finite check domain")
    require(type(m) is int and 2 <= m <= MAX_M, "m outside finite check domain")
    n, t = m - 1, q**m
    s, beta, gamma = q * q - q + 1, q**3 - q + 1, q**3 - q * q + 1
    p = Fraction((q - 1) * s**n, q**n * (t - 1))
    j = Fraction(
        (q - 1) * ((q - 1) * s ** (2 * n) - (q - 2) * beta**n - gamma**n),
        q ** (2 * n) * (t - 1) * (t - q),
    )
    return p, j


def compare(q: int, m: int) -> Fraction:
    p, j = probabilities(q, m)
    n, t = m - 1, q**m
    alpha, beta, gamma = (q * q - q + 1) ** 2, q**3 - q + 1, q**3 - q * q + 1
    correction = Fraction((q - 2) * beta**n + gamma**n, (q - 1) * alpha**n)
    require(beta > gamma > 0, "ordered positive bases")
    require(q * gamma - alpha == (q - 1) ** 3 > 0, "positive polynomial")
    require(correction >= Fraction(gamma**n, alpha**n) > Fraction(1, q**n),
            "dimension-uniform power comparison")
    ratio = j / p**2
    require(ratio == Fraction(t - 1, t - q) * (1 - correction), "ratio identity")
    require(0 <= j <= p <= 1, "probability ranges")
    require(ratio < Fraction(t - 1, t) < 1, "strict quantitative bound")
    return ratio


def restricted_header_control() -> None:
    header = ((1, 0), (1, 1))
    u, v = ((1, 1), (0, 0)), ((0, 0), (0, 1))
    for i in range(2):
        for j in range(2):
            require(sum(header[i][k] * header[k][j] for k in range(2)) % 2
                    == int(i == j), "literal header inverse")
            uv = sum(u[i][k] * v[k][j] for k in range(2)) % 2
            vu = sum(v[i][k] * u[k][j] for k in range(2)) % 2
            require(uv == int(i == 0 and j == 1) and vu == 0, "one-way coupling")
    for kernel in (u, v):
        diagonal = sum(header[0][i] * (int(i == j) - kernel[i][j]) * header[j][0]
                       for i in range(2) for j in range(2)) % 2
        require(diagonal == 1, "both singleton full guards pass")
    require(not Fraction(1) < Fraction(3, 4), "restricted-domain rejection")


def mutation_controls() -> int:
    p, j = probabilities(2, 2)
    upper = Fraction(3, 4) * p**2
    require(not p**2 < upper, "independence cannot pass")
    denominator = 2**2 * (2**2 - 1) * (2**2 - 2)
    for wrong_numerator in (9 + 5, 9):
        mutant = Fraction(wrong_numerator, denominator)
        require(not mutant < upper, "wrong or missing correction rejected")
    require(j == Fraction(1, 6), "boundary fixture")
    restricted_header_control()
    rejected = 0
    for args in ((1, 2), (2, 1), (65, 2), (2, 66), (2.0, 2), (True, 2)):
        try:
            probabilities(*args)
        except ValueError:
            rejected += 1
    require(rejected == 6, "finite-domain rejection controls")
    return 4 + rejected


def file_hashes() -> dict[str, str]:
    package = Path(__file__).resolve().parent
    names = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json",
             "VERIFY.json", "verify.py")
    hashes = {}
    for name in names:
        path = package / name
        require(path.stat().st_size <= 1024 * 1024, "package-file capacity")
        hashes[name] = sha256(path.read_bytes()).hexdigest()
    return hashes


def main() -> None:
    polynomial = check_polynomial()
    cases = 0
    for q in range(2, MAX_Q + 1):
        for m in range(2, MAX_M + 1):
            require(compare(q, m) < 1, "each comparison completed")
            cases += 1
    fixtures = ((2, 2, "1/2", "1/6"), (2, 3, "9/28", "1/12"),
                (3, 3, "49/117", "53/351"), (4, 2, "13/20", "7/20"),
                (5, 2, "7/10", "13/30"))
    examples = []
    for q, m, expected_p, expected_j in fixtures:
        p, j = probabilities(q, m)
        require(p == Fraction(expected_p) and j == Fraction(expected_j),
                "exact fixture")
        examples.append({"q": q, "m": m, "p": str(p), "J": str(j),
                         "J_over_p_squared": str(compare(q, m))})
    print(json.dumps({"status": "PASS_ONEWAY_PAIR_CORRELATION",
                      "claim_type": "scoped algebraic proof with finite corroboration",
                      "integer_parameter_cases": cases, "q_range": [2, MAX_Q],
                      "m_range": [2, MAX_M], "controls": mutation_controls(),
                      "q_gamma_minus_alpha_coefficients": polynomial,
                      "examples": examples, "sha256": file_hashes()}, sort_keys=True))


if __name__ == "__main__":
    main()
