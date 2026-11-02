"""Read-only finite corroboration of PROOF.md; explicit checks survive -O."""

import argparse
from collections import Counter
import hashlib
from itertools import product
import json
from pathlib import Path
import sys

from algebra import (base_field, determinant, evaluate, extension, irreducibles,
                     multiply, pencil, remainder, require, slice_matrix)


def mobius(n: int) -> int:
    remaining, sign = n, 1
    for p in range(2, n + 1):
        if remaining % p == 0:
            remaining //= p
            sign = -sign
            if remaining % p == 0:
                return 0
    return sign


def irreducible_count(q: int, degree: int) -> int:
    numerator = sum(mobius(d) * q ** (degree // d)
                    for d in range(1, degree + 1) if degree % d == 0)
    require(numerator % degree == 0, "integral irreducible count")
    return numerator // degree


def union_size(q: int, degree: int) -> int:
    require(q in (2, 3, 4, 5) and 1 <= degree <= 9, "threshold domain")
    return 1 + sum(k * irreducible_count(q, k) for k in range(1, degree + 1))


def worst_degree(q: int, dimension: int) -> int:
    require(1 <= dimension <= 256, "dimension domain")
    for degree in range(1, 10):
        if union_size(q, degree) > dimension:
            return degree
    raise ValueError("degree bound exhausted")


def fields_and_factors(q: int) -> tuple:
    base = base_field(q)
    maximum = 4 if q == 2 else 3
    factors = {d: irreducibles(base, d) for d in range(1, maximum + 1)}
    fields = {d: extension(base, factors[d][0]) for d in factors}
    for d, polynomials in factors.items():
        require(len(polynomials) == irreducible_count(q, d), "irreducible formula")
        frobenius = (1,)
        for k in range(1, d + 1):
            if d % k == 0:
                for poly in factors[k]:
                    frobenius = multiply(frobenius, poly, base)
        expected = (0, base.neg[1]) + (0,) * (q ** d - 2) + (1,)
        require(frobenius == expected, "complete Frobenius factorization")
    return base, factors, fields


def good_points(poly: tuple, field) -> tuple:
    finite = tuple(a for a in range(field.q) if evaluate(poly, a, field) != 0)
    return finite + ((None,) if poly[-1] != 0 else ())


def all_bad_by_factors(poly: tuple, degree: int, factors: dict, base) -> bool:
    if poly[-1] != 0:
        return False
    return all(remainder(poly, p, base) == (0,)
               for k in range(1, degree + 1) if degree % k == 0
               for p in factors[k])


def exhaustive_forms(q: int, base, factors: dict, fields: dict) -> dict:
    maximum = {2: 6, 3: 4, 4: 3, 5: 3}[q]
    histogram, cases, point_checks = Counter(), 0, 0
    for n in range(1, maximum + 1):
        observed = 0
        bound = worst_degree(q, n)
        for poly in product(range(q), repeat=n + 1):
            if not any(poly):
                continue
            first = 0
            for d in range(1, bound + 1):
                good = good_points(poly, fields[d])
                point_checks += fields[d].q + 1
                require(bool(good) != all_bad_by_factors(poly, d, factors, base),
                        "root/factor disagreement")
                if good and not first:
                    first = d
            require(first > 0, "universal degree bound")
            histogram[f"n={n},first={first}"] += 1
            observed = max(observed, first)
            cases += 1
        require(observed == bound, "sharp worst degree")
    return {"forms": cases, "projective_evaluations": point_checks,
            "first_degree_histogram": dict(sorted(histogram.items()))}


def literal_pencils(q: int, base, factors: dict, fields: dict) -> dict:
    maximum = 3 if q == 2 else 2
    cases, determinants, rows = 0, 0, []
    for d in range(1, maximum + 1):
        blocks = tuple(p for k in range(1, d + 1) for p in factors[k])
        for padding in (0, 1):
            a, b = pencil(blocks, 1 + padding, base)
            n, witness_degrees = len(a), []
            require(n == union_size(q, d) + padding, "extremal dimension")
            for e in range(1, d + 2):
                target = fields[e]
                good = 0
                for point in tuple(range(target.q)) + (None,):
                    actual = determinant(slice_matrix(a, b, point, target), target)
                    expected = 0 if point is None else 1
                    if point is not None:
                        for p in blocks:
                            expected = target.mul[expected][evaluate(p, point, target)]
                    require(actual == expected, "literal determinant product")
                    good += actual != 0
                    determinants += 1
                require((good == 0) == (e <= d), "first extension attained")
                if good:
                    witness_degrees.append(e)
            require(worst_degree(q, n) == d + 1, "padded extremizer threshold")
            rows.append({"dimension": n, "first_degree": witness_degrees[0]})
            cases += 1
    return {"pencils": cases, "literal_determinants": determinants, "cases": rows}


def controls(contexts: dict) -> dict:
    base, factors, fields = contexts[2]
    require(union_size(2, 1) == 3, "infinity must count")
    a, b = pencil(factors[1], 1, base)
    require(all(determinant(slice_matrix(a, b, x, fields[1]), fields[1]) == 0
                for x in (0, 1, None)), "dimension-three base obstruction")
    # t^4-t vanishes on F4 but not at all points of F8 or at infinity.
    finite_f4 = (0, 1, 0, 0, 1)
    homogeneous = finite_f4 + (0,)
    require(not good_points(homogeneous, fields[2]), "F4 root control")
    require(bool(good_points(homogeneous, fields[3])), "F8 escape control")
    require(bool(good_points(finite_f4, fields[2])), "projective infinity control")
    require(union_size(2, 3) == 11 > 9 == 2 ** 3 + 1, "union improves one-field bound")
    repeated = (0, 0, 0, 1, 1, 0, 0)
    require(bool(good_points(repeated, fields[2])), "multiplicity is not new roots")
    singular = ((0, 0), (0, 0))
    require(all(determinant(slice_matrix(singular, singular, x, fields[3]), fields[3]) == 0
                for x in tuple(range(8)) + (None,)), "regularity required")
    # y*(x^16-x*y^15) has a slice over F8 but none over F16.
    nonmonotone = (0, 1) + (0,) * 14 + (1, 0)
    require(bool(good_points(nonmonotone, fields[3])) and
            not good_points(nonmonotone, fields[4]), "success is not degree-monotone")
    rejected = 0
    for operation, args in ((base_field, (6,)), (worst_degree, (2, 0)),
                            (union_size, (2, 0)), (extension, (base, (0, 0, 1))),
                            (pencil, ((), 0, base)), (determinant, (((1, 0),), base))):
        try:
            operation(*args)
        except ValueError:
            rejected += 1
        else:
            raise ValueError("invalid input accepted")
    require(rejected == 6, "all input controls executed")
    names = ("infinity", "F4_obstruction_F8_escape", "affine_projective_difference",
             "union_improves_fixed_field", "root_multiplicity", "regularity",
             "nonmonotone_extension_degrees")
    return {"semantic_controls": list(names), "rejected_inputs": rejected}


def run() -> dict:
    contexts = {q: fields_and_factors(q) for q in (2, 3, 4, 5)}
    result = {"claim_type": "scoped all-prime-power proof with finite corroboration",
              "no_new_kappa": True, "fields": {}}
    for q, (base, factors, fields) in contexts.items():
        result["fields"][str(q)] = {
            "irreducible_counts": {str(d): len(v) for d, v in factors.items()},
            "forms": exhaustive_forms(q, base, factors, fields),
            "literal": literal_pencils(q, base, factors, fields)}
    result["controls"] = controls(contexts)
    result["totals"] = {
        "forms": sum(v["forms"]["forms"] for v in result["fields"].values()),
        "pencils": sum(v["literal"]["pencils"] for v in result["fields"].values()),
        "literal_determinants": sum(v["literal"]["literal_determinants"]
                                    for v in result["fields"].values())}
    package = Path(__file__).resolve().parent
    files = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json",
             "algebra.py", "verify.py")
    result["sha256"] = {name: hashlib.sha256((package / name).read_bytes()).hexdigest()
                        for name in files}
    result["python"] = sys.version.split()[0]
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipt", type=Path, help="write a new external JSON receipt")
    args = parser.parse_args()
    result = run()
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.receipt is not None:
        package = Path(__file__).resolve().parent
        require(not args.receipt.resolve().is_relative_to(package), "receipt must be external")
        with args.receipt.open("x", encoding="utf-8") as stream:
            require(stream.write(rendered) == len(rendered), "complete receipt write")
    print("PASS_PENCIL_FIRST_EXTENSION_DEGREE no_new_kappa")
    print(rendered, end="")


if __name__ == "__main__":
    main()
