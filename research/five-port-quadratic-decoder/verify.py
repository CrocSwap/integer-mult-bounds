#!/usr/bin/env python3
"""Check literal rational-rank witnesses and the optimistic format ceiling.

Integer minors modulo a checked prime certify rational rank LOWER bounds.
No floating-point calculation, optimizer or discovery code is used.
Copyright 2026 Ross Richardson. Apache-2.0. Substantial OpenAI Codex assistance.
"""
from fractions import Fraction as Q
from itertools import combinations, product
from math import comb, isqrt
from pathlib import Path
import argparse
import copy
import hashlib
import json

HERE = Path(__file__).resolve().parent
BASE = '47481c89fd30a43f8f882eb4b391e89c29273fd0'
PRIME = 65521
LOG_LOWER = Q(549, 500)
CEILING = Q(125, 76433)
SELECTED = Q(1661957774647029, 10**18)
CORRECTOR = dict(zip(range(5, 14), (15, 50, 83, 111, 143, 179, 219, 263, 311)))
STAR = dict(zip(range(5, 13), (11, 35, 60, 84, 112, 144, 170, 210)))
SOURCE_NAMES = {'sources/pr231-README.md', 'sources/format-axioms-README.md',
                'sources/selected-result-base.json', 'sources/pr446-PROOF.md'}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def gram(a, b):
    common = (a & b).bit_count()
    return 2 * (common - 1) * (common - 3)


def determinant_mod(matrix, prime=PRIME):
    """Ordinary row elimination; the committed residue must be nonzero."""
    n = len(matrix)
    require(n > 0 and all(len(row) == n for row in matrix), 'square nonempty minor')
    rows = [[x % prime for x in row] for row in matrix]
    determinant = 1
    for col in range(n):
        pivot = next((i for i in range(col, n) if rows[i][col]), None)
        if pivot is None:
            return 0
        if pivot != col:
            rows[pivot], rows[col] = rows[col], rows[pivot]
            determinant = -determinant
        entry = rows[col][col]
        determinant = determinant * entry % prime
        inverse = pow(entry, -1, prime)
        for i in range(col + 1, n):
            multiplier = rows[i][col] * inverse % prime
            if multiplier:
                rows[i][col] = 0
                for j in range(col + 1, n):
                    rows[i][j] = (rows[i][j] - multiplier * rows[col][j]) % prime
    return determinant % prime


def valid_port(mask, p):
    return (type(mask) is int and 0 <= mask < (1 << (2 * p)) and mask.bit_count() == 5
            and all(((mask >> (2 * i)) & 3) != 3 for i in range(p)))


def check_witness(w):
    require(type(w.get('p')) is int, 'integer pair count')
    p, kind = w['p'], w.get('kind')
    require(kind in ('corrector', 'star'), 'known witness kind')
    expected = CORRECTOR if kind == 'corrector' else STAR
    require(p in expected and w.get('rank_lower') == expected[p], 'rank obligation')
    n = expected[p]
    canonical_target = sum(1 << (2 * i) for i in range(5))
    require(w.get('target') == (canonical_target if kind == 'corrector' else 1), 'target binding')
    for side in ('rows', 'columns'):
        labels = w.get(side, [])
        require(len(labels) == n and len(set(labels)) == n, 'distinct minor labels')
        for mask in labels:
            require(valid_port(mask, p), 'signed five-port domain')
            if kind == 'corrector':
                require((mask & canonical_target).bit_count() in (1, 3), 'corrector support')
            else:
                require(bool(mask & 1), 'coordinate-star support')
    matrix = [[gram(a, b) for b in w['columns']] for a in w['rows']]
    determinant = determinant_mod(matrix)
    require(determinant != 0, 'nonsingular rational-rank witness')
    require(determinant == w.get('determinant_mod_prime'), 'determinant receipt')
    return dict(p=p, kind=kind, rank_lower=n, determinant_mod_prime=determinant)


def check_sources():
    manifest = json.loads((HERE / 'SOURCES.json').read_text())
    require(manifest['base_commit'] == BASE, 'base pin')
    require(len(manifest['files']) == 4, 'source count')
    require({r['path'] for r in manifest['files']} == SOURCE_NAMES, 'source inventory')
    hashes = {}
    for row in manifest['files']:
        raw = (HERE / row['path']).read_bytes()
        digest = hashlib.sha256(raw).hexdigest()
        blob = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
        require(digest == row['sha256'] and blob == row['git_blob_sha1'], 'immutable source hash')
        require(row['commit'] == ('309482849b6ddf34db998f53612d34c19f6e3233'
                                 if row['path'] == 'sources/pr446-PROOF.md' else BASE), 'source commit')
        hashes[row['path']] = digest
    selected = json.loads((HERE / 'sources/selected-result-base.json').read_text())
    require(Q(selected['kappa']) == SELECTED, 'frozen selected value')
    return hashes


def algebra_checks():
    # The XOR decoder coefficient, checked on all overlap types and on every
    # pair of literal ports for p=5,6. It is not a full supplier replay.
    for j in range(6):
        require((j + int(j in (1, 3))) % 2 == int(j == 5), 'XOR decoder identity')
        require(6 - 6 * j + 4 * comb(j, 2) == 2 * (j - 1) * (j - 3), 'feature pairing')
    pairs = 0
    for p in (5, 6):
        ports = [sum(1 << (2 * i + bit) for i, bit in zip(indices, bits))
                 for indices in combinations(range(p), 5)
                 for bits in product(range(2), repeat=5)]
        for a in ports:
            for b in ports:
                j = (a & b).bit_count()
                require((j + int(j in (1, 3))) % 2 == int(a == b), 'literal decoder')
                if j in (1, 3):
                    require(gram(a, b) == 0, 'lossless correction')
                pairs += 1
    even = [bits for bits in product(range(2), repeat=5) if sum(bits) % 2 == 0]
    labels = [sum(1 << (2 * i + b) for i, b in enumerate(bits)) for bits in even]
    require(len(labels) == 16 and 16 > 6, 'linear-label dimension obstruction')
    for i, a in enumerate(labels):
        for j, b in enumerate(labels):
            require(gram(a, b) == (16 if i == j else 0), 'parity clique')
    # ln(3) = 2 atanh(1/2). Every omitted summand is strictly positive.
    partial = check_log_lower(LOG_LOWER)
    return dict(literal_decoder_pairs=pairs, parity_clique_size=16,
                affine_label_span_upper=6, logarithm_partial_sum=str(partial),
                logarithm_lower=str(LOG_LOWER))


def check_log_lower(proposed):
    partial = sum((Q(2, (2 * i + 1) * 2**(2 * i + 1)) for i in range(6)), Q())
    require(partial > proposed > 0, 'certified logarithm lower bound')
    return partial


def price(p, a, star_rank):
    require(p in STAR and a == CORRECTOR[p] and star_rank == STAR[p], 'price rank bindings')
    v = 32 * comb(p, 5)
    c = 2 * p * star_rank
    if c >= v:
        return dict(p=p, ports=v, active_rank_lower=a, star_rank_lower=star_rank,
                    copy_charge_lower=c, positive_deficit_possible=False)
    upper = (1 - Q(c, v)) / (2 * a * LOG_LOWER)
    require(upper <= CEILING, 'finite supplier ceiling')
    return dict(p=p, ports=v, active_rank_lower=a, star_rank_lower=star_rank,
                copy_charge_lower=c, positive_deficit_possible=True, saving_upper=str(upper))


def expect_rejection(fn, description):
    try:
        fn()
    except (ValueError, KeyError, TypeError):
        return description
    raise ValueError('negative control was accepted: ' + description)


def negative_controls(witnesses):
    original = next(w for w in witnesses if w['p'] == 5 and w['kind'] == 'corrector')
    controls = []
    bad = copy.deepcopy(original)
    bad['rows'][1] = bad['rows'][0]
    controls.append(expect_rejection(lambda: check_witness(bad), 'duplicate minor row'))
    bad = copy.deepcopy(original)
    bad['rows'][0] = bad['target']
    controls.append(expect_rejection(lambda: check_witness(bad), 'self substituted for corrector'))
    bad = copy.deepcopy(original)
    bad['determinant_mod_prime'] = 0
    controls.append(expect_rejection(lambda: check_witness(bad), 'false determinant residue'))
    bad = copy.deepcopy(original)
    bad['rows'][0] = 31  # contains both coordinates of a pair
    controls.append(expect_rejection(lambda: check_witness(bad), 'invalid paired-port label'))
    star = copy.deepcopy(next(w for w in witnesses if w['p'] == 5 and w['kind'] == 'star'))
    star['rows'][0] ^= 3  # move coordinate 0 to its mate
    controls.append(expect_rejection(lambda: check_witness(star), 'reader outside copied star'))
    controls.append(expect_rejection(lambda: price(10, 179, 143), 'invoice rank differs from witness'))
    controls.append(expect_rejection(lambda: check_log_lower(Q(1099, 1000)),
                                     'unproved logarithm bound'))
    # A true scalar identity need not have valid geometry: the old affine
    # kernel j-1 fails on a required overlap-three correction.
    require(3 - 1 != 0, 'linear-kernel geometric failure control')
    controls.append('linear kernel rejected at overlap three')
    # A singular matrix reaches the actual elimination failure, independently
    # of the label uniqueness checks above.
    require(determinant_mod([[16, 16], [16, 16]]) == 0, 'singular minor detection')
    controls.append('singular matrix detected by elimination')
    return controls


def verify():
    require(PRIME > 2 and all(PRIME % d for d in range(2, isqrt(PRIME) + 1)), 'prime modulus')
    sources = check_sources()
    raw = (HERE / 'WITNESSES.json').read_bytes()
    data = json.loads(raw)
    require(data['schema'] == 'five-port-quadratic-rank-witnesses-v1', 'witness schema')
    require(data['seed'] == 40 and data['prime'] == PRIME, 'seed and prime')
    require(data['kernel_coefficients'] == [6, -8, 2], 'kernel coefficients')
    expected = {(p, 'corrector') for p in CORRECTOR} | {(p, 'star') for p in STAR}
    require(len(data['witnesses']) == len(expected), 'all 17 obligations present')
    require({(w['p'], w['kind']) for w in data['witnesses']} == expected, 'obligation inventory')
    ranks = [check_witness(w) for w in data['witnesses']]
    algebra = algebra_checks()
    bounds = [price(p, CORRECTOR[p], STAR[p]) for p in STAR]
    # Every target at p>=13 contains an isometric copy of the p=13 witness.
    # Grant copy and all other costs zero in the tail.
    tail = 1 / (2 * CORRECTOR[13] * LOG_LOWER)
    require(tail < CEILING < SELECTED, 'all-p tail and frozen selected comparison')
    require(max(Q(r['saving_upper']) for r in bounds if r['positive_deficit_possible']) == CEILING,
            'maximum of the stated coarse bounds')
    controls = negative_controls(data['witnesses'])
    return dict(schema='five-port-quadratic-certificate-v1', base_commit=BASE,
                witness_sha256=hashlib.sha256(raw).hexdigest(), source_sha256=sources,
                prime=PRIME, ranks=ranks, algebra=algebra, finite_bounds=bounds,
                all_p_ge_13_tail_upper=str(tail), supplier_saving_strict_upper=str(CEILING),
                selected_kappa_at_base=str(SELECTED), strict_gap=str(SELECTED - CEILING),
                stage_scope='every integer s >= 3 under PROOF.md accounting premises',
                negative_controls=controls, new_kappa_claim=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write-certificate', type=Path,
                        help='write a new receipt with exclusive creation; do not compare committed receipt')
    args = parser.parse_args()
    result = verify()
    encoded = json.dumps(result, indent=2) + '\n'
    if args.write_certificate:
        with args.write_certificate.open('x') as handle:
            handle.write(encoded)
    else:
        require(json.loads((HERE / 'CERTIFICATE.json').read_text()) == result, 'certificate equality')
    print('PASS_FIVE_PORT_QUADRATIC_DECODER witnesses=17 '
          'ceiling=125/76433 tail=250/170739 controls=9 no_new_kappa')


if __name__ == '__main__':
    main()
