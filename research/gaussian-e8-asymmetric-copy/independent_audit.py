#!/usr/bin/env python3
"""Independently audit the six-plane and hyperplane incidence certificates.

Run from any directory. This script imports no package geometry or verifier.
It builds doubled real E8 roots, uses integer Gram determinants for plane
closures, and checks the saved identities with binary integer elimination.
All validation remains active with optimized Python.
"""
import hashlib
from itertools import combinations, product
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def require(condition, message):
    if not condition:
        raise ValueError(message)


def rotate(root):
    return tuple(value for k in range(4) for value in (-root[2 * k + 1], root[2 * k]))


def reconstruct_geometry():
    roots = []
    for a, b in combinations(range(8), 2):
        for x, y in product((-2, 2), repeat=2):
            root = [0] * 8
            root[a], root[b] = x, y
            roots.append(tuple(root))
    roots.extend(root for root in product((-1, 1), repeat=8)
                 if sum(value < 0 for value in root) % 2 == 0)
    root_set = set(roots)
    require(len(roots) == len(root_set) == 240, "root count")
    require(all(rotate(root) in root_set for root in roots), "rotation closure")
    lines = sorted({min(root, rotate(root), tuple(-x for x in root),
                        tuple(-x for x in rotate(root))) for root in roots})
    require(len(lines) == 60, "line count")
    gram = []
    for left in lines:
        row = []
        for right in lines:
            real = sum(a * b for a, b in zip(left, right))
            imag = -sum(a * b for a, b in zip(left, rotate(right)))
            require(real % 4 == imag % 4 == 0, "nonintegral normalized Gram")
            row.append((real // 4, imag // 4))
        gram.append(row)
    require(all(gram[i][i] == (2, 0) for i in range(60)), "Gram diagonal")
    return lines, gram


def multiply(a, b):
    return (a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0])


def norm(a):
    return a[0] ** 2 + a[1] ** 2


def determinant3(gram, i, j, k):
    # For the Hermitian matrix with diagonal 2 and upper entries a,b,c:
    # det = 8 - 2(|a|^2+|b|^2+|c|^2) + 2 Re(a*c*conj(b)).
    a, b, c = gram[i][j], gram[i][k], gram[j][k]
    return 8 - 2 * (norm(a) + norm(b) + norm(c)) + 2 * multiply(
        multiply(a, c), (b[0], -b[1]))[0]


def binary_rank(rows):
    pivots = {}
    for row in rows:
        while row:
            pivot = row.bit_length() - 1
            if pivot not in pivots:
                pivots[pivot] = row
                break
            row ^= pivots[pivot]
    return len(pivots)


def selected_xor(rows, selection):
    require(selection >= 0 and selection.bit_length() <= len(rows), "coefficient range")
    result = 0
    for i, row in enumerate(rows):
        if selection >> i & 1:
            result ^= row
    return result


def audit():
    six_saved = json.loads((HERE / 'search/six_plane_certificate.json').read_text())
    geometry_saved = json.loads((HERE / 'geometry/verification.json').read_text())
    hyper_saved = geometry_saved['hyperplane_rectangle_kernel_certificate']
    lines, gram = reconstruct_geometry()
    line_hash = hashlib.sha256(json.dumps(lines, separators=(',', ':')).encode()).hexdigest()
    require(line_hash == six_saved['line_coordinates_sha256'] ==
            geometry_saved['line_coordinates_sha256'], "line ordering or coordinate hash")

    require(all(4 - norm(gram[i][j]) > 0 for i, j in combinations(range(60), 2)),
            "distinct lines must span a positive plane")
    # Positive-definite Gram determinants vanish exactly on dependent triples.
    planes = sorted({tuple(k for k in range(60) if determinant3(gram, i, j, k) == 0)
                     for i, j in combinations(range(60), 2)})
    six = [plane for plane in planes if len(plane) == 6]
    require(len(six) == 30, "six-plane count")
    require(six == [tuple(plane) for plane in six_saved['six_line_planes']], "six-plane catalog")
    incidence = [sum(1 << j for j, plane in enumerate(six) if i in plane) for i in range(60)]
    require(binary_rank(incidence) == 25, "six-plane incidence rank")
    witnesses = six_saved['incidence_row_reconstruction_witnesses']
    require(len(witnesses) == 60, "row witness count")
    for i, witness in enumerate(witnesses):
        require(len(witness) == len(set(witness)) == 7, "row witness size")
        require(all(0 <= j < 60 and j != i and gram[i][j] != (0, 0) for j in witness),
                "row witness uses a free or diagonal entry")
        require(selected_xor(incidence, sum(1 << j for j in witness)) == incidence[i],
                "row reconstruction")
        eight = {i, *witness}
        require(all(gram[a][b] != (0, 0) for a, b in combinations(eight, 2)),
                "eight-set is not pairwise nonorthogonal")
        require(all(len(eight.intersection(plane)) in (0, 2) for plane in six),
                "eight-set intersection count")

    hyperplanes = [{i for i in range(60) if gram[u][i] == (0, 0)} for u in range(60)]
    require(all(len(plane) == 15 for plane in hyperplanes), "root-hyperplane size")
    require(all(any(determinant3(gram, *triple) > 0 for triple in combinations(plane, 3))
                for plane in hyperplanes), "root-hyperplane rank less than three")
    pairs = [(u, v) for u in range(60) for v in range(60) if gram[u][v] == (0, 0)]
    require(len(pairs) == 900, "orthogonal-normal pair count")
    pairs += [(u, u) for u in range(60)]
    require([list(pair) for pair in pairs] == hyper_saved['normal_pairs'], "normal-pair ordering")
    forced = [(i, j) for i in range(60) for j in range(60)
              if i != j and gram[i][j] != (0, 0)]
    require(len(forced) == 2640, "forbidden-entry count")
    index = {pair: i for i, pair in enumerate(forced)}
    columns = [sum(1 << index[i, j] for i in hyperplanes[u] for j in hyperplanes[v]
                   if (i, j) in index) for u, v in pairs]
    diagonals = [sum(1 << i for i in hyperplanes[u] & hyperplanes[v]) for u, v in pairs]
    require(binary_rank(columns) == 880, "hyperplane forced rank")
    require(binary_rank(columns[:900]) == 840, "rank-two hyperplane forced rank")
    kernel = [int(value, 16) for value in hyper_saved['kernel_basis_hex']]
    require(len(kernel) == binary_rank(kernel) == 80, "hyperplane kernel basis")
    for relation in kernel:
        require(selected_xor(columns, relation) == 0, "hyperplane kernel relation")
        require(selected_xor(diagonals, relation) == relation >> 900, "hyperplane coefficient identity")

    feasible = int(hyper_saved['feasible_not_optimized_solution_hex'], 16)
    require(selected_xor(columns, feasible) == 0, "feasible forbidden entries")
    require(selected_xor(diagonals, feasible) == (1 << 60) - 1, "feasible diagonal")
    # Each hyperplane has rank three. Its pairing with another has rank two
    # exactly when their distinct normals are orthogonal, by the kernel formula.
    cost = sum((3 if u == v else 2) for i, (u, v) in enumerate(pairs) if feasible >> i & 1)
    require(cost == hyper_saved['feasible_not_optimized_solution_cost'] == 820, "feasible cost")
    require(binary_rank(sum(1 << i for i in plane) for plane in hyperplanes) == 60,
            "orthogonality matrix rank")
    return dict(status='PASS independent Gaussian E8 incidence audit',
                package_geometry_imports=False, roots=240, lines=60,
                six_planes=30, incidence_rank=25, checked_row_witnesses=60,
                hyperplane_types=960, hyperplane_forced_rank=880,
                hyperplane_kernel_dimension=80, feasible_hyperplane_cost=820,
                scope='Exact finite incidence identities; no unrestricted decoder optimum claim.')


if __name__ == '__main__':
    print(json.dumps(audit(), sort_keys=True))
