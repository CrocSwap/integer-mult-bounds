#!/usr/bin/env python3
"""Independent finite census using quotient RREF planes and signed minors.

Standard library only.  This does not import the discovery census.  Rows
are binary linear maps, and the quotient planes have unique RREF matrices.
"""

import hashlib
import itertools
import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
DIMENSION = 9
OMEGA = (1 << DIMENSION) - 1
WEIGHT5 = [sum(1 << i for i in c)
           for c in itertools.combinations(range(DIMENSION), 5)]


def need(condition, message):
    if not condition:
        raise ValueError(message)


def parity(x):
    return bin(x).count('1') & 1


def inner(x, y):
    return parity(x & y)


def rref(rows, width=DIMENSION):
    """Gauss-Jordan row elimination; pivots scan left (low bit) to right."""
    work = list(rows)
    pivot_row = 0
    for col in range(width):
        selected = next((j for j in range(pivot_row, len(work))
                         if (work[j] >> col) & 1), None)
        if selected is None:
            continue
        work[pivot_row], work[selected] = work[selected], work[pivot_row]
        for j in range(len(work)):
            if j != pivot_row and ((work[j] >> col) & 1):
                work[j] ^= work[pivot_row]
        pivot_row += 1
    return tuple(work[:pivot_row])


def image(rows, coefficients):
    result = 0
    for index, row in enumerate(rows):
        if (coefficients >> index) & 1:
            result ^= row
    return result


def elements(rows):
    return sorted(image(rows, c) for c in range(1 << len(rows)))


def contains(rows, vector):
    for row in rows:
        pivot = row & -row
        if vector & pivot:
            vector ^= row
    return vector == 0


def nullspace(rows, width=DIMENSION):
    reduced = rref(rows, width)
    pivots = [(row & -row).bit_length() - 1 for row in reduced]
    free = [j for j in range(width) if j not in pivots]
    result = []
    for col in free:
        vector = 1 << col
        for row, pivot in zip(reduced, pivots):
            if (row >> col) & 1:
                vector |= 1 << pivot
        result.append(vector)
    return tuple(result)


def gram(rows):
    return tuple(sum(inner(x, y) << j for j, y in enumerate(rows))
                 for x in rows)


def characteristic(rows):
    """Solve G c = diagonal(G), then map c back to the ambient space."""
    size = len(rows)
    equations = [row | (inner(x, x) << size)
                 for row, x in zip(gram(rows), rows)]
    reduced = rref(equations, size)
    need(len(reduced) == size, 'singular Gram in characteristic solve')
    coefficients = sum(((row >> size) & 1) << j
                       for j, row in enumerate(reduced))
    result = image(rows, coefficients)
    need(all(inner(result, x) == inner(x, x) for x in rows),
         'incorrect characteristic vector')
    return result


def quotient_complement(pair):
    basis = rref(pair)
    complement = []
    for coordinate in range(DIMENSION):
        candidate = 1 << coordinate
        expanded = rref(basis + tuple(complement) + (candidate,))
        if len(expanded) > len(basis) + len(complement):
            complement.append(candidate)
    need(len(complement) == 7, 'quotient dimension is not seven')
    return tuple(complement)


def quotient_planes():
    """Every rank-two RREF row space in F2^7, once, by pivot pattern."""
    for first, second in itertools.combinations(range(7), 2):
        free_first = [j for j in range(first + 1, 7) if j != second]
        free_second = list(range(second + 1, 7))
        for bits in range(1 << (len(free_first) + len(free_second))):
            row_first, row_second = 1 << first, 1 << second
            for k, col in enumerate(free_first):
                row_first |= ((bits >> k) & 1) << col
            for k, col in enumerate(free_second, len(free_first)):
                row_second |= ((bits >> k) & 1) << col
            yield row_first, row_second


def sign(source, target):
    # cos(pi |source intersect target| / 2), evaluated exactly.
    return (1, 0, -1, 0)[bin(source & target).count('1') % 4]


def degenerate_pair(vectors):
    return any(inner(a, b) == 1
               for a, b in itertools.combinations(vectors, 2))


def check_fixture(basis, sources, targets, row_signs, column_signs):
    need(len(basis) == 4 and len(rref(gram(basis), 4)) == 4,
         'fixture U is not a nonsingular four-space')
    need(all(bin(x).count('1') == 5 for x in sources + targets),
         'fixture endpoint does not have weight five')
    char_u = characteristic(basis)
    char_w = char_u ^ OMEGA
    need(all(contains(basis, x) and x != char_u for x in sources),
         'fixture source outside legal U')
    need(all(all(inner(x, row) == 0 for row in basis) and x != char_w
             for x in targets), 'fixture target outside legal W')
    need(all(sign(s, t) == row_signs[i] * column_signs[j]
             for i, s in enumerate(sources)
             for j, t in enumerate(targets)), 'fixture signed minors failed')
    need(degenerate_pair(sources) and degenerate_pair(targets),
         'fixture lacks degenerate endpoint pairs')
    return char_u, char_w


def negative_controls():
    sources = [31, 55, 457, 458, 481, 482]
    targets = [47, 59, 87, 151, 279, 451]
    basis = rref([31, 481, 3, 40])
    row_signs, column_signs = [1, 1, -1, -1, -1, -1], [1, 1, 1, 1, 1, -1]
    variants = [
        (basis, sources, targets, [1, -1, -1, -1, -1, -1], column_signs),
        (basis, sources, [46] + targets[1:], row_signs, column_signs),
        (rref([31, 481]), sources, targets, row_signs, column_signs),
    ]
    for index, arguments in enumerate(variants):
        rejected = False
        try:
            check_fixture(*arguments)
        except ValueError:
            rejected = True
        need(rejected, 'negative control accepted: %d' % index)
    return len(variants)


def max_block(sources, targets, required_pair):
    """Exhaust source subsets, then saturate T by literal 2x2 minors.

    For any rank-one block with nonzero entries, selecting its first target
    fixes all row ratios.  Every additional compatible target may be added
    without destroying rank one or its required degenerate target pair.
    Thus saturating each pivot target covers every maximum in this domain.
    """
    optional = [x for x in sources if x not in required_pair]
    best_area = 0
    best_sizes = set()
    best_witness = None
    for mask in range(1 << len(optional)):
        chosen = sorted(list(required_pair) +
                        [x for j, x in enumerate(optional) if (mask >> j) & 1])
        first_source = chosen[0]
        for pivot_target in targets:
            corner = sign(first_source, pivot_target)
            need(corner != 0, 'orthogonal spaces have a zero signed entry')
            compatible = [t for t in targets
                          if all(sign(s, t) * corner ==
                                 sign(s, pivot_target) * sign(first_source, t)
                                 for s in chosen)]
            if not degenerate_pair(compatible):
                continue
            area = len(chosen) * len(compatible)
            witness = [chosen, compatible]
            if area > best_area:
                best_area = area
                best_sizes = {(len(chosen), len(compatible))}
                best_witness = witness
            elif area == best_area and area:
                best_sizes.add((len(chosen), len(compatible)))
                if witness < best_witness:
                    best_witness = witness
    return best_area, sorted([list(x) for x in best_sizes]), best_witness


def census():
    plane_matrices = list(quotient_planes())
    expected_planes = ((2 ** 7 - 1) * (2 ** 7 - 2)) // ((4 - 1) * (4 - 2))
    need(len(plane_matrices) == expected_planes == 2667,
         'wrong Gaussian binomial plane count')
    need(len(set(plane_matrices)) == 2667, 'repeated quotient RREF plane')
    records = []
    summaries = []
    winner = None
    for overlap, pair in ((1, (31, 481)), (3, (31, 103))):
        complement = quotient_complement(pair)
        seen = set()
        legal = 0
        histogram = {}
        max_sources = max_targets = 0
        for qrows in plane_matrices:
            basis = rref(pair + tuple(image(complement, q) for q in qrows))
            need(len(basis) == 4, 'quotient plane did not lift to dimension four')
            need(basis not in seen, 'quotient lift repeated a U4')
            seen.add(basis)
            if len(rref(gram(basis), 4)) != 4:
                continue
            legal += 1
            perpendicular = nullspace(basis)
            need(len(perpendicular) == 5, 'perpendicular dimension is not five')
            need(len(rref(gram(perpendicular), 5)) == 5,
                 'nonsingular U has singular perpendicular')
            char_u = characteristic(basis)
            char_w = characteristic(perpendicular)
            need(char_u ^ char_w == OMEGA, 'characteristic decomposition failed')
            sources = sorted(x for x in WEIGHT5
                             if x != char_u and contains(basis, x))
            targets = sorted(x for x in WEIGHT5
                             if x != char_w and all(inner(x, row) == 0
                                                   for row in basis))
            need(all(x in sources for x in pair), 'required sources were lost')
            max_sources = max(max_sources, len(sources))
            max_targets = max(max_targets, len(targets))
            area, sizes, witness = max_block(sources, targets, pair)
            histogram[str(area)] = histogram.get(str(area), 0) + 1
            key = [overlap, elements(basis), len(sources), len(targets), area, sizes]
            records.append(key)
            if witness is not None:
                candidate = [area, overlap, list(basis), witness]
                if winner is None or candidate[0] > winner[0]:
                    winner = candidate
        summaries.append({'overlap': overlap, 'pair': list(pair),
                          'quotient_planes': len(plane_matrices),
                          'legal_planes': legal,
                          'excluded_singular_planes': len(plane_matrices) - legal,
                          'max_available_sources': max_sources,
                          'max_available_targets': max_targets,
                          'area_histogram': dict(sorted(histogram.items(),
                                                        key=lambda item: int(item[0])))})
    encoded = json.dumps(sorted(records), separators=(',', ':')).encode()
    fixture_sources = [31, 55, 457, 458, 481, 482]
    fixture_targets = [47, 59, 87, 151, 279, 451]
    fixture_basis = rref([31, 481, 3, 40])
    row_signs = [1, 1, -1, -1, -1, -1]
    column_signs = [1, 1, 1, 1, 1, -1]
    fixture_u, fixture_w = check_fixture(fixture_basis, fixture_sources,
                                        fixture_targets, row_signs, column_signs)
    return {'schema': 'independent-common-frame-census-v1',
            'method': 'quotient RREF planes; Gauss-Jordan Gram tests; literal signed 2x2 minor saturation',
            'ambient_dimension': DIMENSION, 'weight': 5,
            'summaries': summaries,
            'legal_record_count': len(records),
            'legal_records_sha256': hashlib.sha256(encoded).hexdigest(),
            'maximum_area': max(row[4] for row in records),
            'fixture': {'U_basis_rref': list(fixture_basis),
                        'characteristic_U': fixture_u,
                        'characteristic_W': fixture_w,
                        'sources': fixture_sources, 'targets': fixture_targets,
                        'source_signs': row_signs, 'target_signs': column_signs},
            'global_bound_method': 'exhaust source subsets and saturate each pivot target by exact 2x2 minors; crude endpoint cardinalities alone give only 54',
            'negative_control_count': negative_controls()}


def main():
    need(sys.argv[1:] in ([], ['--write']), 'usage: independent.py [--write]')
    result = census()
    path = HERE / 'INDEPENDENT.json'
    serialized = json.dumps(result, indent=2, sort_keys=True) + '\n'
    if sys.argv[1:] == ['--write']:
        path.write_text(serialized)
    else:
        need(path.read_text() == serialized, 'independent certificate mismatch')
    print('PASS_INDEPENDENT_COMMON_FRAME_CENSUS',
          result['maximum_area'], result['legal_records_sha256'])


if __name__ == '__main__':
    main()
