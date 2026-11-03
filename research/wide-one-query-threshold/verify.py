"""Exact finite corroboration of the wider one-query obstruction."""

import argparse
import hashlib
import itertools
import json
from fractions import Fraction
from pathlib import Path


def require(condition, message):
    if not condition:
        raise ValueError(message)


def identity(n):
    require(0 <= n <= 8, "dimension outside the finite checker")
    return tuple(tuple(int(i == j) for j in range(n)) for i in range(n))


def column(matrix, j):
    return tuple(row[j] for row in matrix)


def support(vector):
    return sum(value != 0 for value in vector)


def action(matrix, vector, prime=0):
    result = tuple(sum(a * b for a, b in zip(row, vector, strict=True))
                   for row in matrix)
    return tuple(value % prime for value in result) if prime else result


def rank(matrix, prime):
    rows = [list(row) for row in matrix]
    size = len(rows)
    require(size <= 8 and all(len(row) == size for row in rows), "bad matrix")
    pivots = 0
    for j in range(size):
        candidates = [i for i in range(pivots, size) if rows[i][j] % prime]
        if not candidates:
            continue
        pivot = candidates[0]
        rows[pivots], rows[pivot] = rows[pivot], rows[pivots]
        inverse = pow(rows[pivots][j], -1, prime)
        rows[pivots] = [value * inverse % prime for value in rows[pivots]]
        for i in range(pivots + 1, size):
            factor = rows[i][j]
            rows[i] = [(a - factor * b) % prime
                       for a, b in zip(rows[i], rows[pivots], strict=True)]
        pivots += 1
    return pivots


def carrier(q, n, helpers, prime=0):
    m = len(q)
    size = 2 * m + helpers
    result = [list(row) for row in identity(size)]
    for i in range(2 * m):
        result[i] = [0] * size
    for i in range(m):
        for j in range(m):
            result[i][j] = q[i][j] - int(i == j)
            result[i][m + j] = n[i][j]
            result[m + i][j] = q[i][j]
    if prime:
        result = [[value % prime for value in row] for row in result]
    return tuple(tuple(row) for row in result)


def query(active, operator, size):
    require(len(active) == len(set(active)), "duplicate active coordinate")
    require(all(type(i) is int and 0 <= i < size for i in active), "bad active set")
    width = len(active)
    require(len(operator) == width, "wrong query width")
    require(all(len(row) == width for row in operator), "nonsquare query")
    result = [list(row) for row in identity(size)]
    for i, row in enumerate(active):
        for j, col in enumerate(active):
            result[row][col] = operator[i][j]
    return tuple(tuple(row) for row in result)


def separated_pairs():
    dense = []
    separation_checks = 0
    for entries in itertools.product((1, 2), repeat=4):
        matrix = (entries[:2], entries[2:])
        if rank(matrix, 3) != 2:
            continue
        dense.append(matrix)
        for vector in itertools.product(range(3), repeat=2):
            if support(vector) == 1:
                require(support(action(matrix, vector, 3)) == 2, "separation")
                separation_checks += 1
    return tuple(dense), separation_checks


def full_endpoint_census(matrix):
    endpoints = tuple((permutation, scales)
                      for permutation in itertools.permutations(range(4))
                      for scales in itertools.product((1, 2), repeat=4))
    widths = [0] * 5
    for f_perm, f_scale in endpoints:
        for g_perm, g_scale in endpoints:
            active = set()
            for i in range(4):
                for j in range(4):
                    value = f_scale[i] * matrix[f_perm[i]][g_perm[j]] * g_scale[j]
                    if value % 3 != int(i == j):
                        active.update((i, j))
            width = len(active)
            require(width >= 4, "under-width monomial factorization")
            widths[width] += 1
    return {"endpoint_pairs": sum(widths), "required_width_histogram": widths}


def helper_census(q):
    cases = below_threshold = new_width_cases = feasible = 0
    for helpers in range(3):
        matrix = carrier(q, q, helpers, 3)
        size = len(matrix)
        for permutation in itertools.permutations(range(size)):
            images = tuple(column(matrix, j) for j in permutation)
            for mask in range(1 << size):
                active = tuple(i for i in range(size) if mask >> i & 1)
                untouched = tuple(i for i in range(size) if not (mask >> i & 1))
                bad = tuple(i for i in untouched if support(images[i]) > 1)
                if len(active) < 4:
                    require(bool(bad), "untouched columns escaped the obstruction")
                    below_threshold += 1
                    new_width_cases += len(active) == 3
                if not bad:
                    # F=G realizes this case: the query is the conjugated carrier.
                    transformed = tuple(tuple(matrix[permutation[i]][permutation[j]]
                                              for j in range(size))
                                        for i in range(size))
                    block = tuple(tuple(transformed[i][j] for j in active)
                                  for i in active)
                    require(query(active, block, size) == transformed, "attainer")
                    feasible += 1
                cases += 1
    return {"permutation_active_sets": cases, "excluded_width_below_four": below_threshold,
            "excluded_new_width_three": new_width_cases, "attaining_active_sets": feasible}


def attaining_queries(dense):
    instances = columns = 0
    for q in dense:
        for n in dense:
            for helpers in range(5):
                matrix = carrier(q, n, helpers, 3)
                size = len(matrix)
                for width in range(4, size + 1):
                    active = tuple(range(width))
                    block = tuple(tuple(matrix[i][j] for j in active) for i in active)
                    require(rank(block, 3) == width, "singular attaining query")
                    candidate = query(active, block, size)
                    for basis in identity(size):
                        require(action(candidate, basis, 3) == action(matrix, basis, 3),
                                "query failed an arbitrary-input basis column")
                        columns += 1
                    instances += 1
    return {"dense_operator_pairs": len(dense) ** 2,
            "attaining_queries": instances, "attaining_basis_columns": columns}


def real_boundary_controls():
    h = tuple(tuple(Fraction((-1) ** ((i & j).bit_count()), 2) for j in range(4))
              for i in range(4))
    for i in range(4):
        for j in range(4):
            require(sum(h[k][i] * h[k][j] for k in range(4)) == int(i == j),
                    "rational Walsh operator is not unitary")
    checked = equality = 0
    for vector in itertools.product((-1, 0, 1), repeat=4):
        if support(vector) == 0:
            continue
        product = support(vector) * support(action(h, vector))
        require(product >= 4, "unitary uncertainty inequality")
        equality += product == 4
        checked += 1
    matrix = carrier(h, h, 0)
    require(query(tuple(range(8)), matrix, 8) == matrix, "width-eight attainer")
    inverse = tuple(tuple(0 if i < 4 and j < 4 else
                          h[i % 4][j % 4] if i < 4 or j < 4 else
                          int(i == j) - h[i % 4][j % 4] for j in range(8))
                    for i in range(8))
    for basis in identity(8):
        require(action(matrix, action(inverse, basis)) == basis, "carrier inverse")
        require(action(inverse, action(matrix, basis)) == basis, "reverse inverse")
    # F=C, G=I and an empty query are legal at K_F K_G = 4, but not below it.
    require(query((), (), 8) == identity(8), "empty query")
    block_support = max(support(column(tuple(row[k:k + 4] for row in matrix[i:i + 4]), j))
                        for i in (0, 4) for k in (0, 4) for j in range(4))
    require(block_support == 4, "strict-threshold counterexample support")
    swap = carrier(identity(4), identity(4), 0)
    require(all(support(column(swap, j)) == 1 for j in range(8)), "monomial control")
    return {"rational_nonzero_vectors": checked, "uncertainty_equalities": equality,
            "sharp_width": 8, "strict_support_boundary": 4,
            "controls": ["width_2M_attains", "support_equality_allows_zero_query",
                         "monomial_carriers_allow_zero_query"]}


def rejection_controls():
    cases = (([0, 0], identity(2), 4), ([True], identity(1), 4),
             ([4], identity(1), 4), ([0], identity(2), 4))
    for active, operator, size in cases:
        try:
            query(active, operator, size)
        except ValueError:
            continue
        raise ValueError("malformed query accepted")
    return len(cases)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()
    dense, separation_checks = separated_pairs()
    require(len(dense) == 8, "finite dense operator domain changed")
    result = {"status": "PASS_WIDE_ONE_QUERY_THRESHOLD",
              "claim_type": "scoped_written_proof_with_finite_corroboration",
              "separation_checks": separation_checks,
              "full_endpoints": full_endpoint_census(carrier(dense[0], dense[0], 0, 3)),
              "helpers": helper_census(dense[0]),
              "attainers": attaining_queries(dense),
              "real_boundaries": real_boundary_controls(),
              "rejected_malformed_queries": rejection_controls()}
    package = Path(__file__).resolve().parent
    names = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py")
    result["source_sha256"] = {name: hashlib.sha256((package / name).read_bytes()).hexdigest()
                               for name in names}
    encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.receipt is not None:
        require(args.receipt.is_absolute(), "receipt path must be absolute")
        require(not args.receipt.resolve().is_relative_to(package.parents[1]),
                "receipt must stay outside the checkout")
        with args.receipt.open("x", encoding="utf-8") as handle:
            require(handle.write(encoded) == len(encoded), "short receipt write")
    print(encoded, end="")
    print(result["status"])


if __name__ == "__main__":
    main()
