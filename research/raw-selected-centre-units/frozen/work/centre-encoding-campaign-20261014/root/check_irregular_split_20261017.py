"""Check the 38-port split from the pinned supplier matrix."""

from fractions import Fraction as F
from hashlib import sha256
from pathlib import Path
import json


HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / "lanes/new-core-transfer-20261017/INTERFACE.json"
SOURCE_PIN = "c6ca09711622ce4ad236f78cc28c03b6c46808a9d91cfc1722ff4fe371f38746"
SELECTED = [
    1, 3, 4, 17, 18, 19, 20, 23, 24, 26, 27, 29, 35, 36, 38, 39, 40,
    42, 45, 60, 63, 66, 69, 74, 75, 77, 78, 84, 86, 88, 97, 99,
    104, 105, 107, 108, 109, 111,
]


def need(ok, message):
    if not ok:
        raise RuntimeError(message)


def identity(n):
    return [[F(i == j) for j in range(n)] for i in range(n)]


def mv(matrix, vector):
    return [sum(a * x for a, x in zip(row, vector)) for row in matrix]


def inverse_and_det(matrix):
    n = len(matrix)
    rows = [list(row) + unit for row, unit in zip(matrix, identity(n))]
    determinant = F(1)
    for j in range(n):
        pivot = next((i for i in range(j, n) if rows[i][j]), None)
        need(pivot is not None, "The centre matrix must be invertible")
        if pivot != j:
            rows[j], rows[pivot] = rows[pivot], rows[j]
            determinant *= -1
        value = rows[j][j]
        determinant *= value
        rows[j] = [x / value for x in rows[j]]
        for i in range(n):
            if i != j and rows[i][j]:
                value = rows[i][j]
                rows[i] = [x - value * y for x, y in zip(rows[i], rows[j])]
    need([row[:n] for row in rows] == identity(n), "Exact elimination")
    return [row[n:] for row in rows], determinant


def dyadic(value):
    d = value.denominator
    return d & (d - 1) == 0


raw = SOURCE.read_bytes()
need(sha256(raw).hexdigest() == SOURCE_PIN, "Supplier matrix pin")
source = json.loads(raw)
R = [[F(row.get(str(p), 0)) for p in range(112)] for row in source["R"]]
K = [[R[i][p] / 4 for i in range(8)] for p in range(112)]
need(len(SELECTED) == len(set(SELECTED)) == 38, "Thirty-eight distinct ports")
selected_set = set(SELECTED)
ordinary = [p for p in range(112) if p not in selected_set]
need(all(sum(R[i][p] * K[p][j] for p in range(112)) == 14 * (i == j)
         for i in range(8) for j in range(8)), "Actual full centre Gram")
G = [[sum(R[i][p] * R[j][p] for p in SELECTED)
      for j in range(8)] for i in range(8)]
L = identity(8)
for i, j in [(0, 2), (0, 3), (1, 4), (1, 5)]:
    L[i][j] = F(1, 4)
need(all(52 * (i == j) - G[i][j]
         == 32 * sum(L[i][k] * L[j][k] for k in range(8))
         for i in range(8) for j in range(8)), "Explicit unipotent factor")
D = [[x / 4 for x in row] for row in G]
T = [[D[i][j] - 13 * (i == j) for j in range(8)] for i in range(8)]
W = [[(i == j) - D[i][j] for j in range(8)] for i in range(8)]
Ti, det_T = inverse_and_det(T)
Wi, det_W = inverse_and_det(W)
need(det_T == 2**24 and det_W == 2**12, "Both exact unit determinants")
need(all(dyadic(x) for matrix in (Ti, Wi) for row in matrix for x in row),
     "Both centre inverses are dyadic")


def e(vector):
    return [-x if p in selected_set else x for p, x in enumerate(vector)]


def response(vector):
    code = mv(Ti, mv(R, vector))
    return [x + y for x, y in zip(e(vector), mv(K, code))]


def response_inverse(vector):
    signed = e(vector)
    correction = e(mv(K, mv(Wi, mv(R, signed))))
    return [x - y for x, y in zip(signed, correction)]


def ordinary_map(vector, invert=False):
    query = [sum(R[i][p] * vector[p] for p in ordinary) for i in range(8)]
    query = mv(Ti, query) if invert else [-x for x in query]
    out = list(vector)
    for p in ordinary:
        out[p] += sum(K[p][i] * query[i] for i in range(8))
    return out


for basis in identity(112):
    need(response_inverse(response(basis)) == basis, "A inverse after A")
    need(response(response_inverse(basis)) == basis, "A after A inverse")
    need(ordinary_map(ordinary_map(basis), True) == basis, "H inverse after H")
    need(ordinary_map(ordinary_map(basis, True)) == basis, "H after H inverse")

controls = {}
wrong_T = [[D[i][j] - 12 * (i == j) for j in range(8)] for i in range(8)]
wrong_Ti, _ = inverse_and_det(wrong_T)


def wrong_ordinary_inverse(vector):
    query = [sum(R[i][p] * vector[p] for p in ordinary) for i in range(8)]
    query = mv(wrong_Ti, query)
    out = list(vector)
    for p in ordinary:
        out[p] += sum(K[p][i] * query[i] for i in range(8))
    return out


controls["wrong_centre_constant"] = any(
    ordinary_map(wrong_ordinary_inverse(x)) != x for x in identity(112))
wrong_response = lambda x: [a + b for a, b in zip(x, mv(K, mv(Ti, mv(R, x))))]
controls["omit_selected_sign"] = any(response_inverse(wrong_response(x)) != x
                                      for x in identity(112))
controls["omit_inverse_outer_signs"] = any(
    [a - b for a, b in zip(e(response(x)), mv(K, mv(Wi, mv(R, response(x)))))] != x
    for x in identity(112))
need(all(controls.values()), "Mutation controls")

receipt = {
    "status": "PASS_ROOT_IRREGULAR_38_PORT_UNIT",
    "source_sha256": SOURCE_PIN,
    "checker_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
    "selected": SELECTED,
    "ordinary_count": len(ordinary),
    "gram": [[int(x) for x in row] for row in G],
    "det_T": str(det_T),
    "det_I_minus_D": str(det_W),
    "det_response": str(det_W / det_T),
    "T_inverse": [[str(x) for x in row] for row in Ti],
    "I_minus_D_inverse": [[str(x) for x in row] for row in Wi],
    "basis_columns_per_inverse_order": 112,
    "mutation_controls": controls,
    "scope": "Exact scalar algebra; no native emission, owner, decoder, or supplier claim",
}
(HERE / "IRREGULAR-SPLIT-20261017.json").write_text(
    json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
print(receipt["status"])
