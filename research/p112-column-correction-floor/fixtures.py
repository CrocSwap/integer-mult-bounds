"""Exact Gaussian-rational full-decoder examples and scope controls. Apache-2.0.

Gareth Davidson with substantial OpenAI Codex assistance.
"""
from fractions import Fraction as F
from math import lcm

from common import digest, need
from geometry import cost, mask, rank


def q(value):
    return tuple(map(F, value)) if isinstance(value, tuple) else (F(value), F(0))


ZERO, ONE = q(0), q(1)


def plus(a, b):
    return a[0]+b[0], a[1]+b[1]


def times(a, b):
    return a[0]*b[0]-a[1]*b[1], a[0]*b[1]+a[1]*b[0]


def minus(a):
    return -a[0], -a[1]


def nonzero(a):
    return a != ZERO


def reciprocal(a):
    norm = a[0]**2+a[1]**2
    need(bool(norm), "singular Gaussian matrix")
    return a[0]/norm, -a[1]/norm


def dot(a, b):
    out = ZERO
    for v, w in zip(a, b):
        out = plus(out, times(v, w))
    return out


def inverse(matrix):
    need(len(matrix) == 3 and all(len(row) == 3 for row in matrix), "GL3 matrix shape")
    rows = [list(row)+[ONE if i == j else ZERO for j in range(3)]
            for i, row in enumerate(matrix)]
    for c in range(3):
        p = next((i for i in range(c, 3) if nonzero(rows[i][c])), None)
        need(p is not None, "singular Gaussian matrix")
        rows[c], rows[p] = rows[p], rows[c]
        scale = reciprocal(rows[c][c])
        rows[c] = [times(v, scale) for v in rows[c]]
        for i in range(3):
            if i != c:
                factor = rows[i][c]
                rows[i] = [plus(v, minus(times(factor, w))) for v, w in zip(rows[i], rows[c])]
    return [row[3:] for row in rows]


def integer_rows(rows):
    denominator = lcm(*(v.denominator for row in rows for z in row for v in z))
    return [[(int(z[0]*denominator), int(z[1]*denominator)) for z in row]
            for row in rows], denominator


def integer_dot(a, b):
    return (sum(v[0]*w[0]-v[1]*w[1] for v, w in zip(a, b)),
            sum(v[0]*w[1]+v[1]*w[0] for v, w in zip(a, b)))


def complex_rank(rows):
    pivots = {}
    for original in rows:
        row = list(original)
        for j, old in sorted(pivots.items()):
            if nonzero(row[j]):
                scale = row[j]
                row = [plus(a, minus(times(scale, b))) for a, b in zip(row, old)]
        pivot = next((j for j, z in enumerate(row) if nonzero(z)), None)
        if pivot is not None:
            scale = reciprocal(row[pivot])
            pivots[pivot] = [times(z, scale) for z in row]
        if len(pivots) == len(original):
            break
    return len(pivots)


def power_certificate(ranks):
    """Sufficient pointwise floors valid for every 0<q<=1, not sampled q."""
    need(len(ranks) == 3 and all(type(r) is int and 0 <= r <= 9 for r in ranks),
         "three integer COPY ranks")
    descending = sorted(ranks, reverse=True)
    if descending[1] >= 8:
        floor = [8, 8, 0]
        reason = "two rank-eight terms"
    elif descending[2] >= 6:
        floor = [6, 6, 6]
        reason = "three ranks at least six"
    else:
        need(all(a >= b for a, b in zip(descending, [6, 6, 4])),
             "complete COPY power bill lacks the proved lower envelope")
        floor = [6, 6, 4]
        reason = "two coordinate products plus charged free factor"
    # For the latter floors, r<=8 and (r/8)^q >= r/8 on 0<q<=1.
    need(sum(floor) >= 16 and max(floor) <= 8, "uniform power comparison")
    return {"sorted_lower_ranks": floor, "reason": reason,
            "q_domain": "0<q<=1", "replacement_floor": "2*8^q",
            "whole_floor": "8*8^q"}


def evaluate(model, pair, u, v, raw_matrix, *, transpose=False, fault=None):
    need(len(pair) == 2 and len(set(pair)) == 2 and all(type(k) is int and 0 <= k < 8 for k in pair),
         "two distinct original coordinates")
    need(len(u) == len(v) == 112, "112-entry correction vectors")
    U, V = [i for i, z in enumerate(u) if nonzero(z)], [i for i, z in enumerate(v) if nonzero(z)]
    need(len(V) == 1, "nonzero singleton correction column")
    b, x = model["pairing"], model["x"]
    need(all(not (b[i] >> V[0] & 1) for i in U), "free correction must vanish on every even entry")
    m = [[q(z) for z in row] for row in raw_matrix]
    back = inverse(m)
    normal_back = [[back[j][i] for j in range(3)] for i in range(3)]
    if fault == "ordinary_inverse":
        normal_back = back
    if fault == "conjugate_transpose":
        normal_back = [[(z[0], -z[1]) for z in row] for row in normal_back]
    d, t = [], []
    for i in range(112):
        left, right = [q(x[i][k]) for k in pair]+[u[i]], [q(x[i][k]) for k in pair]+[v[i]]
        d.append([dot(left, [m[k][j] for k in range(3)]) for j in range(3)])
        t.append([dot(right, [normal_back[k][j] for k in range(3)]) for j in range(3)])
    if transpose:
        d, t = t, d
        u, v = v, u
    other = [k for k in range(8) if k not in pair]
    full_d = [row+[q(x[i][k]) for k in other] for i, row in enumerate(d)]
    full_t = [row+[q(x[i][k]) for k in other] for i, row in enumerate(t)]
    di, den_d = integer_rows(full_d)
    ti, den_t = integer_rows(full_t)
    ui, den_u = integer_rows([[z] for z in u])
    vi, den_v = integer_rows([[z] for z in v])
    actual_entries = []
    for i in range(112):
        for j in range(112):
            actual = integer_dot(di[i], ti[j])
            uv = integer_dot(ui[i], vi[j])
            scalar = sum(a*c for a, c in zip(x[i], x[j]))
            expected = (scalar*den_u*den_v+uv[0], uv[1])
            need(all(a*den_u*den_v == e*den_d*den_t for a, e in zip(actual, expected)),
                 "complete all-pairs decoder identity with ordinary transpose")
            if b[i] >> j & 1:
                need(uv == (0, 0), "masked even-entry identity")
            actual_entries.append(actual)
    left = [mask(i for i in range(112) if nonzero(d[i][k])) for k in range(3)]
    right = [mask(i for i in range(112) if nonzero(t[i][k])) for k in range(3)]
    ranks = [cost(b, s, t_) for s, t_ in zip(left, right)]
    # This check concerns the coefficient identity, irrespective of cancellation
    # in the physical support vectors and including u=0.
    for a in range(2):
        for c in range(2):
            need(dot(m[a], [back[j][c] for j in range(3)]) == (ONE if a == c else ZERO),
                 "rank-two projected product identity")
    a_active = [any(nonzero(m[k][j]) for k in range(2)) for j in range(3)]
    b_active = [any(nonzero(back[j][k]) for k in range(2)) for j in range(3)]
    need(sum(a and c for a, c in zip(a_active, b_active)) >= 2, "at least two projected products")
    if len(U) <= 23:
        proof_branch = "small support: preserve both original spans"
        lower = [8 if a and c else 0 for a, c in zip(a_active, b_active)]
    elif not all(b_active):
        h = b_active.index(False)
        need(all(m[2][k] == ZERO for k in range(3) if k != h),
             "pure singleton factor forces two unmodified left combinations")
        proof_branch = "pure singleton-side factor: coupled inverse protects the other two"
        lower = [0 if k == h else 8 for k in range(3)]
    elif all(a_active):
        proof_branch = "three active products: all survivor ranks apply"
        lower = [6, 6, 6]
    else:
        h = a_active.index(False)
        need(rank(model["labels"][i] for i in U) >= 5, "large pure-factor label span")
        proof_branch = "pure nonsingleton-side factor: retain its rank-four charge"
        lower = [4 if k == h else 6 for k in range(3)]
    need(all(r >= minimum for r, minimum in zip(ranks, lower)), "quantified proof branch on fixture")
    return {"pair": list(pair), "orientation": "row" if transpose else "column",
            "correction_support_sizes": [len(U), len(V)][::-1] if transpose else [len(U), len(V)],
            "replacement_ranks": ranks, "whole_COPY_rank_sum": 48+sum(ranks),
            "at_least_two_rank_eight": sum(r >= 8 for r in ranks) >= 2,
            "left_original_projection_active": b_active if transpose else a_active,
            "right_original_projection_active": a_active if transpose else b_active,
            "nonsingleton_side_label_span": rank(model["labels"][i] for i in U),
            "proof_branch_in_column_orientation": proof_branch,
            "proof_branch_lower_ranks": lower,
            "full_factor_ranks": [complex_rank(full_d), complex_rank(full_t)],
            "power_certificate": power_certificate(ranks),
            "full_entries_checked": 112**2,
            "left_supports": [hex(s) for s in left], "right_supports": [hex(s) for s in right],
            "matrix_sha256": digest([[list(z) for z in row] for row in di]),
            "reader_sha256": digest([[list(z) for z in row] for row in ti]),
            "matrix_denominators": [den_d, den_t],
            "complete_product_sha256": digest([list(z) for z in actual_entries])}


def examples(model, boundary):
    x, b = model["x"], model["pairing"]
    eye = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
    dense = [[1, 1, 1], [1, 2, 1], [1, 1, 2]]
    complex_m = [[1, (1, 1), 1], [1, (2, 1), 1], [(0, 1), (1, 2), (1, 1)]]
    shear = [[1, 0, 0], [0, 1, 0], [-1, 0, 1]]
    pure_right = [[1, 0, -1], [0, 1, 1], [0, 0, 1]]
    cases = []

    def vector(indices, mode="complex"):
        result = [ZERO]*112
        for h, i in enumerate(indices):
            result[i] = q(x[i][0] if mode == "boundary" else ((h % 3)+1, (h % 5)-2))
        return result

    def add_case(name, pair, indices, m, site=0, mode="complex", transpose=False):
        u = vector(indices, mode)
        v = [ZERO]*112
        v[site] = q(1 if mode == "boundary" else (2, -1))
        report = evaluate(model, pair, u, v, m, transpose=transpose)
        report["name"] = name
        cases.append(report)

    U = boundary["deleted"]
    odd = [i for i in range(112) if not b[i] & 1]
    add_case("24-row-identity-sharp", [0, 1], U, eye, mode="boundary")
    add_case("24-row-rank-eight-premise-fails", [0, 1], U, shear, mode="boundary")
    add_case("24-row-transposed-boundary", [0, 1], U, shear, mode="boundary", transpose=True)
    add_case("24-row-arbitrary-complex-amplitudes", [0, 1], U, dense)
    add_case("52-row-identity-sharp", [0, 1], odd, eye)
    add_case("52-row-all-three-products", [0, 1], odd, dense)
    add_case("52-row-pure-free-left-factor", [0, 1], odd, shear)
    add_case("52-row-pure-singleton-right-factor", [0, 1], odd, pure_right)
    add_case("nonreal-factor-basis", [0, 1], odd, complex_m)
    add_case("23-row-credited-regime", [0, 1], odd[:23], dense)
    add_case("one-row-low-span-factor", [0, 1], odd[:1], shear)
    add_case("zero-left-correction", [0, 1], [], complex_m)
    other_site = 111
    other_odd = [i for i in range(112) if not (b[i] >> other_site & 1)]
    add_case("other-pair-and-site", [4, 6], other_odd, complex_m, site=other_site)
    need(cases[0]["replacement_ranks"] == [8, 8, 0], "sharp original boundary basis")
    need(cases[1]["replacement_ranks"] == [7, 8, 7] and not cases[1]["at_least_two_rank_eight"],
         "24-row counterexample to extending the old per-child premise")
    need(cases[4]["replacement_ranks"] == [8, 8, 0], "sharp maximal column support")
    return cases
