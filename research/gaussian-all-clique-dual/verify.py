#!/usr/bin/env python3
"""Exact all-clique Gaussian E8 dual. William Lawyer / Codex, Apache-2.0."""

import argparse
from array import array
from collections import Counter
from fractions import Fraction
import hashlib
from itertools import combinations, product
import json
from pathlib import Path
import struct

HERE = Path(__file__).resolve().parent


def require(condition, message):
    if not condition:
        raise ValueError(message)


def bits(mask):
    while mask:
        bit = mask & -mask
        yield bit.bit_length() - 1
        mask ^= bit


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def rotate(row):
    return tuple(x for i in range(0, len(row), 2)
                 for x in (-row[i + 1], row[i]))


def reduced_basis(rows):
    """Rational RREF, including all columns and zero-pivot fallback."""
    matrix = [list(map(Fraction, row)) for row in rows]
    width = len(matrix[0]) if matrix else 0
    require(all(len(row) == width for row in matrix), 'ragged rank input')
    rank = 0
    for column in range(width):
        pivot = next((i for i in range(rank, len(matrix))
                      if matrix[i][column]), None)
        if pivot is None:
            continue
        matrix[rank], matrix[pivot] = matrix[pivot], matrix[rank]
        value = matrix[rank][column]
        matrix[rank] = [x / value for x in matrix[rank]]
        for i in range(len(matrix)):
            if i != rank and matrix[i][column]:
                scale = matrix[i][column]
                matrix[i] = [x - scale * y for x, y in zip(matrix[i], matrix[rank])]
        rank += 1
    return tuple(tuple(row) for row in matrix[:rank])


def roots_and_lines():
    sparse = []
    for first, second in combinations(range(8), 2):
        for a, b in product((-2, 2), repeat=2):
            row = [0] * 8
            row[first], row[second] = a, b
            sparse.append(tuple(row))
    dense = [row for row in product((-1, 1), repeat=8)
             if sum(x == -1 for x in row) % 2 == 0]
    roots = tuple(sorted((*sparse, *dense)))
    require(len(sparse) == 112 and len(dense) == 128, 'root-family census')
    require(len(roots) == len(set(roots)) == 240, 'root census or duplication')
    require(all(dot(row, row) == 8 for row in roots), 'root norm')
    require(set(map(rotate, roots)) == set(roots), 'complex structure does not preserve roots')
    orbits = {min(row, rotate(row), tuple(-x for x in row),
                  tuple(-x for x in rotate(row))) for row in roots}
    lines = tuple(sorted(orbits))
    require(len(lines) == 60, 'Gaussian line census')
    require(len(reduced_basis(lines)) == 8, 'ambient rank')
    require(all(dot(a, b)**2 + dot(a, rotate(b))**2 < 64
                for a, b in combinations(lines, 2)), 'duplicate Gaussian projective line')
    return roots, lines


def check_orthogonal_graph(orthogonal):
    require(len(orthogonal) == 60, 'orthogonal graph order')
    require(all(mask.bit_count() == 15 for mask in orthogonal), 'orthogonal degree')
    require(all(0 <= mask < (1 << 60) and not mask >> i & 1
                for i, mask in enumerate(orthogonal)), 'orthogonal graph mask or diagonal')
    require(all((orthogonal[i] >> j & 1) == (orthogonal[j] >> i & 1)
                for i in range(60) for j in range(60)), 'graph symmetry')


def graph_data(lines):
    orthogonal = tuple(sum(1 << j for j, b in enumerate(lines)
                          if i != j and dot(a, b) == dot(a, rotate(b)) == 0)
                       for i, a in enumerate(lines))
    full = (1 << len(lines)) - 1
    adjacency = tuple(full ^ mask ^ (1 << i)
                      for i, mask in enumerate(orthogonal))
    check_orthogonal_graph(orthogonal)
    dual_rows = tuple(sum(1 << j for j in bits(orthogonal[i])
                          if (orthogonal[i] & orthogonal[j]).bit_count() == 6)
                      for i in range(len(lines)))
    pairs = tuple((i, j) for i, row in enumerate(dual_rows) for j in bits(row))
    require(len(pairs) == 180 and len(set(pairs)) == 180, 'dual pair census')
    require(all(row.bit_count() == 3 for row in dual_rows), 'dual graph degree')
    return adjacency, orthogonal, dual_rows, pairs


def check_geometry(lines, orthogonal, pairs):
    bases = [reduced_basis(row for i in bits(mask)
                           for row in (lines[i], rotate(lines[i])))
             for mask in orthogonal]
    require(all(len(basis) == 6 for basis in bases), 'root hyperplane does not span rank three')
    require(all(all(dot(row, lines[i]) == dot(row, rotate(lines[i])) == 0
                    for row in bases[i]) for i in range(60)), 'wrong root hyperplane')
    ranks = Counter()
    for i, j in pairs:
        block = tuple(tuple(dot(a, b) for b in bases[j]) for a in bases[i])
        rank = len(reduced_basis(block))
        require(rank == 4, 'dual pair has wrong rational pairing rank')
        ranks[rank // 2] += 1
    return dict(sorted(ranks.items()))


def frames_from_dual(dual_rows):
    left = (1 << len(dual_rows)) - 1
    frames = []
    while left:
        i = next(bits(left))
        mask = (1 << i) | dual_rows[i]
        require(mask.bit_count() == 4, 'dual component is not a four-frame')
        require(all(dual_rows[j] == mask ^ (1 << j) for j in bits(mask)), 'dual component is not K4')
        require(mask & left == mask, 'dual components overlap')
        left ^= mask
        frames.append(mask)
    require(len(frames) == 15, 'four-frame partition')
    return tuple(frames)


def all_cliques(adjacency):
    """Ordered extensions: each nonempty clique has a unique increasing path."""
    def visit(chosen, available):
        while available:
            bit = available & -available
            available ^= bit
            i = bit.bit_length() - 1
            extended = chosen | bit
            yield extended
            yield from visit(extended, available & adjacency[i])
    yield from visit(0, (1 << len(adjacency)) - 1)


def joint_hit_count(clique, orthogonal, dual_rows):
    hit = 0
    for i in bits(clique):
        hit |= orthogonal[i]
    return sum((row & hit).bit_count() for i, row in enumerate(dual_rows)
               if hit >> i & 1)


def check_clique(mask, adjacency):
    require(0 < mask < (1 << len(adjacency)), 'invalid clique mask')
    require(all((mask ^ (1 << i)) & ~adjacency[i] == 0 for i in bits(mask)),
            'orthogonal pair admitted as clique')


def check_dual_hit(size, count, multiplier=9):
    require(count >= multiplier * size, 'dual incidence does not dominate clique size')


def rejected(function, *args):
    try:
        function(*args)
    except ValueError:
        return
    raise ValueError('negative control unexpectedly accepted: ' + function.__name__)


def calculate():
    roots, lines = roots_and_lines()
    adjacency, orthogonal, dual_rows, pairs = graph_data(lines)
    rank_census = check_geometry(lines, orthogonal, pairs)
    frames = frames_from_dual(dual_rows)
    census, minima, witnesses = Counter(), {}, {}
    packed = array('Q')
    for clique in all_cliques(adjacency):
        size = clique.bit_count()
        count = joint_hit_count(clique, orthogonal, dual_rows)
        check_dual_hit(size, count)
        census[size] += 1
        packed.append(clique)
        if count < minima.get(size, 10**9) or (count == minima.get(size) and clique < witnesses[size]):
            minima[size], witnesses[size] = count, clique
    # Explicit little-endian encoding is independent of host array byte order.
    digest = hashlib.sha256()
    ordered = sorted(packed)
    require(all(a < b for a, b in zip(ordered, ordered[1:])), 'duplicate clique enumeration')
    for mask in ordered:
        digest.update(struct.pack('<Q', mask))
    require(census and max(census) == 12, 'maximum clique size')
    single = 1
    old_hits = joint_hit_count(single, orthogonal, orthogonal)
    require(old_hits == 42, 'original dual counterexample')
    rejected(check_dual_hit, 1, old_hits, 45)
    maximum = witnesses[12]
    rejected(check_dual_hit, 12, joint_hit_count(maximum, orthogonal, dual_rows), 10)
    partner = next(bits(orthogonal[0]))
    rejected(check_clique, 1 | (1 << partner), adjacency)
    rejected(check_clique, 0, adjacency)
    bad_pairs = tuple((i, j) for i, row in enumerate(orthogonal) for j in bits(row)
                      if (orthogonal[i] & orthogonal[j]).bit_count() == 2)
    bad_rows = tuple(sum(1 << j for a, j in bad_pairs if a == i) for i in range(60))
    rejected(check_dual_hit, 1, joint_hit_count(single, orthogonal, bad_rows), 36)
    bad_orth = list(orthogonal)
    bad_orth[0] ^= 1 << partner
    rejected(check_orthogonal_graph, bad_orth)
    # Cost 180 * 2 / 9, in Gaussian rank units. No decoder is constructed.
    return {
        'format': 'gaussian-all-clique-dual-v1', 'root_count': len(roots),
        'line_count': len(lines),
        'orthogonal_ordered_pair_count': sum(row.bit_count() for row in orthogonal),
        'dual_pair_count': len(pairs), 'dual_pairs': [list(pair) for pair in pairs],
        'dual_pairing_rank_census': {str(k): v for k, v in rank_census.items()},
        'dual_multiplier': '1/9', 'ceiling': '40',
        'frames': [list(bits(mask)) for mask in frames],
        'clique_counts': {str(k): v for k, v in sorted(census.items())},
        'clique_total': sum(census.values()),
        'minimum_dual_hits': {str(k): v for k, v in sorted(minima.items())},
        'minimum_witnesses': {str(k): list(bits(witnesses[k])) for k in sorted(witnesses)},
        'all_cliques_sha256': digest.hexdigest(),
        'all_cliques_encoding': 'nonempty masks sorted numerically, uint64 little endian',
        'original_dual_failure': {'clique': [0], 'hits': old_hits, 'required': 45},
        'negative_controls': 6,
        'inherited_primal_value': '640*12/192=40; PR738/PR770, not rebuilt here',
        'new_kappa': False,
    }


def check_sources():
    sources = json.loads((HERE / 'SOURCES.json').read_text(encoding='utf-8'))
    for relative, metadata in sources['retained_files'].items():
        target = (HERE / relative).resolve()
        require(target.is_relative_to(HERE) and target.is_file(), 'invalid retained source path')
        data = target.read_bytes()
        require(hashlib.sha256(data).hexdigest() == metadata['sha256'], 'retained source mismatch: ' + relative)
        blob = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
        require(blob == metadata['git_blob'], 'retained Git blob mismatch: ' + relative)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, help='write a new certificate file; existing files refused')
    args = parser.parse_args()
    if args.output:
        require(not args.output.exists(), 'output file already exists')
    check_sources()
    result = calculate()
    if args.output:
        with args.output.open('x', encoding='utf-8', newline='\n') as stream:
            json.dump(result, stream, indent=2)
            stream.write('\n')
    else:
        expected = json.loads((HERE / 'CERTIFICATE.json').read_text(encoding='utf-8'))
        require(result == expected, 'certificate mismatch')
    print('PASS_GAUSSIAN_ALL_CLIQUE_DUAL cliques=' + str(result['clique_total'])
          + ' ordered_pairs=180 ceiling=40 controls=6 no_new_kappa')


if __name__ == '__main__':
    main()
