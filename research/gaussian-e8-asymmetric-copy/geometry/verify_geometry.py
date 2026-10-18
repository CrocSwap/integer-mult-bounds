#!/usr/bin/env python3
"""Rebuild Gaussian E8 geometry and verify finite ingredients of the planar bound."""
from collections import Counter
from fractions import Fraction
import hashlib
from itertools import combinations
import json
from pathlib import Path
import random
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from geometry.core import Geometry, e8_roots, gaussian_rank, hermitian, mul, orthogonal_complement, rowspace


ORTHOGONAL_FRAME_PARTITION = (
    (0, 45, 54, 59), (1, 12, 55, 58), (2, 11, 56, 57),
    (3, 10, 48, 51), (4, 9, 49, 50), (8, 13, 43, 53),
    (5, 20, 38, 46), (17, 23, 32, 42), (16, 26, 33, 39),
    (14, 19, 37, 44), (6, 21, 35, 52), (7, 28, 30, 47),
    (15, 22, 36, 41), (18, 27, 29, 40), (24, 25, 31, 34),
)


def rational_rank(matrix):
    """Independent rational Gaussian elimination, with Fraction arithmetic."""
    work = [[Fraction(value) for value in row] for row in matrix]
    rank = 0
    for column in range(len(work[0]) if work else 0):
        pivot = next((i for i in range(rank, len(work)) if work[i][column]), None)
        if pivot is None:
            continue
        work[rank], work[pivot] = work[pivot], work[rank]
        value = work[rank][column]
        work[rank] = [entry / value for entry in work[rank]]
        for i in range(rank + 1, len(work)):
            value = work[i][column]
            work[i] = [a - value * b for a, b in zip(work[i], work[rank])]
        rank += 1
    return rank


def realified_rank(matrix):
    real = []
    for row in matrix:
        real.append([value for a, b in row for value in (a, -b)])
        real.append([value for a, b in row for value in (b, a)])
    rank = rational_rank(real)
    assert rank % 2 == 0
    return rank // 2


def binary_rank(rows):
    basis = {}
    for row in rows:
        while row:
            pivot = row.bit_length() - 1
            if pivot not in basis:
                basis[pivot] = row
                break
            row ^= basis[pivot]
    return len(basis)


def all_subsets(support):
    return [tuple(support[i] for i in range(len(support)) if mask >> i & 1)
            for mask in range(1 << len(support))]


def verify():
    geometry = Geometry()
    roots = e8_roots()
    assert len(roots) == len(set(roots)) == 240
    assert len(geometry.lines) == 60 and geometry.rank(range(60)) == 4
    for i, row in enumerate(geometry.gram):
        assert row[i] == (8, 0)
        for j, (real, imag) in enumerate(row):
            assert geometry.gram[j][i] == (real, -imag)
            assert real % 4 == imag % 4 == 0

    flat_families = geometry.flats(3)
    census = {rank: dict(Counter(map(len, flats))) for rank, flats in flat_families.items()}
    assert census == {0: {0: 1}, 1: {1: 60}, 2: {2: 360, 3: 320, 6: 30},
                      3: {4: 960, 6: 480, 15: 60}}
    pair_owners = Counter()
    for flat in flat_families[2]:
        assert geometry.rank(flat) == 2
        assert geometry.closure(flat) == flat
        for pair in combinations(flat, 2):
            pair_owners[pair] += 1
        # Every line in a complex plane has at most one orthogonal line there.
        assert all(sum(geometry.gram[i][j] == (0, 0) for j in flat) <= 1 for i in flat)
    assert len(pair_owners) == 1770 and set(pair_owners.values()) == {1}

    rng = random.Random(3476255234)
    independent_checks = 0
    for case in range(160):
        readers = tuple(sorted(rng.sample(range(60), rng.randrange(0, 9))))
        sources = tuple(sorted(rng.sample(range(60), rng.randrange(0, 9))))
        direct = [[geometry.gram[i][j] for j in sources] for i in readers]
        assert geometry.pairing_rank(readers, sources) == realified_rank(direct)
        assert geometry.rank(readers) == realified_rank([geometry.vectors[i] for i in readers])
        shuffled = list(readers)
        rng.shuffle(shuffled)
        assert rowspace(geometry.vectors[i] for i in shuffled) == geometry.basis(readers)
        independent_checks += 2
    for case in range(160):
        rows, columns = rng.randrange(0, 7), rng.randrange(0, 7)
        matrix = [[(rng.randrange(-4, 5), rng.randrange(-4, 5)) for _ in range(columns)]
                  for _ in range(rows)]
        assert gaussian_rank(matrix) == realified_rank(matrix)
        scaled = [tuple(mul((2, 3), value) for value in row) for row in matrix]
        assert rowspace(scaled) == rowspace(matrix)
        independent_checks += 1

    # Check all rectangles in one flat of each possible size. The proof covers
    # all planes; this independently confirms its geometric cases on E8 data.
    local_reports = []
    for size in (2, 3, 6):
        flat = next(flat for flat in flat_families[2] if len(flat) == size)
        subsets = all_subsets(flat)
        ranks = Counter()
        for readers in subsets:
            for sources in subsets:
                rank = geometry.pairing_rank(readers, sources)
                ranks[rank] += 1
                if rank == 0:
                    assert all(geometry.gram[i][j] == (0, 0)
                               for i in readers for j in sources)
                    assert not (set(readers) & set(sources))
                elif rank == 1:
                    assert len(readers) == 1 or len(sources) == 1
                else:
                    assert rank == 2
        allowed = [(i, j) for i in range(size) for j in range(size)
                   if i == j or geometry.gram[flat[i]][flat[j]] == (0, 0)]
        rank_vs_diagonal = Counter()
        for mask in range(1 << len(allowed)):
            rows = [0] * size
            diagonal = 0
            for bit, (i, j) in enumerate(allowed):
                if mask >> bit & 1:
                    rows[i] |= 1 << j
                    diagonal += (i == j)
            rank = binary_rank(rows)
            assert diagonal <= 2 * rank
            rank_vs_diagonal[(rank, diagonal)] += 1
        local_reports.append(dict(size=size, representative=flat,
                                  rectangle_count=len(subsets)**2,
                                  pairing_rank_counts=dict(ranks),
                                  fitting_matrix_count=1 << len(allowed),
                                  fitting_rank_diagonal_counts={str(k): v for k, v in rank_vs_diagonal.items()}))

    # Pairing rank alone does not imply the common-plane restriction.
    readers, sources = (0, 3), (0, 1)
    assert geometry.pairing_rank(readers, sources) == 1
    assert geometry.rank(readers + sources) == 3
    assert all(geometry.gram[i][j] != (0, 0) for i in readers for j in sources)

    # Complete classification of pairing-rank-two rectangles whose two supports
    # are full rank-three root flats. Their normals must be orthogonal.
    hyperplanes = flat_families[3]
    normals = []
    for flat in hyperplanes:
        complement = orthogonal_complement(geometry.basis(flat))
        assert len(complement) == 1
        normal = complement[0]
        assert all(hermitian(normal, geometry.vectors[i]) == (0, 0) for i in flat)
        normals.append(normal)
    hyperplane_rank2 = Counter()
    hyperplane_rank2_examples = {}
    for i, left in enumerate(hyperplanes):
        for j in range(i + 1, len(hyperplanes)):
            if hermitian(normals[i], normals[j]) == (0, 0):
                right = hyperplanes[j]
                key = tuple(sorted((len(left), len(right)))) + (len(set(left) & set(right)),)
                hyperplane_rank2[key] += 1
                hyperplane_rank2_examples.setdefault(key, (left, right))
    for left, right in hyperplane_rank2_examples.values():
        assert geometry.pairing_rank(left, right) == 2
        assert geometry.rank(left + right) == 4

    rank2_readers = tuple(i for i in range(60) if geometry.gram[0][i] == (0, 0))
    rank2_sources = tuple(i for i in range(60) if geometry.gram[45][i] == (0, 0))
    assert geometry.pairing_rank(rank2_readers, rank2_sources) == 2
    assert geometry.rank(rank2_readers + rank2_sources) == 4
    reader_basis, source_basis = (45, 46, 48), (0, 3, 5)
    assert geometry.rank(reader_basis) == geometry.rank(source_basis) == 3

    # Explicit cost-60 decoder in the extended class: each term is saturated,
    # since a four-line orthogonal frame has pairing rank four.
    assert sorted(i for frame in ORTHOGONAL_FRAME_PARTITION for i in frame) == list(range(60))
    decoder = [[0] * 60 for _ in range(60)]
    frame_terms = []
    for frame in ORTHOGONAL_FRAME_PARTITION:
        assert all(geometry.gram[i][j] == (0, 0) for i, j in combinations(frame, 2))
        charge = geometry.pairing_rank(frame, frame)
        assert charge == geometry.rank(frame) == len(frame) == 4
        for i in frame:
            for j in frame:
                decoder[i][j] ^= 1
        frame_terms.append(dict(readers=frame, sources=frame, charge=charge))
    for i in range(60):
        assert decoder[i][i] == 1
        for j in range(60):
            if i != j and geometry.gram[i][j] != (0, 0):
                assert decoder[i][j] == 0

    # A finite class outside the plane theorem: all oriented pairing-rank-two
    # pairs of root-orthogonal hyperplanes, plus the 60 symmetric hyperplanes.
    root_hyperplanes = [set(i for i in range(60) if geometry.gram[u][i] == (0, 0))
                       for u in range(60)]
    forced_pairs = [(i, j) for i in range(60) for j in range(60)
                    if i != j and geometry.gram[i][j] != (0, 0)]
    forced_index = {pair: i for i, pair in enumerate(forced_pairs)}
    normal_pairs, syndrome_columns, diagonal_columns = [], [], []
    for u in range(60):
        for v in range(60):
            left, right = root_hyperplanes[u], root_hyperplanes[v]
            if geometry.gram[u][v] != (0, 0):
                continue
            assert geometry.pairing_rank(left, right) == 2
            normal_pairs.append((u, v))
            syndrome_columns.append(sum(1 << forced_index[(i, j)] for i in left for j in right
                                        if (i, j) in forced_index))
            diagonal_columns.append(sum(1 << i for i in left & right))
    assert len(normal_pairs) == 900
    for u, flat in enumerate(root_hyperplanes):
        assert geometry.pairing_rank(flat, flat) == 3
        normal_pairs.append((u, u))
        syndrome_columns.append(sum(1 << forced_index[(i, j)] for i in flat for j in flat
                                    if (i, j) in forced_index))
        diagonal_columns.append(sum(1 << i for i in flat))
    elimination_basis = {}
    relations = []
    pivot_columns = []
    for index, column in enumerate(syndrome_columns):
        value, combination = column, 1 << index
        while value:
            pivot = value.bit_length() - 1
            if pivot not in elimination_basis:
                elimination_basis[pivot] = (value, combination)
                pivot_columns.append(index)
                break
            earlier, relation = elimination_basis[pivot]
            value ^= earlier
            combination ^= relation
        if not value:
            relations.append(combination)
    assert len(normal_pairs) == 960 and len(forced_pairs) == 2640
    assert len(elimination_basis) == 880 and len(relations) == 80
    assert binary_rank(relations) == 80
    assert binary_rank(syndrome_columns[:900]) == 840
    diagonal_images = []
    for relation in relations:
        forced, diagonal = 0, 0
        for index in range(len(normal_pairs)):
            if relation >> index & 1:
                forced ^= syndrome_columns[index]
                diagonal ^= diagonal_columns[index]
        assert forced == 0
        assert diagonal == relation >> 900
        diagonal_images.append(diagonal)
    assert binary_rank(diagonal_images) == 20
    orthogonality_rows = [sum(1 << i for i in flat) for flat in root_hyperplanes]
    assert binary_rank(orthogonality_rows) == 60

    # Confirm that the class is feasible, while the coefficient identity forces
    # all 60 rank-three terms. This explicit solution is not claimed optimal.
    image_basis = {}
    for relation, image in zip(relations, diagonal_images):
        combination = relation
        while image:
            pivot = image.bit_length() - 1
            if pivot not in image_basis:
                image_basis[pivot] = (image, combination)
                break
            earlier, previous = image_basis[pivot]
            image ^= earlier
            combination ^= previous
    target, feasible = (1 << 60) - 1, 0
    while target:
        pivot = target.bit_length() - 1
        assert pivot in image_basis
        image, combination = image_basis[pivot]
        target ^= image
        feasible ^= combination
    assert feasible >> 900 == (1 << 60) - 1
    feasible_cost = sum(3 if u == v else 2 for index, (u, v) in enumerate(normal_pairs)
                        if feasible >> index & 1)
    forced, diagonal = 0, 0
    for index in range(len(normal_pairs)):
        if feasible >> index & 1:
            forced ^= syndrome_columns[index]
            diagonal ^= diagonal_columns[index]
    assert forced == 0 and diagonal == (1 << 60) - 1

    record = dict(
        status="PASS exact Gaussian E8 geometry and planar-bound ingredients",
        seed=3476255234,
        roots=240,
        gaussian_lines=60,
        ambient_gaussian_rank=4,
        root_flat_census=census,
        line_pairs_with_unique_rank2_flat=len(pair_owners),
        independent_fraction_rank_checks=independent_checks,
        local_finite_checks=local_reports,
        restriction_witness=dict(readers=readers, sources=sources,
                                 reader_coordinates=[geometry.lines[i] for i in readers],
                                 source_coordinates=[geometry.lines[i] for i in sources],
                                 cross_gram=[[geometry.gram[i][j] for j in sources] for i in readers],
                                 pairing_rank=1, joint_span_rank=3),
        rank2_ambient_span_witness=dict(readers=rank2_readers, sources=rank2_sources,
                                       reader_basis=reader_basis, source_basis=source_basis,
                                       basis_cross_gram=[[geometry.gram[i][j] for j in source_basis]
                                                        for i in reader_basis],
                                       reader_rank=3, source_rank=3, pairing_rank=2, joint_span_rank=4),
        full_rank3_flat_pairs=dict(unordered_pairs_checked=len(hyperplanes)*(len(hyperplanes)-1)//2,
                                   pairing_rank2_count=sum(hyperplane_rank2.values()),
                                   pairing_rank2_by_sizes_and_common_lines={str(key): value
                                                                         for key, value in hyperplane_rank2.items()},
                                   scope="Full root-flat supports only; arbitrary subsets are not enumerated."),
        saturated_cost60_certificate=dict(total_cost=sum(term['charge'] for term in frame_terms),
                                           total_count=len(frame_terms), terms=frame_terms,
                                           fitting_pattern_verified=True),
        hyperplane_rectangle_kernel_certificate=dict(
            rectangle_count=960, forced_offdiagonal_rows=2640, forced_rank=880,
            kernel_dimension=80, diagonal_image_rank=20,
            diagonal_equals_symmetric_normal_coefficients=True,
            rank2_subclass_rectangle_count=900, rank2_subclass_forced_rank=840,
            rank2_subclass_kernel_dimension=60, rank2_subclass_diagonal_image_zero=True,
            orthogonality_matrix_binary_rank=60,
            normal_pairs=normal_pairs, pivot_column_indices=pivot_columns,
            kernel_basis_hex=[hex(relation) for relation in relations],
            fitting_cost_lower_bound=180,
            feasible_not_optimized_solution_hex=hex(feasible),
            feasible_not_optimized_solution_cost=feasible_cost,
            conclusion="Every fitting decoder in this class contains all 60 symmetric rank-three hyperplane terms.",
            scope="These 960 rectangles only. Other reader or source supports are not covered."),
        line_coordinates_sha256=hashlib.sha256(json.dumps(geometry.lines, separators=(',', ':')).encode()).hexdigest(),
    )
    return record


if __name__ == '__main__':
    if sys.flags.optimize:
        raise SystemExit('Run without -O: this verifier uses assertions.')
    print(json.dumps(verify(), sort_keys=True, indent=2))
