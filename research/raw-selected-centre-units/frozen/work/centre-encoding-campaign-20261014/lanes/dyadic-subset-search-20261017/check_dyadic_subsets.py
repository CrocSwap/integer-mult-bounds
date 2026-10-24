"""Check fixed source subsets and their two unit conditions.

This check uses only exact arithmetic and the Python standard library.
It does not run an optimizer or a native local replay.
"""

from fractions import Fraction as F
from hashlib import sha256
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / "circuit-interface/INTERFACE.json"
PIN = "5c6c51fbffc07a683e922f17532fd90262ae9e23cc3560a696002073dd234ef3"
raw = SOURCE.read_bytes()
assert sha256(raw).hexdigest() == PIN
source = json.loads(raw)
vectors = [tuple(F(row.get(str(p), 0)) for row in source["R"]) for p in range(112)]
assert all(c.denominator == 1 and abs(c) <= 1 for v in vectors for c in v)
assert all(sum(c * c for c in v) == 4 for v in vectors)
assert set(sum(vectors[p][i] * vectors[q][i] for i in range(8))
           for p in range(112) for q in range(p)) == {F(-2), F(0), F(2)}


def identity(n):
    return [[F(i == j) for j in range(n)] for i in range(n)]


def transpose(a):
    return list(map(list, zip(*a)))


def product(a, b):
    return [[sum(a[i][k] * b[k][j] for k in range(len(b)))
             for j in range(len(b[0]))] for i in range(len(a))]


def difference(a, b):
    return [[x - y for x, y in zip(ar, br)] for ar, br in zip(a, b)]


def scale(a, c):
    return [[c * x for x in row] for row in a]


def inverse(a):
    n = len(a)
    out = [list(map(F, row)) + identity(n)[i] for i, row in enumerate(a)]
    for col in range(n):
        pivot = next(i for i in range(col, n) if out[i][col])
        out[col], out[pivot] = out[pivot], out[col]
        value = out[col][col]
        out[col] = [x / value for x in out[col]]
        for i in range(n):
            if i != col:
                value = out[i][col]
                out[i] = [x - value * y for x, y in zip(out[i], out[col])]
    assert [row[:n] for row in out] == identity(n)
    return [row[n:] for row in out]


def determinant(a):
    out = [list(map(F, row)) for row in a]
    value = F(1)
    for col in range(len(out)):
        pivots = [i for i in range(col, len(out)) if out[i][col]]
        if not pivots:
            return F(0)
        pivot = pivots[0]
        if pivot != col:
            out[col], out[pivot] = out[pivot], out[col]
            value = -value
        diagonal = out[col][col]
        value *= diagonal
        for i in range(col + 1, len(out)):
            factor = out[i][col] / diagonal
            out[i] = [x - factor * y for x, y in zip(out[i], out[col])]
    return value


def dyadic(c):
    return bool(c) and c.denominator & (c.denominator - 1) == 0


def power_two(c):
    return dyadic(c) and abs(c.numerator) & (abs(c.numerator) - 1) == 0


def serial(a):
    return [[str(c) for c in row] for row in a]


eye = identity(8)
zero = scale(eye, 0)
assert [[sum(v[i] * v[j] for v in vectors) for j in range(8)]
        for i in range(8)] == scale(eye, 56)
cases = [
    ("thirty_nine", [(0, 1), (0, 2)],
     [3, 7, 8, 9, 10, 15, 19, 21, 26, 30, 34, 38, 39, 40, 41, 45, 46,
      51, 53, 58, 61, 62, 65, 67, 68, 69, 77, 78, 79, 81, 84, 86, 94,
      96, 103, 104, 105, 106, 110]),
    ("thirty_eight", [(0, 2), (0, 3), (1, 4), (1, 5)],
     [1, 3, 4, 17, 18, 19, 20, 23, 24, 26, 27, 29, 35, 36, 38, 39,
      40, 42, 45, 60, 63, 66, 69, 74, 75, 77, 78, 84, 86, 88, 97, 99,
      104, 105, 107, 108, 109, 111]),
]
rows = []
for name, edges, selected in cases:
    assert selected == sorted(set(selected)) and all(0 <= p < 112 for p in selected)
    a = scale(eye, 0)
    for i, j in edges:
        assert i < j
        a[i][j] = 1
    assert product(a, a) == zero
    gram = [[sum(vectors[p][i] * vectors[p][j] for p in selected)
             for j in range(8)] for i in range(8)]
    lower = difference(eye, scale(a, F(-1, 4)))
    lower_inverse = difference(eye, scale(a, F(1, 4)))
    assert product(lower, lower_inverse) == eye
    n = difference(scale(eye, 52), gram)
    assert n == scale(product(lower, transpose(lower)), 32)
    assert determinant(n) == 2 ** 40
    t = scale(n, F(-1, 4))
    t_inverse = scale(product(transpose(lower_inverse), lower_inverse), F(-1, 8))
    assert product(t, t_inverse) == product(t_inverse, t) == eye
    assert determinant(t) == 2 ** 24 and inverse(t) == t_inverse
    response_numerator = difference(eye, scale(gram, F(1, 4)))
    response_inverse = inverse(response_numerator)
    assert all(not c or dyadic(c) for row in response_inverse for c in row)
    assert power_two(determinant(response_numerator))
    k = len(edges) // 2
    assert len(selected) == 40 - k
    assert determinant(difference(scale(eye, 4), gram)) == 2 ** (32 - 2 * k)
    assert determinant(response_numerator) == 2 ** (16 - 2 * k)
    rows.append({
        "name": name, "selected": selected, "selected_count": len(selected),
        "shear_edges": edges, "gram": serial(gram), "T_inverse": serial(t_inverse),
        "response_numerator_inverse": serial(response_inverse),
        "det_52I_minus_gram": str(determinant(n)), "det_T": str(determinant(t)),
        "det_4I_minus_gram": str(determinant(difference(scale(eye, 4), gram))),
        "both_unit_conditions": True,
    })

# The exact pair bound gives the lower-cardinality estimate in the proof.
assert 13 ** 6 * 7 * 8 > 2 ** 28
assert 12 ** 8 < 2 ** 29
lower_bounds = []
for s in range(8, 12):
    cap = F(s + 1, 2)
    lower = 13 ** 6 * (13 - cap) * (13 - s + cap)
    upper = (13 - F(s, 8)) ** 8
    assert 2 ** 28 < lower <= upper < 2 ** 29
    lower_bounds.append({"selected_count": s, "det_T_lower": str(lower),
                         "det_T_upper": str(upper)})

receipt = {
    "status": "PASS_EXACT_FIXED_SUBSETS_AND_TWO_UNIT_CONDITIONS",
    "source_sha256": PIN,
    "checker_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
    "cases": rows,
    "lower_cardinality_intervals": lower_bounds,
    "scope": {
        "minimum_proved": 12, "smallest_exhibited": 38,
        "global_minimum_known": False, "native_local_replay_run_here": False,
        "global_controller_or_complete_cost_proved_here": False,
    },
}
(HERE / "DYADIC-SUBSETS.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
print(receipt["status"])
