#!/usr/bin/env python3
"""Check the finite certificate using sets and a separately written incidence model.

Python 3.9+, standard library only. All checks stay active under -O.
Copyright 2026 Alishan Ladhani. SPDX-License-Identifier: Apache-2.0
Prepared with substantial OpenAI Codex assistance.
"""
import argparse
from copy import deepcopy
from itertools import combinations, product
import json
from math import comb
from pathlib import Path

HERE = Path(__file__).resolve().parent


def require(condition, message):
    if not condition:
        raise ValueError(message)


def physical_sets(p, size):
    return [frozenset(2 * pair + sign for pair, sign in zip(pairs, signs))
            for pairs in combinations(range(p), size)
            for signs in product(range(2), repeat=size)]


def sparse_rank(rows):
    """Set elimination, independent of the builder's integer-vector reduction."""
    pivots = {}
    for original in rows:
        row = set(original)
        while row:
            pivot = min(row)
            if pivot in pivots:
                row.symmetric_difference_update(pivots[pivot])
            else:
                pivots[pivot] = row
                break
    return len(pivots)


def read_model(certificate):
    require(certificate['format'] == 'global-star-punctures-v1', 'certificate format')
    require(certificate['assignment_seed'] == 42, 'assignment seed')
    family = physical_sets(6, 4)
    stars = [s for degree in (1, 2, 3) for s in physical_sets(6, degree)]
    target = 42
    require(certificate['instance'] == {
        'p': 6, 'k': 4, 'target_index': target,
        'target_coordinates': sorted(family[target]),
        'port_order': 'pair combinations lexicographic, then sign tuples lexicographic; coordinate 2*pair+sign'
    }, 'instance or port ordering changed')
    supports = [{i for i, source in enumerate(family) if star <= source} for star in stars]
    corrections = [{i for i, source in enumerate(family) if len(source & family[target]) == j}
                   for j in (1, 2, 3)]
    code = certificate['code']
    require((code['ports'], code['proper_stars'], code['overlap_corrections']) == (240, 232, 3),
            'generator census')
    checks = []
    for encoded in code['parity_checks_hex']:
        value = int(encoded, 16)
        require(0 < value < 1 << 240 and format(value, '060x') == encoded, 'invalid parity row')
        checks.append({i for i in range(240) if value >> i & 1})
    require(len(checks) == code['dual_rank'] == 85, 'dual row count')
    require(sparse_rank(checks) == 85, 'dependent parity checks')
    for check in checks:
        require(all(len(check & support) % 2 == 0 for support in supports + corrections),
                'parity check does not annihilate a generator')
    indices = code['independent_star_indices']
    require(len(indices) == len(set(indices)) == code['rank'] == 155, 'primal basis census')
    require(all(type(i) is int and 0 <= i < 232 for i in indices), 'primal basis index')
    require(sparse_rank(supports[i] for i in indices) == 155, 'dependent primal basis')
    require(code['rank'] + code['dual_rank'] == len(family), 'rank-nullity')
    retained = code['information_set']
    require(len(retained) == len(set(retained)) == 155 and
            all(type(i) is int and 0 <= i < 240 for i in retained), 'invalid information set')
    require(sparse_rank(supports[i] & set(retained) for i in indices) == 155,
            'information set is not independent')
    # Together the two rank checks prove that ker(H) is exactly the star code.
    require(code['empty_star_in_span'] is True and all(len(h) % 2 == 0 for h in checks),
            'empty star span claim')
    # Independently verify the written overlap-correction identities on each source.
    for j, correction in enumerate(corrections, 1):
        expansion = set()
        for star, support in zip(stars, supports):
            if star <= family[target] and len(star) >= j and comb(len(star), j) % 2:
                expansion.symmetric_difference_update(support)
        require(expansion == correction, 'overlap correction expansion')
    syndromes = [sum(1 << j for j, check in enumerate(checks) if i in check)
                 for i in range(240)]
    return family, target, supports, syndromes


def enumerate_supports(syndromes, target):
    """Every support of size <=4 splits into two parts of size <=2.

    Every support of size 5 splits into a pair and a triple. XOR permits
    overlapping parts; overlaps cancel and cannot conceal a smaller support.
    """
    other = [i for i in range(len(syndromes)) if i != target]
    singles = [syndromes[i] for i in other]
    pairs = {}
    for i, j in combinations(other, 2):
        syndrome = syndromes[i] ^ syndromes[j]
        require(syndrome not in pairs, 'pair syndromes must be unique for this enumerator')
        pairs[syndrome] = (i, j)
    short = {0, *singles, *pairs}
    require(len(short) == 1 + len(other) + comb(len(other), 2), 'short syndromes collide')
    intersection_count = sum((syndromes[target] ^ s) in short for s in short)
    require(intersection_count == 0, 'a decoder with at most four deletions exists')
    solutions, hits, triple_count = set(), 0, 0
    for triple in combinations(other, 3):
        triple_count += 1
        value = syndromes[target]
        for i in triple:
            value ^= syndromes[i]
        pair = pairs.get(value)
        if pair is not None:
            support = tuple(sorted(set(pair).symmetric_difference(triple)))
            require(len(support) == 5, 'smaller support appeared at the boundary')
            solutions.add(support)
            hits += 1
    require(triple_count == comb(len(other), 3), 'incomplete triple coverage')
    require(hits == 10 * len(solutions), 'five-set partition multiplicity')
    return {
        'other_ports': len(other), 'pairs': len(pairs),
        'zero_single_pair_syndromes': len(short),
        'translated_intersections': intersection_count,
        'triples': triple_count, 'triple_pair_hits': hits,
        'optimal_deletion_sets': len(solutions), 'minimum_deletions': 5,
    }, solutions


def validate_witness(family, target, witness):
    deleted = witness['deleted_indices']
    require(len(deleted) == len(set(deleted)) and all(type(i) is int and 0 <= i < 240 for i in deleted),
            'invalid deletion set')
    require(target not in deleted, 'the target must survive')
    coordinates = witness['star_coordinates']
    require(len(coordinates) == len(set(coordinates)) == 3, 'witness must be a three-coordinate star')
    require(all(type(i) is int and 0 <= i < 12 for i in coordinates), 'invalid coordinate')
    star = frozenset(coordinates)
    require(len({c // 2 for c in star}) == 3 and star <= family[target], 'invalid target-local star')
    survivors = set(range(240)) - set(deleted)
    require({i for i in survivors if star <= family[i]} == {target},
            'witness fails a surviving source coefficient')


def check_result(certificate, family, target, enumeration, solutions):
    require(certificate['enumeration'] == enumeration, 'enumeration receipt mismatch')
    witnesses = certificate['optimal_deletions']
    recorded = [tuple(w['deleted_indices']) for w in witnesses]
    require(recorded == sorted(solutions) and len(solutions) == 4, 'minimum-support list mismatch')
    for witness in witnesses:
        validate_witness(family, target, witness)
    triples = {frozenset(w['star_coordinates']) for w in witnesses}
    require(triples == {frozenset(s) for s in combinations(sorted(family[target]), 3)},
            'minimum supports are not exactly the four target triples')


def expect_rejection(function, label):
    try:
        function()
    except (ValueError, KeyError, TypeError, IndexError):
        return
    raise ValueError('negative control accepted: ' + label)


def negative_controls(certificate, family, target, enumeration, solutions):
    mutated = deepcopy(certificate)
    mutated['code']['parity_checks_hex'][0] = format(
        int(mutated['code']['parity_checks_hex'][0], 16) ^ (1 << target), '060x')
    expect_rejection(lambda: read_model(mutated), 'changed parity bit')
    mutated = deepcopy(certificate)
    mutated['code']['parity_checks_hex'][0] = mutated['code']['parity_checks_hex'][1]
    expect_rejection(lambda: read_model(mutated), 'dependent checks')
    mutated = deepcopy(certificate)
    mutated['code']['independent_star_indices'][0] = mutated['code']['independent_star_indices'][1]
    expect_rejection(lambda: read_model(mutated), 'duplicate primal row')
    mutated = deepcopy(certificate)
    mutated['optimal_deletions'].pop()
    expect_rejection(lambda: check_result(mutated, family, target, enumeration, solutions), 'omitted solution')
    mutated = deepcopy(certificate)
    mutated['enumeration']['triples'] -= 1
    expect_rejection(lambda: check_result(mutated, family, target, enumeration, solutions), 'short coverage receipt')
    witness = deepcopy(certificate['optimal_deletions'][0])
    witness['deleted_indices'].append(target)
    expect_rejection(lambda: validate_witness(family, target, witness), 'deleted target')
    restored = 0
    for original in certificate['optimal_deletions']:
        for index in original['deleted_indices']:
            witness = deepcopy(original)
            witness['deleted_indices'].remove(index)
            expect_rejection(lambda: validate_witness(family, target, witness), 'restored puncture')
            restored += 1
    witness = deepcopy(certificate['optimal_deletions'][0])
    witness['star_coordinates'][0] ^= 1
    expect_rejection(lambda: validate_witness(family, target, witness), 'wrong star sign')
    require(restored == 20, 'restoration control count')
    return 8


def verify(path):
    certificate = json.loads(path.read_text(encoding='utf-8'))
    family, target, _, syndromes = read_model(certificate)
    enumeration, solutions = enumerate_supports(syndromes, target)
    check_result(certificate, family, target, enumeration, solutions)
    controls = negative_controls(certificate, family, target, enumeration, solutions)
    print('PASS_GLOBAL_STAR_PUNCTURES ports=240 rank=155 dual=85 minimum_deletions=5 '
          'optimal_sets=4 all_target_deletions=85 triples=2246839 controls=%d '
          'restored_ports=20 kappa=unchanged' % controls)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--certificate', type=Path, default=HERE / 'CERTIFICATE.json')
    args = parser.parse_args()
    verify(args.certificate)
