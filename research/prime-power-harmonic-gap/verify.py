"""Exact finite corroboration of the new primitive-unit envelope."""

from fractions import Fraction as F
from hashlib import sha256
from math import factorial, gcd, isqrt
from pathlib import Path
import json
import sys


def require(condition, message):
    if not condition:
        raise ValueError(message)


def prime(n):
    return n >= 2 and all(n % d for d in range(2, isqrt(n) + 1))


def prime_power(q):
    require(2 <= q <= 4096, "radix outside finite domain")
    p = next((d for d in range(2, isqrt(q) + 1) if q % d == 0), q)
    remaining = q
    for _ in range(q.bit_length()):
        if remaining % p:
            break
        remaining //= p
    require(remaining == 1 and prime(p), "radix is not a prime power")
    return p


def logarithm_core(y):
    require(F(1) <= y <= F(2), "logarithm argument outside [1,2]")
    x = (y - 1) / (y + 1)
    total = sum((2 * x ** (2 * k + 1) / (2 * k + 1)
                 for k in range(32)), F(0))
    tail = 2 * x ** 65 / (65 * (1 - x * x))
    return total, total + tail


def logarithm(n):
    require(isinstance(n, int) and 1 <= n <= 4096, "invalid logarithm input")
    e = n.bit_length() - 1
    lo2, hi2 = logarithm_core(F(2))
    lo, hi = logarithm_core(F(n, 2 ** e))
    return e * lo2 + lo, e * hi2 + hi


def arctangent(x, terms):
    require(F(0) < x <= F(1, 5) and 1 <= terms <= 24, "invalid arctangent")
    value = sum(((-1) ** k * x ** (2 * k + 1) / (2 * k + 1)
                 for k in range(terms)), F(0))
    following = (-1) ** terms * x ** (2 * terms + 1) / (2 * terms + 1)
    return min(value, value + following), max(value, value + following)


def pi_interval():
    lo5, hi5 = arctangent(F(1, 5), 24)
    lo239, hi239 = arctangent(F(1, 239), 8)
    lower = F(3141592653589793238, 10 ** 18)
    upper = lower + F(1, 10 ** 18)
    require(lower < 16 * lo5 - 4 * hi239, "Machin lower bound")
    require(16 * hi5 - 4 * lo239 < upper, "Machin upper bound")
    return lower, upper


def sine_interval(lo, hi):
    require(0 < lo <= hi <= F(8, 5), "sine argument outside finite domain")
    lower = F(0)
    upper = F(0)
    for k in range(12):
        degree = 2 * k + 1
        denominator = factorial(degree)
        if k % 2:
            lower -= hi ** degree / denominator
            upper -= lo ** degree / denominator
        else:
            lower += lo ** degree / denominator
            upper += hi ** degree / denominator
    upper += hi ** 25 / factorial(25)
    require(0 < lower <= upper, "invalid positive sine enclosure")
    return lower, upper


def harmonic_checks():
    values = [F(0)]
    for j in range(1, 2049):
        values.append(values[-1] + F(1, j))
    rows = []
    direct_count = 0
    for q in range(2, 4097):
        try:
            p = prime_power(q)
        except ValueError:
            continue
        n = q // 2
        m = n // p
        envelope = (p * values[n] - values[m]) / (p - 1)
        loglo, loghi = logarithm(q)
        require(envelope <= loglo + 2, f"new harmonic bound at {q}")
        require(n < p * (m + 1), "floor remainder contract")
        require(p <= 2 ** (p - 1), "integer logarithm comparison")
        if q <= 512:
            direct = sum((F(1, j) for j in range(1, n + 1) if j % p), F(0))
            require(envelope == F(p, p - 1) * direct, "primitive harmonic identity")
            direct_count += 1
        rows.append((q, p, envelope, loglo, loghi))
    require(2 * values[32] > logarithm(64)[1] + 2,
            "dropping the divisible terms must break the bound")
    return rows, direct_count


def trigonometric_checks(rows):
    pi_lo, pi_hi = pi_interval()
    radices = 0
    pairs = 0
    represented_units = 0
    for q, p, envelope, loglo, _ in rows:
        if q > 128:
            continue
        phi = q // p * (p - 1)
        average_hi = F(0)
        counted = 0
        for j in range(1, q // 2 + 1):
            if gcd(j, q) != 1:
                continue
            multiplicity = 1 if 2 * j == q else 2
            if 2 * j == q:
                sin_lo = F(1)
            else:
                sin_lo, _ = sine_interval(pi_lo * j / q, pi_hi * j / q)
                require(sin_lo >= F(2 * j, q), "sine chord bound")
            average_hi += F(multiplicity, phi) / sin_lo
            counted += multiplicity
            pairs += 1
        require(counted == phi, "primitive pair coverage")
        require(average_hi <= envelope, "cosecant versus harmonic envelope")
        require(average_hi <= loglo + 2, "new primitive-unit envelope")
        represented_units += counted
        radices += 1
    return radices, pairs, represented_units


def gap(r, p):
    require(3 <= r <= 2 ** 256 and 2 <= p <= 4096 and prime(p),
            "invalid gap parameters")
    remaining = r
    for _ in range(257):
        if remaining % p:
            break
        remaining //= p
    require(remaining == 1, "gap radix is not a power of p")
    ell = (r - 1).bit_length()
    numerator = 3 * ell * ell + 12 * ell
    b = (numerator + 3) // 4
    require(4 * (b - 1) < numerator <= 4 * b, "exact dyadic ceiling")
    require(b <= 3 * ell * ell, "comparison with cited bound")
    mass = (r - 1) * (r // p * (p - 1))
    return 1 + 2 * ell + mass * min(r, b), 1 + 2 * ell + mass * min(r, 3 * ell * ell)


def budget_checks(rows):
    cases = {(q, p) for q, p, *_ in rows if q >= 3}
    cases.update((2 ** e, 2) for e in range(2, 257))
    cases.update((3 ** e, 3) for e in range(1, 129))
    improvements = 0
    for q, p in sorted(cases):
        new, old = gap(q, p)
        require(new <= old, "budget worsened")
        improvements += new < old
    require(gap(4096, 2) == (1207664665, 3622993945), "4096 example")
    return len(cases), improvements


def rejection_checks():
    controls = (
        (prime_power, (6,)), (prime_power, (1,)), (prime_power, (4097,)),
        (logarithm, (0,)), (logarithm, (4097,)),
        (logarithm_core, (F(3),)), (arctangent, (F(1), 8)),
        (sine_interval, (F(2), F(3))), (gap, (6, 2)), (gap, (16, 4)),
        (gap, (2, 2)),
    )
    for function, arguments in controls:
        try:
            function(*arguments)
        except ValueError:
            continue
        raise ValueError("invalid-input control accepted")
    require(4 * ((3 * 3 ** 2 + 12 * 3) // 4) < 3 * 3 ** 2 + 12 * 3,
            "floor mutant should undercharge the exponent")
    return len(controls) + 2


def main():
    rows, direct = harmonic_checks()
    radices, pairs, units = trigonometric_checks(rows)
    budgets, improvements = budget_checks(rows)
    controls = rejection_checks()
    package = Path(__file__).resolve().parent
    names = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py")
    hashes = {}
    for name in names:
        path = package / name
        require(path.stat().st_size <= 1024 ** 2, "package file exceeds one MiB")
        hashes[name] = sha256(path.read_bytes()).hexdigest()
    print("PASS_PRIME_POWER_HARMONIC_GAP")
    print(json.dumps({"schema": "prime-power-harmonic-gap/1",
                      "python": sys.version.split()[0], "package_sha256": hashes,
                      "harmonic_radices": len(rows), "direct_harmonic_identities": direct,
                      "cosecant_radices": radices, "primitive_pairs": pairs,
                      "primitive_units": units, "budget_cases": budgets,
                      "strict_budget_improvements": improvements, "controls": controls,
                      "example_4096": {"new": 1207664665, "cited": 3622993945}},
                     sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
