#!/usr/bin/env python3
"""Exact finite corroboration of the positive-width boundary-rank horizon."""

import argparse
from collections import Counter
import hashlib
from itertools import combinations, product
import json
from pathlib import Path


def need(condition, message):
    if not condition:
        raise ValueError(message)


def horizon(dimension, seed_rank, boundary_rank):
    need(type(dimension) is int and 0 <= dimension <= 32, 'dimension')
    need(type(seed_rank) is int and 0 <= seed_rank <= dimension, 'seed rank')
    need(type(boundary_rank) is int and 0 <= boundary_rank <= dimension,
         'boundary rank')
    if seed_rank == 0 or boundary_rank == 0:
        return 0
    return max(1, dimension - seed_rank - boundary_rank + 2)


def basis(rows, dimension):
    """Canonical binary RREF, using row XORs rather than the endpoint oracle."""
    pivots = [0] * dimension
    for original in rows:
        value = original
        for pivot in range(dimension - 1, -1, -1):
            if (value >> pivot) & 1:
                if pivots[pivot]:
                    value ^= pivots[pivot]
                else:
                    pivots[pivot] = value
                    break
    for pivot in range(dimension):
        for other in range(pivot + 1, dimension):
            if (pivots[other] >> pivot) & 1:
                pivots[other] ^= pivots[pivot]
    return tuple(row for row in pivots if row)


def row_action(row, transition):
    value = 0
    for index, matrix_row in enumerate(transition):
        if (row >> index) & 1:
            value ^= matrix_row
    return value


def positive_rank(left, transitions, dimension):
    rows = [row_action(row, transition)
            for transition in transitions for row in left]
    return len(basis(rows, dimension))


def all_subspaces(dimension):
    spaces = {()}
    for size in range(1, dimension + 1):
        for rows in combinations(range(1, 1 << dimension), size):
            reduced = basis(rows, dimension)
            if len(reduced) == size:
                spaces.add(reduced)
    return tuple(sorted(spaces))


def matrix_columns(transition):
    dimension = len(transition)
    return tuple(sum(((transition[i] >> j) & 1) << i
                     for i in range(dimension)) for j in range(dimension))


def first_discrepancy(left, transitions, right, depth):
    """Literal word tree, retaining duplicate paths and using column dot products."""
    columns = tuple(matrix_columns(matrix) for matrix in transitions)
    frontier = [(left, ())]
    blocks = 0
    for width in range(1, depth + 1):
        following = []
        for rows, word in frontier:
            for symbol, matrix in enumerate(columns):
                advanced = tuple(sum(((row & column).bit_count() & 1) << j
                                     for j, column in enumerate(matrix))
                                 for row in rows)
                blocks += 1
                for output_role, row in enumerate(advanced):
                    for input_role, column in enumerate(right):
                        if (row & column).bit_count() & 1:
                            return width, blocks, word + (symbol,), output_role, input_role
                following.append((advanced, word + (symbol,)))
        frontier = following
    return 0, blocks, (), -1, -1


def census(dimension, alphabet_size):
    spaces = all_subspaces(dimension)
    matrices = tuple(product(range(1 << dimension), repeat=dimension))
    histogram = Counter()
    cases = blocks = shortened = 0
    for transitions in product(matrices, repeat=alphabet_size):
        for left in spaces:
            seed = positive_rank(left, transitions, dimension)
            for right in spaces:
                bound = horizon(dimension, seed, len(right))
                first, work, _, _, _ = first_discrepancy(
                    left, transitions, right, dimension + 1)
                need(first == 0 or (bound > 0 and first <= bound), 'horizon violation')
                need(bound != 0 or first == 0, 'zero-boundary violation')
                cases += 1
                blocks += work
                shortened += int(bound > 0 and bound < dimension - seed + 1)
                histogram[str(first)] += 1
    return dict(dimension=dimension, alphabet_size=alphabet_size,
                subspaces=len(spaces), cases=cases, endpoint_blocks=blocks,
                strictly_shorter_horizons=shortened,
                first_discrepancy_histogram=dict(sorted(histogram.items())))


def sharp_instance(dimension, seed, boundary):
    length = horizon(dimension, seed, boundary)
    transition = [1 << i for i in range(dimension)]
    if seed + boundary <= dimension + 1:
        start = seed - 1
        stop = start + length - 1
        for index in range(start, stop + 1):
            transition[index] = 1 << (start if index == stop else index + 1)
        left = tuple(1 << i for i in range(seed - 1)) + (1 << stop,)
        right = (1 << stop,) + tuple(1 << i for i in range(stop + 1, dimension))
    else:
        left = tuple(1 << i for i in range(seed))
        right = tuple(1 << i for i in range(dimension - boundary, dimension))
    need(len(left) == seed and len(right) == boundary, 'sharp boundary shapes')
    return left, (tuple(transition),), right


def sharp_cases():
    count = 0
    transcript = hashlib.sha256()
    for dimension in range(1, 13):
        for seed in range(1, dimension + 1):
            for boundary in range(1, dimension + 1):
                left, transitions, right = sharp_instance(dimension, seed, boundary)
                need(positive_rank(left, transitions, dimension) == seed, 'sharp seed rank')
                need(len(basis(right, dimension)) == boundary, 'sharp right rank')
                first, _, _, _, _ = first_discrepancy(left, transitions, right, dimension)
                need(first == horizon(dimension, seed, boundary), 'sharp first width')
                transcript.update(f'{dimension},{seed},{boundary},{first}\n'.encode())
                count += 1
    return dict(cases=count, transcript_sha256=transcript.hexdigest())


def controls():
    bad = ((-1, 0, 0), (33, 0, 0), (3, -1, 1), (3, 4, 1),
           (3, 1, -1), (3, 1, 4), (True, 1, 1), (3, True, 1), (3, 1, False))
    rejected = 0
    for arguments in bad:
        try:
            horizon(*arguments)
        except ValueError:
            rejected += 1
        else:
            raise ValueError('invalid domain accepted')
    left, transitions, right = sharp_instance(8, 2, 3)
    first, _, _, _, _ = first_discrepancy(left, transitions, right, 8)
    need(first == 5 and first > 8 - 2 - 3 + 1, 'off-by-one control')
    # Only the mixed word (0,1) is nonzero. Repeated-symbol testing misses it.
    mixed = ((2, 0, 0), (0, 4, 0))
    hit = first_discrepancy((1,), mixed, (4,), 4)
    need(hit[0] == 2 and hit[2] == (0, 1), 'mixed physical word')
    for matrix in mixed:
        need(first_discrepancy((1,), (matrix,), (4,), 4)[0] == 0,
             'constant-word trap')
    # The only discrepancy can occur in a required returned-role block.
    need(first_discrepancy((0, 1), ((1,),), (0, 1), 1)[3:] == (1, 1),
         'complete-role control')
    need(first_discrepancy((0,), ((1,),), (0,), 3)[0] == 0,
         'dropped-role control')
    need(horizon(0, 0, 0) == 0, 'zero dimension')
    return dict(invalid_domains_rejected=rejected, semantic_controls=5)


def report():
    censuses = [census(dimension, 1) for dimension in range(1, 4)]
    censuses += [census(dimension, 2) for dimension in range(1, 3)]
    result = dict(status='PASS_BOUNDARY_RANK_HORIZON', censuses=censuses,
                  sharpness=sharp_cases(), controls=controls())
    result['cases'] = sum(row['cases'] for row in censuses)
    result['endpoint_blocks'] = sum(row['endpoint_blocks'] for row in censuses)
    package = Path(__file__).resolve().parent
    names = ('README.md', 'PROOF.md', 'TASK.json', 'SOURCES.json', 'VERIFY.json', 'verify.py')
    result['source_sha256'] = {name: hashlib.sha256((package / name).read_bytes()).hexdigest()
                               for name in names}
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--emit', type=Path, help='exclusively create a generated receipt')
    arguments = parser.parse_args()
    result = report()
    encoded = json.dumps(result, sort_keys=True, indent=2) + '\n'
    if arguments.emit is not None:
        with arguments.emit.open('x', encoding='utf-8') as stream:
            stream.write(encoded)
    else:
        expected = json.loads((Path(__file__).resolve().parent / 'RESULT.json').read_text())
        need(encoded == json.dumps(expected, sort_keys=True, indent=2) + '\n',
             'complete typed receipt mismatch')
    print(encoded, end='')


if __name__ == '__main__':
    main()
