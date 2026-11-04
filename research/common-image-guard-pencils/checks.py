"""Cross-check the general theorem, sign certificates and predecessor cases."""
from fractions import Fraction
from math import comb

from dependency import joint, minimal_forms, prefix_count
from finite import Field
from laws import (binary_independent, direction, independent_triple, marginal,
                  orbit_size, pattern, pencil, ratio_floor)
from windows import sign_window


def require(condition, message):
    if not condition:
        raise ValueError(message)


def independent(k):
    return [(1, *(int(j == i) for j in range(1, k))) for i in range(k)]


def fields_ok():
    for q in (2, 3, 4, 5, 7, 8, 9):
        f = Field(q)
        for x in range(q):
            for y in range(q):
                for z in range(q):
                    require(f.mul[x][f.add[y][z]] == f.add[f.mul[x][y]][f.mul[x][z]],
                            "field distributivity")
        for x in range(1, q):
            require(f.mul[x][f.inv[x]] == 1, "field inverse")
        if q in (4, 8, 9):
            a, b, c = {4: (2, 2, 3), 8: (2, 4, 3), 9: (3, 3, 2)}[q]
            require(f.mul[a][b] == c, "extension field polynomial")


def controls():
    """Short named anchors; also used on real source faults in private copies."""
    require(pencil(5, 5, 2) == Fraction(1, 6) and marginal(5, 2) == Fraction(7, 10),
            "five-direction anchor")
    require([480*pattern(5, 5, j, 2) for j in range(6)] == [80, 0, 0, 0, 64, 80],
            "five-direction mask spectrum")
    f = Field(3)
    fs = independent(3)
    require(independent_triple(3, 3) == joint(f, fs, 3) == Fraction(20, 117),
            "independent ternary triple")
    require(prefix_count(f, fs, 3) == orbit_size(3, 3, 3)*joint(f, fs, 3),
            "prefix rank and final coordinate")
    require(joint(f, [(1, 0), (1, 1), (1, 2)], 4) == pencil(3, 3, 4),
            "pencil support count")
    require(sign_window(4, 3) == dict(positive=[2, 60], ties=[]), "q4 triple boundary")
    fields_ok()


def formula_rows():
    checks = dict(pencils=0, binary=0, triples=0, patterns=0)
    for q in (2, 3, 4, 5, 7, 8, 9):
        f = Field(q)
        for k in range(2, q + 1):
            for m in (2, 3, 5, 8):
                forms = [(1, a) for a in range(k)]
                require(joint(f, forms, m) == pencil(q, k, m), "rank-two specialization")
                # Distinct subsets can have different literal coordinates.
                reverse = [(1, a) for a in range(q - 1, q - k - 1, -1)]
                require(joint(f, reverse, m) == pencil(q, k, m), "translated pencil")
                checks["pencils"] += 2
                cells = [pattern(q, k, j, m) for j in range(k + 1)]
                require(all(v >= 0 for v in cells) and sum(comb(k, j)*v
                        for j, v in enumerate(cells)) == 1, "pattern normalization")
                require(all((cells[j] > 0) == (k - j <= m - 1) for j in range(1, k + 1)),
                        "support of nonempty passing masks")
                checks["patterns"] += len(cells)
        for m in range(3, 9):
            require(joint(f, independent(3), m) == independent_triple(q, m),
                    "independent triple specialization")
            checks["triples"] += 1
    f = Field(2)
    for k in range(1, 7):
        for m in sorted({max(2, k), max(2, k + 1), 7, 10, 16}):
            if m >= k:
                require(joint(f, independent(k), m) == binary_independent(k, m),
                        "binary predecessor specialization")
                checks["binary"] += 1
    return checks


def prefix_rows():
    result = []
    for q in (2, 3, 4, 5, 8, 9):
        f = Field(q)
        families = [[(1, a) for a in range(min(q, 4))]]
        if q <= 4:
            families.append(independent(3))
            families.append([*independent(3), (1, 1, 1), independent(3)[0]])
        for forms in families:
            rank = len(minimal_forms(f, forms)[0])
            for m in sorted({max(2, rank), max(3, rank + 1), 6}):
                counted = prefix_count(f, forms, m)
                require(counted == orbit_size(q, rank, m)*joint(f, forms, m),
                        "raw prefix DP vs lattice")
                result.append(dict(q=q, m=m, forms=forms, rank=rank,
                                   passing_tuples=counted, orbit=orbit_size(q, rank, m)))
    return result


def sign_rows():
    q_values = (2, 3, 4, 5, 7, 8, 9, 11, 13, 16, 17, 19, 23, 25, 27, 29, 31)
    windows = {}
    comparisons = 0
    for q in q_values:
        for k in range(2, q + 1):
            w = sign_window(q, k)
            span = w["positive"]
            # An independent finite domain checks the infinite interval finder.
            for m in range(2, 82):
                positive = bool(span) and m >= span[0] and (span[1] is None or m <= span[1])
                expected = 1 if positive else (0 if m in w["ties"] else -1)
                require(direction(q, k, m) == expected, "sign window vs finite scan")
                comparisons += 1
            windows[f"{q},{k}"] = w
    certs = [(4, 3, 2), (4, 3, 60), (4, 3, 61), (4, 4, 2), (4, 4, 8),
             (4, 4, 9), (5, 5, 2), (5, 5, 3), (5, 5, 4), (5, 5, 5),
             (7, 7, 2), (7, 7, 3)]
    coeffs = [dict(q=q, k=k, m=m, floor_1e8_ratio=ratio_floor(q, k, m)) for q, k, m in certs]
    return dict(windows=windows, finite_comparisons=comparisons, boundary_certificates=coeffs)


def scientific_result():
    controls()
    a = independent_triple(4, 61)/marginal(4, 61)**3
    b = pencil(4, 3, 61)/marginal(4, 61)**3
    require(a > 1 > b, "same pair laws, opposite triple signs")
    return dict(five_direction_GL2_F5=[str(pencil(5, k, 2)) for k in range(1, 6)],
                opposite_triples_q4_m61=dict(independent_floor_1e8=a.numerator*10**8//a.denominator,
                                              pencil_floor_1e8=b.numerator*10**8//b.denominator),
                finite_formula_checks=formula_rows(), raw_prefix_cases=prefix_rows())
