#!/usr/bin/env python3
"""Exact finite corroboration of the rounded inverse oracle lower bound."""

from fractions import Fraction as F
from hashlib import sha256
from pathlib import Path
import ast
import json


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def parameters(p: int) -> tuple[F, F, F, F, F]:
    require(type(p) is int and 101 <= p <= 4096, "precision outside 101..4096")
    h = F(1, 2**p)
    eta = p * h / 3
    delta = eta - h
    return h, eta, delta, F(2, 5) - delta, F(2, 5) + delta


def rounded_numerator(n: int) -> int:
    """Nearest integer to 2*n/5. Its odd denominator excludes ties."""
    q, r = divmod(2 * n, 5)
    return q + int(2 * r > 5)


def oracle(z: tuple[tuple[int, int], tuple[int, int]]) -> tuple:
    """Grid numerators of the two complex entries, with their roles swapped."""
    return tuple(tuple(rounded_numerator(t) for t in w) for w in reversed(z))


def inverse_answer(c: F) -> tuple[F, F]:
    """Literal determinant inverse of [[1,c],[c,1]] on (1,-1)/2."""
    determinant = 1 - c * c
    require(determinant > 0, "singular or unsupported inverse")
    return (F(1, 2) + c / 2) / determinant, (-c / 2 - F(1, 2)) / determinant


def check_answer(c: F, answer: tuple[F, F]) -> None:
    x, y = answer
    require(x + c * y == F(1, 2), "first inverse equation")
    require(c * x + y == -F(1, 2), "second inverse equation")


def error_squared(actual: tuple[int, int], n: int, m: int, c: F, h: F) -> F:
    return h * h * ((actual[0] - c * n) ** 2 + (actual[1] - c * m) ** 2)


def check_rounding() -> dict:
    points = 0
    for p in range(8):
        scale = 2**p
        for n in range(-scale, scale + 1):
            for m in range(-scale, scale + 1):
                if n * n + m * m > scale * scale:
                    continue
                r, s = rounded_numerator(n), rounded_numerator(m)
                literal = tuple((F(2 * t, 5) + F(1, 2)).__floor__() for t in (n, m))
                require((r, s) == literal, "literal rounding disagrees")
                require((5 * r - 2 * n) ** 2 + (5 * s - 2 * m) ** 2 <= 8,
                        "complex rounding residual exceeds 8/25")
                require(r * r + s * s <= scale * scale, "rounded disk exit")
                require(rounded_numerator(-n) == -r, "rounding is not odd")
                points += 1
    residues = []
    for n in range(5):
        for m in range(5):
            r, s = rounded_numerator(n), rounded_numerator(m)
            residues.append((5 * r - 2 * n) ** 2 + (5 * s - 2 * m) ** 2)
    require(max(residues) == 8 and len(residues) == 25, "residue coverage")
    return {"disk_points": points, "residue_pairs": len(residues), "maximum_scaled_error_squared": 8}


def source_fixtures(p: int) -> tuple:
    scale = 2**p
    return ((0, 0), (1, 1), (-1, 2), (scale, 0), (-scale, 0),
            (0, scale), (scale // 2, -scale // 2),
            (3 * scale // 5, 4 * scale // 5))


def check_precision_cases() -> dict:
    precisions = tuple(range(101, 513)) + (768, 1024, 2048, 4096)
    samples = 0
    tail_powers = 0
    for p in precisions:
        h, eta, delta, lo, hi = parameters(p)
        require(0 < lo < hi < F(21, 50) < F(1, 2), "operator norm bounds")
        require(delta + h == eta and F(8, 25) < 1, "strict local margin")
        require(F(2, 5) + h < 1, "oracle disk bound")
        a, b = inverse_answer(lo), inverse_answer(hi)
        check_answer(lo, a)
        check_answer(hi, b)
        gap = max(abs(x - y) for x, y in zip(a, b))
        radius = delta / (2 * (F(9, 25) - delta * delta))
        require(gap == 2 * radius, "inverse separation formula")
        require(radius > F(25, 18) * delta > F(4, 9) * p * h, "linear floor")
        midpoint = tuple((x + y) / 2 for x, y in zip(a, b))
        require(max(abs(x - y) for x, y in zip(a, midpoint)) == radius,
                "two-instance midpoint radius")
        for n, m in source_fixtures(p):
            require(n * n + m * m <= 2 ** (2 * p), "fixture outside disk")
            z = ((n, m), (-m, n))
            got = oracle(z)
            require(oracle(tuple(tuple(-t for t in w) for w in z)) ==
                    tuple(tuple(-t for t in w) for w in got), "oracle oddness")
            for c in (lo, hi):
                for actual, (nr, ni) in zip(got, reversed(z)):
                    require(error_squared(actual, nr, ni, c, h) < eta * eta,
                            "common oracle violates local error")
                    samples += 1
        if p in (101, 128, 256):
            for c in (lo, hi):
                require(c**p < h, "literal tail-power check")
                tail_powers += 1
    return {"precision_cases": len(precisions), "local_component_checks": samples,
            "literal_tail_powers": tail_powers, "largest_precision": max(precisions)}


def rejected(call, message: str) -> None:
    try:
        call()
    except ValueError:
        return
    raise ValueError("accepted control: " + message)


def check_controls() -> dict:
    invalid = (False, 100, 4097, F(101), 101.0, "101")
    for value in invalid:
        rejected(lambda value=value: parameters(value), "invalid precision")
    h, eta, delta, lo, hi = parameters(128)
    a, b = inverse_answer(lo), inverse_answer(hi)
    wrong = ((lo, tuple(2 * t for t in a)), (hi, a),
             (lo, tuple(-t for t in a)), (lo, (a[1], a[0])))
    for c, answer in wrong:
        rejected(lambda c=c, answer=answer: check_answer(c, answer), "false inverse")
    scale = 2**128
    got = oracle(((scale, 0), (0, 0)))[1]
    require(max(error_squared(got, scale, 0, F(2, 5) + s * eta, h)
                for s in (-1, 1)) > eta * eta, "omitted rounding margin undetected")
    require(hi > h, "invalid one-call tail not detected")
    require(a != b and oracle(((0, 0), (0, 0))) == ((0, 0), (0, 0)),
            "hidden operator or zero-input discriminator")
    positive_gap = delta / (F(49, 25) - delta * delta)
    require(positive_gap / 2 < F(4, 9) * 128 * h, "wrong input eigenspace undetected")
    require(max(abs(x - y) for x, y in zip(a, b)) > F(8, 9) * 128 * h,
            "separation lost")
    return {"invalid_precisions_rejected": len(invalid),
            "false_inverse_answers_rejected": len(wrong), "semantic_discriminators": 4}


def check_pair_minimax() -> dict:
    """Independent one-dimensional two-instance decisions in rational units."""
    cases = 0
    for distance in range(1, 33):
        for numerator in range(-32, 65):
            answer = F(numerator, 2)
            left, right = abs(answer), abs(answer - distance)
            require(max(left, right) >= F(distance, 2), "deterministic minimax")
            radius = F(distance, 2) - F(1, 4)
            require(not (left < radius and right < radius), "overlapping success balls")
            cases += 1
    mixtures = 0
    for distance in range(1, 9):
        for weight in range(17):
            probability = F(weight, 16)
            e0, e1 = (1 - probability) * distance, probability * distance
            require(max(e0, e1) >= F(distance, 2), "randomized expected minimax")
            mixtures += 1
    return {"deterministic_decisions": cases, "two_output_mixtures": mixtures}


def package_hashes() -> dict:
    package = Path(__file__).resolve().parent
    names = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py")
    hashes = {}
    for name in names:
        path = package / name
        require(path.is_file() and not path.is_symlink(), "missing regular package file")
        require(path.stat().st_size <= 1024 * 1024, "package file exceeds 1 MiB")
        hashes[name] = sha256(path.read_bytes()).hexdigest()
    ast.parse((package / "verify.py").read_text())
    return hashes


def main() -> None:
    report = {"status": "PASS_NEUMANN_ORACLE_ERROR_FLOOR",
              "rounding": check_rounding(), "instances": check_precision_cases(),
              "controls": check_controls(), "minimax": check_pair_minimax(),
              "package_sha256": package_hashes()}
    print(json.dumps(report, sort_keys=True))


if __name__ == "__main__":
    main()
