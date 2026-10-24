#!/usr/bin/env python3
"""Exact finite corroboration of the separately written all-role proof."""

from dataclasses import dataclass
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
from random import Random


Matrix = tuple[tuple[int, ...], ...]
Factor = tuple[int, int, int]
MAX_ROLES = 8
MAX_LENGTH = 12


def need(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def fmul(a: int, b: int) -> int:
    """F4 = F2[t]/(t^2+t+1), encoded by two polynomial bits."""
    value = 0
    for bit in range(2):
        if b & (1 << bit):
            value ^= a << bit
    return value ^ 7 if value & 4 else value


def mmul(a: Matrix, b: Matrix) -> Matrix:
    n = len(a)
    need(1 <= n <= MAX_ROLES and len(b) == n, "matrix size")
    need(all(len(row) == n for row in (*a, *b)), "square matrices")
    out = [[0] * n for _ in range(n)]
    for row, col, inner in product(range(n), repeat=3):
        out[row][col] ^= fmul(a[row][inner], b[inner][col])
    return tuple(map(tuple, out))


def madd(a: Matrix, b: Matrix) -> Matrix:
    return tuple(tuple(x ^ y for x, y in zip(ar, br, strict=True))
                 for ar, br in zip(a, b, strict=True))


def scale(a: Matrix, value: int) -> Matrix:
    return tuple(tuple(fmul(x, value) for x in row) for row in a)


def identity(n: int) -> Matrix:
    need(1 <= n <= MAX_ROLES, "role bound")
    return tuple(tuple(int(i == j) for j in range(n)) for i in range(n))


def outer(n: int, x: int, y: int) -> Matrix:
    need(0 < x < (1 << n) and 0 < y < (1 << n), "nonzero binary vectors")
    need((x & y).bit_count() % 2 == 1, "rank-one idempotent")
    return tuple(tuple(((x >> i) & 1) * ((y >> j) & 1)
                       for j in range(n)) for i in range(n))


def qfactor(n: Matrix, value: int) -> Matrix:
    return madd(identity(len(n)), scale(n, value ^ 1))


def rank(a: Matrix) -> int:
    rows = [list(row) for row in a]
    height, width = len(rows), len(rows[0])
    need(height <= MAX_ROLES and width <= MAX_ROLES, "rank dimensions")
    pivots = 0
    for col in range(width):
        pivot = next((r for r in range(pivots, height) if rows[r][col]), None)
        if pivot is None:
            continue
        rows[pivots], rows[pivot] = rows[pivot], rows[pivots]
        inverse = (0, 1, 3, 2)[rows[pivots][col]]
        rows[pivots] = [fmul(x, inverse) for x in rows[pivots]]
        for r in range(height):
            if r != pivots and rows[r][col]:
                coefficient = rows[r][col]
                rows[r] = [x ^ fmul(coefficient, y)
                           for x, y in zip(rows[r], rows[pivots], strict=True)]
        pivots += 1
    return pivots


def gmul(a: tuple[int, ...], b: tuple[int, ...]) -> tuple[int, ...]:
    return ((a[0]*b[0] + a[1]*b[2]) % 3,
            (a[0]*b[1] + a[1]*b[3]) % 3,
            (a[2]*b[0] + a[3]*b[2]) % 3,
            (a[2]*b[1] + a[3]*b[3]) % 3)


@dataclass(frozen=True)
class Model:
    table: tuple[tuple[int, ...], ...]
    psi: tuple[int, ...]
    delta: tuple[int, ...]
    unit: int
    i: int
    w: int
    c: int
    labels: tuple[int, ...]


def make_model() -> Model:
    group = tuple(a for a in product(range(3), repeat=4)
                  if (a[0]*a[3] - a[1]*a[2]) % 3 == 1)
    unit, i, w = (1, 0, 0, 1), (0, 1, 2, 0), (0, 2, 1, 2)
    w2 = gmul(w, w)
    c = gmul(gmul(w2, i), w)
    ic = gmul(i, c)
    mu = {}
    for p, value in ((unit, 0), (i, 1), (c, 2), (ic, 3)):
        mu[p] = value
        mu[tuple((-x) % 3 for x in p)] = value
    delta, psi = {}, {}
    for h, character in ((unit, 1), (w, 2), (w2, 3)):
        for p, value in mu.items():
            g = gmul(h, p)
            need(g not in delta, "unique semidirect normal form")
            delta[g], psi[g] = value, character
    need(len(group) == len(delta) == 24 and len(mu) == 8, "group orders")
    need(set(group) == set(delta), "semidirect coverage")
    for p, q in product(mu, repeat=2):
        need(mu[gmul(p, q)] == mu[p] ^ mu[q], "Frattini homomorphism")
    for p in mu:
        need(mu[gmul(gmul(w2, p), w)] == fmul(mu[p], 2), "equivariance")
    table = tuple(tuple(group.index(gmul(a, b)) for b in group) for a in group)
    inverse_i = tuple((-x) % 3 for x in i)
    return Model(table, tuple(psi[g] for g in group),
                 tuple(delta[g] for g in group), group.index(unit),
                 group.index(i), group.index(w), group.index(c),
                 tuple(group.index(g) for g in (i, inverse_i, w, w2)))


def check_cocycle(model: Model) -> dict:
    pairs = 0
    wrong_orientation = 0
    for a, b in product(range(24), repeat=2):
        ab = model.table[a][b]
        need(model.psi[ab] == fmul(model.psi[a], model.psi[b]), "character")
        expected = model.delta[b] ^ fmul(model.delta[a], model.psi[b])
        need(model.delta[ab] == expected, "right cocycle")
        inverse = (0, 1, 3, 2)[model.psi[b]]
        wrong_orientation += model.delta[ab] != (model.delta[b] ^
                                                fmul(model.delta[a], inverse))
        pairs += 1
    need(wrong_orientation > 0, "wrong-conjugation control")
    need(tuple(model.delta[g] for g in model.labels) == (1, 1, 0, 0),
         "paid-label defects")
    need(model.delta[model.c] == 2, "conjugate defect")
    minus_one = model.table[model.i][model.i]
    need(minus_one != model.unit and model.delta[minus_one] == 0,
         "central-kernel limitation")
    return {"cocycle_pairs": pairs, "wrong_orientation_failures": wrong_orientation,
            "cocycle_controls": ["wrong_orientation", "central_kernel"]}


def projectors(n: int) -> tuple[Matrix, ...]:
    need(2 <= n <= 4, "exhaustive quotient role bound")
    matrices = tuple(outer(n, x, y) for x, y in
                     product(range(1, 1 << n), repeat=2)
                     if (x & y).bit_count() % 2 == 1)
    need(len(matrices) == (2**n - 1)*2**(n - 1), "projector coverage")
    need(len(set(matrices)) == len(matrices), "no repeated projectors")
    return matrices


def check_quotient() -> dict[str, int]:
    singles = doubles = single_hits = double_hits = 0
    for n in (2, 3, 4):
        e = outer(n, 2, 2)
        target = qfactor(e, 2)
        alphabet = tuple((value, p, qfactor(p, value))
                         for value, p in product((2, 3), projectors(n)))
        for value, p, factor in alphabet:
            hit = factor == target
            need(hit == (value == 2 and p == e), "one-call rigidity")
            singles += 1
            single_hits += hit
        for (v, p, a), (u, q, b) in product(alphabet, repeat=2):
            hit = mmul(a, b) == target
            need(hit == (v == u == 3 and p == q == e), "two-call rigidity")
            doubles += 1
            double_hits += hit
    return {"quotient_single_words": singles, "quotient_double_words": doubles,
            "quotient_single_hits": single_hits, "quotient_double_hits": double_hits}


def translate(model: Model, mask: int, label: int, left: bool) -> int:
    result = 0
    for g in range(24):
        if mask & (1 << g):
            image = model.table[label][g] if left else model.table[g][label]
            result ^= 1 << image
    return result


def ring_word(model: Model, n: int, word: tuple[Factor, ...]) -> Matrix:
    need(3 <= n <= MAX_ROLES and len(word) <= MAX_LENGTH, "word bounds")
    state = [[(1 << model.unit) if row == col else 0
              for col in range(n)] for row in range(n)]
    for label, x, y in word:
        outer(n, x, y)
        need(label in model.labels, "paid label")
        column = [0] * n
        for row, col in product(range(n), repeat=2):
            if x & (1 << col):
                column[row] ^= state[row][col]
        changed = [v ^ translate(model, v, label, False) for v in column]
        for row, col in product(range(n), repeat=2):
            if y & (1 << col):
                state[row][col] ^= changed[row]
    return tuple(map(tuple, state))


def evaluate(a: Matrix, values: tuple[int, ...]) -> Matrix:
    out = []
    for row in a:
        output_row = []
        for mask in row:
            value = 0
            for g in range(24):
                if mask & (1 << g):
                    value ^= values[g]
            output_row.append(value)
        out.append(tuple(output_row))
    return tuple(out)


def decomposition(model: Model, n: int, word: tuple[Factor, ...]) -> tuple[Matrix, Matrix]:
    suffix = identity(n)
    defect = scale(suffix, 0)
    for label, x, y in reversed(word):
        p = outer(n, x, y)
        term = mmul(scale(p, model.delta[label]), suffix)
        need(rank(term) <= int(model.delta[label] != 0), "rank per paid call")
        defect = madd(defect, term)
        suffix = mmul(qfactor(p, model.psi[label]), suffix)
    return defect, suffix


def check_words(model: Model) -> dict[str, int]:
    rng = Random(1907)
    words = 0
    for n, length, _ in product((3, 5, 8), range(MAX_LENGTH + 1), range(8)):
        factors = []
        for _ in range(length):
            x = rng.randrange(1, 1 << n)
            ys = tuple(y for y in range(1, 1 << n)
                       if (x & y).bit_count() % 2 == 1)
            factors.append((rng.choice(model.labels), x, rng.choice(ys)))
        word = tuple(factors)
        state = ring_word(model, n, word)
        defect, quotient = decomposition(model, n, word)
        need(evaluate(state, model.delta) == defect, "full-algebra defect identity")
        need(evaluate(state, model.psi) == quotient, "full-algebra quotient")
        active = sum(model.delta[g] != 0 for g, _, _ in word)
        need(rank(defect) <= active, "first-order rank floor")
        words += 1
    return {"sampled_full_algebra_words": words}


def upper_word(model: Model) -> tuple[Factor, ...]:
    return ((model.i, 1, 1), (model.w, 2, 2),
            (model.labels[3], 4, 4), (model.i, 4, 4), (model.w, 4, 4))


def target_matrix(model: Model, n: int) -> Matrix:
    diagonal = (model.i, model.w, model.c) + (model.unit,) * (n - 3)
    return tuple(tuple((1 << diagonal[i]) if i == j else 0
                       for j in range(n)) for i in range(n))


def regular_action(model: Model, n: int, word: tuple[Factor, ...],
                   source: tuple[int, ...]) -> tuple[int, ...]:
    state = list(source)
    # A formal product F1...FL acts on columns by FL first.
    for label, x, y in reversed(word):
        total = 0
        for row in range(n):
            if y & (1 << row):
                total ^= state[row]
        change = total ^ translate(model, total, label, True)
        for row in range(n):
            if x & (1 << row):
                state[row] ^= change
    return tuple(state)


def check_upper(model: Model) -> dict[str, int]:
    word = upper_word(model)
    basis_inputs = 0
    for n in (3, 5, 8):
        target = target_matrix(model, n)
        need(ring_word(model, n, word) == target, "five-call formal endpoint")
        need(rank(evaluate(target, model.delta)) == 2, "target rank two")
        diagonal = (model.i, model.w, model.c) + (model.unit,) * (n - 3)
        for row, address in product(range(n), range(24)):
            source = tuple((1 << address) if j == row else 0 for j in range(n))
            expected = tuple(translate(model, value, g, True)
                             for value, g in zip(source, diagonal, strict=True))
            need(regular_action(model, n, word, source) == expected,
                 "independent regular-action basis endpoint")
            basis_inputs += 1
    return {"upper_role_counts": 3, "regular_basis_inputs": basis_inputs}


def check_controls(model: Model) -> dict:
    word, target = upper_word(model), target_matrix(model, 5)
    controls = []
    for omitted in range(5):
        need(ring_word(model, 5, word[:omitted] + word[omitted + 1:]) != target,
             "omitted-call control")
        controls.append(f"omitted_call_{omitted}")
    wrong_conjugate = word[:2] + (word[4], word[3], word[2])
    need(ring_word(model, 5, wrong_conjugate) != target, "conjugate-order control")
    controls.append("conjugate_order")
    dirty = ring_word(model, 5, word + ((model.i, 8, 8),))
    need(dirty != target and dirty[:3] == target[:3], "data-only equality control")
    controls.append("unrestored_dirty_role")
    short = ((model.i, 1, 1), (model.w, 2, 2), (model.i, 4, 4))
    changed = [list(row) for row in target]
    changed[2][2] = 1 << model.i
    need(ring_word(model, 5, short) == tuple(map(tuple, changed)),
         "unconjugated target has a three-call word")
    controls.append("changed_target")
    e = ((1, 0), (0, 0))
    p, q = ((1, 1), (0, 0)), ((1, 2), (0, 0))
    need(mmul(p, p) == p and mmul(q, q) == q and p != q,
         "nonbinary rank-one idempotents")
    need(mmul(qfactor(p, 3), qfactor(q, 3)) == qfactor(e, 2),
         "binary-coefficient hypothesis is necessary for rigidity")
    controls.append("nonbinary_projectors")
    return {"endpoint_controls": controls}


def main() -> None:
    model = make_model()
    report = {"claim_type": "scoped proof with finite corroboration",
              "minimum_calls": 5, "quaternion_call_floor": 2,
              "order_three_call_floor": 3,
              "dirty_roles": "every finite number, by PROOF.md"}
    for section in (check_cocycle(model), check_quotient(), check_words(model),
                    check_upper(model), check_controls(model)):
        report.update(section)
    report["semantic_controls"] = len(report["cocycle_controls"]) + len(report["endpoint_controls"])
    package = Path(__file__).resolve().parent
    names = ("verify.py", "README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json")
    report["source_sha256"] = {
        name: sha256((package / name).read_bytes()).hexdigest() for name in names}
    print(json.dumps(report, sort_keys=True, indent=2))
    print("PASS_SL2F3_ALL_DIRTY_MINIMUM minimum=5 i_floor=2 w_floor=3")


if __name__ == "__main__":
    main()
