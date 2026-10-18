#!/usr/bin/env python3
"""Replay an exact primal/dual clique certificate, with no solver dependency.

Jonathan Lam, with substantial OpenAI Codex assistance; Apache-2.0.
"""

import argparse
from collections import Counter
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import random

from geometry import (all_cliques, bits, contains, dot, echelon, flats,
                      geometry, maximal_cliques, pairing_rank, require)

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def digest(value):
    data = json.dumps(value, separators=(',', ':'), sort_keys=True).encode()
    return hashlib.sha256(data).hexdigest()


def fraction_rank(rows):
    """Independent ordinary Gaussian elimination over Fraction."""
    matrix = [list(map(Fraction, row)) for row in rows]
    if not matrix:
        return 0
    rank = 0
    for column in range(len(matrix[0])):
        pivot = next((i for i in range(rank, len(matrix)) if matrix[i][column]), None)
        if pivot is None:
            continue
        matrix[rank], matrix[pivot] = matrix[pivot], matrix[rank]
        q = matrix[rank][column]
        matrix[rank] = [x / q for x in matrix[rank]]
        for i in range(rank + 1, len(matrix)):
            q = matrix[i][column]
            matrix[i] = [x - q * y for x, y in zip(matrix[i], matrix[rank])]
        rank += 1
        if rank == len(matrix):
            break
    return rank


def check_sources():
    source = json.loads((HERE / 'SOURCES.json').read_text())
    for item in source['local_inputs']:
        actual = hashlib.sha256((ROOT / item['path']).read_bytes()).hexdigest()
        require(actual == item['sha256'], 'source hash mismatch: ' + item['path'])
    return {item['path']: item['sha256'] for item in source['local_inputs']}


def check_clique(mask, adjacent):
    require(0 < mask < (1 << len(adjacent)), 'invalid clique mask')
    require(all((mask ^ (1 << i)) & ~adjacent[i] == 0 for i in bits(mask)),
            'orthogonal pair in claimed clique')


def check_fitting(rectangles, adjacent):
    rows = [0] * len(adjacent)
    limit = (1 << len(adjacent)) - 1
    for readers, sources in rectangles:
        require(readers >= 0 and sources >= 0 and not ((readers | sources) & ~limit),
                'invalid rectangle support')
        for i in bits(readers):
            rows[i] ^= sources
    require(all(row & (1 << i) for i, row in enumerate(rows)), 'missing fitting diagonal')
    require(all(not (row & adjacent[i]) for i, row in enumerate(rows)),
            'forbidden nonorthogonal entry')
    return rows


def require_rejected(label, function):
    try:
        function()
    except ValueError:
        return label
    raise ValueError('negative control accepted: ' + label)


def replay():
    source_hashes = check_sources()
    reps, images, adjacent, a2_pairs, orbits = geometry()
    every_clique = all_cliques(adjacent)
    maximal = maximal_cliques(adjacent)
    largest = [q for q in every_clique if q.bit_count() == 7]
    require(max(q.bit_count() for q in every_clique) == 7, 'maximum clique size')
    require(largest == [q for q in maximal if q.bit_count() == 7],
            'independent maximum-clique enumerations disagree')
    require(len(every_clique) == len(set(every_clique)), 'duplicate clique')
    for q in every_clique:
        check_clique(q, adjacent)
    ff = flats(reps, images)
    require(len(ff) == 772 and len(largest) == 2880, 'geometry census')
    hits = [sum(1 << i for i, q in enumerate(largest) if mask & q)
            for mask, _, _ in ff]

    # All unordered pairs, INCLUDING empty supports, are checked exactly.
    # Symmetry of the Gram pairing covers the reversed order.
    pair_census = Counter()
    dual_pairs = []
    sharp_pair = None
    pair_count = 0
    for i, (left, bleft, _) in enumerate(ff):
        for k in range(i + 1):
            right, bright, _ = ff[k]
            cost = pairing_rank(bleft, bright)
            h7 = (hits[i] & hits[k]).bit_count()
            h1 = (left & right).bit_count()
            require(24 * h1 + h7 <= 960 * cost, 'primal clique inequality')
            pair_census[(h1, h7, cost)] += 1
            pair_count += 1
            if (len(bleft) == len(bright) == 6
                    and left.bit_count() == right.bit_count() == 12 and cost == 2):
                dual_pairs.append((left, right))
                require((h1, h7) == (2, 1872), 'dual-pair incidence')
                if sharp_pair is None:
                    sharp_pair = (i, k)
    require(pair_count == len(ff) * (len(ff) + 1) // 2, 'complete flat pairs')
    require(len(dual_pairs) == 240, 'dual-pair census')
    require(len(set(dual_pairs)) == 240, 'duplicate dual pair')

    # This dual is checked on EVERY literal clique, not merely on orbit
    # representatives or averages. Thus arbitrary nonuniform weights are covered.
    dual_census = Counter()
    for q in every_clique:
        hit_count = sum(bool(q & left) and bool(q & right) for left, right in dual_pairs)
        require(hit_count + 12 >= 24 * q.bit_count(), 'dual clique inequality')
        dual_census[(q.bit_count(), hit_count)] += 1
    primal = Fraction(40, 40) + Fraction(len(largest) * 7, 960)
    dual = Fraction(len(dual_pairs) * 2, 24) + Fraction(4, 2)
    require(primal == dual == 22, 'exact primal-dual equality')

    # Independent rank controls use original root generators, not RREF rows.
    rng = random.Random(48)
    rank_pairs = set((rng.randrange(len(ff)), rng.randrange(len(ff))) for _ in range(256))
    rank_pairs.add(sharp_pair)
    rank_pairs.add((0, len(ff) - 1))
    rank_pairs.add((len(ff) - 1, len(ff) - 1))
    for i, k in sorted(rank_pairs):
        aa = [v for n in ff[i][2] for v in (reps[n], images[n])]
        bb = [v for n in ff[k][2] for v in (reps[n], images[n])]
        gram = [[dot(x, y) for y in bb] for x in aa]
        require(fraction_rank(gram) == 2 * pairing_rank(ff[i][1], ff[k][1]),
                'independent Fraction Gram rank disagreement')
    # Another completeness check closes every possible one-line extension.
    flat_keys = {b for _, b, _ in ff}
    for mask, basis, _ in ff:
        for i in range(40):
            require(echelon(basis + (reps[i], images[i])) in flat_keys,
                    'missing one-line flat extension')

    identity = [(1 << i, 1 << i) for i in range(40)]
    check_fitting(identity, adjacent)
    directed = []
    for i in range(40):
        sources = (1 << i) | sum(1 << k for k in range(40)
                                if k != i and not (adjacent[i] >> k) & 1 and rng.randrange(2))
        directed.append((1 << i, sources))
    rows = check_fitting(directed, adjacent)
    require(any(bool(rows[i] & (1 << k)) != bool(rows[k] & (1 << i))
                for i in range(40) for k in range(40)), 'asymmetric positive control')
    costs = []
    for readers, sources in directed:
        aa = echelon(tuple(v for n in bits(readers) for v in (reps[n], images[n])))
        bb = echelon(tuple(v for n in bits(sources) for v in (reps[n], images[n])))
        costs.append(pairing_rank(aa, bb))
    require(costs == [1] * 40, 'cost-40 directed row decomposition')

    i, k = sharp_pair
    left, bl, _ = ff[i]
    right, br, _ = ff[k]
    h1 = (left & right).bit_count()
    h7 = (hits[i] & hits[k]).bit_count()
    orthogonal = next((i, k) for i in range(40) for k in range(i)
                      if not (adjacent[i] >> k) & 1)
    nonorthogonal = next(bits(adjacent[0]))
    controls = []
    controls.append(require_rejected('nonclique_orthogonal_pair',
        lambda: check_clique(sum(1 << n for n in orthogonal), adjacent)))
    controls.append(require_rejected('missing_decoder_diagonal',
        lambda: check_fitting(identity[1:], adjacent)))
    controls.append(require_rejected('forbidden_decoder_entry',
        lambda: check_fitting(identity + [(1, 1 << nonorthogonal)], adjacent)))
    controls.append(require_rejected('increased_maximum_clique_weight',
        lambda: require(Fraction(h1, 40) + Fraction(h7, 959) <= 2, 'invalid weight')))
    controls.append(require_rejected('source_dimension_substituted_for_pairing_rank',
        lambda: require(pairing_rank(bl, br) == len(bl) // 2, 'rank-three supports pair at rank two')))
    controls.append(require_rejected('missing_eisenstein_direction',
        lambda: pairing_rank((reps[8],), (reps[8],))))
    # Each singleton hits both flats in exactly twelve dual pairs.
    singleton = 1 << 8  # assignment seed 48 modulo 40
    single_hits = sum(bool(singleton & x) and bool(singleton & y) for x, y in dual_pairs)
    require(single_hits == 12, 'singleton dual saturation')
    controls.append(require_rejected('underweighted_dual',
        lambda: require(Fraction(1, 2) + Fraction(single_hits, 25) >= 1, 'dual weight too small')))
    reduced = list(dual_pairs)
    reduced.remove(next((x, y) for x, y in reduced if singleton & x and singleton & y))
    controls.append(require_rejected('omitted_dual_flat_pair',
        lambda: require(12 + sum(bool(singleton & x) and bool(singleton & y) for x, y in reduced)
                        >= 24, 'incomplete dual coverage')))

    return {
        'status': 'PASS_EISENSTEIN_CLIQUE_COPY_BOUND',
        'base_commit': '66849e1475c930fd7732b1a0067ffee7e1e95f60',
        'assignment_seed': 48,
        'source_sha256': source_hashes,
        'scope': 'Scalar F2 totals; whole Eisenstein lines; abstract pairing-rank charge; no new kappa.',
        'geometry': {
            'a2_pairs': a2_pairs, 'representatives': reps, 'J_images': images,
            'root_orbits_sha256': digest(orbits),
            'nonorthogonality_masks': adjacent,
            'flat_census': [[rank, size, n] for (rank, size), n in sorted(Counter(
                (len(b) // 2, m.bit_count()) for m, b, _ in ff).items())],
            'flats': [{'mask': m, 'rank': len(b) // 2, 'generators': g} for m, b, g in ff],
            'clique_census': sorted(Counter(q.bit_count() for q in every_clique).items()),
            'all_cliques_sha256': digest(every_clique),
            'maximal_clique_census': sorted(Counter(q.bit_count() for q in maximal).items()),
        },
        'primal': {'singleton_weight': '1/40', 'maximum_clique_weight': '1/960',
                   'maximum_cliques': largest, 'objective': str(primal),
                   'flat_pairs_checked': pair_count,
                   'pair_census': [list(key) + [n] for key, n in sorted(pair_census.items())]},
        'dual': {'pair_weight': '1/24', 'full_pair_weight': '1/2', 'flat_pairs': dual_pairs,
                 'objective': str(dual), 'cliques_checked': len(every_clique),
                 'clique_hit_census': [list(key) + [n] for key, n in sorted(dual_census.items())]},
        'sharp_example': {'flat_indices': sharp_pair, 'left': list(bits(left)), 'right': list(bits(right)),
                          'support_ranks': [3, 3], 'pairing_rank': 2, 'joint_maximum_clique_hits': h7},
        'abstract_decoder_cost_interval': [22, 40],
        'all_clique_weight_certificate_optimum': '22',
        'optimistic_Dfc': {'rational_copy_floor': 44, 'upper_deficit_per_replica': '36*s-80',
                           'three_stage_upper_deficit': 28,
                           'conclusion': 'Does not exclude three or more stages; no achieved supplier.'},
        'independent_fraction_pairs': len(rank_pairs),
        'one_line_extensions_checked': len(ff) * 40,
        'asymmetric_positive_control_sha256': digest(directed),
        'negative_controls': controls,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', type=Path, help='Export the receipt AFTER checking the committed certificate.')
    args = parser.parse_args()
    result = replay()
    # Round-trip tuples so semantic JSON equality is independent of whitespace.
    result = json.loads(json.dumps(result))
    expected = json.loads((HERE / 'certificate.json').read_text())
    require(result == expected, 'committed certificate differs from exact replay')
    if args.write:
        require(args.write.resolve() != (HERE / 'certificate.json').resolve(),
                'refusing to overwrite the committed certificate')
        args.write.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print('PASS_EISENSTEIN_CLIQUE_COPY_BOUND: cost >= 22; clique-method optimum 22; '
          f"{result['primal']['flat_pairs_checked']} flat pairs; "
          f"{result['dual']['cliques_checked']} cliques; {len(result['negative_controls'])} negative controls; no new kappa")


if __name__ == '__main__':
    main()
