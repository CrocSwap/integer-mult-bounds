#!/usr/bin/env python3
"""Label-free P112 support spectra; Python 3.10+, standard library only.

Apache-2.0. Prepared for @adamgall with substantial OpenAI Codex assistance.
No imports from predecessor checkers; no numerical eigensolver or minor census.
"""

import argparse
from collections import Counter
from hashlib import sha256
from itertools import combinations, product
import json
from math import gcd
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PREDECESSOR = ROOT / 'research/p112-single-lift'
SPECTRA = {
    (0, 32, 32, 32, 32, 32, 32, 32): 8,
    (4, 32, 32, 32, 32, 36, 36, 36): 112,
    (20, 20, 20, 24, 24, 24, 24, 52): 112,
    (24, 24, 24, 24, 24, 24, 24, 24): 7,
    (24, 24, 24, 24, 24, 24, 24, 56): 8,
    (24, 24, 24, 24, 28, 28, 28, 28): 112,
    (28, 28, 28, 28, 28, 28, 28, 28): 32,
    (28, 28, 28, 28, 32, 32, 32, 32): 112,
    (32, 32, 32, 32, 32, 32, 32, 32): 7,
    (56, 56, 56, 56, 56, 56, 56, 56): 1,
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def encoded(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode('ascii')


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def identity():
    return [[int(i == j) for j in range(8)] for i in range(8)]


def multiply(a, b):
    columns = list(zip(*b))
    return [[dot(row, column) for column in columns] for row in a]


def shifted(a, scalar):
    return [[a[i][j] - scalar * (i == j) for j in range(8)] for i in range(8)]


def geometry():
    # Twice each root: integral coordinates, norm squared eight.
    roots = set()
    for i, j in combinations(range(8), 2):
        for sign in (-1, 1):
            r = [0] * 8
            r[i], r[j] = 2, 2 * sign
            roots.add(tuple(r))
    roots.update((1,) + signs for signs in product((-1, 1), repeat=7)
                 if sum(s < 0 for s in signs) % 2 == 0)
    frame = []
    for i in range(0, 8, 2):
        for sign in (1, -1):
            r = [0] * 8
            r[i], r[i + 1] = 2, 2 * sign
            frame.append(tuple(r))
    require(len(roots) == 120 and set(frame) <= roots, 'E8/frame census')
    roots = sorted(roots - set(frame))
    require(all(dot(r, r) == 8 for r in roots), 'root normalization')
    require(all(dot(r, f) % 4 == 0 for r in roots for f in frame), 'integral X')
    x = [[dot(r, f) // 4 for f in frame] for r in roots]
    return roots, frame, x


def pairing_rows(roots, constant=1):
    require(all(dot(r, s) % 4 == 0 for r in roots for s in roots), 'integral Gram')
    return [sum(((constant + dot(r, s) // 4) % 2) << j
                for j, s in enumerate(roots)) for r in roots]


def characters(rows):
    basis = {}
    for row in rows:
        while row:
            pivot = row.bit_length() - 1
            if pivot in basis:
                row ^= basis[pivot]
            else:
                basis[pivot] = row
                break
    require(len(basis) == 9, 'pairing dimension must be nine')
    space = [0]
    for pivot in sorted(basis):
        row = basis[pivot]
        space += [word ^ row for word in space]
    require(len(space) == len(set(space)) == 512, 'character space size')
    return sorted(set(space) - {0})


def gram(x, mask):
    selected = [row for i, row in enumerate(x) if mask >> i & 1]
    return [[sum(row[i] * row[j] for row in selected)
             for j in range(8)] for i in range(8)]


def certify_spectrum(g, spectrum):
    require(len(g) == 8 and all(len(row) == 8 for row in g), 'Gram shape')
    require(all(g[i][j] == g[j][i] for i in range(8) for j in range(8)),
            'Gram symmetry')
    require(len(spectrum) == 8, 'spectrum dimension')
    # The annihilator has distinct roots. Its vanishing confines the spectrum;
    # the first d traces determine multiplicities by an invertible Vandermonde.
    distinct = sorted(set(spectrum))
    annihilator = identity()
    for value in distinct:
        annihilator = multiply(annihilator, shifted(g, value))
    require(not any(v for row in annihilator for v in row), 'Gram polynomial identity')
    power = identity()
    for degree in range(len(distinct)):
        require(sum(power[i][i] for i in range(8)) == sum(v ** degree for v in spectrum),
                'spectral multiplicity trace')
        power = multiply(power, g)


def classify(g):
    power = identity()
    moments = []
    for degree in range(4):
        moments.append(sum(power[i][i] for i in range(8)))
        power = multiply(power, g)
    candidates = [s for s in SPECTRA
                  if moments == [sum(v ** k for v in s) for k in range(4)]]
    require(len(candidates) == 1, 'unrecognized Gram moments')
    spectrum = candidates[0]
    certify_spectrum(g, spectrum)
    return spectrum


def check_coverage(masks, expected):
    require(len(masks) == len(set(masks)) == 511 and set(masks) == set(expected),
            'nonzero character coverage')


def bind_sources():
    pins = json.loads((HERE / 'SOURCES.json').read_text(encoding='utf-8'))
    for relative, digest in pins['files'].items():
        require(sha256((ROOT / relative).read_bytes()).hexdigest() == digest,
                'source hash: ' + relative)


def audit():
    bind_sources()
    roots, frame, x = geometry()
    reference = json.loads((PREDECESSOR / 'reference-geometry.json').read_text(encoding='utf-8'))
    require([list(f) for f in frame] == reference['frame'], 'predecessor frame binding')
    by_root = {tuple(r): row for r, row in zip(reference['roots'], reference['X'])}
    require(len(by_root) == len(reference['roots']) == 112
            and by_root == dict(zip(roots, x)), 'predecessor root/X binding')
    # Deliberately never read reference labels, duals, reader bases or minors.
    masks = characters(pairing_rows(roots))
    check_coverage(masks, masks)
    counts = Counter()
    exceptions = []
    trace = sha256()
    witness = None
    for mask in masks:
        g = gram(x, mask)
        spectrum = classify(g)
        counts[spectrum] += 1
        trace.update(encoded([format(mask, '028x'), g, spectrum]) + b'\n')
        if spectrum[0] == 0:
            zero = [j for j in range(8) if g[j][j] == 0]
            require(len(zero) == 1, 'one coordinate kernel')
            j = zero[0]
            require(g == [[32 * (a == b and a != j) for b in range(8)]
                          for a in range(8)], 'coordinate kernel Gram identity')
            exceptions.append({'mask': format(mask, '028x'), 'coordinate': j})
        elif spectrum[0] == 4 and witness is None:
            projector = multiply(shifted(g, 32), shifted(g, 36))
            vector = next(list(col) for col in zip(*projector) if any(col))
            divisor = gcd(*vector)
            vector = [v // divisor for v in vector]
            require([dot(row, vector) for row in g] == [4 * v for v in vector],
                    'sharp lower bound witness')
            witness = {'mask': format(mask, '028x'), 'vector': vector,
                       'norm_squared': dot(vector, vector),
                       'restricted_energy': dot(vector, [dot(row, vector) for row in g])}
    require(counts == Counter(SPECTRA), 'complete spectrum census')
    require(sorted(e['coordinate'] for e in exceptions) == list(range(8)),
            'eight distinct coordinate kernels')
    require(witness is not None, 'attained lower bound')
    controls = negative_controls(roots, x, masks)
    return {
        'format': 'p112-label-free-gram-v1', 'seed': 80,
        'roots': len(roots), 'pairing_dimension': 9, 'nonzero_characters': len(masks),
        'full_rank': 503, 'coordinate_kernels': sorted(exceptions, key=lambda e: e['coordinate']),
        'spectra': [{'eigenvalues': list(s), 'count': counts[s]} for s in sorted(counts)],
        'sharp_full_rank_energy_constant': 4, 'sharp_witness': witness,
        'geometry_sha256': sha256(encoded([roots, frame, x])).hexdigest(),
        'complete_gram_trace_sha256': trace.hexdigest(), 'rejected_controls': controls,
    }


def negative_controls(roots, x, masks):
    rejected = []

    def reject(name, message, operation):
        try:
            operation()
        except ValueError as error:
            require(str(error) == message, name + ': unexpected rejection: ' + str(error))
            rejected.append(name)
        else:
            raise ValueError(name + ': mutation accepted')

    reject('missing character', 'nonzero character coverage',
           lambda: check_coverage(masks[:-1], masks))
    reject('duplicate replaces character', 'nonzero character coverage',
           lambda: check_coverage(masks[:-1] + [masks[0]], masks))
    reject('zero replaces character', 'nonzero character coverage',
           lambda: check_coverage([0] + masks[1:], masks))
    reject('omit affine pairing constant', 'pairing dimension must be nine',
           lambda: characters(pairing_rows(roots, constant=0)))
    g = gram(x, masks[0])
    spectrum = classify(g)
    corrupted = [row[:] for row in g]
    corrupted[0][0] += 1
    reject('alter one Gram entry', 'Gram polynomial identity',
           lambda: certify_spectrum(corrupted, spectrum))
    # Same allowed eigenvalues but wrong multiplicities: polynomial alone passes.
    g = [[32 * (i == j and i != 0) for j in range(8)] for i in range(8)]
    reject('false kernel multiplicity', 'spectral multiplicity trace',
           lambda: certify_spectrum(g, (0, 0, 32, 32, 32, 32, 32, 32)))
    # Both spectra have equal trace and trace of the square. The matrix
    # polynomial prevents treating a full-rank support as coordinate-singular.
    g = [[(56 if i == 0 else 24) * (i == j) for j in range(8)] for i in range(8)]
    reject('rank-seven spectrum with matching first two moments', 'Gram polynomial identity',
           lambda: certify_spectrum(g, (0, 32, 32, 32, 32, 32, 32, 32)))
    require(classify([[28 * (i == j) for j in range(8)] for i in range(8)]) == (28,) * 8,
            'positive scalar-spectrum control')
    return rejected


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', type=Path, help='write a new receipt; never overwrite')
    args = parser.parse_args()
    receipt = audit()
    if args.write is not None:
        with args.write.open('x', encoding='utf-8') as stream:
            json.dump(receipt, stream, indent=2, sort_keys=True)
            stream.write('\n')
    else:
        expected = json.loads((HERE / 'RESULTS.json').read_text(encoding='utf-8'))
        require(receipt == expected, 'committed receipt mismatch')
    print('PASS_P112_GRAM_SUPPORT characters=511 full_rank=503 coordinate_kernels=8 '
          'spectra=10 sharp_energy=4 controls=7 no_new_kappa')


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, KeyError, TypeError) as error:
        print('FAIL_P112_GRAM_SUPPORT: ' + str(error), file=sys.stderr)
        raise SystemExit(1)
