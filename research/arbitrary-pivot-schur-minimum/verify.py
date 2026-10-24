#!/usr/bin/env python3
"""Exact new-boundary constructions; no predecessor code is imported.

Krzysztof Wojt, substantial OpenAI Codex assistance. Apache-2.0.
The proof is in PROOF.md. This finite replay corroborates it, not proves it.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
CAP = 48


def require(condition, message):
    if not condition:
        raise ValueError(message)


def norm(value, prime):
    return value % prime if prime else Fraction(value)


def reciprocal(value, prime):
    require(value != 0, "zero denominator")
    return pow(value, -1, prime) if prime else 1 / Fraction(value)


@dataclass(frozen=True)
class Mat:
    rows: tuple
    nc: int

    def __post_init__(self):
        require(0 <= len(self.rows) <= CAP and 0 <= self.nc <= 2 * CAP,
                "matrix capacity")
        require(all(len(row) == self.nc for row in self.rows), "ragged matrix")

    @property
    def nr(self):
        return len(self.rows)


def mat(rows, prime, nc=None):
    data = tuple(tuple(norm(x, prime) for x in row) for row in rows)
    return Mat(data, len(data[0]) if data else (0 if nc is None else nc))


def zero(nr, nc):
    return Mat(tuple((0,) * nc for _ in range(nr)), nc)


def eye(n):
    return Mat(tuple(tuple(int(i == j) for j in range(n)) for i in range(n)), n)


def add(a, b, prime, sign=1):
    require((a.nr, a.nc) == (b.nr, b.nc), "addition shape")
    return mat(([x + sign * y for x, y in zip(ra, rb)]
                for ra, rb in zip(a.rows, b.rows)), prime, a.nc)


def mul(a, b, prime):
    require(a.nc == b.nr, "product shape")
    out = [[0] * b.nc for _ in range(a.nr)]
    for i, row in enumerate(a.rows):
        for k, x in enumerate(row):
            if x:
                for j, y in enumerate(b.rows[k]):
                    out[i][j] += x * y
    return mat(out, prime, b.nc)


def chain(prime, *items):
    result = items[0]
    for item in items[1:]:
        result = mul(result, item, prime)
    return result


def transpose(a):
    return Mat(tuple(tuple(a.rows[i][j] for i in range(a.nr))
                     for j in range(a.nc)), a.nr)


def hcat(*items):
    require(bool(items) and len({a.nr for a in items}) == 1, "horizontal shape")
    return Mat(tuple(tuple(x for a in items for x in a.rows[i])
                     for i in range(items[0].nr)), sum(a.nc for a in items))


def vcat(*items):
    require(bool(items) and len({a.nc for a in items}) == 1, "vertical shape")
    return Mat(tuple(row for a in items for row in a.rows), items[0].nc)


def block(a, row_indices, col_indices):
    rr, cc = tuple(row_indices), tuple(col_indices)
    return Mat(tuple(tuple(a.rows[i][j] for j in cc) for i in rr), len(cc))


def rref(a, prime):
    rows = [list(row) for row in a.rows]
    pivots = []
    for col in range(a.nc):
        pos = next((i for i in range(len(pivots), a.nr) if rows[i][col]), None)
        if pos is None:
            continue
        lead = len(pivots)
        rows[lead], rows[pos] = rows[pos], rows[lead]
        factor = reciprocal(rows[lead][col], prime)
        rows[lead] = [norm(x * factor, prime) for x in rows[lead]]
        for i in range(a.nr):
            if i != lead and rows[i][col]:
                factor = rows[i][col]
                rows[i] = [norm(x - factor * y, prime)
                           for x, y in zip(rows[i], rows[lead])]
        pivots.append(col)
        if len(pivots) == a.nr:
            break
    return mat(rows, prime, a.nc), tuple(pivots)


def rank(a, prime):
    return len(rref(a, prime)[1])


def inverse(a, prime):
    require(a.nr == a.nc, "inverse shape")
    reduced, pivots = rref(hcat(a, eye(a.nr)), prime)
    require(pivots[:a.nr] == tuple(range(a.nr)), "singular pivot")
    return block(reduced, range(a.nr), range(a.nr, 2 * a.nr))


def kernel(a, prime):
    reduced, pivots = rref(a, prime)
    free = [j for j in range(a.nc) if j not in pivots]
    columns = []
    for col in free:
        vector = [0] * a.nc
        vector[col] = 1
        for i, pivot in enumerate(pivots):
            vector[pivot] = norm(-reduced.rows[i][col], prime)
        columns.append(vector)
    return transpose(mat(columns, prime, a.nc))


def rank_factor(t, prime):
    pivots = rref(t, prime)[1]
    x = block(t, range(t.nr), pivots)
    if not pivots:
        return x, zero(0, t.nc)
    row_basis = rref(transpose(x), prime)[1]
    square = block(x, row_basis, range(x.nc))
    y = mul(inverse(square, prime), block(t, row_basis, range(t.nc)), prime)
    require(mul(x, y, prime) == t, "rank factor product")
    return x, y


def full_factor(t, prime):
    require(t.nr == t.nc, "full factor shape")
    d = t.nr
    x = t
    complement = []
    current_rank = rank(t, prime)
    for j in range(d):
        col = block(eye(d), range(d), (j,))
        candidate = hcat(x, col)
        new_rank = rank(candidate, prime)
        if new_rank > current_rank:
            complement.append(j)
            x, current_rank = candidate, new_rank
    y = vcat(eye(d), zero(len(complement), d))
    require(current_rank == d and mul(x, y, prime) == t, "full factor product")
    return x, y


def products(a, b, h, prime):
    d = a.nr
    require(d >= 1 and all(t.nr == d and t.nc == d for t in (a, b, h)),
            "prescribed block shape")
    inverse(a, prime)
    inverse(b, prime)
    return (add(add(add(eye(d), a, prime, -1), b, prime, -1), h, prime),
            add(a, h, prime, -1), add(b, h, prime, -1), h)


def theorem_data(a, b, h, prime):
    ts = products(a, b, h, prime)
    d = a.nr
    rr = [rank(ts[0], prime)] + [2 * d - rank(t, prime) for t in ts[1:]]
    return {"sectors": rr, "n": sum(rr), "rank_p": rr[1] + rr[3],
            "rank_q": rr[2] + rr[3]}


def diagonal_on_rows(a, mask, prime):
    return mat(([x * mask[i] for x in row] for i, row in enumerate(a.rows)),
               prime, a.nc)


def realize(a, b, h, prime, missing=None):
    ts = products(a, b, h, prime)
    pairs = [rank_factor(ts[0], prime)] + [full_factor(t, prime) for t in ts[1:]]
    if missing is not None:
        sector, which = missing
        x, y = pairs[sector]
        require(ts[sector] == zero(a.nr, a.nr), "control requires zero product")
        if which == "Y":
            data = [list(row) for row in y.rows]
            data[0][0] = 0
            y = mat(data, prime, y.nc)
        else:
            data = [list(row) for row in x.rows]
            data[0][a.nr] = 0
            x = mat(data, prime, x.nc)
        pairs[sector] = x, y
    xs, ys = tuple(pair[0] for pair in pairs), tuple(pair[1] for pair in pairs)
    projection, inclusion = hcat(*xs), vcat(*ys)
    require(mul(projection, inclusion, prime) == eye(a.nr), "split projection")
    change = hcat(inclusion, kernel(projection, prime))
    undo = inverse(change, prime)
    sizes = [x.nc for x in xs]
    pmask = [v for size, v in zip(sizes, (0, 1, 0, 1)) for _ in range(size)]
    qmask = [v for size, v in zip(sizes, (0, 0, 1, 1)) for _ in range(size)]
    p = mul(undo, diagonal_on_rows(change, pmask, prime), prime)
    q = mul(undo, diagonal_on_rows(change, qmask, prime), prime)
    return {"P": p, "Q": q, "X": xs, "Y": ys, "sectors": sizes}


def commutator(a, b, prime):
    return add(mul(a, b, prime), mul(b, a, prime), prime, -1)


def check_pair(a, b, h, prime, witness, sharp=True):
    p, q = witness["P"], witness["Q"]
    d, n = a.nr, p.nr
    rr, tail = range(d), range(d, n)
    require(p.nc == n and (q.nr, q.nc) == (n, n), "ambient shapes")
    pq = mul(p, q, prime)
    require(mul(p, p, prime) == p and mul(q, q, prime) == q, "idempotence")
    require(pq == mul(q, p, prime), "ambient commutation")
    require(block(p, rr, rr) == a and block(q, rr, rr) == b, "prescribed pivots")
    require(block(pq, rr, rr) == h, "prescribed product")
    c, r = block(p, tail, rr), block(p, rr, tail)
    e, ell = block(q, tail, rr), block(q, rr, tail)
    ai, bi = inverse(a, prime), inverse(b, prime)
    s = add(block(p, tail, tail), chain(prime, c, ai, r), prime, -1)
    z = add(block(q, tail, tail), chain(prime, e, bi, ell), prime, -1)
    require(mul(s, s, prime) == s and mul(z, z, prime) == z, "Schur idempotence")
    k = commutator(s, z, prime)
    u = add(mul(c, ai, prime), mul(e, bi, prime), prime, -1)
    v = add(mul(ai, r, prime), mul(bi, ell, prime), prime, -1)
    w, t = block(pq, tail, rr), block(pq, rr, tail)
    x = add(w, chain(prime, e, bi, h), prime, -1)
    y = add(t, chain(prime, h, bi, ell), prime, -1)
    require(k == add(mul(x, v, prime), mul(u, y, prime), prime, -1), "ordered factors")
    six = all(rank(t, prime) == d for t in witness["X"][1:] + witness["Y"][1:])
    rk = rank(k, prime)
    require((rk == 2 * d) == six, "six-map criterion")
    require(rank(s, prime) == rank(p, prime) - d, "P rank drop")
    require(rank(z, prime) == rank(q, prime) - d, "Q rank drop")
    if sharp:
        expected = theorem_data(a, b, h, prime)
        require(rk == 2 * d, "commutator not sharp")
        require(n == expected["n"] and witness["sectors"] == expected["sectors"],
                "dimension minimum")
        require(rank(p, prime) == expected["rank_p"] and
                rank(q, prime) == expected["rank_q"], "input rank minima")
    wrong_x = add(w, chain(prime, e, h, bi), prime, -1)
    wrong_y = add(t, chain(prime, bi, h, ell), prime, -1)
    errors = (k != add(mul(wrong_x, v, prime), mul(u, y, prime), prime, -1),
              k != add(mul(x, v, prime), mul(u, wrong_y, prime), prime, -1))
    return rk, errors


def small_matrices(prime, d):
    for entries in itertools.product(range(prime), repeat=d * d):
        yield mat([entries[i * d:(i + 1) * d] for i in range(d)], prime)


def encode(a):
    return [list(row) for row in a.rows]


def record_case(a, b, h, prime, counts, binary=None):
    w = realize(a, b, h, prime)
    _, errors = check_pair(a, b, h, prime, w)
    key = "Q" if prime == 0 else f"F{prime}"
    counts[key] = counts.get(key, 0) + 1
    counts["ordered_X_mutation_detected"] += int(errors[0])
    counts["ordered_Y_mutation_detected"] += int(errors[1])
    if binary is not None:
        binary.append({"A": encode(a), "B": encode(b), "H": encode(h),
                       "P": encode(w["P"]), "Q": encode(w["Q"])})
    return w


def finite_cases(counts):
    binary = []
    matrices = list(small_matrices(2, 2))
    invertibles = [a for a in matrices if rank(a, 2) == 2]
    require(len(invertibles) == 6, "GL2 binary census")
    for a, b, h in itertools.product(invertibles, invertibles, matrices):
        record_case(a, b, h, 2, counts, binary)
    ternary = list(small_matrices(3, 2))
    gl3 = [a for a in ternary if rank(a, 3) == 2]
    require(len(gl3) == 48, "GL2 ternary census")
    pairs = [(a, b) for a, b in itertools.product(gl3, gl3)
             if commutator(a, b, 3) != zero(2, 2)][:8]
    require(len(pairs) == 8, "ternary pair coverage")
    for (a, b), h in itertools.product(pairs, ternary):
        record_case(a, b, h, 3, counts)
    return {"schema_version": 1, "field": 2, "d": 2, "fixtures": binary}


def wider_cases(counts):
    for prime in (2, 3, 5, 7, 0):
        for d in (2, 3, 4):
            for diagonal in (1, 2):
                if prime and diagonal % prime == 0:
                    continue
                a = mat([[diagonal if i == j else int(j == i + 1)
                          for j in range(d)] for i in range(d)], prime)
                b = transpose(a)
                hs = (zero(d, d), eye(d), a, b, mul(a, b, prime),
                      add(add(a, b, prime), eye(d), prime, -1))
                for h in hs:
                    record_case(a, b, h, prime, counts)


def rejection_controls():
    a = mat([[1, 1], [0, 1]], 2)
    b = transpose(a)
    controls = []
    for sector, h in ((1, a), (2, b), (3, zero(2, 2))):
        for which in ("X", "Y"):
            w = realize(a, b, h, 2, (sector, which))
            rk, _ = check_pair(a, b, h, 2, w, sharp=False)
            require(rk < 4, "missing active map accepted")
            controls.append(f"sector{sector}_missing_{which}")
    for pivot in ("A", "B"):
        aa, bb = (zero(2, 2), b) if pivot == "A" else (a, zero(2, 2))
        try:
            realize(aa, bb, eye(2), 2)
        except ValueError as exc:
            require(str(exc) == "singular pivot", "unexpected singular-pivot rejection")
            controls.append(f"singular_{pivot}")
        else:
            raise ValueError("singular pivot accepted")
    return controls


def noncommuting_example(prime):
    a = mat([[2, 1], [0, 2]], prime)
    b = transpose(a)
    h = mat([[3, 1], [1, 3]], prime)
    w = realize(a, b, h, prime)
    check_pair(a, b, h, prime, w)
    require(all(commutator(x, y, prime) != zero(2, 2)
                for x, y in ((a, b), (a, h), (b, h))), "example commutes")
    info = theorem_data(a, b, h, prime)
    require(info == {"sectors": [0, 2, 2, 2], "n": 6, "rank_p": 4, "rank_q": 4},
            "sharp noncommuting example")
    items = (("A", a), ("B", b), ("H", h), ("P", w["P"]), ("Q", w["Q"]))
    if prime:
        matrices = {name: encode(value) for name, value in items}
    else:
        matrices = {name: [[str(x) for x in row] for row in value.rows]
                    for name, value in items}
    return {"field": prime or "Q", **info, **matrices}


def canonical(value):
    return (json.dumps(value, sort_keys=True, indent=2) + "\n").encode()


def fixture_bytes(value):
    """Keep each raw-matrix fixture on one line for reviewable, bounded receipts."""
    header = {key: item for key, item in value.items() if key != "fixtures"}
    prefix = json.dumps(header, sort_keys=True, indent=2).removesuffix("\n}")
    rows = ["    " + json.dumps(item, sort_keys=True, separators=(",", ":"))
            for item in value["fixtures"]]
    return (prefix + ',\n  "fixtures": [\n' + ",\n".join(rows) + "\n  ]\n}\n").encode()


def run():
    counts = {"ordered_X_mutation_detected": 0, "ordered_Y_mutation_detected": 0}
    fixtures = finite_cases(counts)
    wider_cases(counts)
    controls = rejection_controls()
    require(counts["ordered_X_mutation_detected"] > 0 and
            counts["ordered_Y_mutation_detected"] > 0, "no factor-order witnesses")
    result = {"schema_version": 1, "status": "PASS_ARBITRARY_PIVOT_SCHUR_MINIMUM",
              "counts": counts, "rejected_controls": controls,
              "binary_fixture_count": len(fixtures["fixtures"]),
              "binary_fixture_sha256": hashlib.sha256(fixture_bytes(fixtures)).hexdigest(),
              "noncommuting_examples": [noncommuting_example(0), noncommuting_example(3)],
              "scope": "Finite corroboration of PROOF.md; no physical admission or new kappa."}
    return fixtures, result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true",
                        help="regenerate this package's FIXTURES.json and RESULT.json")
    args = parser.parse_args()
    fixtures, result = run()
    for name, value in (("FIXTURES.json", fixtures), ("RESULT.json", result)):
        expected = fixture_bytes(value) if name == "FIXTURES.json" else canonical(value)
        path = HERE / name
        if args.write:
            path.write_bytes(expected)
        else:
            require(path.stat().st_size <= 2 * 1024 * 1024, "receipt size cap")
            require(path.read_bytes() == expected, f"regenerated payload differs: {name}")
    print(json.dumps({"status": result["status"], "counts": result["counts"],
                      "binary_fixture_count": result["binary_fixture_count"],
                      "rejected_controls": result["rejected_controls"]}, sort_keys=True))


if __name__ == "__main__":
    main()
