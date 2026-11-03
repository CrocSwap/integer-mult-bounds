#!/usr/bin/env python3
"""Exact distinct-axis obstruction, produced by Nick Petalas. Apache-2.0."""

from collections import Counter
from hashlib import sha256
from itertools import combinations, permutations
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
N = 7
UNIVERSE = (1 << 128) - 1


def need(condition, message):
    if not condition:
        raise ValueError(message)


def span(generators):
    values = [0]
    for generator in generators:
        values += [old ^ generator for old in values]
    return tuple(sorted(values))


def axis_codes():
    """Permute the seven points (1,j), j=0,...,6, in the affine cube."""
    base = tuple(sum(((row & (1 | (j << 1))).bit_count() % 2) << j
                     for j in range(N)) for row in range(16))
    codes = set()
    for order in permutations(range(N)):
        code = tuple(sorted(sum(((word >> order[j]) & 1) << j
                                for j in range(N)) for word in base))
        codes.add(code)
    return tuple(sorted(codes))


def orthogonal_codes():
    """Separate domain generator: enumerate binary RREF three-row matrices."""
    codes = set()
    rref_count = 0
    for pivots in combinations(range(N), 3):
        free = [(row, col) for row in range(3) for col in range(N)
                if col not in pivots and col > pivots[row]]
        for assignment in range(1 << len(free)):
            rows = [1 << col for col in pivots]
            for bit, (row, col) in enumerate(free):
                if assignment & (1 << bit):
                    rows[row] |= 1 << col
            rref_count += 1
            dual = span(rows)
            if any(word.bit_count() != 4 for word in dual if word):
                continue
            code = tuple(word for word in range(128)
                         if all((word & row).bit_count() % 2 == 0 for row in rows))
            codes.add(code)
    need(rref_count == 11811, 'Complete three-dimensional RREF domain')
    return tuple(sorted(codes))


def mandatory_scan(code):
    return sum(1 << mask for mask in range(1, 128)
               if not any(word != 127 and mask & ~word == 0 for word in code))


def mandatory_subsets(code):
    allowed = 1  # Empty support is contained in every proper codeword.
    for word in code:
        if word == 127:
            continue
        positions = [j for j in range(N) if word & (1 << j)]
        for choice in range(1 << len(positions)):
            mask = sum(1 << col for j, col in enumerate(positions)
                       if choice & (1 << j))
            allowed |= 1 << mask
    return UNIVERSE ^ allowed


def prefix_differences(order):
    parity, points = 0, [0]
    for label in tuple(range(N)) + order:
        parity ^= 1 << label
        points.append(parity)
    need(parity == 0, 'Paired source restoration')
    return sum(1 << mask for mask in {a ^ b for a in points for b in points})


def interval_differences(order):
    word = tuple(range(N)) + order
    result = 1
    for start in range(14):
        parity = 0
        for end in range(start, 14):
            parity ^= 1 << word[end]
            result |= 1 << parity
    return result


def census(codes, secondary=False):
    """Return every missing-mask set, in lexicographic order of (order,code)."""
    mandatory = tuple(mandatory_subsets(code) if secondary else mandatory_scan(code)
                      for code in codes)
    need(all(bits.bit_count() == 57 for bits in mandatory), 'Mandatory-set sizes')
    results, histogram = [], Counter()
    minimum, witness = 128, None
    for order in permutations(range(N)):
        differences = (interval_differences(order) if secondary
                       else prefix_differences(order))
        need(differences & (1 << 127), 'Normalized all-ones interval')
        for code, required in zip(codes, mandatory):
            missing = required & ~differences
            results.append(missing)
            count = missing.bit_count()
            histogram[count] += 1
            if count < minimum:
                minimum = count
                witness = {'second_order': list(order), 'code': list(code),
                           'missing_masks': [m for m in range(128) if missing >> m & 1]}
    need(len(results) == 151200, 'Complete order/code product')
    return results, dict(sorted(histogram.items())), minimum, witness


def missing_for_word(word, code):
    need(len(word) == 14 and all(word.count(j) == 2 for j in range(N)),
         'Need exactly two calls of each of seven sources')
    parity, points = 0, [0]
    for label in word:
        parity ^= 1 << label
        points.append(parity)
    differences = {a ^ b for a in points for b in points}
    return {m for m in range(1, 128) if mandatory_scan(code) >> m & 1} - differences


def controls(codes, witness):
    code = tuple(witness['code'])
    word = list(range(N)) + witness['second_order']
    missing = set(witness['missing_masks'])
    need(len(missing) == 22 and missing_for_word(word, code) == missing,
         'Attaining missing-set witness')
    for shift in range(14):
        rotated = word[shift:] + word[:shift]
        need(missing_for_word(rotated, code) == missing, 'Closed-word rotation')
    for transposition in combinations(range(N), 2):
        relabel = list(range(N))
        a, b = transposition
        relabel[a], relabel[b] = relabel[b], relabel[a]
        new_word = [relabel[j] for j in word]
        new_code = tuple(sorted(sum(((h >> j) & 1) << relabel[j] for j in range(N))
                                for h in code))
        need(new_code in codes, 'Code inventory closes under coordinate relabeling')
        need(len(missing_for_word(new_word, new_code)) == 22, 'Relabeled witness')
    # Prior star's repeated-axis code supplies a discriminating positive case.
    axes = (1, 1, 1, 1, 2, 4, 8)
    star_code = tuple(sorted({sum(((r & v).bit_count() % 2) << j
                                  for j, v in enumerate(axes)) for r in range(16)}))
    star_word = (0, 1, 0, 1, 4, 5, 6, 2, 3, 2, 3, 4, 5, 6)
    q, points = 0, [0]
    for label in star_word:
        q ^= 1 << label
        points.append(q)
    coverage = {h & (a ^ b) for h in star_code for a in points for b in points}
    need(coverage == set(range(128)) and star_code not in codes,
         'Repeated-axis positive control must remain feasible')
    need(mandatory_scan(code) != UNIVERSE ^ 1, 'Not every mask is mandatory')
    need(0 not in missing and 127 not in missing, 'Zero and full-mask boundaries')
    need(len(missing) > 21, 'False deficit ceiling 21')
    need(len(missing) < 23, 'False deficit floor 23')
    for bad in (word[:-1], [word[1]] + word[1:]):
        try:
            missing_for_word(bad, code)
        except ValueError:
            continue
        raise ValueError('Invalid source multiplicity accepted')
    return {'cyclic_rotations': 14, 'coordinate_transpositions': 21,
            'repeated_axis_positive': 1, 'false_variant_controls': 4,
            'invalid_word_rejections': 2}


def source_pins():
    record = json.loads((HERE / 'SOURCES.json').read_bytes())
    checked = []
    for row in record['files']:
        if row['usage'] != 'input':
            continue
        path = HERE.parents[1] / row['path']
        need(sha256(path.read_bytes()).hexdigest() == row['sha256'],
             'Changed cited source: ' + row['path'])
        checked.append(row['path'])
    need(len(checked) == 2, 'Both cited main-tree source inputs are bound')
    return checked


def main():
    pins = source_pins()
    first_codes, second_codes = axis_codes(), orthogonal_codes()
    need(first_codes == second_codes and len(first_codes) == 30,
         'Two complete code-domain generators must agree')
    primary = census(first_codes)
    secondary = census(second_codes, secondary=True)
    need(primary == secondary, 'Every missing-mask set must agree, not only minima')
    values, histogram, minimum, witness = primary
    need(minimum == 22 and 0 not in histogram, 'Distinct-axis exclusion')
    need(histogram[22] == 4, 'All four minimum-deficit pairs')
    check = controls(first_codes, witness)
    encoded = b''.join(value.to_bytes(16, 'big') for value in values)
    files = {path.name: sha256(path.read_bytes()).hexdigest()
             for path in sorted(HERE.iterdir()) if path.is_file()}
    print(json.dumps({'status': 'PASS_SEVEN_SOURCE_DISTINCT_AXIS_OBSTRUCTION',
        'claim_type': 'scoped obstruction with exhaustive finite certificate',
        'codes': len(first_codes), 'orders': 5040, 'cases': len(values),
        'mandatory_per_code': 57, 'minimum_missing_mandatory_masks': minimum,
        'maximum_nonzero_outputs_if_full_mask_served_upper_bound': 105,
        'histogram': histogram, 'attaining_deficit_witness': witness,
        'census_sha256': sha256(encoded).hexdigest(), 'controls': check,
        'source_inputs': pins, 'package_sha256': files}, sort_keys=True, indent=2))


if __name__ == '__main__':
    main()
