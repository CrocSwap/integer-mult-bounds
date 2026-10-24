#!/usr/bin/env python3
"""Check the reciprocal response with a separate column method."""

from fractions import Fraction as F
from hashlib import sha256
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
CAMPAIGN = HERE.parents[2]
PINS = {
    "root/RECIPROCAL-RANK-TWO-20261020.md":
        "5d7855b2360093629530aceb91d38204a9a0a42654f53a150f35279efc8de172",
    "root/check_reciprocal_rank_two_20261020.py":
        "2fc272bf47b7840f5464b1f589f16d069e66b6cd41c8d2fce03f9f04878635bc",
    "root/RECIPROCAL-RANK-TWO-20261020.json":
        "971df2cc46160babf79b668c5677ab03e48ae86551d727db05c6f4118fc6658e",
    "root/RECIPROCAL-RANK-TWO-FREEZE-20261020.json":
        "4cc076c7b551ee2f4259de10ef3cd0e00fa395882b4175f12af948f7eefb5b75",
    "root/RECIPROCAL-RANK-TWO-ADDENDUM-20261020.md":
        "7c7bf50e6f61af68ecda8a4c0cc4d6ba0cbf9a89aec9ccbeedc3eec794da486d",
    "lanes/independent-review-20261017/cyclic-pair-flags-20261018/CYCLIC-FLAGS.json":
        "3034e1df3670f64e5b79a51a435d7903f3be7cef10d6b486a8bd4d420c989585",
}


def need(ok, reason):
    if not ok:
        raise ValueError(reason)


def rank(rows):
    rows = [list(map(F, row)) for row in rows]
    k = 0
    for j in range(len(rows[0])):
        p = next((i for i in range(k, len(rows)) if rows[i][j]), None)
        if p is None:
            continue
        rows[k], rows[p] = rows[p], rows[k]
        lead = rows[k][j]
        rows[k] = [x / lead for x in rows[k]]
        for i in range(k + 1, len(rows)):
            lead = rows[i][j]
            rows[i] = [x - lead * y for x, y in zip(rows[i], rows[k])]
        k += 1
        if k == len(rows):
            break
    return k


def bitrank(values):
    basis = {}
    for x in values:
        while x:
            k = x.bit_length()
            if k not in basis:
                basis[k] = x
                break
            x ^= basis[k]
    return len(basis)


def determinant(rows):
    a = [list(map(F, r)) for r in rows]
    answer = F(1)
    for k in range(len(a)):
        p = next((i for i in range(k, len(a)) if a[i][k]), None)
        if p is None:
            return F(0)
        if p != k:
            a[p], a[k] = a[k], a[p]
            answer = -answer
        d = a[k][k]
        answer *= d
        for i in range(k + 1, len(a)):
            c = a[i][k] / d
            a[i] = [x - c * y for x, y in zip(a[i], a[k])]
    return answer


def unit(n, j):
    return [F(i == j) for i in range(n)]


def reflect(x, wrong=False):
    m = len(x) - 2
    value = x[m] - sum(x[:m])
    u = [1] * m + [m - 2 + int(wrong), 0]
    return [a + b * value for a, b in zip(x, u)]


def swap(x):
    return list(x[:-2]) + [x[-1], x[-2]]


def act(x, inverse=False):
    return reflect(swap(x)) if inverse else swap(reflect(x))


def correction_rank(columns):
    n = len(columns)
    return rank([[columns[j][i] - (i == j) for j in range(n)]
                 for i in range(n)])


def quad_add(x, y):
    return x[0] + y[0], x[1] + y[1]


def quad_mul(x, y):
    return x[0] * y[0] + 3 * x[1] * y[1], x[0] * y[1] + x[1] * y[0]


def main():
    for name, expected in PINS.items():
        need(sha256((CAMPAIGN / name).read_bytes()).hexdigest() == expected,
             "Source pin: " + name)
    source = json.loads((CAMPAIGN / next(p for p in PINS if p.endswith("CYCLIC-FLAGS.json"))).read_text())
    producer = json.loads((CAMPAIGN / "root/RECIPROCAL-RANK-TWO-20261020.json").read_text())
    dimensions = []
    for n in range(3, 33):
        e = [act(unit(n, j)) for j in range(n)]
        inverse = [act(unit(n, j), True) for j in range(n)]
        for j in range(n):
            need(act(e[j], True) == act(inverse[j]) == unit(n, j), "Two inverse orders")
            need(e[j][j] == inverse[j][j] == 0, "Two zero diagonals")
            need(reflect(reflect(unit(n, j))) == unit(n, j), "Reflection square")
        need(correction_rank(e) == correction_rank(inverse) == 2, "Two correction ranks")
        need(determinant(e) == determinant(inverse) == 1, "Integer unit")
        for j in range(n - 2):
            x = unit(n - 2, j) + [F(1), F(1)]
            need(act(x) == x, "Fixed basis")
        dimensions.append(n)
    # The n=2 exchange is the excluded rank-one example.
    need(correction_rank([unit(2, 1), unit(2, 0)]) == 1, "Dimension hypothesis")
    need(any(swap(reflect(swap(reflect(unit(6, j))))) != unit(6, j)
             for j in range(6)), "Reject E in place of its inverse")
    need(any(reflect(reflect(unit(6, j), True), True) != unit(6, j)
             for j in range(6)), "Reject changed reflection coefficient")

    def balanced(x, inverse=False):
        d = [1, 1, 1, 1, -2, 2]
        return [y / t for y, t in zip(act([t * y for t, y in zip(d, x)], inverse), d)]

    def tariff(columns):
        return sum(2 * (1 + abs(x.numerator).bit_length() +
                        abs(x.numerator).bit_count() + x.denominator.bit_length())
                   for col in columns for x in col if x)

    balanced_counts = []
    for inverse in [False, True]:
        original = [act(unit(6, j), inverse) for j in range(6)]
        adjusted = [balanced(unit(6, j), inverse) for j in range(6)]
        for j in range(6):
            x = unit(6, j)
            a, b, c = x[:4], x[4], x[5]
            s = sum(a)
            formula = ([v - s + 2 * c for v in a] + [s - 3 * c, -b]
                       if inverse else [v - s - 2 * b for v in a] + [-c, -s - 3 * b])
            need(adjusted[j] == formula, "Balanced displayed formula")
            need(balanced(adjusted[j], not inverse) == x, "Balanced inverse order")
        norms = [max(sum(abs(col[i]) for col in cs) for i in range(6))
                 for cs in [original, adjusted]]
        need(norms == [11, 7], "Original and balanced row norms")
        need(tariff(original) == tariff(adjusted) == 188, "Equal transfer tariff")
        need(correction_rank(adjusted) == 2, "Balanced correction rank")
        need(all(original[j][i] == adjusted[j][i] for i in range(4) for j in range(4)),
             "The a-to-a minor is unchanged")
        balanced_counts.append({"inverse": inverse, "row_norms": [11, 7], "transfer_tariff": 188})

    ports = source["affected_ports"]
    carriers = source["cyclic_carriers"]
    need(len(carriers) == 8 and all(len(c) == 6 for c in carriers), "Eight six-mode blocks")
    need(sorted(p for c in carriers for p in c) == ports, "Mode partition")
    need(sorted(p for pair in source["pair_codes"] for p in pair["ports"]) == ports,
         "Pair partition")

    def pair_code(x, inverse=False):
        answer = {}
        for pair in source["pair_codes"]:
            ps, h = pair["ports"], pair["matrix"]
            for i, p in enumerate(ps):
                answer[p] = sum(F(h[j][i], 2) * x[ps[j]] if inverse
                                else F(h[i][j]) * x[ps[j]] for j in range(2))
        return answer

    def physical(x, inverse=False, omit_undo=False):
        coded = pair_code(x)
        mixed = {}
        for c in carriers:
            mixed.update(zip(c, act([coded[p] for p in c], inverse)))
        return mixed if omit_undo else pair_code(mixed, True)

    columns = []
    inverse_columns = []
    for j, p in enumerate(ports):
        x = {q: F(p == q) for q in ports}
        need(pair_code(pair_code(x), True) == x, "Actual pair inverse")
        y, z = physical(x), physical(x, True)
        need(physical(y, True) == physical(z) == x, "Physical inverse orders")
        columns.append([y[q] for q in ports])
        inverse_columns.append([z[q] for q in ports])
        need([y[q] for q in ports] == [F(row[j]) for row in producer["physical_response"]],
             "Independent physical response column")
        need([z[q] for q in ports] == [F(row[j]) for row in producer["physical_inverse"]],
             "Independent physical inverse column")
    need(correction_rank(columns) == correction_rank(inverse_columns) == 16,
         "Physical correction ranks")
    need(determinant(columns) == determinant(inverse_columns) == 1, "Physical determinants")
    need(all(columns[j][j] == inverse_columns[j][j] == 0 for j in range(48)),
         "Physical zero diagonals")
    need(any(physical({p: F(p == q) for p in ports}, omit_undo=True) !=
             physical({p: F(p == q) for p in ports}) for q in ports),
         "Reject omitted pair undo")
    need(columns != [list(row) for row in zip(*columns)], "Response is asymmetric")
    need(inverse_columns != [list(row) for row in zip(*inverse_columns)],
         "Backward inverse needs a transpose in the generator")

    query_geometry = []
    for v, c in enumerate(carriers):
        qs = [source["ports"][p] for p in c]
        z = source["common_line"]
        need(all((a & b).bit_count() % 2 == (i == j)
                 for i, a in enumerate(qs) for j, b in enumerate(qs)),
             "Orthonormal mode representatives")
        ranks = [bitrank([z] + qs[:5]), bitrank([z] + qs[4:]), bitrank([z] + qs)]
        need(ranks == [6, 3, 7], "First, second, and combined query planes")
        query_geometry.append({"vertex": v, "query_supports": [5, 2], "union_support": 6,
                               "plane_dimensions": ranks})

    # A real symmetric example shows why rational entries are a material premise.
    signs = [1, 1, 1, -1, -1, -1]
    a = [[(F(i == j) - F(1 + signs[i] * signs[j], 2),
           F(1 - signs[i] * signs[j], 6)) for j in range(6)] for i in range(6)]
    b = [[(x, -y) for x, y in row] for row in a]
    for x, y in [(a, b), (b, a)]:
        for i in range(6):
            for j in range(6):
                entry = (F(0), F(0))
                for k in range(6):
                    entry = quad_add(entry, quad_mul(x[i][k], y[k][j]))
                need(entry == (F(i == j), F(0)), "Quadratic-field inverse")
    need(all(a[i][i] == b[i][i] == (0, 0) for i in range(6)), "Real example diagonals")
    need(any(y for row in a for _, y in row), "The real example is not rational")
    need(all((n - 3) ** 2 < n * (n - 4) < (n - 2) ** 2 for n in range(5, 101)),
         "Discriminant inequalities corroboration")
    receipt = {
        "status": "PASS_INDEPENDENT_RECIPROCAL_RANK_TWO",
        "source_pins": PINS,
        "dimensions_checked": dimensions,
        "physical_columns_per_direction": 48,
        "physical_correction_ranks": [16, 16],
        "physical_determinants": ["1", "1"],
        "balanced_response": balanced_counts,
        "query_geometry": query_geometry,
        "negative_controls": ["wrong reflection coefficient", "E as its inverse",
                              "omitted pair undo", "inverse without transpose",
                              "n=2 rank-one exception", "real nonrational symmetric example"],
        "scope": "Exact response algebra and actual pair binding. No native or terminal price.",
    }
    raw = (json.dumps(receipt, indent=2, sort_keys=True) + "\n").encode()
    (HERE / "CHECKS.json").write_bytes(raw)
    print(receipt["status"])
    print("receipt_sha256=" + sha256(raw).hexdigest())


if __name__ == "__main__":
    main()
