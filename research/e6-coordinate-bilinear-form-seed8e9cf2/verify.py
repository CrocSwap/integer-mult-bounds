#!/usr/bin/env python3
"""Exact E6 B0 screen for one rational root-coordinate bilinear form."""

import hashlib
import itertools
import json
import sys
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ADE = ROOT / "research/root-unit-decoder-lemmas/lib/ade.py"
ADE_SHA256 = "8185afc77fd34a599094e9f93b293a5afac61f4184ec5c5a02b81ee3c0b0053c"


def check(condition, message):
    if not condition:
        raise RuntimeError(message)


def normalized_lines(vectors):
    out = set()
    for vector in vectors:
        v = tuple(vector)
        first = next((x for x in v if x), None)
        check(first is not None, "zero root")
        if first < 0:
            v = tuple(-x for x in v)
        out.add(v)
    return sorted(out)


def e8_lines_scaled():
    """The 120 E8 root lines, with every root scaled by two."""
    roots = []
    for i in range(8):
        for j in range(i + 1, 8):
            for sign in (1, -1):
                v = [0] * 8
                v[i], v[j] = 2, 2 * sign
                roots.append(v)
    for signs in itertools.product((-1, 1), repeat=8):
        if signs.count(-1) % 2 == 0:
            roots.append(signs)
    return normalized_lines(roots)


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def rref(rows, ncols):
    a = [list(map(Q, row)) for row in rows]
    pivot_cols = []
    row = 0
    for col in range(ncols):
        p = next((i for i in range(row, len(a)) if a[i][col]), None)
        if p is None:
            continue
        a[row], a[p] = a[p], a[row]
        scale = a[row][col]
        a[row] = [x / scale for x in a[row]]
        for i in range(len(a)):
            if i != row and a[i][col]:
                scale = a[i][col]
                a[i] = [x - scale * y for x, y in zip(a[i], a[row])]
        pivot_cols.append(col)
        row += 1
        if row == len(a):
            break
    return a[:row], pivot_cols


def rank_q(rows, ncols):
    return len(rref(rows, ncols)[1])


def solve_square(a, b):
    n = len(a)
    m = [list(map(Q, row)) + [Q(x)] for row, x in zip(a, b)]
    for col in range(n):
        p = next((i for i in range(col, n) if m[i][col]), None)
        check(p is not None, "coordinate Gram matrix is singular")
        m[col], m[p] = m[p], m[col]
        d = m[col][col]
        m[col] = [x / d for x in m[col]]
        for i in range(n):
            if i != col and m[i][col]:
                c = m[i][col]
                m[i] = [x - c * y for x, y in zip(m[i], m[col])]
    return [m[i][-1] for i in range(n)]


def qstr(x):
    x = Q(x)
    return f"{x.numerator}/{x.denominator}"


def matrix_rank(a):
    return rank_q(a, len(a[0]) if a else 0)


def bilinear(x, l, y):
    return sum(x[i] * l[i][j] * y[j] for i in range(len(x)) for j in range(len(y)))


def solve_family():
    source_hash = hashlib.sha256(ADE.read_bytes()).hexdigest()
    check(source_hash == ADE_SHA256, "pinned ADE root source changed")

    e8 = e8_lines_scaled()
    check(len(e8) == 120, "E8 line count")
    r1, r2 = (2, 2, 0, 0, 0, 0, 0, 0), (2, 0, 2, 0, 0, 0, 0, 0)
    check(dot(r1, r1) == dot(r2, r2) == 8 and abs(dot(r1, r2)) == 4, "A2 pin")
    roots = [r for r in e8 if dot(r, r1) == 0 and dot(r, r2) == 0]
    check(len(roots) == 36, "E6 line count")
    check(all(dot(r, r) == 8 for r in roots), "E6 root norm")

    basis = []
    for r in roots:
        if rank_q(basis + [r], 8) > len(basis):
            basis.append(r)
        if len(basis) == 6:
            break
    check(len(basis) == 6, "E6 coordinate basis rank")
    gram = [[Q(dot(x, y)) for y in basis] for x in basis]
    check(matrix_rank(gram) == 6, "basis Gram rank")
    coords = []
    for r in roots:
        rhs = [dot(b, r) for b in basis]
        coords.append(solve_square(gram, rhs))
    check(all(sum(coords[t][i] * basis[i][k] for i in range(6)) == roots[t][k]
              for t in range(36) for k in range(8)), "root coordinate reconstruction")

    orthogonal = [(t, s) for t in range(36) for s in range(36)
                  if t != s and dot(roots[t], roots[s]) == 0]
    check(len(orthogonal) == 540, "ordered B0 orthogonal-pair count")
    constraints = []
    for t, s in orthogonal:
        constraints.append([coords[t][i] * coords[s][j]
                            for i in range(6) for j in range(6)])
    reduced, pivots = rref(constraints, 36)
    free = [j for j in range(36) if j not in pivots]
    check(len(free) == 1, f"unexpected kernel dimension {len(free)}")
    f = free[0]
    vector = [Q(0)] * 36
    vector[f] = Q(1)
    for ri, p in enumerate(pivots):
        vector[p] = -reduced[ri][f]
    kernel = [[vector[6 * i + j] for j in range(6)] for i in range(6)]
    check(matrix_rank(kernel) == 6, "kernel generator is not full rank")

    factor = None
    for i in range(6):
        for j in range(6):
            if gram[i][j]:
                factor = kernel[i][j] / gram[i][j]
                break
        if factor is not None:
            break
    check(factor is not None and factor != 0, "zero kernel generator")
    check(all(kernel[i][j] == factor * gram[i][j] for i in range(6) for j in range(6)),
          "kernel is not exactly the Gram line")

    # Positive control: the Gram form vanishes on every orthogonal pair and has nonzero diagonal.
    diagonal = [bilinear(coords[t], gram, coords[t]) for t in range(36)]
    check(diagonal == [Q(8)] * 36, "Gram diagonal control")
    check(all(bilinear(coords[t], gram, coords[s]) == 0 for t, s in orthogonal),
          "Gram orthogonality control")

    # Negative controls: the zero form violates exactness; a rank-one perturbation violates B0.
    zero_diagonal = [bilinear(x, [[Q(0)] * 6 for _ in range(6)], x) for x in coords]
    check(not any(zero_diagonal), "zero-form control should fail exactness")
    mutant = [row[:] for row in gram]
    mutant[0][0] += 1
    violating = [(t, s) for t, s in orthogonal if bilinear(coords[t], mutant, coords[s]) != 0]
    check(violating, "mutated-form control should violate an orthogonal-pair zero")

    def matrix_json(m):
        return [[qstr(x) for x in row] for row in m]

    canonical = {
        "e8_lines_scaled": [list(x) for x in e8],
        "e6_lines_scaled": [list(x) for x in roots],
        "basis_scaled": [list(x) for x in basis],
        "coordinates": matrix_json(coords),
        "constraints": [[qstr(x) for x in row] for row in constraints],
    }
    hashes = {
        key: hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        for key, value in canonical.items()
    }
    return {
        "status": "PASS_E6_B0_COORDINATE_BILINEAR_RANK_FLOOR",
        "ade_source_sha256": source_hash,
        "root_counts": {"E8_lines": len(e8), "E6_lines": len(roots), "ordered_orthogonal_pairs": len(orthogonal)},
        "coordinate_basis_scaled": [list(x) for x in basis],
        "constraint_rank_Q": len(pivots),
        "kernel_dimension_Q": len(free),
        "kernel_generator": matrix_json(kernel),
        "gram_matrix": matrix_json(gram),
        "kernel_equals_gram_line": True,
        "kernel_generator_rank_Q": matrix_rank(kernel),
        "decoder_diagonal_scaled": [qstr(x) for x in diagonal],
        "mutant_orthogonal_pair_violations": len(violating),
        "negative_controls": 2,
        "positive_controls": 2,
        "input_sha256": hashes,
        "scope": "Only M=R L R^T on this fixed E6 root-coordinate realization and B0 orthogonality mask. This is not a theorem about arbitrary E6 decoders, other admissible pairings, or the selected multiplication bound.",
    }


def main():
    write = "--write" in sys.argv[1:]
    result = solve_family()
    encoded = json.dumps(result, sort_keys=True, indent=2) + "\n"
    out = HERE / "RESULT.json"
    if write:
        out.write_text(encoded)
    elif out.exists():
        check(json.loads(out.read_text()) == result, "RESULT.json differs from exact replay")
    print(result["status"],
          f"lines={result['root_counts']['E6_lines']}",
          f"orthogonal_ordered={result['root_counts']['ordered_orthogonal_pairs']}",
          f"constraint_rank={result['constraint_rank_Q']}",
          f"kernel={result['kernel_dimension_Q']}",
          f"generator_rank={result['kernel_generator_rank_Q']}",
          "no_rank_le4_in_coordinate_form_family no_new_kappa")


if __name__ == "__main__":
    main()
