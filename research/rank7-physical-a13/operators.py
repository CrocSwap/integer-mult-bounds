# SPDX-License-Identifier: Apache-2.0
"""Exact sparse Gaussian operators at the forward native A13 boundary."""

import hashlib
import json
from fractions import Fraction as Q

H = 9
N = 1 << H
ZERO = (Q(0), Q(0))
UNITS = ((Q(1), Q(0)), (Q(0), Q(1)), (Q(-1), Q(0)), (Q(0), Q(-1)))


def need(condition, message):
    if not condition:
        raise ValueError(message)


def digest(value):
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def mul(a, b):
    return a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0]


def apply(matrix, vector):
    need(len(matrix) == N and len(vector) == N, "operator dimension")
    out = [ZERO] * N
    for column, value in zip(matrix, vector, strict=True):
        need(len(column) <= N, "bounded column")
        for j, coefficient in column.items():
            a, b = mul(coefficient, value)
            out[j] = out[j][0] + a, out[j][1] + b
    return out


def product(left, right):
    need(len(left) == len(right) == N, "product dimension")
    columns = []
    for column in right:
        out = {}
        need(len(column) <= N, "bounded right column")
        for k, value in column.items():
            for j, coefficient in left[k].items():
                a, b = mul(coefficient, value)
                old = out.get(j, ZERO)
                out[j] = old[0] + a, old[1] + b
        columns.append({j: value for j, value in out.items() if value != ZERO})
    return tuple(columns)


def linear(columns, value):
    result = 0
    for i, column in enumerate(columns):
        if value >> i & 1:
            result ^= column
    return result


def monomial(columns):
    need(len(columns) == H and all(0 <= x < N for x in columns), "binary map")
    permutation = [linear(columns, x) for x in range(N)]
    need(len(set(permutation)) == N, "invertible binary map")
    inverse = [0] * N
    for x, y in enumerate(permutation):
        inverse[y] = x
    inverse_columns = [inverse[1 << i] for i in range(H)]
    form = [
        [int(i == j) ^ ((a & b).bit_count() & 1) for j, b in enumerate(inverse_columns)]
        for i, a in enumerate(inverse_columns)
    ]
    result = []
    for y in permutation:
        phase = sum(form[i][i] for i in range(H) if y >> i & 1)
        phase += 2 * sum(
            form[i][j]
            for i in range(H)
            for j in range(i + 1, H)
            if y >> i & 1 and y >> j & 1
        )
        result.append({y: UNITS[phase % 4]})
    return tuple(result)


def adjoint_monomial(matrix):
    inverse = [{} for _ in range(N)]
    for x, column in enumerate(matrix):
        need(len(column) == 1, "monomial column")
        y, (a, b) = next(iter(column.items()))
        need(a * a + b * b == 1 and not inverse[y], "unit monomial bijection")
        inverse[y][x] = a, -b
    return tuple(inverse)


def adjoint(matrix):
    need(len(matrix) == N, "adjoint dimension")
    result = [{} for _ in range(N)]
    for x, column in enumerate(matrix):
        need(len(column) <= N, "bounded adjoint column")
        for y, (a, b) in column.items():
            result[y][x] = a, -b
    return tuple(result)


def closed_source(g, target, source):
    entry = product(rank_one_frame(382), cgate(382, -1))
    warp = product(target, product(monomial(g), adjoint(rank_one_frame(382))))
    adjoint_monomial(warp)
    result = product(adjoint(warp), source)
    need(result == entry, "physical closing warp restores pre-warp source")
    return result


def cgate(q, sign=1):
    need(type(q) is int and 0 < q < N and sign in (-1, 1), "coordinate Fourier")
    return tuple(
        {x: (Q(1, 2), Q(sign, 2)), x ^ q: (Q(1, 2), Q(-sign, 2))} for x in range(N)
    )


def rank_one_frame(q):
    need(type(q) is int and 0 < q < N, "rank-one frame")
    columns, span = [q], {0, q}
    for i in range(H):
        if 1 << i not in span:
            columns.append(1 << i)
            span |= {x ^ (1 << i) for x in tuple(span)}
    need(len(columns) == H, "complete frame basis")
    k = monomial(columns)
    return product(k, product(cgate(1), adjoint_monomial(k)))


def signature(matrix):
    return [
        [[j, str(a), str(b)] for j, (a, b) in sorted(column.items())]
        for column in matrix
    ]


def scalar_pullback(events, target):
    """Exact row of a zero-frame slice; reject any live non-scalar action."""
    need(len(events) <= 12_000, "bounded preparation")
    row = {target: Q(1)}
    for event in reversed(events):
        need(type(event) is list and 2 <= len(event) <= 8, "preparation event")
        kind, destination = event[:2]
        weight = row.get(destination, Q(0))
        if not weight:
            continue
        need(kind in ("add", "scale") and event[-1] == 0, "live zero-frame scalar")
        if kind == "scale":
            row[destination] *= Q(event[2], event[3])
        else:
            source, a, b = event[2:5]
            need(source != destination, "distinct preparation roles")
            row[source] = row.get(source, Q(0)) + weight * Q(a, b)
        row = {r: q for r, q in row.items() if q}
        need(len(row) <= 632, "bounded preparation row")
    return row


def boundary(canonical):
    need(canonical["h"] == H and canonical["v"] == 112, "native dimension")
    a = canonical["A"]
    need(a[12] == ["warp", 83, 52, 85, 136], "literal preceding warp")
    need(a[13] == ["add", 126, 83, -1, 2, 136], "literal A13")
    frames = canonical["frames"]
    need(frames[0] == [] and frames[85] == [382] and frames[136] == [45], "frames")
    need(canonical["start"][83] == 85 and canonical["start"][126] == 0, "entry frames")
    need(canonical["ports"][83] == 382, "old source port")
    prefix = canonical["precondition"] + canonical["compensation"] + a[:12]
    source = scalar_pullback(prefix, 83)
    target = scalar_pullback(prefix, 126)
    need(source == {83: Q(1)}, "untouched source before adapters")
    need(
        target == {126: Q(1, 2), 127: Q(-1, 2), 164: Q(1, 2), 165: Q(-1, 2)},
        "prepared target",
    )
    need(all(canonical["start"][r] == 0 for r in target), "preparation input frames")
    warp = next(w for w in canonical["warps"] if w["op"] == 52)
    g = warp["G_columns"]
    need(linear(g, 382) == 45, "warp carries source frame")
    t = rank_one_frame(45)
    # Source adapter and warp telescope: T45 K52 T382^-1 T382 C382^-1.
    m = product(t, product(monomial(g), cgate(382, -1)))
    adjoint_monomial(m)  # Check actual unit entries and bijection, not only rank.
    return target, g, t, m


def group(canonical):
    preparation, g, target, source = boundary(canonical)
    roles = (126, 153, 164, 218)
    expected = (
        {126: Q(1, 2), 127: Q(-1, 2), 164: Q(1, 2), 165: Q(-1, 2)},
        {153: Q(1, 2), 154: Q(-1, 2), 218: Q(1, 2), 217: Q(-1, 2)},
        {164: Q(-1, 2), 217: Q(1, 2), 126: Q(1, 2), 154: Q(-1, 2)},
        {218: Q(-1, 2), 165: Q(1, 2), 153: Q(1, 2), 127: Q(-1, 2)},
    )
    prefix = canonical["precondition"] + canonical["compensation"] + canonical["A"][:12]
    rows = {}
    for i, (role, row) in enumerate(zip(roles, expected, strict=True)):
        need(
            canonical["A"][13 + i] == ["add", role, 83, -1, 2, 136],
            "literal four-ADD group",
        )
        need(canonical["start"][role] == 0, "target starts unframed")
        need(scalar_pullback(prefix, role) == row, "literal prepared group row")
        need(all(canonical["start"][r] == 0 for r in row), "zero-frame input support")
        rows[role] = row
    need(canonical["A"][17] == ["warp", 83, -52, 136, 85], "closing source warp")
    need(rows[126] == preparation, "A13 included in group")
    return rows, g, target, source


def real_rows(preparation, target, source):
    rows = [[] for _ in range(2 * N)]
    for role, weight in sorted(preparation.items()):
        for x, column in enumerate(target):
            for y, (a, b) in column.items():
                for component, coefficients in enumerate(((a, -b), (b, a))):
                    rows[2 * y + component].extend(
                        (role, x, c, weight * q)
                        for c, q in enumerate(coefficients)
                        if q
                    )
    for x, column in enumerate(source):
        for y, (a, b) in column.items():
            for component, coefficients in enumerate(((a, -b), (b, a))):
                rows[2 * y + component].extend(
                    (83, x, c, -q / 2) for c, q in enumerate(coefficients) if q
                )
    need(
        all(len({term[:3] for term in row}) == len(row) for row in rows),
        "distinct real input variables",
    )
    need(all(len(row) == 17 for row in rows), "sixteen quarter terms and one half term")
    need(
        all(sum(abs(t[3]) for t in row) == Q(9, 2) for row in rows), "physical row norm"
    )
    need(
        all(all((4 * t[3]).denominator == 1 for t in row) for row in rows),
        "quarter grid",
    )
    return rows
