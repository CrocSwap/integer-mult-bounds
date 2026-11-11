#!/usr/bin/env python3
"""Check the n-axis monomial record bound. Standard library only."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MAPS = 311304


def fail(message):
    raise SystemExit(message)


def require(condition, message):
    if not condition:
        fail(message)


def record_bound(n):
    """R(n) = (3n^2 + 9n + 2) / 2."""
    numerator = 3 * n * n + 9 * n + 2
    require(numerator % 2 == 0, "record numerator is odd at n=%s" % n)
    return numerator // 2


def loose_specialization_bound(n):
    """#4610 accounting: n(n-1) additions and n-1 swaps, charged separately."""
    address = n * (n - 1) + 3 * (n - 1)
    return address + n + 3 * n + n * (n - 1) // 2 + 3


def review_sum(n):
    """Operation list in the #7000 application review, summed."""
    return n * (n - 1) + 3 * n + n + 3 * n + n * (n - 1) // 2 + 3


def loose_square(n):
    return 4 * (n + 1) * (n + 1)


def witness_matrix(n):
    matrix = [[0] * n for _ in range(n)]
    if n == 1:
        matrix[0][0] = 1
        return matrix
    matrix[0][n - 1] = 1
    for i in range(1, n):
        matrix[i][0] = 1
        matrix[i][i] = 1
    return matrix


def eliminate(matrix):
    """Return per-column (swap, additions), or None if a pivot is missing.

    The final matrix must be the identity. A missing pivot or a non-identity
    result is rejection, not a successful recipe.
    """
    n = len(matrix)
    rows = [row[:] for row in matrix]
    columns = []
    for k in range(n):
        pivot = None
        for r in range(k, n):
            if rows[r][k] == 1:
                pivot = r
                break
        if pivot is None:
            return None
        swapped = 0
        if pivot != k:
            rows[k], rows[pivot] = rows[pivot], rows[k]
            swapped = 1
        additions = 0
        for i in range(n):
            if i != k and rows[i][k] == 1:
                for j in range(n):
                    rows[i][j] ^= rows[k][j]
                additions += 1
        columns.append((swapped, additions))
    for i in range(n):
        for j in range(n):
            if rows[i][j] != (1 if i == j else 0):
                return None
    return columns


def address_count(columns):
    return sum(additions + 3 * swapped for swapped, additions in columns)


def monomial_records(n, columns):
    return address_count(columns) + n + 3 * n + n * (n - 1) // 2 + 3


def gl_order(n):
    order = 1
    for i in range(n):
        order *= (1 << n) - (1 << i)
    return order


def check_algebra():
    for n in range(1, 65):
        address = (n + 2) * (n - 1)
        phase = n + 3 * n + n * (n - 1) // 2 + 3
        require(record_bound(n) == address + phase, "closed form disagrees at n=%s" % n)
        require(
            loose_specialization_bound(n) - record_bound(n) == n - 1,
            "gap against the separate-maxima count is not n-1",
        )
        require(review_sum(n) - record_bound(n) == n + 2, "review gap is not n+2")
        gap_num = 5 * n * n + 7 * n + 6
        require(gap_num % 2 == 0, "square gap is not an integer")
        require(loose_square(n) - record_bound(n) == gap_num // 2, "square gap formula")
        require(loose_square(n) > record_bound(n), "square bound does not dominate")
    require(record_bound(1) == 7, "n=1 record count")
    require(record_bound(9) == 163, "n=9 sharp count")
    require(loose_specialization_bound(9) == 171, "n=9 specialization count")
    require(review_sum(9) == 174, "n=9 review sum")
    require(loose_square(9) == 400, "n=9 square")
    require(record_bound(153) == 35803, "n=153 sharp per-map count")
    require(loose_square(153) == 94864, "n=153 square per-map count")
    loose_product = MAPS * loose_square(153)
    sharp_product = MAPS * record_bound(153)
    require(loose_product == 29531542656, "loose product %s" % loose_product)
    require(sharp_product == 11145617112, "sharp product %s" % sharp_product)
    require(loose_product < 2**35 < 2**40, "loose product is not below 2^35")
    require(sharp_product < 2**34, "sharp product is not below 2^34")
    return sharp_product


def check_swap_identity():
    """Three XOR additions swap two rows. Two do not."""
    left = [1, 0, 1, 1]
    right = [0, 1, 1, 0]
    a, b = left[:], right[:]
    a = [x ^ y for x, y in zip(a, b)]
    b = [x ^ y for x, y in zip(b, a)]
    require(a != right or b != left, "two XOR additions already swapped the control rows")
    a, b = left[:], right[:]
    a = [x ^ y for x, y in zip(a, b)]
    b = [x ^ y for x, y in zip(b, a)]
    a = [x ^ y for x, y in zip(a, b)]
    require(a == right and b == left, "three XOR additions did not swap the control rows")


def check_witness_family():
    for n in range(1, 65):
        columns = eliminate(witness_matrix(n))
        require(columns is not None, "witness is singular at n=%s" % n)
        require(address_count(columns) == (n + 2) * (n - 1), "witness address at n=%s" % n)
        require(monomial_records(n, columns) == record_bound(n), "witness records at n=%s" % n)
        if n == 1:
            require(columns == [(0, 0)], "n=1 column charge")
            continue
        for k, (swapped, additions) in enumerate(columns):
            if k < n - 1:
                require(swapped == 1 and additions == n - 2, "early witness column n=%s k=%s" % (n, k))
            else:
                require(swapped == 0 and additions == n - 1, "final witness column n=%s" % n)


def matrices(n):
    size = n * n
    for mask in range(1 << size):
        yield [[(mask >> (i * n + j)) & 1 for j in range(n)] for i in range(n)]


def check_exhaustive_census():
    """Every matrix of size n<=4. Acceptance count equals |GL(n,F2)|."""
    expected_maximizers = {1: 1, 2: 1, 3: 1, 4: 1}
    for n in range(1, 5):
        accepted = 0
        maximizers = 0
        joint = 0
        max_adds = -1
        max_swaps = -1
        target = (n + 2) * (n - 1)
        for matrix in matrices(n):
            columns = eliminate(matrix)
            if columns is None:
                continue
            accepted += 1
            additions = sum(item[1] for item in columns)
            swaps = sum(item[0] for item in columns)
            max_adds = max(max_adds, additions)
            max_swaps = max(max_swaps, swaps)
            for k, (swapped, added) in enumerate(columns):
                require(added + swapped <= n - 1, "column charge failed")
                if k == n - 1:
                    require(swapped == 0, "last column swapped")
            if address_count(columns) == target:
                maximizers += 1
            if additions == n * (n - 1) and swaps == n - 1:
                joint += 1
        require(accepted == gl_order(n), "accepted %s invertible matrices at n=%s, |GL|=%s" % (accepted, n, gl_order(n)))
        require(max_adds == n * (n - 1), "addition maximum is short at n=%s" % n)
        require(max_swaps == n - 1, "swap maximum is short at n=%s" % n)
        require(maximizers == expected_maximizers[n], "maximizer count %s at n=%s" % (maximizers, n))
        require(joint == (1 if n == 1 else 0), "joint separate-maxima count %s at n=%s" % (joint, n))
    zero = eliminate([[0, 0], [0, 0]])
    require(zero is None, "the zero matrix was accepted")
    identity = eliminate([[1, 0], [0, 1]])
    require(identity == [(0, 0), (0, 0)], "identity elimination")


def check_sources():
    selected = json.loads((ROOT / "certificates/selected-result.json").read_text(encoding="utf-8"))
    require(selected["kappa"] == "363005817/100000000000", "selected kappa changed")
    require(selected["previous_kappa"] == "781451/250000000", "previous kappa pin")
    review = (ROOT / "docs/research/pr-intake-evidence/pr7000-application/PROOF-REVIEW.md").read_text(encoding="utf-8")
    for phrase in ("n(n-1)+3n", "4(n+1)^2", "311,304", "29,531,542,656", "precision_tape"):
        require(phrase in review, "application review is missing %r" % phrase)
    specialization = (ROOT / "research/final4610-independent-admission/SPECIALIZATION.md").read_text(encoding="utf-8")
    require("96+9+27+36+3 = 171" in specialization, "n=9 specialization count is missing")


def main():
    check_swap_identity()
    check_algebra()
    check_witness_family()
    check_exhaustive_census()
    check_sources()
    print(
        "PASS_N_AXIS_MONOMIAL_RECORDS"
        " R9=163 specialization9=171 review9=174 square9=400"
        " R153=35803 square153=94864"
        " sharp_product=11145617112 loose_product=29531542656"
        " census=GL(n,2) for n<=4 no_new_kappa"
    )


if __name__ == "__main__":
    main()
