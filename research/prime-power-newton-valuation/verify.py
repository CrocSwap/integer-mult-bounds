#!/usr/bin/env python3
"""Independent integer reconstruction of prime-power kernel valuations."""

import argparse
from fractions import Fraction
from hashlib import sha256
import json
from math import comb, gcd
from pathlib import Path


DOMAIN = (3, 4, 5, 7, 8, 9, 16, 25, 27, 32, 49, 64, 81)
PACKAGE = Path(__file__).resolve().parent


def require(condition, message):
    if not condition:
        raise ValueError(message)


def prime_power(radix):
    require(isinstance(radix, int) and radix >= 3, "radix must be at least three")
    prime = next(p for p in range(2, radix + 1) if radix % p == 0)
    remainder, exponent = radix, 0
    while remainder % prime == 0:
        remainder //= prime
        exponent += 1
    require(remainder == 1, "radix must be a prime power")
    return prime, exponent


def prime_order(value, prime):
    require(value != 0, "zero has no finite valuation")
    order = 0
    while value % prime == 0:
        value //= prime
        order += 1
    return order


def tail_coefficients(radix, power):
    """Return a_j in the integral u power basis, without field division."""
    prime, exponent = prime_power(radix)
    require(isinstance(power, int) and gcd(radix, power) == 1, "nonprimitive power")
    step = prime ** (exponent - 1)
    degree = (prime - 1) * step
    # First compute in Z[u]/(u^r-1): multiply by 1-u^s as a cyclic difference.
    cyclic = [1] + [0] * (radix - 1)
    coefficients = [None] * radix
    for j in range(radix - 1, -1, -1):
        reduced = cyclic.copy()
        # Phi_r(u) = 1+u^step+...+u^degree. Each high monomial reduces
        # directly to exponents below degree, since the input degree is < r.
        for h in range(degree, radix):
            for k in range(prime - 1):
                reduced[h - degree + k * step] -= reduced[h]
        coefficients[j] = tuple(reduced[:degree])
        if j:
            shift = (power * j) % radix
            cyclic = [cyclic[h] - cyclic[(h - shift) % radix]
                      for h in range(radix)]
    return coefficients


def in_uniformizer_basis(coefficients):
    """Substitute u=1-pi using the binomial theorem over the integers."""
    degree = len(coefficients)
    return [(-1) ** i * sum(coefficients[h] * comb(h, i)
                            for h in range(i, degree))
            for i in range(degree)]


def coefficient_valuation(coefficients, prime, exponent):
    degree = (prime - 1) * prime ** (exponent - 1)
    require(len(coefficients) == degree, "wrong cyclotomic basis length")
    shifted = in_uniformizer_basis(coefficients)
    weights = [degree * prime_order(value, prime) + i
               for i, value in enumerate(shifted) if value]
    require(bool(weights), "zero coefficient")
    # The nonzero summands have different valuations modulo degree, so the
    # least valuation cannot cancel. v(pi)=1 and v(prime)=degree.
    return min(weights)


def lower_hull(values):
    hull = []
    for point in enumerate(values):
        while len(hull) >= 2:
            a, b = hull[-2:]
            cross = ((b[0] - a[0]) * (point[1] - b[1])
                     - (b[1] - a[1]) * (point[0] - b[0]))
            if cross > 0:
                break
            hull.pop()
        hull.append(point)
    return hull


def predicted_hull(radix):
    prime, exponent = prime_power(radix)
    x = 0
    y = Fraction(exponent * (prime - 1) * prime ** (exponent - 1))
    hull = [(x, int(y))]
    for b in range(exponent, 0, -1):
        multiplicity = (prime - 1) * prime ** (b - 1)
        valuation = 1 + Fraction((b - 1) * (prime - 1), prime)
        x += multiplicity
        y -= multiplicity * valuation
        require(y.denominator == 1, "nonintegral predicted vertex")
        hull.append((x, int(y)))
    require(hull[-1] == (radix - 1, 0), "wrong predicted endpoint")
    return hull


def check_coefficients(radix, coefficients):
    prime, exponent = prime_power(radix)
    require(len(coefficients) == radix, "wrong polynomial length")
    values = [coefficient_valuation(c, prime, exponent) for c in coefficients]
    expected = [0] * radix
    for j in range(radix - 2, -1, -1):
        expected[j] = expected[j + 1] + prime ** prime_order(j + 1, prime)
    require(values == expected, "exact coefficient valuations disagree with tail sum")
    require(lower_hull(values) == predicted_hull(radix), "Newton polygon mismatch")
    return values


def shifted_cyclotomic(radix):
    prime, exponent = prime_power(radix)
    step = prime ** (exponent - 1)
    degree = (prime - 1) * step
    polynomial = [sum((-1) ** i * comb(k * step, i)
                      for k in range(prime) if k * step >= i)
                  for i in range(degree + 1)]
    require(polynomial[0] == prime and abs(polynomial[-1]) == 1,
            "wrong shifted cyclotomic endpoints")
    require(all(c % prime == 0 for c in polynomial[:-1]),
            "shifted cyclotomic is not Eisenstein")
    require(polynomial[0] % (prime * prime) != 0,
            "shifted cyclotomic constant is not Eisenstein")
    return polynomial


def division_valuation(coefficients, radix):
    """Count exact integral divisions by pi, rather than weighted minima."""
    prime, _ = prime_power(radix)
    polynomial = shifted_cyclotomic(radix)
    shifted = in_uniformizer_basis(coefficients)
    require(len(shifted) == len(polynomial) - 1, "wrong cyclotomic basis length")
    require(any(shifted), "zero coefficient")
    count = 0
    while shifted[0] % prime == 0:
        multiple = shifted[0] // prime
        # F(pi)=p+F_1*pi+...+F_e*pi^e=0. If c_0=m*p, replace
        # c_0 by -m*sum(F_i*pi^i), then divide the entire expression by pi.
        shifted = [shifted[i] - multiple * polynomial[i]
                   for i in range(1, len(shifted))] + [-multiple * polynomial[-1]]
        count += 1
    return count


def check_sources(root=None):
    root = Path(root) if root is not None else PACKAGE.parents[1]
    pins = json.loads((PACKAGE / "SOURCE.json").read_text(encoding="utf-8"))
    for path, digest in pins["files_sha256_lf"].items():
        data = (root / path).read_bytes().replace(b"\r\n", b"\n")
        require(sha256(data).hexdigest() == digest, "source pin mismatch: " + path)
    return pins


def negative_controls():
    rejected = []

    def reject(label, operation, reason):
        try:
            operation()
        except ValueError as error:
            require(reason in str(error), "wrong rejection for " + label)
            rejected.append(label)
        else:
            raise ValueError("negative control accepted: " + label)

    for radix, power in ((4, 2), (9, 3)):
        reject("nonprimitive_%d_%d" % (radix, power),
               lambda: tail_coefficients(radix, power), "nonprimitive")
    for radix in (1, 12):
        reject("invalid_radix_%d" % radix,
               lambda: tail_coefficients(radix, 1), "radix must")
    coefficients = tail_coefficients(4, 1)
    tampered = coefficients.copy()
    tampered[1] = tuple(2 * c for c in tampered[1])
    # This preserves every residue checked in #621 modulo (1-u), including
    # a_0=r and a_n=1, but v(a_1) changes from 3 to 5.
    require([sum(c) % 2 for c in coefficients]
            == [sum(c) % 2 for c in tampered], "control changed ideal residues")
    reject("same_ideal_residues_wrong_valuation",
           lambda: check_coefficients(4, tampered), "coefficient valuations")
    omitted = coefficients[1:] + [coefficients[-1]]
    reject("omitted_tail_factor", lambda: check_coefficients(4, omitted),
           "coefficient valuations")
    reject("unit_root_polynomial", lambda: check_coefficients(4, [(1, 0)] * 4),
           "coefficient valuations")
    reject("zero_coefficient", lambda: coefficient_valuation((0, 0), 2, 2),
           "zero coefficient")
    return rejected


def replay():
    pins = check_sources()
    cases = []
    embedding_count = coefficient_count = 0
    for radix in DOMAIN:
        prime, exponent = prime_power(radix)
        shifted_cyclotomic(radix)
        degree = (prime - 1) * prime ** (exponent - 1)
        powers = [power for power in range(1, radix) if gcd(power, radix) == 1]
        digests = {}
        common_values = None
        for power in powers:
            coefficients = tail_coefficients(radix, power)
            require(coefficients[0] == (radix,) + (0,) * (degree - 1),
                    "full tail product is not radix")
            require(coefficients[-1] == (1,) + (0,) * (degree - 1),
                    "kernel is not monic")
            values = check_coefficients(radix, coefficients)
            require([division_valuation(c, radix) for c in coefficients] == values,
                    "integral-division valuation disagrees with weighted minimum")
            require(all(value > 0 for value in values[:-1]),
                    "nonleading coefficient has nonpositive valuation")
            if common_values is None:
                common_values = values
            require(values == common_values, "primitive embeddings disagree")
            payload = json.dumps(coefficients, separators=(",", ":")).encode("ascii")
            digests[str(power)] = sha256(payload).hexdigest()
            embedding_count += 1
            coefficient_count += radix
        hull = lower_hull(common_values)
        root_values = [{"multiplicity": b[0] - a[0],
                        "valuation": str(Fraction(a[1] - b[1], b[0] - a[0]))}
                       for a, b in zip(hull, hull[1:])]
        cases.append({"radix": radix, "prime": prime, "prime_exponent": exponent,
                      "ramification_degree": degree, "primitive_powers": powers,
                      "coefficient_valuations": common_values,
                      "lower_hull": hull, "root_valuations": root_values,
                      "coefficient_sha256_by_power": digests})
    return {"status": "PASS_PRIME_POWER_NEWTON_VALUATIONS",
            "assignment_seed": 80, "domain": list(DOMAIN),
            "embedding_count": embedding_count, "coefficient_count": coefficient_count,
            "valuation_methods": ["weighted_uniformizer_basis_minimum",
                                  "repeated_exact_integral_uniformizer_division"],
            "source_files_sha256_lf": pins["files_sha256_lf"],
            "cases": cases, "negative_controls": negative_controls(),
            "scope": "Exact finite coefficient and polygon replay; not an archimedean "
                     "root bound, paid inverse program or multiplication theorem."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--check", type=Path)
    args = parser.parse_args()
    result = replay()
    payload = json.dumps(result, indent=2) + "\n"
    if args.check:
        # JSON equality includes every proof-relevant field; converting through
        # JSON also canonicalizes the tuples emitted by the hull calculation.
        expected = json.loads(args.check.read_text(encoding="utf-8"))
        require(json.loads(payload) == expected, "receipt mismatch")
    if args.output:
        args.output.write_text(payload, encoding="utf-8", newline="\n")
    print("PASS %d primitive embeddings; %d exact coefficients; %d negative controls"
          % (result["embedding_count"], result["coefficient_count"],
             len(result["negative_controls"])))


if __name__ == "__main__":
    main()
