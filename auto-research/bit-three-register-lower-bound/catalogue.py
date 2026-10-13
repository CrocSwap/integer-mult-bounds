"""Enumerate the complete scalar catalogue with explicit binary subspaces."""

from collections import Counter
from itertools import combinations, combinations_with_replacement, permutations, product
from math import factorial, prod
from pathlib import Path
import argparse
import json

VECTORS = tuple(product(range(2), repeat=3))
POSITIONS = ((0, 1), (0, 2), (1, 0), (1, 2), (2, 0), (2, 1))


def xor(a, b):
    return tuple(x ^ y for x, y in zip(a, b))


def closure(vectors, zero):
    space = {zero}
    for vector in vectors:
        space.update([xor(vector, other) for other in space])
    return frozenset(space)


def multiply(a, b):
    return tuple(sum(a[3 * i + k] * b[3 * k + j] for k in range(3)) % 2
                 for i in range(3) for j in range(3))


def action(matrix, vector):
    return tuple(sum(matrix[3 * i + j] * vector[j] for j in range(3)) % 2
                 for i in range(3))


def encode(matrix):
    return sum(value << i for i, value in enumerate(matrix))


def off(matrix):
    return tuple(matrix[3 * i + j] for i, j in POSITIONS)


def transpose(matrix):
    return tuple(matrix[3 * j + i] for i in range(3) for j in range(3))


def conjugate(matrix, permutation):
    return tuple(matrix[3 * permutation[i] + permutation[j]]
                 for i in range(3) for j in range(3))


def catalogue():
    projectors = tuple(sorted(
        (matrix for matrix in product(range(2), repeat=9)
         if len({action(matrix, v) for v in VECTORS}) == 2
         and multiply(matrix, matrix) == matrix), key=encode))
    by_code = {encode(matrix): matrix for matrix in projectors}
    patterns = set(map(off, projectors)) - {(0,) * 6}
    lines = [frozenset(((0, 0, 0), v)) for v in VECTORS[1:]]
    planes = {closure((v, w), (0, 0, 0)) for v, w in combinations(VECTORS[1:], 2)}
    subspaces = set(lines) | planes
    flags = [(line, plane) for line in lines for plane in planes if line <= plane]
    invariant = {matrix: {space for space in subspaces
                         if all(action(matrix, v) in space for v in space)}
                 for matrix in projectors}

    def preserved(pool):
        return set.intersection(subspaces, *(invariant[matrix] for matrix in pool))

    def has_flag(pool):
        common = preserved(pool)
        return any(line in common and plane in common for line, plane in flags)

    def transforms(pool):
        return [tuple(encode(conjugate(transpose(matrix) if turn else matrix, permutation))
                      for matrix in pool)
                for permutation in permutations(range(3)) for turn in (False, True)]

    spaces = {frozenset(((0,) * 6,))}
    for _ in range(3):
        spaces |= {closure(tuple(space) + (pattern,), (0,) * 6)
                   for space in spaces for pattern in patterns}
    records = []
    for space in spaces:
        pool = tuple(matrix for matrix in projectors if off(matrix) in space)
        noncoordinate = tuple(matrix for matrix in pool if any(off(matrix)))
        records.append((len(space).bit_length() - 1, pool, noncoordinate))

    # This complete classification is the finite step in the span-six proof.
    exceptions = []
    for dimension, _, pool in records:
        if dimension == 2 and not has_flag(pool):
            assert len(pool) == 3
            assert all(has_flag(pool[:i] + pool[i + 1:]) for i in range(3))
            exceptions.append(tuple(sorted(map(encode, pool))))
    representative = tuple(by_code[code] for code in (3, 18, 360))
    expected_exceptions = {tuple(sorted(encode(conjugate(matrix, permutation))
                                        for matrix in representative))
                           for permutation in permutations(range(3))}
    assert set(exceptions) == expected_exceptions and len(exceptions) == 6
    basis = (1, 1, 0, 0, 1, 0, 0, 0, 1)
    assert [encode(multiply(multiply(basis, matrix), basis))
            for matrix in representative] == [1, 16, 511]

    canonical = {min(tuple(sorted(row)) for row in transforms(pool)): dimension
                 for dimension, pool, _ in records}
    counts = Counter()
    passing = []
    dimensions = Counter()
    for key, dimension in sorted(canonical.items(), key=lambda item: (item[1], item[0])):
        if dimension == 0:
            continue
        pool = tuple(by_code[code] for code in key)
        stabilizers = [tuple(key.index(code) for code in row)
                       for row in transforms(pool) if set(row) == set(key)]
        support_cache = {}
        # Precompute the seven row and seven column incidence tests.
        incidence = []
        for vector in VECTORS[1:]:
            for turn in (False, True):
                images = []
                for matrix in pool:
                    matrix = transpose(matrix) if turn else matrix
                    image = next(action(matrix, v) for v in VECTORS if any(action(matrix, v)))
                    images.append(sum(a * b for a, b in zip(vector, image)) % 2)
                incidence.append(images)
        for gates in combinations_with_replacement(range(len(pool)), 8):
            support = tuple(sorted(set(gates)))
            if support not in support_cache:
                occurring = tuple(pool[i] for i in support)
                full = len(closure(map(off, occurring), (0,) * 6)) == 2 ** dimension
                irreducible = not preserved(occurring)
                flag = dimension < 3 or not has_flag(tuple(m for m in occurring if any(off(m))))
                support_cache[support] = full, irreducible, flag
            full, irreducible, flag = support_cache[support]
            if not full:
                continue
            counts['full_rank_multiplicities'] += 1
            if not irreducible:
                continue
            counts['irreducible'] += 1
            if not flag:
                continue
            counts['nonzero_flag_pass'] += 1
            multiplicity = tuple(gates.count(i) for i in range(len(pool)))
            if any(sum(a * b for a, b in zip(multiplicity, row)) < 3 for row in incidence):
                continue
            counts['distance_pass'] += 1
            variants = []
            for symmetry in stabilizers:
                transformed = [0] * len(pool)
                for i, j in enumerate(symmetry):
                    transformed[j] = multiplicity[i]
                variants.append(tuple(transformed))
            if multiplicity != min(variants):
                continue
            counts['canonical_pass'] += 1
            dimensions[dimension] += 1
            passing.append(tuple(key[i] for i in gates))
    passing.sort()
    assert len(passing) == len(set(passing))
    summary = {
        'projectors': len(projectors), 'nonzero_patterns': len(patterns),
        'pattern_spaces': dict(sorted(Counter(dimension for dimension, _, _ in records).items())),
        'complete_flags': len(flags), 'plane_exceptions': len(exceptions),
        'canonical_pools': len(canonical), 'filter_counts': dict(counts),
        'families_by_dimension': dict(sorted(dimensions.items())), 'families': len(passing),
        'orders': sum(factorial(8) // prod(factorial(c) for c in Counter(word).values())
                      for word in passing),
    }
    return passing, summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    words, summary = catalogue()
    args.output.write_text(str(len(words)) + '\n' + ''.join(
        ' '.join(map(str, (index, *word))) + '\n' for index, word in enumerate(words)))
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
