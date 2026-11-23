#!/usr/bin/env python3
"""Exact algebraic checks of the pinned dyadic Measure, with source mutations.

The written induction proves the universal result. These finite checks use
integer-power inequalities, rather than reproducing its root recurrence.
"""
import argparse
import ast
from fractions import Fraction as F
from hashlib import sha256
from math import isqrt
from pathlib import Path
import json

HERE = Path(__file__).resolve().parent
SOURCE_SHA = "98bdb540233794338b426d1b0d0e72cff7fcbbd08be702af0d81e237dbecaae9"


def need(condition, message):
    if not condition:
        raise ArithmeticError(message)


def load_measure(text):
    parsed = ast.parse(text)
    nodes = [n for n in parsed.body if isinstance(n, (ast.FunctionDef, ast.ClassDef))
             and n.name in ("ceil", "Measure")]
    need(len(nodes) == 2, "literal source definitions missing")
    scope = {"F": F, "isqrt": isqrt}
    exec(compile(ast.Module(body=nodes, type_ignores=[]),
                 "<pinned-transport-Measure>", "exec", optimize=0), scope)
    return scope["Measure"]


def error_units(t, bound):
    d = t.denominator.bit_length() - 1
    return F((d + 1) * (d + 2), 2) * bound + d + 1


def inverse_check(Measure, t, precision, x):
    measure = Measure(t, 1, precision)
    lo, hi = measure.inverse_power(x)
    g, exponent, power = 1 << precision, t.numerator, t.denominator
    low, high = F(lo, g), F(hi, g)
    # Raising nonnegative values to the positive integer 2^d is monotone.
    # Thus these are exact tests against x^(-k/2^d), without a real oracle.
    need(0 <= low <= high <= 1, "unit-interval enclosure failed")
    need(low**power * x**exponent <= 1, "lower enclosure failed")
    need(high**power * x**exponent >= 1, "upper enclosure failed")
    error = error_units(t, x) / g
    need((low + error)**power * x**exponent >= 1,
         "lower error bound failed")
    if high > error:
        need((high - error)**power * x**exponent <= 1,
             "upper error bound failed")
    return lo == 0


def ceil(value):
    return -(-value.numerator // value.denominator)


def mass_check(Measure, t, precision, volume, a, b):
    # Perfect powers make both endpoint targets rational, so subtraction
    # and each directed integer allocation have a separate exact oracle.
    power, exponent = t.denominator, t.numerator
    left, right = F(a)**power, F(b)**power
    low, high = Measure(t, volume, precision).mass(left, right)
    true = volume / t * (F(a)**(-exponent) - F(b)**(-exponent))
    delta = 2 * volume * error_units(t, right) / (t * (1 << precision))
    need(0 <= low <= true <= high, "mass enclosure failed")
    need(true - low <= delta and high - true <= delta,
         "mass endpoint error failed")
    allocated = 0
    if delta < F(1, 4):
        need(0 <= ceil(high) - true < F(5, 4), "bin ceiling failed")
        for share in (F(0), F(1, 7), F(1, 2), F(1)):
            amount = (low * share).numerator // (low * share).denominator
            need(0 <= amount <= share * true, "allocation direction failed")
            need(share * true - amount < 1 + share * delta,
                 "allocation loss failed")
            allocated += 1
    return allocated


def reject_inverse_mutation(text, old, new, fixtures):
    need(text.count(old) == 1, "mutation does not target one literal site")
    mutant = load_measure(text.replace(old, new))
    for t, precision, x in fixtures:
        try:
            inverse_check(mutant, t, precision, x)
        except ArithmeticError as failure:
            return {"t": str(t), "precision": precision, "x": str(x),
                    "rejection": str(failure)}
    raise ArithmeticError("mutation escaped exact inverse oracle")


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--output", type=Path, default=Path("/tmp/dyadic-mass-check.json"))
    args = cli.parse_args()
    raw = (HERE / "sources" / "transport.py").read_bytes()
    need(sha256(raw).hexdigest() == SOURCE_SHA, "retained source SHA differs")
    text = raw.decode()
    Measure = load_measure(text)
    exponents = sorted({F(k, 2**d) for d in range(6) for k in range(1, 2**d + 1)})
    endpoints = tuple(map(F, (1, 2, 17))) + (F(5, 4), F(3, 2), F(17, 3), F(513, 2))
    fixtures = [(t, p, x) for t in exponents for p in (0, 1, 4, 8, 17, 32)
                for x in endpoints]
    lower_zero_cases = sum(inverse_check(Measure, *fixture) for fixture in fixtures)
    mass_cases = allocations = 0
    for t in (F(1), F(1, 2), F(3, 4), F(5, 8), F(7, 16)):
        for p in (0, 8, 32, 80):
            for volume in (F(0), F(1), F(7, 3), F(128)):
                for a, b in ((1, 2), (2, 3), (F(3, 2), F(5, 2))):
                    allocations += mass_check(Measure, t, p, volume, a, b)
                    mass_cases += 1
    empty_cases = 0
    for left, right in ((0, 0), (-1, -1), (1, 1), (2, 1), (17, 3)):
        need(Measure(F(3, 4), 7, 8).mass(left, right) == (0, 0),
             "empty interval branch changed")
        empty_cases += 1
    rejected_exponents = []
    for t in (F(-1), F(0), F(2), F(1, 3)):
        try:
            Measure(t, 1, 8)
        except ValueError:
            rejected_exponents.append(str(t))
        else:
            raise ArithmeticError("invalid exponent accepted")
    mutations = {}
    for name, old, new in (
        ("upper-root-floor", "b = isqrt(b * g - 1) + 1", "b = isqrt(b * g)"),
        ("upper-product-floor", "-(-hi * b // g)", "hi * b // g"),
        ("reversed-numerator-bits", "(t.denominator.bit_length() - 1 - j)", "j"),
    ):
        mutations[name] = reject_inverse_mutation(text, old, new, fixtures)
    old = "F(self.volume, self.grid) / self.t"
    need(text.count(old) == 1, "mass mutation site differs")
    mutant = load_measure(text.replace(old, "F(self.volume, self.grid)"))
    try:
        mass_check(mutant, F(1, 2), 32, F(7), 1, 2)
    except ArithmeticError as failure:
        mutations["omitted-density-normalization"] = str(failure)
    else:
        raise ArithmeticError("density normalization mutation escaped")
    need(1891 * 2064 == 3903024, "production integer arithmetic changed")
    need(3903024 * 2 + 61 < 2**22 * 2, "production E margin failed")
    need(F(2**24, 2**57) == F(1, 2**33) < F(1, 4), "mass margin failed")
    result = {"status": "PASS_DYADIC_MASS_ENCLOSURE", "source_sha256": SOURCE_SHA,
              "inverse_power_cases": len(fixtures), "zero_lower_cases": lower_zero_cases,
              "rational_exact_mass_cases": mass_cases, "directed_allocation_cases": allocations,
              "empty_interval_cases": empty_cases, "invalid_exponents": rejected_exponents,
              "source_mutations_rejected": mutations,
              "scope": "Finite exact corroboration of the separate universal proof; no production calendar execution"}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(result["status"], len(fixtures), mass_cases, allocations)


if __name__ == "__main__":
    main()
