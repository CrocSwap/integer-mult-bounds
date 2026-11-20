"""Independent exact determinant audit: Kronecker substitution + Berkowitz.

Imports neither classifier nor its mixed-column checker. Certificate rows are
claims to verify. The determinant path uses dense integer residue arithmetic,
not sparse multivariate polynomials or subset/Laplace determinant expansion.
"""
from collections import Counter, defaultdict
from fractions import Fraction
from hashlib import sha256
from itertools import permutations
from math import factorial
from pathlib import Path
import argparse
import json
import time

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parents[1]
RADIX = 9
BITS = 25
PLANE = RADIX ** 3


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def orbit_key(order):
    # Coordinate words along an order: coordinate permutation sorts the three
    # words, while simultaneous complementation replaces each by its complement.
    columns = [sum(((vertex // (2 ** axis)) % 2) * (2 ** index)
                   for index, vertex in enumerate(order)) for axis in range(3)]
    return min(tuple(sorted(columns)), tuple(sorted(255 - word for word in columns)))


def coverage(rows):
    groups = defaultdict(list)
    for order in permutations(range(8)):
        groups[orbit_key(order)].append(order)
    expected = {min(group) for group in groups.values()}
    require(len(groups) == 3360 and all(len(group) == 12 for group in groups.values()),
            "coordinate-word orbit coverage")
    observed = [tuple(row["order"]) for row in rows]
    require(len(set(observed)) == len(observed) == 3360, "duplicate/missing certificate order")
    require(set(observed) == expected, "certificate representatives differ from independent orbits")
    return {"orders": sum(map(len, groups.values())), "orbits": len(groups),
            "orbit_size": 12, "canonical_representatives_equal": True}


def source_monomials():
    # Build a literal tensor with Kronecker indices using ordinary 2-by-2
    # products. A monomial is its univariate exponent, with radix-nine upper
    # exponents and a separate w plane. No primary bit-coordinate code is used.
    result = [[0]]
    for upper_weight in (1, RADIX, RADIX ** 2):
        factor = [[0, upper_weight], [PLANE, 0]]
        result = [[x + y for x in ra for y in rb]
                  for ra in result for rb in factor]
    return result


H = source_monomials()


def displacement(order):
    a = [[H[i][j] for j in order] for i in order]
    return [[((a[i][j], 1),) if not (i and j) else
             ((a[i][j], 1), (a[i - 1][j - 1], -1))
             for j in range(8)] for i in range(8)]


def entry_times(entry, value, mask):
    return sum(sign * (value << (BITS * exponent)) for exponent, sign in entry) & mask


def berkowitz(entries, mask):
    """Characteristic coefficients, high degree first, in Z/(2^n).

    For [[a,R],[S,C]], multiply charpoly(C) by the lower triangular
    Toeplitz matrix with first column (1,-a,-RS,-RCS,...).
    This is division-free and valid in every commutative ring.
    """
    n = len(entries)
    if not n:
        return [1]
    c = [row[1:] for row in entries[1:]]
    previous = berkowitz(c, mask)
    q = [1, -entry_times(entries[0][0], 1, mask) & mask]
    if n > 1:
        vector = [entry_times(row[0], 1, mask) for row in entries[1:]]
        for power in range(n - 1):
            q.append(-sum(entry_times(entry, value, mask)
                          for entry, value in zip(entries[0][1:], vector)) & mask)
            if power < n - 2:
                vector = [sum(entry_times(entry, value, mask)
                              for entry, value in zip(row, vector)) & mask for row in c]
    return [sum(q[k - j] * previous[j]
                for j in range(max(0, k - n), min(k, n - 1) + 1)) & mask
            for k in range(n + 1)]


def determinant_residue(order, cap):
    digits = PLANE * (cap + 1)
    mask = (1 << (BITS * digits)) - 1
    # n=8 is even, so charpoly's constant coefficient is det(A).
    return berkowitz(displacement(order), mask)[-1], mask


def expected_residue(poly, degree, mask):
    return sum(value << (BITS * (key[0] + RADIX * key[1] + RADIX ** 2 * key[2]
                                + PLANE * degree)) for key, value in poly.items()) & mask


def decode_residue(residue, cap):
    # Balanced base digits recover signed coefficients uniquely because the
    # full determinant coefficient mass is below 2^24, half the digit radix.
    base = 1 << BITS
    half = base // 2
    polynomials = [dict() for _ in range(cap + 1)]
    for degree in range(cap + 1):
        for k in range(PLANE):
            digit = residue & (base - 1)
            if digit >= half:
                digit -= base
            residue = (residue - digit) >> BITS
            if digit:
                key = (k % RADIX, (k // RADIX) % RADIX, k // (RADIX ** 2))
                polynomials[degree][key] = digit
    return polynomials


def horner_translate(poly):
    # Substitute each variable by 1-delta using univariate Horner recurrences.
    # This computes the complete translated polynomial, not only its claimed
    # first homogeneous degree; no binomial coefficient routine is used.
    result = dict(poly)
    for axis in range(3):
        groups = defaultdict(dict)
        for powers, value in result.items():
            others = tuple(powers[i] for i in range(3) if i != axis)
            groups[others][powers[axis]] = value
        result = {}
        for others, coefficients in groups.items():
            translated = []
            for degree in range(max(coefficients), -1, -1):
                next_coefficients = [0] * (len(translated) + 1)
                for j, value in enumerate(translated):
                    next_coefficients[j] += value
                    next_coefficients[j + 1] -= value
                next_coefficients[0] += coefficients.get(degree, 0)
                translated = next_coefficients
            for degree, value in enumerate(translated):
                if value:
                    powers = list(others)
                    powers.insert(axis, degree)
                    result[tuple(powers)] = value
    return result


def negative_controls(rows):
    rejected = []
    for target_degree in (0, 4):
        row = next(row for row in rows if row["lower_degree"] == target_degree)
        actual, mask = determinant_residue(tuple(row["order"]), target_degree)
        poly = {tuple(key): value for key, value in row["leading"]}
        poly[(0, 0, 0)] = poly.get((0, 0, 0), 0) + 1
        require(actual != expected_residue(poly, target_degree, mask), "coefficient mutation survived")
        rejected.append("degree-%d leading coefficient mutation" % target_degree)
        if target_degree:
            good = {tuple(key): value for key, value in row["leading"]}
            require(actual != (expected_residue(good, target_degree, mask) + 1) & mask,
                    "spurious lower-w term survived")
            rejected.append("spurious lower-w constant")
    return rejected


def scalar_method_checks():
    # A third determinant method validates the new characteristic-polynomial
    # implementation on dense scalar matrices, including singular cases.
    def bareiss(matrix):
        a = [row[:] for row in matrix]
        n, previous, sign = len(a), 1, 1
        for k in range(n - 1):
            pivot = next((i for i in range(k, n) if a[i][k]), None)
            if pivot is None:
                return 0
            if pivot != k:
                a[k], a[pivot] = a[pivot], a[k]
                sign *= -1
            value = a[k][k]
            for i in range(k + 1, n):
                for j in range(k + 1, n):
                    quotient, remainder = divmod(value * a[i][j] - a[i][k] * a[k][j], previous)
                    require(not remainder, "scalar Bareiss nonexact division")
                    a[i][j] = quotient
                a[i][k] = 0
            previous = value
        return sign * a[-1][-1]

    state, checks = 42, 0
    for n in range(1, 9):
        for case in range(10):
            matrix = []
            for i in range(n):
                row = []
                for j in range(n):
                    state = (1664525 * state + 1013904223) & (2 ** 32 - 1)
                    row.append((state >> 16) % 11 - 5)
                matrix.append(row)
            if case == 8:
                matrix = [[int(j == (i + 1) % n) for j in range(n)] for i in range(n)]
            elif case == 9 and n > 1:
                matrix[-1] = matrix[0][:]
            entries = [[((0, value),) for value in row] for row in matrix]
            mask = 2 ** 200 - 1
            actual = ((-1) ** n * berkowitz(entries, mask)[-1]) & mask
            require(actual == bareiss(matrix) & mask, "scalar Berkowitz/Bareiss mismatch")
            checks += 1
    return checks


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--receipt", type=Path, help="Optional fresh receipt; default replay is read-only.")
    args = parser.parse_args()
    filenames = ("PROOF.md", "classify_leading.py", "leading-classification.json",
                 "classification-result.json", "check_mixed_columns.py")
    source_bytes = {name: (SOURCE / name).read_bytes() for name in filenames}
    source_hashes = {name: sha256(data).hexdigest() for name, data in source_bytes.items()}
    rows = json.loads(source_bytes["leading-classification.json"])["rows"]
    claimed_result = json.loads(source_bytes["classification-result.json"])
    start = time.monotonic()
    scalar_checks = scalar_method_checks()
    orbit_result = coverage(rows)
    require(factorial(8) * 2 ** 8 < 2 ** (BITS - 1), "balanced radix insufficient")
    counts = Counter()
    max_mass = max_gradient = 0
    minimum = None
    upper_degree = 0
    unique = set()
    digest = sha256()
    chosen = rows[:args.limit] if args.limit else rows
    for index, row in enumerate(chosen):
        degree = row["lower_degree"]
        require(0 <= degree <= 4, "uncovered lower degree")
        actual, mask = determinant_residue(tuple(row["order"]), degree)
        claimed = {tuple(key): value for key, value in row["leading"]}
        require(actual == expected_residue(claimed, degree, mask),
                ("independent determinant residue mismatch", index, row["order"]))
        decoded = decode_residue(actual, degree)
        require(all(not poly for poly in decoded[:degree]) and decoded[degree] == claimed,
                ("independent complete coefficient decode mismatch", index))
        leading = decoded[degree]
        translated = horner_translate(leading)
        k = min(map(sum, translated))
        taylor = {powers: value for powers, value in translated.items() if sum(powers) == k}
        require(k == row["taylor_degree"] and taylor ==
                {tuple(key): value for key, value in row["taylor"]},
                ("Horner Taylor reconstruction mismatch", index))
        counts[(degree, k)] += 1
        unique.add(tuple(sorted(leading.items())))
        max_mass = max(max_mass, sum(abs(value) * 2 ** sum(powers)
                                     for powers, value in leading.items()))
        max_gradient = max(max_gradient, sum(sum(powers) * abs(value)
                                             for powers, value in taylor.items()))
        upper_degree = max(upper_degree, max(max(powers) for powers in leading))
        for point in permutations((33, 47, 62)):
            value = sum(coefficient * point[0] ** powers[0] * point[1] ** powers[1]
                        * point[2] ** powers[2] for powers, coefficient in taylor.items())
            absolute = Fraction(abs(value), 64 ** k)
            require(absolute > 0, ("vanishing center", index, point))
            minimum = absolute if minimum is None else min(minimum, absolute)
        digest.update(str((tuple(row["order"]), degree, tuple(sorted(leading.items())),
                           k, tuple(sorted(taylor.items())))).encode() + b"\n")
        if index % 250 == 0:
            print(index, round(time.monotonic() - start, 3), flush=True)
    result = {"status": "PASS_INDEPENDENT_KRONECKER_BERKOWITZ",
              "coverage": orbit_result, "determinants_reconstructed": len(chosen),
              "counts": [[list(key), value] for key, value in sorted(counts.items())],
              "unique_leading_polynomials": len(unique),
              "minimum_center_coefficient": str(minimum),
              "maximum_shifted_coefficient_mass_bound": max_mass,
              "maximum_leading_gradient_bound": max_gradient,
              "maximum_observed_upper_exponent": upper_degree,
              "coefficient_digit_bits": BITS, "upper_exponent_radix": RADIX,
              "full_determinant_mass_bound": factorial(8) * 2 ** 8,
              "scalar_berkowitz_bareiss_cross_checks": scalar_checks,
              "negative_controls": negative_controls(rows),
              "independent_ordered_result_sha256": digest.hexdigest(),
              "reviewed_source_sha256": source_hashes,
              "seconds": round(time.monotonic() - start, 3)}
    if not args.limit:
        require(len(unique) == 2677 and minimum == Fraction(7, 131072)
                and max_mass == 6656 and max_gradient == 156, "reported constants differ")
        require(result["counts"] == claimed_result["counts"], "reported class census differs")
        require(all(sha256((SOURCE / name).read_bytes()).hexdigest() == value
                    for name, value in source_hashes.items()), "source changed during review")
        if args.receipt is not None:
            args.receipt.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2), flush=True)


if __name__ == "__main__":
    main()
