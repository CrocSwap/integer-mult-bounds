#!/usr/bin/env python3
"""Independent Gaussian-integer geometry for the Gaussian E8 copy bound.

Uses four complex coordinates and fraction-free Gaussian-integer elimination,
rather than the primary verifier's eight-dimensional rational calculation.
Only the Python standard library is needed. No repository modules are imported.
"""

from itertools import combinations, product
from math import gcd
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def add(a, b):
    return (a[0] + b[0], a[1] + b[1])


def subtract(a, b):
    return (a[0] - b[0], a[1] - b[1])


def multiply(a, b):
    return (a[0] * b[0] - a[1] * b[1],
            a[0] * b[1] + a[1] * b[0])


def hermitian(a, b):
    result = (0, 0)
    for x, y in zip(a, b):
        result = add(result, multiply((x[0], -x[1]), y))
    return result


def gaussian_rank(matrix):
    """Rank over Q(i), using only multiplication and exact integer division.

    At a pivot, row <- pivot * row - entry * pivot_row. A nonzero
    Gaussian pivot makes this an invertible row operation over Q(i).
    Dividing by the positive gcd of all real/imaginary components controls
    growth without changing rank. No floating point or modular rank is used.
    """
    if not matrix:
        return 0
    width = len(matrix[0])
    require(all(len(row) == width for row in matrix), 'ragged matrix')
    rows = [[tuple(value) for value in row] for row in matrix]
    pivot_row = 0
    for column in range(width):
        pivot = next((i for i in range(pivot_row, len(rows))
                      if rows[i][column] != (0, 0)), None)
        if pivot is None:
            continue
        rows[pivot_row], rows[pivot] = rows[pivot], rows[pivot_row]
        pivot_value = rows[pivot_row][column]
        for i in range(pivot_row + 1, len(rows)):
            entry = rows[i][column]
            if entry == (0, 0):
                continue
            for j in range(column + 1, width):
                rows[i][j] = subtract(multiply(pivot_value, rows[i][j]),
                                      multiply(entry, rows[pivot_row][j]))
            rows[i][column] = (0, 0)
            divisor = 0
            for value in rows[i][column + 1:]:
                divisor = gcd(divisor, abs(value[0]))
                divisor = gcd(divisor, abs(value[1]))
            if divisor > 1:
                rows[i][column + 1:] = [
                    (value[0] // divisor, value[1] // divisor)
                    for value in rows[i][column + 1:]]
        pivot_row += 1
        if pivot_row == len(rows):
            break
    return pivot_row


def complexify(root):
    return tuple((root[i], root[i + 1]) for i in range(0, 8, 2))


def times_i(root):
    return tuple(value for i in range(0, 8, 2)
                 for value in (-root[i + 1], root[i]))


def geometry():
    roots = set()
    for first, second in combinations(range(8), 2):
        for signs in product((-2, 2), repeat=2):
            root = [0] * 8
            root[first], root[second] = signs
            roots.add(tuple(root))
    for signs in product((-1, 1), repeat=8):
        if sum(value == -1 for value in signs) % 2 == 0:
            roots.add(signs)
    require(len(roots) == 240, 'E8 root census')
    require(all(sum(x * x for x in root) == 8 for root in roots), 'root norms')
    require({times_i(root) for root in roots} == roots, 'complex structure')
    orbit_keys = set()
    for root in roots:
        jr = times_i(root)
        orbit_keys.add(min(root, jr, tuple(-x for x in root), tuple(-x for x in jr)))
    representatives = sorted(orbit_keys)
    require(len(representatives) == 60, 'Gaussian line census')
    lines = [complexify(root) for root in representatives]
    require(gaussian_rank(lines) == 4, 'ambient complex rank')
    require(all(gaussian_rank([lines[i], lines[j]]) == 2
                for i, j in combinations(range(60), 2)),
            'distinct Gaussian lines outside unit orbits')
    gram = [[hermitian(a, b) for b in lines] for a in lines]
    check_gram(gram)
    degrees = [sum(j != i and value != (0, 0)
                   for j, value in enumerate(row)) for i, row in enumerate(gram)]
    require(set(degrees) == {44}, 'nonorthogonality degrees')
    return representatives, lines, gram


def check_gram(gram):
    require(len(gram) == 60 and all(len(row) == 60 for row in gram), 'Gram dimensions')
    for i, row in enumerate(gram):
        require(row[i] == (8, 0), 'doubled-root Gram normalization')
        for j, value in enumerate(row):
            require(value == (gram[j][i][0], -gram[j][i][1]), 'Hermitian Gram symmetry')


def pairing_rank(left, right, gram):
    return gaussian_rank([[gram[i][j] for j in right] for i in left])


def rank_two_flats(gram):
    """Enumerate all two-dimensional flats by exact 3x3 Gram determinants."""
    def norm(value):
        return value[0] * value[0] + value[1] * value[1]

    result = set()
    covered_pairs = set()
    for first, second in combinations(range(len(gram)), 2):
        if (first, second) in covered_pairs:
            continue
        flat = []
        ab = gram[first][second]
        for third in range(len(gram)):
            ac, bc = gram[first][third], gram[second][third]
            triple = multiply(multiply(ab, bc), (ac[0], -ac[1]))
            determinant = 512 - 8 * (norm(ab) + norm(ac) + norm(bc)) + 2 * triple[0]
            require(determinant >= 0, 'negative principal Gram determinant')
            if determinant == 0:
                flat.append(third)
        key = tuple(flat)
        result.add(key)
        covered_pairs.update(combinations(key, 2))
    return sorted(result)


def maximal_cliques(gram):
    """Bron--Kerbosch enumeration, used for independent certificate diagnostics."""
    adjacency = [sum(1 << j for j, value in enumerate(row)
                     if i != j and value != (0, 0))
                 for i, row in enumerate(gram)]

    def visit(chosen, possible, excluded):
        if not (possible or excluded):
            yield chosen
            return
        remaining = possible | excluded
        pivot = None
        score = -1
        while remaining:
            bit = remaining & -remaining
            index = bit.bit_length() - 1
            candidate_score = (possible & adjacency[index]).bit_count()
            if candidate_score > score:
                pivot, score = index, candidate_score
            remaining ^= bit
        candidates = possible & ~adjacency[pivot]
        while candidates:
            bit = candidates & -candidates
            index = bit.bit_length() - 1
            yield from visit(chosen | bit, possible & adjacency[index],
                             excluded & adjacency[index])
            possible ^= bit
            excluded |= bit
            candidates ^= bit

    yield from visit(0, (1 << len(gram)) - 1, 0)


def determinant(matrix):
    """Exact determinant over Gaussian integers (matrices here have size <= 3)."""
    size = len(matrix)
    if size == 0:
        return (1, 0)
    if size == 1:
        return matrix[0][0]
    if size == 2:
        return subtract(multiply(matrix[0][0], matrix[1][1]),
                        multiply(matrix[0][1], matrix[1][0]))
    result = (0, 0)
    for column in range(size):
        minor = [[value for j, value in enumerate(row) if j != column]
                 for row in matrix[1:]]
        term = multiply(matrix[0][column], determinant(minor))
        result = add(result, term) if column % 2 == 0 else subtract(result, term)
    return result


def canonical_direction(vector):
    pivot = next((value for value in vector if value != (0, 0)), None)
    if pivot is None:
        return None
    values = [multiply(value, (pivot[0], -pivot[1])) for value in vector]
    content = 0
    for real, imag in values:
        content = gcd(content, abs(real))
        content = gcd(content, abs(imag))
    return tuple((real // content, imag // content) for real, imag in values)


def flat_catalogue(lines, gram):
    """All root-generated Gaussian flats, with an independent complex basis.

    Rank-two closures use positive Gram determinants. Rank-three flats are
    kernels of the cofactor normal of each independent triple. Every flat
    has a basis among its root lines, so these enumerations are exhaustive.
    """
    catalogue = {0: (0, ())}
    for i in range(len(lines)):
        catalogue[1 << i] = (1, (i,))
    for indices in rank_two_flats(gram):
        mask = sum(1 << i for i in indices)
        catalogue[mask] = (2, indices[:2])
    normals = {}
    for basis in combinations(range(len(lines)), 3):
        rows = [lines[i] for i in basis]
        normal = []
        for column in range(4):
            minor = [[value for j, value in enumerate(row) if j != column]
                     for row in rows]
            value = determinant(minor)
            normal.append(value if column % 2 == 0 else (-value[0], -value[1]))
        key = canonical_direction(normal)
        if key is not None and key not in normals:
            normals[key] = basis
    for normal, basis in normals.items():
        mask = 0
        for index, line in enumerate(lines):
            value = (0, 0)
            for a, b in zip(normal, line):
                value = add(value, multiply(a, b))
            if value == (0, 0):
                mask |= 1 << index
        require(mask not in catalogue, 'duplicate/low-rank hyperplane')
        catalogue[mask] = (3, basis)
    basis = []
    for index, line in enumerate(lines):
        if gaussian_rank([lines[i] for i in basis] + [line]) > len(basis):
            basis.append(index)
        if len(basis) == 4:
            break
    catalogue[(1 << len(lines)) - 1] = (4, tuple(basis))
    return [(rank, mask, basis) for mask, (rank, basis) in sorted(catalogue.items())]


def has_minor_rank_at_least(left, right, gram, required):
    """Certify a rank lower bound by an explicitly nonzero Gaussian minor."""
    if required == 0:
        return True
    if len(left) + len(right) - 4 >= required:
        # Restrict the positive definite ambient form to the two subspaces:
        # rank >= dim(left) + dim(right) - ambient_dimension.
        return True
    for rows in combinations(left, required):
        for columns in combinations(right, required):
            if determinant([[gram[i][j] for j in columns] for i in rows]) != (0, 0):
                return True
    return False


def pair_bound(left, right, gram, hit_count, denominator=192):
    require(denominator > 0, 'positive clique denominator')
    needed = (hit_count + denominator - 1) // denominator
    require(has_minor_rank_at_least(left, right, gram, needed), 'clique/Gram rank inequality')


def check_clique(clique, gram):
    vertices = [i for i in range(60) if clique & (1 << i)]
    require(all(gram[i][j] != (0, 0) for i, j in combinations(vertices, 2)),
            'nonorthogonality clique')


def check_flat_record(rank, mask, basis, lines):
    require(gaussian_rank([lines[i] for i in basis]) == rank, 'flat-basis rank')
    closure = sum(1 << j for j, line in enumerate(lines)
                  if gaussian_rank([lines[i] for i in basis] + [line]) == rank)
    require(mask == closure, 'complete flat closure')


def compare_receipt(expected, actual):
    require(expected == actual, 'independent receipt differs from complete exact replay')


def check_source_payload(payload, expected_hash):
    from hashlib import sha256
    require(sha256(payload).hexdigest() == expected_hash, 'source pin mismatch')


def verify_sources():
    import json
    from hashlib import sha256

    payload = (HERE / 'SOURCES.json').read_bytes()
    manifest = json.loads(payload)
    require(manifest['source_code_imports'] == [], 'no predecessor code imports')
    seen = set()
    for source in manifest['sources']:
        relative = Path(source['path'])
        require(not relative.is_absolute() and '..' not in relative.parts, 'source path escape')
        require(source['path'] not in seen, 'duplicate source pin')
        seen.add(source['path'])
        path = (ROOT / relative).resolve()
        require(path.is_relative_to(ROOT.resolve()), 'resolved source path escape')
        check_source_payload(path.read_bytes(), source['sha256'])
    require(len(seen) > 0, 'empty source manifest')
    return {'source_manifest_sha256': sha256(payload).hexdigest(), 'source_pin_count': len(seen)}


def negative_controls(flats, lines, gram, cliques, hits, orthogonal, hyperplanes, index_by_mask):
    """Deliberately wrong claims must be rejected by the same exact primitives."""
    passed = []

    def reject(name, operation):
        try:
            operation()
        except ValueError:
            passed.append(name)
        else:
            raise ValueError('negative control accepted: ' + name)

    first, second = orthogonal[0]
    fi, fj = index_by_mask[hyperplanes[first]], index_by_mask[hyperplanes[second]]
    left, right = flats[fi][2], flats[fj][2]
    count = (hits[fi] & hits[fj]).bit_count()
    pair_bound(left, right, gram, count, 192)
    reject('overstrong_denominator_191', lambda: pair_bound(left, right, gram, count, 191))
    reject('false_rank_one_for_sharp_gram_block', lambda: require(
        pairing_rank(left, right, gram) == 1, 'incorrect pairing rank'))
    reject('orthogonal_pair_called_clique', lambda: check_clique((1 << first) | (1 << second), gram))
    doubled = [[(2 * real, 2 * imag) for real, imag in row] for row in gram]
    reject('changed_gram_normalization', lambda: check_gram(doubled))
    nonhermitian = [row[:] for row in gram]
    nonhermitian[0][1] = add(nonhermitian[0][1], (0, 1))
    reject('nonhermitian_gram', lambda: check_gram(nonhermitian))
    rank, mask, basis = next(flat for flat in flats if flat[0] == 2 and flat[1].bit_count() == 6)
    check_flat_record(rank, mask, basis, lines)
    reject('dependent_flat_basis', lambda: check_flat_record(rank, mask, (basis[0], basis[0]), lines))
    reject('omitted_flat_member', lambda: check_flat_record(rank, mask ^ (mask & -mask), basis, lines))
    reject('corrupt_bound_receipt', lambda: compare_receipt({'copy_lower_bound': 41}, {'copy_lower_bound': 40}))
    reject('corrupt_clique_count_receipt', lambda: compare_receipt({'maximum_clique_count': 639}, {'maximum_clique_count': 640}))
    from hashlib import sha256
    reject('modified_pinned_source_bytes', lambda: check_source_payload(
        b'changed source', sha256(b'pinned source').hexdigest()))
    return passed


def audit():
    from collections import Counter
    from fractions import Fraction

    sources = verify_sources()
    self_check()
    representatives, lines, gram = geometry()
    all_maximal = list(maximal_cliques(gram))
    largest = max(clique.bit_count() for clique in all_maximal)
    cliques = [clique for clique in all_maximal if clique.bit_count() == largest]
    require(largest == 12 and len(cliques) == 640, 'maximum-clique census')
    flats = flat_catalogue(lines, gram)
    census = Counter((rank, mask.bit_count()) for rank, mask, _ in flats)
    expected = {(0, 0): 1, (1, 1): 60, (2, 2): 360, (2, 3): 320,
                (2, 6): 30, (3, 4): 960, (3, 6): 480, (3, 15): 60, (4, 60): 1}
    require(dict(census) == expected, 'flat census')
    hits = [sum(1 << i for i, clique in enumerate(cliques) if clique & mask)
            for _, mask, _ in flats]
    pair_count = 0
    for first, (_, _, left) in enumerate(flats):
        for second in range(first, len(flats)):
            hit_count = (hits[first] & hits[second]).bit_count()
            pair_bound(left, flats[second][2], gram, hit_count)
            pair_count += 1
    # The 450 orthogonal line pairs yield rank-two pairs of perpendicular
    # hyperplanes. Each maximum clique meets both hyperplanes for 270 pairs.
    # Thus no nonnegative reweighting of this maximum-clique family exceeds 40.
    orthogonal = [(i, j) for i, j in combinations(range(60), 2) if gram[i][j] == (0, 0)]
    hyperplanes = [sum(1 << j for j, value in enumerate(row) if value == (0, 0))
                  for row in gram]
    require(len(orthogonal) == 450, 'orthogonal-pair census')
    index_by_mask = {mask: index for index, (_, mask, _) in enumerate(flats)}
    require(all(mask.bit_count() == 15 and flats[index_by_mask[mask]][0] == 3
                for mask in hyperplanes), 'root-normal hyperplanes')
    for first, second in orthogonal:
        fi, fj = index_by_mask[hyperplanes[first]], index_by_mask[hyperplanes[second]]
        require(pairing_rank(flats[fi][2], flats[fj][2], gram) == 2,
                'hyperplane-pair rank')
        require((hits[fi] & hits[fj]).bit_count() == 384, 'sharp pair incidence')
    require(all(sum(bool(clique & hyperplanes[i]) and bool(clique & hyperplanes[j])
                    for i, j in orthogonal) == 270 for clique in cliques),
            'maximum-clique weighting ceiling')
    for clique in all_maximal:
        size = clique.bit_count()
        incidence = sum(bool(clique & hyperplanes[i]) and bool(clique & hyperplanes[j])
                        for i, j in orthogonal)
        require(incidence == 450 - 15 * size, 'maximal-clique sharp-pair incidence')
        require(2 * incidence >= 45 * size, 'maximal-clique weighting ceiling')
    lower = Fraction(len(cliques) * largest, 192)
    ceiling = Fraction(largest * len(orthogonal) * 2, 270)
    require(lower == ceiling == 40, 'copy bound and weighting ceiling')
    controls = negative_controls(flats, lines, gram, cliques, hits,
                                 orthogonal, hyperplanes, index_by_mask)
    return {
        'status': 'PASS_INDEPENDENT_GAUSSIAN_COPY_BOUND',
        'arithmetic': 'Gaussian integers; fraction-free rank and exact minors',
        'root_count': 240, 'line_count': len(representatives),
        'maximum_clique_size': largest, 'maximum_clique_count': len(cliques),
        'maximal_clique_counts': {str(k): v for k, v in sorted(Counter(
            clique.bit_count() for clique in all_maximal).items())},
        'flat_count': len(flats),
        'flat_counts': {'%d:%d' % key: value for key, value in sorted(census.items())},
        'unordered_flat_pairs_with_repetition': pair_count,
        'maximum_clique_weight': '1/192', 'copy_lower_bound': 40,
        'maximum_clique_weighting_ceiling': 40,
        'inclusion_maximal_clique_weighting_ceiling': 40,
        'inclusion_maximal_clique_count': len(all_maximal),
        'sharp_hyperplane_pairs': len(orthogonal),
        'sharp_pair_clique_incidence': 384,
        'per_clique_sharp_pair_incidence': 270,
        'negative_controls': controls,
        'negative_control_count': len(controls),
        'geometry_self_checks': 'mandatory; distinct lines and principal two-line Gram ranks',
        **sources,
    }


def self_check():
    zero, one, imag = (0, 0), (1, 0), (0, 1)
    require(gaussian_rank([]) == 0, 'empty rank')
    require(gaussian_rank([[zero]]) == 0, 'zero rank')
    require(gaussian_rank([[one, imag], [imag, (-1, 0)]]) == 1,
            'complex dependent rank')
    require(gaussian_rank([[one, imag], [imag, one]]) == 2,
            'complex independent rank')
    representatives, lines, gram = geometry()
    for first, second in combinations(range(60), 2):
        require(gaussian_rank([lines[first], lines[second]]) == 2,
                'two distinct complex lines')
        require(pairing_rank([first, second], [first, second], gram) == 2,
                'positive two-line Gram block')
    return {'roots': 240, 'lines': len(representatives), 'complex_rank': 4,
            'nonorthogonal_degree': 44, 'two_line_checks': 1770}


if __name__ == '__main__':
    import argparse
    import json
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--geometry-only', action='store_true')
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--check', type=Path, default=HERE / 'INDEPENDENT.json')
    mode.add_argument('--write', type=Path)
    args = parser.parse_args()
    result = self_check() if args.geometry_only else audit()
    if not args.geometry_only:
        if args.write:
            with args.write.open('x', encoding='utf-8', newline='\n') as handle:
                handle.write(json.dumps(result, indent=2, sort_keys=True) + '\n')
        else:
            compare_receipt(json.loads(args.check.read_text(encoding='utf-8')), result)
    if args.geometry_only:
        print(json.dumps(result, sort_keys=True))
    else:
        print('PASS_INDEPENDENT_GAUSSIAN_COPY_BOUND lower=40 pairs=2582128 maximal_cliques=8704 controls=10')
