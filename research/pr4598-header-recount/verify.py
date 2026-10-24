#!/usr/bin/env python3
"""Independent recount of PR #4598 (petalas): complete passing binary threshold headers for k requests in dimension k+1.

Problem (from #4598/#4275): U_1..U_k pairwise orthogonal rank-one idempotents on F_2^m, m = k+1, normalized to
U_t = e_t e_t^T; P_t = I - U_t; a header G in GL_m(F_2) passes when every leading principal minor of G P_t G^-1 of
orders 1..m-1 is nonzero, for every t. #4598 claims 2,880 passing headers at k = 5 (and 12, 48 at k = 3, 4).

Method, deliberately not #4598's (no J - I decomposition, no rank/idempotence argument, no rectangle-subset search):
  * G P_t G^-1 = I - g_t h_t^T with g_t column t of G and h_t row t of G^-1, so the order-j minor is
    1 - sum_{i<=j} h_t[i] g_t[i] (matrix determinant lemma, derived here and checked by brute force below);
  * headers correspond bijectively to pairs (X, Y), X the first k columns of G (rows x_i), Y the first k rows of
    G^-1 (columns y_i), with Y X = sum_i y_i x_i^T = I_k: the last column is the unique nonzero vector of ker Y;
  * so the count is the number of ordered sequences of m pairs (y_i, x_i) in F_2^k x F_2^k whose first k
    increments y_i x_i^T have zero diagonal (supports disjoint) and whose total is I_k. Increments are weighted by
    how many pairs give them (the zero matrix arises from 2*2^k - 1 pairs), so zero and repeated increments are
    counted, not excluded a priori. The ordered convolution is evaluated exactly by meet-in-the-middle;
  * the reformulation is cross-checked against the leading-minor definition by brute force over all of GL_4(F_2)
    (k = 3) and GL_3 (k = 2), for the coordinate requests and for a non-coordinate orthogonal family.
Ryanson Jonathan with Claude Code (Claude Opus 5.5) assistance. Apache-2.0.
"""
from collections import Counter
from itertools import product
import json
import sys


def need(condition, message):
    if not condition:
        raise AssertionError(message)


def outer(y, x, k):
    return sum(1 << (k * a + b) for a in range(k) if y >> a & 1 for b in range(k) if x >> b & 1)


def convolve(table, weights):
    out = Counter()
    for a, wa in table.items():
        for r, wr in weights.items():
            out[a ^ r] += wa * wr
    return out


def count_by_convolution(k, guarded=None, zero_weight=None):
    """Ordered count of (y_i, x_i), i = 1..k+1, whose first `guarded` increments have zero diagonal
    (default k: every guard order 1..k) and whose total is the identity."""
    guarded = k if guarded is None else guarded
    zero_diag, anything = Counter(), Counter()
    for y, x in product(range(1 << k), repeat=2):
        r = outer(y, x, k)
        anything[r] += 1
        if y & x == 0:
            zero_diag[r] += 1
    need(sum(zero_diag.values()) == 3 ** k and zero_diag[0] == 2 ** (k + 1) - 1, "increment weights")
    if zero_weight is not None:
        zero_diag[0] = zero_weight
    steps = [zero_diag] * guarded + [anything] * (k + 1 - guarded)
    head, tail = Counter({0: 1}), Counter({0: 1})
    for w in steps[:(k + 1) // 2]:
        head = convolve(head, w)
    for w in steps[(k + 1) // 2:]:
        tail = convolve(tail, w)
    ident = sum(1 << (k * a + a) for a in range(k))
    return sum(w * tail.get(a ^ ident, 0) for a, w in head.items())


def mat_mul(a, b, n):
    return [[sum(a[i][l] & b[l][j] for l in range(n)) & 1 for j in range(n)] for i in range(n)]


def inverse(a, n):
    m = [row[:] + [int(i == j) for j in range(n)] for i, row in enumerate(a)]
    for c in range(n):
        p = next((r for r in range(c, n) if m[r][c]), None)
        if p is None:
            return None
        m[c], m[p] = m[p], m[c]
        for r in range(n):
            if r != c and m[r][c]:
                m[r] = [u ^ v for u, v in zip(m[r], m[c])]
    return [row[n:] for row in m]


def leading_minors_nonzero(a, n, orders):
    """Leading principal minors of orders 1..orders nonzero, by elimination without pivoting."""
    m = [row[:] for row in a]
    for c in range(orders):
        if not m[c][c]:
            return False
        for r in range(c + 1, n):
            if m[r][c]:
                m[r] = [u ^ v for u, v in zip(m[r], m[c])]
    return True


def brute_force(n, requests, orders=None):
    orders = n - 1 if orders is None else orders
    passing = total = 0
    for bits in range(1 << (n * n)):
        g = [[bits >> (n * i + j) & 1 for j in range(n)] for i in range(n)]
        gi = inverse(g, n)
        if gi is None:
            continue
        total += 1
        passing += all(leading_minors_nonzero(mat_mul(mat_mul(g, p, n), gi, n), n, orders) for p in requests)
    return passing, total


def requests_from(q, n, k):
    qi = inverse(q, n)
    out = []
    for t in range(k):
        p = [[int(i == j) ^ (i == t and j == t) for j in range(n)] for i in range(n)]
        out.append(mat_mul(mat_mul(q, p, n), qi, n))
    return out


def main():
    counts = {k: count_by_convolution(k) for k in (2, 3, 4, 5)}
    need(counts[3] == 12 and counts[4] == 48, "k = 3, 4 controls (#4275 / #4345)")
    need(counts[5] == 2880, "#4598: 2,880 headers at k = 5")
    order6 = 1
    for i in range(6):
        order6 *= 64 - 2 ** i
    need(order6 == 20158709760 and order6 % 2880 == 0 and order6 // 2880 == 6999552, "density 1/6,999,552")
    need(counts[5] != 2 * 120, "the proposed 2 k! pattern fails at k = 5")
    coordinate, gl4 = brute_force(4, requests_from([[int(i == j) for j in range(4)] for i in range(4)], 4, 3))
    q = [[1, 1, 0, 0], [0, 1, 1, 0], [1, 0, 1, 1], [0, 1, 0, 1]]
    need(inverse(q, 4) is not None, "Q invertible")
    other, _ = brute_force(4, requests_from(q, 4, 3))
    need(gl4 == 20160 and coordinate == counts[3] == other, "brute force over GL_4 matches the convolution at k = 3")
    need(all(count_by_convolution(k, zero_weight=0) == counts[k] for k in (2, 3, 4, 5)),
         "zero increments never occur in a passing sequence (counts unchanged with zero weight 0)")
    dropped = count_by_convolution(3, guarded=2)
    dropped_bf, _ = brute_force(4, requests_from([[int(i == j) for j in range(4)] for i in range(4)], 4, 3), orders=2)
    need(dropped == dropped_bf != counts[3], "failure control: dropping the order-3 guard changes the count, both ways")
    small, gl3 = brute_force(3, requests_from([[int(i == j) for j in range(3)] for i in range(3)], 3, 2))
    need(gl3 == 168 and small == counts[2], "brute force over GL_3 matches the convolution at k = 2")
    print(json.dumps({"status": "PASS_PR4598_INDEPENDENT_RECOUNT",
                      "passing_headers_by_k": {str(k): v for k, v in counts.items()},
                      "brute_force_GL4_k3": {"coordinate": coordinate, "non_coordinate_family": other,
                                             "group_order": gl4},
                      "brute_force_GL3_k2": small,
                      "k5_density": "1/%d" % (order6 // 2880), "two_k_factorial_at_k5": 240,
                      "zero_increments_contribute": 0,
                      "failure_control_drop_last_guard_k3": dropped, "new_kappa_claimed": False}, indent=1))


if __name__ == "__main__":
    sys.exit(main())
