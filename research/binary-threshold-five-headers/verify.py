#!/usr/bin/env python3
"""Exact five-request binary threshold census, produced by Nick Petalas.

Standard library only. Apache-2.0. No imported predecessor code.
"""
from collections import defaultdict
from fractions import Fraction
from hashlib import sha256
from itertools import combinations, permutations
from math import comb, factorial, prod
from pathlib import Path
import json


WITNESS = ((3, 12), (6, 17), (9, 18), (20, 10), (24, 5))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def target(k):
    require(3 <= k <= 5, "supported request count is 3..5")
    return sum((((1 << k) - 1) ^ (1 << i)) << (k * i) for i in range(k))


def rectangle(k, s, t):
    require(3 <= k <= 5 and 0 < s < 1 << k and 0 < t < 1 << k,
            "rectangle domain")
    require(s & t == 0, "rectangle must avoid the diagonal")
    return sum(t << (k * i) for i in range(k) if s >> i & 1)


def alphabet(k):
    require(3 <= k <= 5, "supported request count is 3..5")
    result = [(rectangle(k, s, t), s, t)
              for s in range(1, 1 << k) for t in range(1, 1 << k)
              if not s & t]
    require(len(result) == 3 ** k - 2 ** (k + 1) + 1, "alphabet size")
    require(len({r[0] for r in result}) == len(result), "unique factors")
    return result


def xor_bits(values):
    require(len(values) <= 6, "at most six factors")
    result = 0
    for value in values:
        result ^= value
    return result


def enumerate_sets(k, candidates):
    """Unique increasing sets, split before the last ceil(k/2) indices."""
    require(3 <= k <= 5 and k <= len(candidates) <= 180, "census bounds")
    left_size = k // 2
    table = defaultdict(list)
    left_work = 0
    for indices in combinations(range(len(candidates)), left_size):
        bits = xor_bits([candidates[i][0] for i in indices])
        table[bits].append(indices)
        left_work += 1
    found = []
    right_work = 0
    for suffix in combinations(range(len(candidates)), k - left_size):
        needed = target(k) ^ xor_bits([candidates[i][0] for i in suffix])
        for prefix in table.get(needed, ()):
            if prefix[-1] < suffix[0]:
                found.append(prefix + suffix)
        right_work += 1
    require(left_work == comb(len(candidates), left_size), "left coverage")
    require(right_work == comb(len(candidates), k - left_size), "right coverage")
    require(len(found) == len(set(found)), "each set counted once")
    return sorted(found), {"left_subsets": left_work, "right_subsets": right_work}


def matrix_product(a, b):
    n = len(a)
    require(1 <= n <= 6 and len(b) == n, "matrix dimensions")
    require(all(len(row) == n for row in a + b), "square matrices")
    return [[sum(a[i][h] * b[h][j] for h in range(n)) % 2
             for j in range(n)] for i in range(n)]


def identity(n):
    require(1 <= n <= 6, "identity domain")
    return [[int(i == j) for j in range(n)] for i in range(n)]


def inverse(a):
    n = len(a)
    require(1 <= n <= 6 and all(len(row) == n for row in a), "inverse domain")
    rows = [row[:] + unit for row, unit in zip(a, identity(n))]
    for j in range(n):
        pivots = [i for i in range(j, n) if rows[i][j]]
        require(bool(pivots), "singular header")
        p = pivots[0]
        rows[j], rows[p] = rows[p], rows[j]
        for i in range(n):
            if i != j and rows[i][j]:
                rows[i] = [x ^ y for x, y in zip(rows[i], rows[j])]
    require([row[:n] for row in rows] == identity(n), "inverse elimination")
    return [row[n:] for row in rows]


def full_guards(a):
    """Literal no-pivot elimination through rank n-1 over F2."""
    n = len(a)
    require(2 <= n <= 6 and all(len(row) == n for row in a), "guard domain")
    rows = [row[:] for row in a]
    for j in range(n - 1):
        if rows[j][j] != 1:
            return False
        for i in range(j + 1, n):
            if rows[i][j]:
                rows[i] = [x ^ y for x, y in zip(rows[i], rows[j])]
    return True


def passing_header(g):
    n = len(g)
    gi = inverse(g)
    for t in range(n - 1):
        request = identity(n)
        request[t][t] = 0
        conjugate = matrix_product(matrix_product(g, request), gi)
        if not full_guards(conjugate):
            return False
    return True


def complete_header(k, factors):
    require(3 <= k <= 5 and len(factors) == k, "completion domain")
    require(xor_bits([rectangle(k, s, t) for s, t in factors]) == target(k),
            "wrong rectangle sum")
    full = (1 << k) - 1
    x = [[t >> j & 1 for j in range(k)] for _, t in factors]
    x.append([1] * k)
    columns = [s for s, _ in factors] + [full]
    kernel = [z for z in range(1, 1 << (k + 1))
              if xor_bits([columns[i] for i in range(k + 1) if z >> i & 1]) == 0]
    require(len(kernel) == 1, "unique nonzero kernel vector")
    z = kernel[0]
    g = [row + [z >> i & 1] for i, row in enumerate(x)]
    gi = inverse(g)
    require([row[:] for row in gi[:k]] ==
            [[column >> j & 1 for column in columns] for j in range(k)],
            "completed inverse has prescribed rows")
    return g


def header_census(k, candidates, found):
    seen = set()
    for indices in found:
        factors = tuple((candidates[i][1], candidates[i][2]) for i in indices)
        for ordered in permutations(factors):
            g = complete_header(k, ordered)
            require(passing_header(g), "literal full guards reject a constructed header")
            encoded = tuple(sum(bit << j for j, bit in enumerate(row)) for row in g)
            require(encoded not in seen, "duplicate full header")
            seen.add(encoded)
    require(len(seen) == len(found) * factorial(k), "header fiber count")
    return len(seen)


def row_column_only(k, candidates, found):
    full = (1 << k) - 1
    rows = {(1 << i, full ^ (1 << i)) for i in range(k)}
    columns = {(t, s) for s, t in rows}
    return sum({(candidates[i][1], candidates[i][2]) for i in inds}
               in (rows, columns) for inds in found)


def expect_rejection(k, factors):
    try:
        complete_header(k, factors)
    except ValueError:
        return
    raise ValueError("corrupted factor fixture was accepted")


def controls(candidates, found):
    require(row_column_only(5, candidates, found) == 2, "row/column baseline")
    require(len(found) > 2, "row/column-only conjecture must fail")
    require(all(s.bit_count() == t.bit_count() == 2 for s, t in WITNESS),
            "witness is outside both star classes")
    witness_indices = tuple(sorted(candidates.index((rectangle(5, s, t), s, t))
                                   for s, t in WITNESS))
    require(witness_indices in found, "explicit counterexample missing")
    changed = list(WITNESS)
    changed[0] = (3, 4)
    expect_rejection(5, changed)
    changed[0] = (3, 13)
    expect_rejection(5, changed)
    require(not passing_header(identity(6)), "identity fails full guard chain")
    late_failure = [identity(6)[-1]] + identity(6)[:-1]
    gi = inverse(late_failure)
    for t in range(5):
        request = identity(6)
        request[t][t] = 0
        conjugate = matrix_product(matrix_product(late_failure, request), gi)
        require(conjugate[0][0] == 1, "late-failure fixture passes every first guard")
    require(not passing_header(late_failure), "later guards must reject the fixture")
    broken = complete_header(5, WITNESS)
    broken[-1] = broken[0][:]
    try:
        inverse(broken)
    except ValueError:
        pass
    else:
        raise ValueError("singular header admitted")
    return {"row_column_sets": 2, "nonstar_sets": len(found) - 2,
            "rejected_corruptions": 5, "witness_membership": True}


def main():
    report = {"claim_type": "finite certificate", "censuses": []}
    five_candidates = five_found = None
    for k in range(3, 6):
        candidates = alphabet(k)
        found, work = enumerate_sets(k, candidates)
        expected = {3: 2, 4: 2, 5: 24}[k]
        require(len(found) == expected, "exact decomposition count")
        count = header_census(k, candidates, found)
        gl_order = prod((1 << (k + 1)) - (1 << j) for j in range(k + 1))
        report["censuses"].append({"k": k, "m": k + 1,
            "rectangles": len(candidates), "unordered_decompositions": len(found),
            "passing_headers": count, "GL_order": gl_order,
            "density": str(Fraction(count, gl_order)), **work})
        if k == 5:
            five_candidates, five_found = candidates, found
    require(five_candidates is not None and five_found is not None, "five-case executed")
    report["controls"] = controls(five_candidates, five_found)
    report["five_decompositions"] = [
        [[five_candidates[i][1], five_candidates[i][2]] for i in indices]
        for indices in five_found]
    report["explicit_witness_header_rows"] = complete_header(5, WITNESS)
    package = Path(__file__).resolve().parent
    files = sorted(p for p in package.iterdir() if p.is_file())
    require(len(files) == 6, "expected six package files")
    report["package_sha256"] = {p.name: sha256(p.read_bytes()).hexdigest() for p in files}
    print("PASS_BINARY_THRESHOLD_FIVE_HEADERS")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
