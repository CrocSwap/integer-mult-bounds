"""Exact rank-one-residue lift census; Python 3.12 standard library only."""

from __future__ import annotations

import hashlib
import itertools
import json
from dataclasses import dataclass
from pathlib import Path

Matrix = tuple[int, int, int, int]
Vector = tuple[int, int]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def field_tables(q: int) -> tuple[list[list[int]], list[list[int]]]:
    require(q in (2, 3, 4), "unsupported field")
    add = [[(a ^ b) if q == 4 else (a + b) % q for b in range(q)]
           for a in range(q)]
    mul = [[0] * q for _ in range(q)]
    for a, b in itertools.product(range(q), repeat=2):
        if q == 4:
            a0, a1, b0, b1 = a & 1, a >> 1, b & 1, b >> 1
            mul[a][b] = ((a0 * b0) ^ (a1 * b1)) | (
                ((a0 * b1) ^ (a1 * b0) ^ (a1 * b1)) << 1)
        else:
            mul[a][b] = a * b % q
    for a, b, c in itertools.product(range(q), repeat=3):
        require(mul[a][add[b][c]] == add[mul[a][b]][mul[a][c]],
                "field distributivity")
        require(mul[mul[a][b]][c] == mul[a][mul[b][c]], "field associativity")
    require(all(any(mul[a][b] == 1 for b in range(q)) for a in range(1, q)),
            "nonzero field element lacks inverse")
    return add, mul


@dataclass(frozen=True)
class Algebra:
    name: str
    q: int
    dimension: int
    add: list[list[int]]
    mul: list[list[int]]
    neg: list[int]
    inverse: dict[int, int]

    @property
    def size(self) -> int:
        return len(self.add)


def coefficient_product(a: tuple[int, ...], b: tuple[int, ...],
                        basis: tuple[tuple[int, ...], ...],
                        add: list[list[int]], mul: list[list[int]]) -> tuple[int, ...]:
    out = [0] * len(a)
    for i, j in itertools.product(range(len(a)), repeat=2):
        k = basis[i][j]
        if k >= 0:
            out[k] = add[out[k]][mul[a[i]][b[j]]]
    return tuple(out)


def make_algebra(name: str, q: int, basis: tuple[tuple[int, ...], ...]) -> Algebra:
    dimension = len(basis)
    require(1 <= dimension <= 4 and q ** dimension <= 16, "algebra size bound")
    require(all(len(row) == dimension for row in basis), "basis table shape")
    require(all(-1 <= k < dimension for row in basis for k in row), "basis index")
    fa, fm = field_tables(q)
    size = q ** dimension
    digits = [tuple((a // q ** i) % q for i in range(dimension))
              for a in range(size)]
    add = [[sum(fa[x][y] * q ** i for i, (x, y) in enumerate(zip(a, b)))
            for b in digits] for a in digits]
    mul = [[sum(x * q ** i for i, x in enumerate(
        coefficient_product(a, b, basis, fa, fm))) for b in digits] for a in digits]
    neg = [next(b for b in range(size) if add[a][b] == 0) for a in range(size)]
    inverse = {a: b for a, b in itertools.product(range(size), repeat=2)
               if mul[a][b] == mul[b][a] == 1}
    for a, b, c in itertools.product(range(size), repeat=3):
        require(mul[mul[a][b]][c] == mul[a][mul[b][c]], "ring associativity")
        require(mul[a][add[b][c]] == add[mul[a][b]][mul[a][c]], "left distributivity")
        require(mul[add[a][b]][c] == add[mul[a][c]][mul[b][c]], "right distributivity")
    for a, b in itertools.product(range(size), repeat=2):
        require(mul[a][1] == mul[1][a] == a, "ring identity")
        require(mul[a][b] % q == fm[a % q][b % q], "residue homomorphism")
        if a < q:
            require(mul[a][b] == mul[b][a], "base field is not central")
    require(set(inverse) == {a for a in range(size) if a % q}, "local unit test")
    return Algebra(name, q, dimension, add, mul, neg, inverse)


def matmul(r: Algebra, a: Matrix, b: Matrix) -> Matrix:
    plus, times = r.add, r.mul
    return (plus[times[a[0]][b[0]]][times[a[1]][b[2]]],
            plus[times[a[0]][b[1]]][times[a[1]][b[3]]],
            plus[times[a[2]][b[0]]][times[a[3]][b[2]]],
            plus[times[a[2]][b[1]]][times[a[3]][b[3]]])


def act(r: Algebra, a: Matrix, x: Vector) -> Vector:
    return (r.add[r.mul[a[0]][x[0]]][r.mul[a[1]][x[1]]],
            r.add[r.mul[a[2]][x[0]]][r.mul[a[3]][x[1]]])


def paid(r: Algebra, u: Vector, y: Vector) -> Matrix:
    return (r.add[1][r.mul[u[0]][y[0]]], r.mul[u[0]][y[1]],
            r.mul[u[1]][y[0]], r.add[1][r.mul[u[1]][y[1]]])


def residue_rank(r: Algebra, a: Matrix) -> int:
    a0, a1, a2, a3 = (x % r.q for x in a)
    determinant = r.add[r.mul[a0][a3]][r.neg[r.mul[a1][a2]]]
    if determinant:
        return 2
    return int(any((a0, a1, a2, a3)))


def one_call_images(r: Algebra) -> set[Matrix]:
    # Scaling a nonzero right vector into this projective list is absorbed in u.
    lines = [(1, t) for t in range(r.q)] + [(0, 1)]
    free = [a for a in itertools.product(range(r.q), repeat=4)
            if residue_rank(r, a) == 2]
    require(len(free) == (r.q ** 2 - 1) * (r.q ** 2 - r.q), "GL2 cardinality")
    images: set[Matrix] = set()
    for u in itertools.product(range(r.size), repeat=2):
        for y in lines:
            p = paid(r, u, y)
            for s in free:
                images.add(matmul(r, p, s))
    return images


def two_call_word(r: Algebra, m: Matrix) -> tuple[Matrix, Matrix, Matrix]:
    # Permute one unit entry to (0,0), then use the predecessor's unit-pivot word.
    k = next(i for i in range(4) if m[i] % r.q)
    identity, swap = (1, 0, 0, 1), (0, 1, 1, 0)
    g = swap if k // 2 else identity
    h = swap if k % 2 else identity
    a, b, c, d = matmul(r, matmul(r, g, m), h)
    quotient = r.mul[r.inverse[a]][b]
    schur = r.add[d][r.neg[r.mul[c][quotient]]]
    u1 = act(r, g, (r.add[a][r.neg[1]], c))
    u2 = act(r, g, (quotient, r.add[schur][r.neg[1]]))
    p1 = paid(r, u1, act(r, g, (1, 0)))
    p2 = paid(r, u2, act(r, g, (0, 1)))
    return p1, p2, matmul(r, g, h)


def criterion(r: Algebra, a: Matrix, m: Matrix) -> tuple[int, int]:
    # Count eligible lines and the tempting incorrect test allowing A v = 0.
    valid, wrong = 0, 0
    for v in [(1, t) for t in range(r.q)] + [(0, 1)]:
        av, mv = act(r, a, v), act(r, m, v)
        if av == mv:
            wrong += 1
            valid += int(av != (0, 0))
    return valid, wrong


def check_case(r: Algebra) -> dict[str, object]:
    one_images = one_call_images(r)
    residues = [a for a in itertools.product(range(r.q), repeat=4)
                if residue_rank(r, a) == 1]
    require(len(residues) == (r.q - 1) * (r.q + 1) ** 2, "rank-one residue count")
    z = r.size // r.q
    expected_one = r.q * z ** 2 - r.q + 1
    histograms = []
    controls = {key: False for key in ("zero_image", "reverse", "drop")}
    for a in residues:
        histogram = [0, 0]
        for radical in itertools.product(range(z), repeat=4):
            m = tuple(x + r.q * j for x, j in zip(a, radical))
            good, wrong = criterion(r, a, m)
            one = m in one_images
            require(one == bool(good), "literal one-factor/line discrepancy")
            require(good == (r.q if m == a else int(one)), "line intersections")
            p1, p2, s = two_call_word(r, m)
            require(matmul(r, matmul(r, p1, p2), s) == m, "two-call word")
            # Literal action on every coordinate of the underlying K-vector space.
            for i in range(r.dimension):
                for x in ((r.q ** i, 0), (0, r.q ** i)):
                    require(act(r, p1, act(r, p2, act(r, s, x))) == act(r, m, x),
                            "dirty input basis action")
            histogram[0 if one else 1] += 1
            controls["zero_image"] |= bool(wrong and not good)
            controls["reverse"] |= matmul(r, matmul(r, p2, p1), s) != m
            controls["drop"] |= matmul(r, p1, s) != m
        require(histogram == [expected_one, z ** 4 - expected_one], "census formula")
        histograms.append(histogram)
    require(controls["drop"], "dropped-factor control did not discriminate")
    if z > 1:
        require(all(controls.values()), "one of the three semantic controls did not discriminate")
    return {"name": r.name, "q": r.q, "radical_dimension": r.dimension - 1,
            "residues": len(residues), "targets": len(residues) * z ** 4,
            "one_per_residue": expected_one, "two_per_residue": z ** 4 - expected_one,
            "one_total": sum(x[0] for x in histograms),
            "two_total": sum(x[1] for x in histograms), "controls": controls}


def boundary_controls() -> dict[str, object]:
    dual = make_algebra("dual", 3, ((0, 1), (1, -1)))
    # Addition instead of subtraction in the Schur complement is wrong at odd q.
    m = (1, 1, 1, 1)
    bad = paid(dual, (1, 1), (0, 1))
    first = paid(dual, (0, 1), (1, 0))
    require(matmul(dual, first, bad) != m, "odd-field sign control")
    noncomm = make_algebra("noncomm", 2,
                          ((0, 1, 2, 3), (1, -1, 3, -1),
                           (2, -1, -1, -1), (3, -1, -1, -1)))
    require(noncomm.mul[2][4] != noncomm.mul[4][2], "noncommutative fixture")
    a, b, c, d = 3, 4, 1, 0
    wrong = noncomm.mul[b][noncomm.inverse[a]]
    f1 = paid(noncomm, (noncomm.add[a][noncomm.neg[1]], c), (1, 0))
    s = noncomm.add[d][noncomm.neg[noncomm.mul[c][wrong]]]
    f2 = paid(noncomm, (wrong, noncomm.add[s][noncomm.neg[1]]), (0, 1))
    require(matmul(noncomm, f1, f2) != (a, b, c, d), "inverse order control")
    rejected = 0
    for q in (1, 6):
        try:
            field_tables(q)
        except ValueError:
            rejected += 1
    require(rejected == 2, "invalid field orders were accepted")
    binary = make_algebra("dual", 2, ((0, 1), (1, -1)))
    images = one_call_images(binary)
    zero, one, two = 0, 0, 0
    for m in itertools.product(range(4), repeat=4):
        if residue_rank(binary, m) == 2:
            if all(x < 2 for x in m):
                zero += 1
            elif m in images:
                one += 1
            else:
                two += 1
    require((zero, one, two) == (6, 54, 36), "binary invertible compatibility")
    return {"odd_sign": True, "inverse_order": True, "invalid_fields_rejected": rejected,
            "binary_dual_invertible_compatibility": [zero, one, two]}


def main() -> None:
    field = ((0,),)
    dual = ((0, 1), (1, -1))
    cube = ((0, 1, 2), (1, 2, -1), (2, -1, -1))
    square = ((0, 1, 2), (1, -1, -1), (2, -1, -1))
    noncomm = ((0, 1, 2, 3), (1, -1, 3, -1),
               (2, -1, -1, -1), (3, -1, -1, -1))
    cases = [("F2", 2, field), ("F2[e]/e2", 2, dual),
             ("F3[e]/e2", 3, dual), ("F4[e]/e2", 4, dual),
             ("F2[x]/x3", 2, cube), ("F2[x,y]/(x,y)2", 2, square),
             ("F2<x,y>/(x2,y2,yx,degree3)", 2, noncomm)]
    results = [check_case(make_algebra(name, q, basis)) for name, q, basis in cases]
    root = Path(__file__).resolve().parent
    files = ("PROOF.md", "README.md", "SOURCES.json", "TASK.json", "VERIFY.json", "verify.py")
    require(all((root / name).stat().st_size <= 1024 ** 2 for name in files),
            "package receipt input exceeds 1 MiB")
    receipt = {"claim_type": "scoped counting proof with finite corroboration",
               "cases": results, "boundary_controls": boundary_controls(),
               "source_sha256": {name: hashlib.sha256((root / name).read_bytes()).hexdigest()
                                 for name in files}}
    print(json.dumps(receipt, sort_keys=True))
    print("PASS_RIGHT_VECTOR_RANKONE_RESIDUE",
          "targets=" + str(sum(int(x["targets"]) for x in results)),
          "residues=" + str(sum(int(x["residues"]) for x in results)))


if __name__ == "__main__":
    main()
