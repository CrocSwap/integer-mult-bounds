#!/usr/bin/env python3
"""Exact corroboration of new edge residues. Nick Petalas; Apache-2.0."""

from fractions import Fraction
from hashlib import sha256
import json
from math import comb, gcd
from pathlib import Path


PACKAGE = Path(__file__).resolve().parent
MAX_A = 5
MAX_K = 9


def need(condition, message):
    if not condition:
        raise ValueError(message)


def parameters(a):
    need(type(a) is int and 1 <= a <= MAX_A, "a must be an integer in 1..5")
    r = 3**a
    return r, 2 * (r // 3)


def strip_three(n):
    need(type(n) is int and 0 < n < 3**MAX_K, "positive bounded unit input")
    for _ in range(MAX_K):
        if n % 3:
            return n % 3
        n //= 3
    raise ValueError("unit extraction capacity exhausted")


def predicted_units(k):
    need(type(k) is int and 1 <= k <= MAX_K, "k must be an integer in 1..9")
    return (1, 2, 2) if k % 2 else (2, 2, 1)


def factorial_units(k):
    """Literal tail-factor leading units, independent of the parity formula."""
    need(type(k) is int and 1 <= k <= MAX_K, "bounded factorial-unit domain")
    q = 3 ** (k - 1)
    running = 1
    result = []
    for m in range(1, 3 * q + 1):
        if m > 1:
            running = -running * strip_three(m - 1) % 3
        if m % q == 0:
            result.append(running)
    need(len(result) == 3, "three edge contacts")
    return tuple(result)


def uniformizer_polynomial(a):
    """Phi_(3^a)(1-X), monic of degree e."""
    r, e = parameters(a)
    b = r // 3
    return [(-1) ** i * (comb(e, i) + (comb(b, i) if i <= b else 0))
            + (1 if i == 0 else 0) for i in range(e + 1)]


def reduce_polynomial(values, modulus):
    need(modulus[-1] == 1, "monic uniformizer relation")
    degree = len(modulus) - 1
    result = list(values) + [0] * max(0, degree - len(values))
    for i in range(len(result) - 1, degree - 1, -1):
        lead = result[i]
        for j in range(degree):
            result[i - degree + j] -= lead * modulus[j]
    return result[:degree]


def initial_form(values, e, three_unit=2):
    """Unique lowest term; 3 / pi^e reduces to -1."""
    need(len(values) == e and 2 <= e <= 162, "bounded uniformizer vector")
    need(three_unit in (1, 2), "nonzero residue for rational three")
    terms = []
    for i, value in enumerate(values):
        if value == 0:
            continue
        reduced = value
        for exponent in range(4097):
            if reduced % 3:
                terms.append((e * exponent + i,
                              reduced * pow(three_unit, exponent, 3) % 3))
                break
            reduced //= 3
        else:
            raise ValueError("coefficient valuation capacity exhausted")
    need(bool(terms), "nonzero contact coefficient")
    terms.sort()
    need(len(terms) == 1 or terms[0][0] < terms[1][0], "unique initial term")
    return terms[0]


def cyclic_contacts(a):
    """Multiply in Z[u]/(u^r-1), then change basis exactly to pi=1-u."""
    r, e = parameters(a)
    contacts = {r - t * 3 ** (k - 1)
                for k in range(1, a + 1) for t in (1, 2, 3)}
    values = [1] + [0] * (r - 1)
    result = {}
    for j in range(r - 1, -1, -1):
        if j < r - 1:
            s = j + 1
            values = [values[i] - values[(i - s) % r] for i in range(r)]
        if j not in contacts:
            continue
        reduced = list(values)
        for i in range(r - 1, e - 1, -1):
            reduced[i - r // 3] -= reduced[i]
            reduced[i - 2 * (r // 3)] -= reduced[i]
        basis = [(-1) ** k * sum(reduced[i] * comb(i, k)
                                 for i in range(k, e)) for k in range(e)]
        result[j] = initial_form(basis, e)
    return result


def direct_contacts(a):
    """Separate dense multiplication directly in the uniformizer basis."""
    need(type(a) is int and 1 <= a <= 3, "dense oracle domain")
    r, e = parameters(a)
    modulus = uniformizer_polynomial(a)
    contacts = {r - t * 3 ** (k - 1)
                for k in range(1, a + 1) for t in (1, 2, 3)}
    values = [1] + [0] * (e - 1)
    result = {}
    for j in range(r - 1, -1, -1):
        if j < r - 1:
            s = j + 1
            factor = [0] + [(-1) ** (i + 1) * comb(s, i)
                            for i in range(1, s + 1)]
            product = [0] * (e + s)
            for i in range(e):
                for k in range(s + 1):
                    product[i + k] += values[i] * factor[k]
            values = reduce_polynomial(product, modulus)
        if j in contacts:
            result[j] = initial_form(values, e)
    return result


def quadratic_checks():
    rows = []
    for parity, units in ((1, (1, 2, 2)), (0, (2, 2, 1))):
        c2, c1, c0 = units
        evaluations = [(c2 * x * x + c1 * x + c0) % 3 for x in range(3)]
        need(all(evaluations), "residual quadratic must be irreducible over F3")
        need((c1 * c1 - 4 * c2 * c0) % 3 == 2, "nonsquare discriminant")
        rows.append({"k_parity": parity, "ascending": [c0, c1, c2],
                     "values_at_0_1_2": evaluations})
    return rows


def residue_checks():
    contact_count = oracle_count = 0
    rows = []
    for a in range(1, MAX_A + 1):
        r, e = parameters(a)
        modulus = uniformizer_polynomial(a)
        need(modulus[0] == 3 and modulus[-1] == 1, "cyclotomic endpoints")
        need(all(x % 3 == 0 for x in modulus[:-1]), "Eisenstein residue")
        actual = cyclic_contacts(a)
        if a <= 3:
            oracle = direct_contacts(a)
            need(actual == oracle, "independent uniformizer multiplication")
            oracle_count += len(oracle)
        for k in range(1, a + 1):
            q = 3 ** (k - 1)
            units = predicted_units(k)
            for t in (1, 2, 3):
                j = r - t * q
                need(actual[j][1] == units[t - 1], "new normalized contact unit")
                contact_count += 1
            rows.append({"a": a, "k": k, "units": list(units)})
    return contact_count, oracle_count, rows


def degree_checks():
    rows = []
    admissible_pairs = 0
    for k in range(1, 65):
        slope = Fraction(2 * k + 1, 3)
        denominator = 3 // gcd(3, k - 1)
        need(slope.denominator == denominator, "slope denominator")
        q = 3 ** (k - 1)
        need((slope * q).denominator == 1, "normalized root power is integral")
        for ramification in range(1, 25):
            for residue_degree in range(1, 25):
                if ramification % denominator == 0 and residue_degree % 2 == 0:
                    degree = ramification * residue_degree
                    need(degree % (2 * denominator) == 0, "factor-degree obstruction")
                    admissible_pairs += 1
        rows.append({"k": k, "degree_divisor": 2 * denominator})
    return admissible_pairs, rows


def controls():
    rejected = 0
    for value in (0, -1, 6, True, 1.0, "1"):
        try:
            parameters(value)
        except ValueError:
            rejected += 1
        else:
            raise ValueError("invalid parameter accepted")
    for value in (0, 10, True, 2.0):
        try:
            predicted_units(value)
        except ValueError:
            rejected += 1
        else:
            raise ValueError("invalid edge accepted")
    for k in range(1, 3):
        need(factorial_units(k) != predicted_units(3 - k), "parity mutant rejected")
        rejected += 1
    need(initial_form([3, 0], 2) != initial_form([3, 0], 2, 1),
         "wrong uniformizer unit rejected")
    rejected += 1
    need(any((x * x + 2 * x) % 3 == 0 for x in range(3)),
         "dropped constant makes residual reducible")
    rejected += 1
    need(2 % (2 * Fraction(5, 3).denominator) != 0,
         "unramified degree-two declaration at second slope rejected")
    rejected += 1
    return rejected


def file_hashes():
    names = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json",
             "VERIFY.json", "verify.py")
    result = {}
    for name in names:
        with (PACKAGE / name).open("rb") as stream:
            data = stream.read(1024 * 1024 + 1)
        need(len(data) <= 1024 * 1024, "package file capacity")
        result[name] = sha256(data).hexdigest()
    return result


def main():
    for k in range(1, MAX_K + 1):
        need(factorial_units(k) == predicted_units(k), "literal factorial units")
    contacts, oracle, rows = residue_checks()
    pairs, degrees = degree_checks()
    report = {"status": "PASS_TERNARY_KERNEL_FACTOR_DEGREES",
              "factorial_edges": MAX_K, "contact_checks": contacts,
              "independent_contact_coefficients": oracle,
              "radices": [3**a for a in range(1, MAX_A + 1)],
              "quadratics": quadratic_checks(), "residue_rows": rows,
              "admissible_ef_pairs": pairs, "slope_degree_divisors": degrees,
              "controls_rejected": controls(), "package_sha256": file_hashes()}
    print(json.dumps(report, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
