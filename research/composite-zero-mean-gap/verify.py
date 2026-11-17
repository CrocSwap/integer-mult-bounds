#!/usr/bin/env python3
"""Exact corroboration of the new mixed-radix height and gap estimates."""

from fractions import Fraction as Q
from hashlib import sha256
from math import factorial, gcd, isqrt
from pathlib import Path
import json


BITS = 80
SCALE = 1 << BITS
MAX_RADIX = 1 << 32


def require(condition, message):
    if not condition:
        raise ValueError(message)


def outward(lo, hi):
    require(lo <= hi, "reversed interval")
    return (Q((lo * SCALE).__floor__(), SCALE),
            Q((hi * SCALE).__ceil__(), SCALE))


def plus(a, b):
    return outward(a[0] + b[0], a[1] + b[1])


def times(a, b):
    products = (a[0] * b[0], a[0] * b[1],
                a[1] * b[0], a[1] * b[1])
    return outward(min(products), max(products))


def arctangent_reciprocal(denominator, terms):
    require(2 <= denominator <= 239 and 1 <= terms <= 64,
            "arctangent domain")
    value = sum((Q((-1) ** j, (2 * j + 1) * denominator ** (2 * j + 1))
                 for j in range(terms)), Q(0))
    other = value + Q((-1) ** terms,
                      (2 * terms + 1) * denominator ** (2 * terms + 1))
    return outward(min(value, other), max(value, other))


def pi_interval():
    a = arctangent_reciprocal(5, 40)
    b = arctangent_reciprocal(239, 12)
    return outward(16 * a[0] - 4 * b[1], 16 * a[1] - 4 * b[0])


def root_modulus(radix, residue, pi):
    require(3 <= radix <= 30 and 1 <= residue < radix, "root domain")
    distance = min(residue, radix - residue)
    angle = outward(2 * pi[0] * distance / radix,
                    2 * pi[1] * distance / radix)
    cosine = (Q(0), Q(0))
    for j in range(24):
        low = angle[0] ** (2 * j) / factorial(2 * j)
        high = angle[1] ** (2 * j) / factorial(2 * j)
        term = (low, high) if j % 2 == 0 else (-high, -low)
        cosine = plus(cosine, term)
    # Taylor's remainder after degree 47: |remainder| <= angle^48/48!.
    error = angle[1] ** 48 / factorial(48)
    squared = outward(2 - 2 * (cosine[1] + error),
                      2 - 2 * (cosine[0] - error))
    require(squared[0] > 0, "nonzero root modulus")
    low = isqrt((squared[0] * SCALE * SCALE).__floor__())
    high = isqrt((squared[1] * SCALE * SCALE).__floor__()) + 1
    result = (Q(low, SCALE), Q(high, SCALE))
    require(result[0] ** 2 <= squared[0] and
            result[1] ** 2 >= squared[1], "square-root enclosure")
    return result


def reduced_log(value):
    require(Q(1) <= value <= Q(2), "reduced logarithm domain")
    x = (value - 1) / (value + 1)
    partial = 2 * sum((x ** (2 * j + 1) / (2 * j + 1)
                       for j in range(40)), Q(0))
    tail = 2 * x ** 81 / (81 * (1 - x * x))
    return outward(partial, partial + tail)


def logarithm(value, log_two):
    require(Q(1) <= value <= (1 << 32), "logarithm domain")
    exponent = value.numerator.bit_length() - value.denominator.bit_length()
    # This estimate differs from floor(log2(value)) by at most one.
    if value < 2 ** exponent:
        exponent -= 1
    require(0 <= exponent <= 32, "logarithm exponent")
    reduced = reduced_log(value / (1 << exponent))
    return plus((exponent * log_two[0], exponent * log_two[1]), reduced)


def totient(radix):
    require(type(radix) is int and 3 <= radix <= MAX_RADIX, "radix domain")
    remainder, answer = radix, radix
    for divisor in range(2, isqrt(radix) + 1):
        if divisor * divisor > remainder:
            break
        if remainder % divisor == 0:
            answer -= answer // divisor
            for _ in range(radix.bit_length()):
                if remainder % divisor:
                    break
                remainder //= divisor
            require(remainder % divisor != 0, "factor removal exhausted")
    if remainder > 1:
        answer -= answer // remainder
    return answer


def gap_exponents(radix):
    degree = totient(radix)
    ell = (radix - 1).bit_length()
    n = radix - 1
    coarse = n * degree * radix
    new_numerator = n * (3 * radix * ell * ell + 4 * (radix + degree) * ell)
    new_term = (new_numerator + 3) // 4
    old_term = 3 * n * radix * (ell + 1) ** 2 // 2 + 2 * n * degree * ell
    require(Q(new_numerator, 4) <= new_term < Q(new_numerator, 4) + 1,
            "integer ceiling")
    require(new_term < old_term, "new analytic branch must improve")
    return (1 + 2 * ell + min(coarse, new_term),
            1 + 2 * ell + min(coarse, old_term))


def height_instance(radix, pi, log_two):
    require(3 <= radix <= 30, "height-instance domain")
    moduli = [None] + [root_modulus(radix, s, pi) for s in range(1, radix)]
    total = (Q(0), Q(0))
    embeddings = 0
    for k in range(1, radix):
        if gcd(k, radix) != 1:
            continue
        suffix, height = (Q(1), Q(1)), (Q(1), Q(1))
        for s in range(radix - 1, 0, -1):
            suffix = times(suffix, moduli[k * s % radix])
            height = plus(height, suffix)
        log_height = (logarithm(height[0], log_two)[0],
                      logarithm(height[1], log_two)[1])
        total = plus(total, log_height)
        embeddings += 1
    require(embeddings == totient(radix), "embedding count")
    log_radix = logarithm(Q(radix), log_two)
    bound = plus(times((Q(radix), Q(radix)),
                       times(log_radix, plus((Q(1), Q(1)), log_radix))),
                 times((Q(embeddings), Q(embeddings)), log_radix))
    require(total[1] < bound[0], "new averaged height bound")
    return {"radix": radix, "embeddings": embeddings,
            "height_log_sum_upper": total[1].__ceil__(),
            "new_bound_lower": bound[0].__floor__()}


def new_dyadic_inequality():
    log_two = reduced_log(Q(2))
    require(Q(2, 3) < log_two[0] <= log_two[1] < Q(3, 4), "log two")
    cases = 0
    for radix in range(3, 257):
        degree = totient(radix)
        ell = (radix - 1).bit_length()
        log_radix = logarithm(Q(radix), log_two)
        height_bound = plus(times((Q(radix), Q(radix)),
                                 times(log_radix, plus((Q(1), Q(1)), log_radix))),
                           times((Q(degree), Q(degree)), log_radix))
        dyadic = Q(3 * radix * ell * ell, 4) + (radix + degree) * ell
        require(height_bound[1] / log_two[0] < dyadic,
                "new natural-to-binary conversion")
        cases += 1
    return log_two, cases


def rejection_controls():
    invalid = (True, 0, 1, 2, -3, MAX_RADIX + 1, Q(6))
    rejected = 0
    for radix in invalid:
        try:
            gap_exponents(radix)
        except ValueError:
            rejected += 1
        else:
            raise ValueError("invalid radix accepted")
    for low, high in ((Q(1), Q(0)),):
        try:
            outward(low, high)
        except ValueError:
            rejected += 1
        else:
            raise ValueError("reversed interval accepted")
    r = 1030
    ell, degree = (r - 1).bit_length(), totient(r)
    threshold = (r - 1) * (Q(3 * r * ell * ell, 4) + (r + degree) * ell)
    require(threshold.denominator == 2 and threshold.__floor__() < threshold,
            "ceiling boundary control")
    return rejected + 1


def main():
    log_two, dyadic_cases = new_dyadic_inequality()
    pi = pi_interval()
    radices = (6, 10, 12, 14, 15, 18, 20, 21, 22, 24, 26, 28, 30)
    heights = [height_instance(r, pi, log_two) for r in radices]
    budget_radices = list(range(3, 2049))
    budget_radices.extend(2 * p ** a for p in (5, 7, 11, 67) for a in range(1, 5))
    strict = 0
    for radix in budget_radices:
        new, old = gap_exponents(radix)
        require(new <= old, "complete exponent regression")
        strict += new < old
    samples = {str(r): {"new": gap_exponents(r)[0], "old": gap_exponents(r)[1]}
               for r in (10, 134, 1030, 8978)}
    root = Path(__file__).resolve().parent
    names = ("PROOF.md", "README.md", "SOURCES.json", "TASK.json", "VERIFY.json", "verify.py")
    hashes = {}
    for name in names:
        content = (root / name).read_bytes()
        require(len(content) <= 256 * 1024, "package-file size")
        hashes[name] = sha256(content).hexdigest()
    receipt = {"status": "PASS_COMPOSITE_ZERO_MEAN_GAP", "heights": heights,
               "height_embeddings": sum(x["embeddings"] for x in heights),
               "dyadic_cases": dyadic_cases, "budget_cases": len(budget_radices),
               "strict_budget_improvements": strict, "samples": samples,
               "controls": rejection_controls(), "sha256": hashes}
    print(json.dumps(receipt, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
