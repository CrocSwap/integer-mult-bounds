#!/usr/bin/env python3
"""Bounded exact controls for the all-size orbit theorem in PROOF.md.

Standard library only. No external inputs, writes, or disabled assertions.
Orbit powers, tensor entries, shift products, inverses and ordinary Toeplitz
reconstruction are checked with different literal formulas.
"""

from fractions import Fraction as F
from itertools import product
import json


class VerificationError(RuntimeError):
    pass


def require(condition, message):
    if not condition:
        raise VerificationError(message)


def zeros(rows, cols=None):
    return [[F(0) for _ in range(rows if cols is None else cols)]
            for _ in range(rows)]


def eye(n):
    out = zeros(n)
    for i in range(n):
        out[i][i] = F(1)
    return out


def transpose(a):
    return [list(row) for row in zip(*a)]


def multiply(a, b):
    out = zeros(len(a), len(b[0]))
    for i, row in enumerate(a):
        for k, value in enumerate(row):
            if value:
                for j, other in enumerate(b[k]):
                    if other:
                        out[i][j] += value * other
    return out


def sub(a, b):
    return [[x - y for x, y in zip(ar, br)] for ar, br in zip(a, b)]


def rank(a):
    work = [row[:] for row in a]
    pivot = 0
    for col in range(len(work[0])):
        row = next((i for i in range(pivot, len(work)) if work[i][col]), None)
        if row is None:
            continue
        work[pivot], work[row] = work[row], work[pivot]
        value = work[pivot][col]
        for i in range(pivot + 1, len(work)):
            if work[i][col]:
                ratio = work[i][col] / value
                for j in range(col, len(work[0])):
                    work[i][j] -= ratio * work[pivot][j]
        pivot += 1
        if pivot == len(work):
            break
    return pivot


def inverse(a):
    n = len(a)
    work = [row[:] + unit for row, unit in zip(a, eye(n))]
    for col in range(n):
        row = next((i for i in range(col, n) if work[i][col]), None)
        require(row is not None, "singular inverse fixture")
        work[col], work[row] = work[row], work[col]
        value = work[col][col]
        work[col] = [x / value for x in work[col]]
        for i in range(n):
            if i != col and work[i][col]:
                ratio = work[i][col]
                work[i] = [x - ratio * y for x, y in zip(work[i], work[col])]
    out = [row[n:] for row in work]
    require(multiply(a, out) == eye(n), "left inverse residual")
    require(multiply(out, a) == eye(n), "right inverse residual")
    return out


def tensor(factors):
    out = [[F(1)]]
    for b in factors:
        out = [[x * y for x in ar for y in br] for ar in out for br in b]
    return out


def act(x, n, ell):
    return x[1:ell] + (n - 1 - x[0],) + x[ell:]


def power_formula(x, n, ell, k):
    """Signed-index formula independent of repeated act calls."""
    first = tuple((n - 1 - x[(i + k) % ell])
                  if ((i + k) // ell) % 2 else x[(i + k) % ell]
                  for i in range(ell))
    return first + x[ell:]


def raw_order(shape, n, ell):
    vertices = list(product(*(range(s) for s in shape)))
    seen = set()
    ordered = []
    starts = []
    lengths = []
    for vertex in vertices:
        if vertex in seen:
            continue
        starts.append(len(ordered))
        current = vertex
        while current not in seen:
            seen.add(current)
            ordered.append(current)
            current = act(current, n, ell)
        require(current == vertex, "orbit did not close at representative")
        lengths.append(len(ordered) - starts[-1])
    require(set(ordered) == set(vertices) and len(ordered) == len(vertices),
            "ordering is not a permutation")
    return vertices, ordered, starts, lengths


def guarded_order(shape, n, ell):
    require(n >= 2 and n % 2 == 0, "even local dimension is required")
    require(ell >= 1 and ell & (ell - 1) == 0, "ell must be a power of two")
    require(len(shape) >= ell and all(s == n for s in shape[:ell]),
            "selected dimensions differ")
    out = raw_order(shape, n, ell)
    vertices, ordered, starts, lengths = out
    require(all(length == 2 * ell for length in lengths), "wrong orbit length")
    require(len(starts) * 2 * ell == len(vertices), "wrong orbit count")
    independent = []
    for vertex in vertices:
        orbit = [power_formula(vertex, n, ell, k) for k in range(2 * ell)]
        require(len(set(orbit)) == 2 * ell, "direct powers are not distinct")
        require(power_formula(vertex, n, ell, 2 * ell) == vertex,
                "direct full period is not identity")
        if vertex == min(orbit):
            independent.extend(orbit)
    require(independent == ordered, "independent representative order differs")
    return out


def gaussian(n, q, v=F(1)):
    require(F(0) < q < F(1), "q must lie in (0,1)")
    return [[q ** ((i - j) ** 2) * v ** (i - j) for j in range(n)]
            for i in range(n)]


def entry_tensor(factors, x, y):
    value = F(1)
    for b, i, j in zip(factors, x, y):
        value *= b[i][j]
    return value


def permuted_matrix(factors, vertices, ordered):
    full = tensor(factors)
    indices = {x: i for i, x in enumerate(vertices)}
    out = [[full[indices[x]][indices[y]] for y in ordered] for x in ordered]
    literal = [[entry_tensor(factors, x, y) for y in ordered] for x in ordered]
    require(out == literal, "literal kernel differs from permuted tensor")
    return out


def stein(h):
    return [[value - (h[i - 1][j - 1] if i and j else F(0))
             for j, value in enumerate(row)] for i, row in enumerate(h)]


def literal_stein(h):
    z = zeros(len(h))
    for i in range(1, len(h)):
        z[i][i - 1] = F(1)
    return sub(h, multiply(multiply(z, h), transpose(z)))


def supported(e, starts):
    starts = set(starts)
    return all(e[i][j] == 0 for i in range(len(e)) for j in range(len(e))
               if i not in starts and j not in starts)


def generators(e, starts):
    """Support decomposition without numerical rank factorization."""
    n = len(e)
    start_set = set(starts)
    out = []
    for s in starts:
        unit = [F(int(i == s)) for i in range(n)]
        out.append((unit, e[s][:]))
        out.append(([e[i][s] if i not in start_set else F(0)
                     for i in range(n)], unit))
    recovered = [[sum(u[i] * v[j] for u, v in out)
                  for j in range(n)] for i in range(n)]
    require(recovered == e, "support-generator decomposition failed")
    return out


def toeplitz_reconstruct(terms):
    n = len(terms[0][0])
    out = zeros(n)
    for u, v in terms:
        lower = [[u[i - j] if i >= j else F(0) for j in range(n)]
                 for i in range(n)]
        upper = [[v[j - i] if j >= i else F(0) for j in range(n)]
                 for i in range(n)]
        value = multiply(lower, upper)
        out = [[x + y for x, y in zip(ar, br)] for ar, br in zip(out, value)]
    return out


def check_case(name, factors, n, ell, expected_rank=None):
    shape = tuple(len(b) for b in factors)
    vertices, ordered, starts, _ = guarded_order(shape, n, ell)
    index = {x: i for i, x in enumerate(ordered)}
    successors = [index[act(x, n, ell)] for x in ordered]
    targets = [factors, [inverse(b) for b in factors]]
    ranks = []
    reconstructions = 0
    for target in targets:
        h = permuted_matrix(target, vertices, ordered)
        require(all(h[successors[i]][successors[j]] == h[i][j]
                    for i in range(len(h)) for j in range(len(h))),
                "kernel does not commute with orbit permutation")
        e = stein(h)
        require(supported(e, starts), "displacement escaped start support")
        actual_rank = rank(e)
        require(actual_rank <= 2 * len(starts), "rank exceeds support bound")
        if expected_rank is not None:
            require(actual_rank == expected_rank, "incorrect exact fixture rank")
        ranks.append(actual_rank)
        terms = generators(e, starts)
        if len(h) <= 16:
            require(literal_stein(h) == e, "literal shift product differs")
            require(toeplitz_reconstruct(terms) == h, "Toeplitz reconstruction differs")
            reconstructions += 1
    if len(ordered) <= 16:
        h = permuted_matrix(factors, vertices, ordered)
        hi = permuted_matrix(targets[1], vertices, ordered)
        require(inverse(h) == hi, "tensor inverse differs from full elimination")
    return {"case": name, "dimension": len(ordered), "ell": ell,
            "orbits": len(starts), "bound": 2 * len(starts),
            "forward_rank": ranks[0], "inverse_rank": ranks[1],
            "literal_reconstructions": reconstructions}


def must_reject(action, message):
    try:
        action()
    except VerificationError:
        return
    raise VerificationError(message)


def controls():
    must_reject(lambda: guarded_order((3, 3), 3, 2), "odd dimension accepted")
    _, _, _, odd_lengths = raw_order((3, 3), 3, 2)
    require(1 in odd_lengths, "odd fixed-point witness disappeared")
    must_reject(lambda: guarded_order((2, 2, 2), 2, 3), "nonpower ell accepted")
    _, _, _, wrong_lengths = raw_order((2, 2, 2), 2, 3)
    require(2 in wrong_lengths and 6 in wrong_lengths,
            "nonpower orbit-length witness disappeared")
    vertices, ordered, starts, _ = guarded_order((2, 2, 2, 2), 2, 4)
    broken = [gaussian(2, F(1, 2)) for _ in range(4)]
    broken[1] = gaussian(2, F(1, 3))
    h = permuted_matrix(broken, vertices, ordered)
    require(not supported(stein(h), starts), "unequal-q witness disappeared")
    shifts = [F(3, 2), F(5, 4), F(7, 5), F(9, 7)]
    shifted = [gaussian(2, F(1, 2), v) for v in shifts]
    hs = permuted_matrix(shifted, vertices, ordered)
    require(not supported(stein(hs), starts), "ungauged shifted witness disappeared")
    base = permuted_matrix([gaussian(2, F(1, 2))] * 4, vertices, ordered)
    weights = []
    for x in ordered:
        value = F(1)
        for v, exponent in zip(shifts, x):
            value *= v ** exponent
        weights.append(value)
    conjugated = [[weights[i] * base[i][j] / weights[j]
                   for j in range(len(base))] for i in range(len(base))]
    require(hs == conjugated, "paid diagonal-conjugation identity failed")
    wrong = [[base[i][j] * weights[j] / weights[i]
              for j in range(len(base))] for i in range(len(base))]
    require(wrong != hs, "reversed-gauge control did not detect failure")
    damaged = [row[:] for row in base]
    damaged[1][2] += F(1, 1 << 20)
    require(not supported(stein(damaged), starts), "unstructured perturbation accepted")
    must_reject(lambda: inverse([[F(1), F(1)], [F(1), F(1)]]),
                "singular inverse target accepted")
    must_reject(lambda: require(rank(stein(base)) <= 3, "forged rank bound"),
                "forged lower rank survived")
    return {"odd_dimension_fixed_point": odd_lengths,
            "nonpower_orbit_lengths": wrong_lengths,
            "negative_controls": 8, "paid_gauge_identity": "PASS"}


def main():
    cases = []
    for d in range(1, 7):
        ell = 1 << (d.bit_length() - 1)
        cases.append(check_case("cube-q1/2-d" + str(d),
                                [gaussian(2, F(1, 2))] * d, 2, ell,
                                (1 << d) // ell))
    for q in (F(2, 3), F(4, 5)):
        cases.append(check_case("cube-q" + str(q) + "-d4",
                                [gaussian(2, q)] * 4, 2, 4, 4))
    for d in (1, 2, 3):
        ell = 1 << (d.bit_length() - 1)
        cases.append(check_case("gaussian-n4-d" + str(d),
                                [gaussian(4, F(1, 2))] * d, 4, ell))
    cases.append(check_case("gaussian-n6-d2",
                            [gaussian(6, F(1, 3))] * 2, 6, 2))
    arbitrary = [[F(x) for x in row] for row in
                 ((7, 1, 2, 3), (4, 11, 5, 6), (6, 5, 11, 4), (3, 2, 1, 7))]
    cases.append(check_case("nonsymmetric-centrosymmetric-n4-d2",
                            [arbitrary] * 2, 4, 2))
    spectator = [[F(3), F(2)], [F(1), F(5)]]
    cases.append(check_case("noncentrosymmetric-spectator",
                            [gaussian(2, F(1, 2))] * 2 + [spectator], 2, 2))
    rounded = [[F(int(x * 16 + F(1, 2)), 16) for x in row]
               for row in gaussian(4, F(2, 3))]
    cases.append(check_case("centrosymmetric-four-bit-factor-rounding",
                            [rounded] * 2, 4, 2))
    _, ordered, starts, _ = guarded_order((2, 2, 2, 2), 2, 4)
    integer_order = [sum(bit << (3 - i) for i, bit in enumerate(x)) for x in ordered]
    require(integer_order == [0, 1, 3, 7, 15, 14, 12, 8, 2, 5, 11, 6, 13, 10, 4, 9],
            "documented d4 example changed")
    result = {"status": "PASS", "scope": "bounded exact controls; all-size proof in PROOF.md",
              "cases": cases, "case_count": len(cases),
              "target_count": 2 * len(cases),
              "literal_reconstructions": sum(x["literal_reconstructions"] for x in cases),
              "d4_example": {"order": integer_order, "starts": starts,
                             "forward_rank": 4, "inverse_rank": 4},
              "controls": controls(), "new_kappa": False}
    print(json.dumps(result, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
