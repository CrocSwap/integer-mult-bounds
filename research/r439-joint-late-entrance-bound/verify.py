#!/usr/bin/env python3
"""Exact joint necessary-condition check. Matthieu Pascal / Codex, Apache-2.0.

Credits: Sagar Thakrar (PR1932's late-access condition and open joint test),
Philipp / mightyOil (PR1253 closure), Adam Gall (PR1179), and the PR589/555 word.
No predecessor Python implementation is imported.
"""
import argparse
import copy
from fractions import Fraction
from functools import lru_cache
import gzip
import hashlib
import itertools
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WORD = 'research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz'
CLOSURE = 'research/r439-kernel-entrance-closure/CERTIFICATE.json'
BILL = 'research/bit-kernel-entrance-seed18/CERTIFICATE.json'
V, R, N = 111, 439, 661


def need(condition, message):
    if not condition:
        raise ValueError(message)


def checked(data, digest):
    need(hashlib.sha256(data).hexdigest() == digest, 'source digest mismatch')
    return data


def parity(x):
    return x.bit_count() & 1


def mask(registers):
    return sum(1 << (r - 2 * V) for r in registers)


def labels(x):
    return [r + 2 * V for r in range(R) if x >> r & 1]


def binary_basis(rows):
    pivots = {}
    for row in rows:
        x = row
        while x:
            p = x.bit_length() - 1
            if p not in pivots:
                pivots[p] = x
                break
            x ^= pivots[p]
    return pivots


def member(x, rows):
    pivots = binary_basis(rows)
    while x:
        p = x.bit_length() - 1
        if p not in pivots:
            return False
        x ^= pivots[p]
    return True


def rational_basis(rows):
    pivots = {}
    for row in rows:
        row = [Fraction(x) for x in row]
        for p, b in sorted(pivots.items()):
            if row[p]:
                a = row[p]
                row = [x - a * y for x, y in zip(row, b)]
        p = next((j for j, x in enumerate(row) if x), None)
        if p is not None:
            a = row[p]
            pivots[p] = tuple(x / a for x in row)
    return tuple(b for _, b in sorted(pivots.items()))


def in_rational_span(row, basis):
    row = [Fraction(x) for x in row]
    for b in basis:
        p = next(j for j, x in enumerate(b) if x)
        a = row[p]
        row = [x - a * y for x, y in zip(row, b)]
    return not any(row)


def reconstruct(w):
    need((w['v'], w['R'], w['h']) == (V, R, 8), 'word dimensions')
    fb = [rational_basis([w['lines'][j] for j in f]) for f in w['frames']]

    @lru_cache(None)
    def contained(a, b):
        return all(in_rational_span(row, fb[b]) for row in fb[a])

    values = [1 << i for i in range(N)]
    frames = list(w['start'])
    first = {}

    def apply(gates):
        for f, dst, srcs in gates:
            need(dst not in srcs, 'self-read outside the frozen gate convention')
            for r in (dst, *srcs):
                need(contained(frames[r], f), 'illegal frozen frame climb')
                frames[r] = f
                if r >= 2 * V:
                    first.setdefault(r, f)
            for r in srcs:
                values[dst] ^= values[r]

    need(all(not V <= r < 2 * V for _, d, ss in w['A'] for r in (d, *ss)),
         'A must not touch targets')
    apply(w['A'])
    need(len(first) == R, 'every helper must first occur in A')
    need(all(not fb[frames[V + t]] for t in range(V)), 'target left zero before scatter')
    snapshots = [values[r] for r in w['ret']]
    for t, row in enumerate(w['scatter']):
        for j in row:
            values[V + t] ^= snapshots[j]
    sigma = values[:]
    sigma_frames = frames[:]
    apply(w['B'])
    response = [values[V + t] >> (2 * V) for t in range(V)]
    low = (1 << (2 * V)) - 1
    for t in range(V):
        need(values[V + t] & low == (1 << (V + t)) | (1 << t), 'raw source/target boundary')
    apply(w['C'])
    need(all(contained(frames[r], w['final'][r]) for r in range(N)), 'final frame descent')
    for r in range(N):
        expected = (1 << r) if not V <= r < 2 * V else ((1 << r) | (1 << (r - V))) ^ (response[r - V] << (2 * V))
        need(values[r] == expected, 'raw cleanup boundary')
    d_values = [1 << i for i in range(N)]
    for f, dst, srcs in w['D']:
        need(not fb[f] and V <= dst < 2 * V and all(r >= 2 * V for r in srcs), 'selected D format')
        for r in srcs:
            d_values[dst] ^= d_values[r]
    need(all(d_values[V + t] >> (2 * V) == response[t] for t in range(V)), 'D != K')

    accessible = []
    generators = []
    witnesses = []
    for t in range(V):
        gs = [('snapshot:' + str(j), x) for j, x in enumerate(snapshots)]
        gs += [('register:' + str(r), sigma[r]) for r in range(N)
               if r != V + t and contained(sigma_frames[r], w['final'][V + t])]
        # Move source columns above helper columns; discard y, a favorable
        # relaxation. Low-pivot echelon vectors span the source-free kernel.
        pivots = {}
        for i, (_, value) in enumerate(gs):
            x = (value >> (2 * V)) | ((value & ((1 << V) - 1)) << R)
            combination = 1 << i
            while x:
                p = x.bit_length() - 1
                if p not in pivots:
                    pivots[p] = (x, combination)
                    break
                x ^= pivots[p][0]
                combination ^= pivots[p][1]
        rows, recipes = [], []
        for p, (x, combination) in sorted(pivots.items()):
            if p < R:
                rows.append(x)
                # Independently materialize the selected raw generator XOR.
                actual = 0
                names = []
                for i, (name, value) in enumerate(gs):
                    if combination >> i & 1:
                        actual ^= value
                        names.append(name)
                need(actual & ((1 << V) - 1) == 0 and actual >> (2 * V) == x,
                     'invalid accessible dirt witness')
                recipes.append({'helper_support': labels(x), 'xor_of': names})
        accessible.append(rows)
        generators.append(gs)
        witnesses.append(recipes)
    return response, accessible, witnesses, fb, first


def image(x, columns):
    return sum(parity(x & c) << i for i, c in enumerate(columns))


def joint_failures(response, spaces, columns):
    return [V + t for t in range(V)
            if not member(image(response[t], columns), [image(u, columns) for u in spaces[t]])]


def separating_check(row, space, columns, dual):
    need(dual > 0 and dual < (1 << len(columns)), 'invalid dual')
    need(parity(image(row, columns) & dual) == 1, 'dual does not separate response')
    need(all(parity(image(u, columns) & dual) == 0 for u in space), 'dual does not annihilate access')


def analyse(w, closure, bill):
    k, spaces, recipes, fb, first = reconstruct(w)
    classes = closure['classification']['classes']
    need(len(classes) == 366, 'closure class count')
    supports = set()
    # The completeness of these classes is the pinned PR1253 proof dependency.
    # Recheck each class's entire eligible helper set against this word.
    for row in classes:
        basis = [[Fraction(x) for x in b] for b in row['frame']]
        eligible = [r for r in range(2 * V, N)
                    if all(in_rational_span(b, fb[first[r]]) for b in basis)]
        need(eligible == row['eligible_helpers'], 'closure eligibility differs')
        for size in range(1, len(eligible) + 1):
            for ss in itertools.combinations(eligible, size):
                supports.add(mask(ss))
    need(len(supports) == 4954, 'support coverage count')
    survivors = sorted(c for c in supports if not joint_failures(k, spaces, [c]))
    c1, c2 = mask([444, 470]), mask([444, 470, 578])
    need(set(survivors) == {c1, c2}, 'single-direction survivor set')
    targets = joint_failures(k, spaces, [c1, c2])
    need(targets == [113, 118, 150, 153, 192, 197, 214, 219], 'joint obstruction targets')
    need(len(binary_basis([c1, c2])) == 2, 'directions must be independent')
    certificates = []
    for r in targets:
        t = r - V
        separating_check(k[t], spaces[t], [c1, c2], 3)
        need(set(binary_basis(image(u, [c1, c2]) for u in spaces[t]).values()) == {3},
             'joint access image basis')
        certificates.append({'target': r, 'response_bits': [0, 1], 'access_image_basis_bits': [[1, 1]],
                             'dual_bits': [1, 1], 'dual_helper_support': labels(c1 ^ c2),
                             'accessible_dirt_basis': [labels(u) for u in spaces[t]],
                             'access_witnesses': recipes[t]})
    # Exhaustive tiny image oracle corroborates joint membership at every target.
    for t in range(V):
        images = {0}
        for u in spaces[t]:
            a = image(u, [c1, c2])
            images |= {x ^ a for x in list(images)}
        need((image(k[t], [c1, c2]) not in images) == (V + t in targets), 'image oracle differs')
    controls = []

    def reject(name, fn):
        try:
            fn()
        except ValueError:
            controls.append(name)
        else:
            raise ValueError('accepted control: ' + name)

    t = targets[0] - V
    reject('wrong dual coefficient', lambda: separating_check(k[t], spaces[t], [c1, c2], 1))
    reject('response bit removed', lambda: separating_check(k[t] ^ mask([578]), spaces[t], [c1, c2], 3))
    reject('unavailable helper578 admitted', lambda: separating_check(k[t], spaces[t] + [mask([578])], [c1, c2], 3))
    reject('changed source bytes', lambda: checked(b'changed', hashlib.sha256(b'original').hexdigest()))
    need(not joint_failures(k, spaces, [c1]), 'kernel positive control')
    need(not joint_failures(k, spaces, [c2]), 'single-triple relaxation positive control')
    need(not joint_failures(k, spaces, [c1, c1]), 'dependent duplicate is not a rank-two obstruction')
    need(joint_failures(k, spaces, [mask([578])]) == targets, 'difference direction must fail')
    relaxed = copy.deepcopy(spaces)
    for r in targets:
        relaxed[r - V].append(mask([578]))
    need(not joint_failures(k, relaxed, [c1, c2]), 'geometry-relaxed positive control')
    for a, b in itertools.permutations([c1, c2, c1 ^ c2], 2):
        need(joint_failures(k, spaces, [a, b]) == targets, 'joint condition changed under basis change')
    return {'status': 'PASS_R439_JOINT_LATE_ENTRANCE_BOUND', 'word_columns': N,
            'closure_classes': len(classes), 'support_columns_checked': len(supports),
            'single_direction_survivors': [labels(c1), labels(c2)],
            'maximum_joint_rank': 1, 'joint_pair_rank': 2,
            'joint_obstructions': certificates,
            'positive_controls': ['kernel pair', 'single triple in necessary relaxation',
                                  'dependent repeated column', 'geometry-relaxed joint pair'],
            'rejection_controls': controls, 'invertible_basis_changes_checked': 6,
            'inherited_kernel_entrance_invoice': {'source': BILL, 'baseline': bill['baseline']['profile'],
              'candidate': bill['candidate']['profile'], 'rank_mass': [bill['baseline']['rank_mass'], bill['candidate']['rank_mass']],
              'ADDs': [bill['baseline']['ADDs'], bill['candidate']['ADDs']], 'reexecuted_here': False},
            'scope': 'fixed PR589 A/scatter, helper-only common-first-contact entrance columns, joint late-access necessary condition; single triple construction remains open',
            'new_kappa': False}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--write', action='store_true', help='create the missing certificate; never overwrite')
    args = parser.parse_args()
    sources = json.loads((HERE / 'SOURCES.json').read_text(encoding='utf-8'))
    for row in sources['files']:
        if row['usage'] == 'input':
            checked((ROOT / row['path']).read_bytes(), row['sha256'])
    result = analyse(json.loads(gzip.decompress((ROOT / WORD).read_bytes())),
                     json.loads((ROOT / CLOSURE).read_text(encoding='utf-8')),
                     json.loads((ROOT / BILL).read_text(encoding='utf-8')))
    certificate = HERE / 'CERTIFICATE.json'
    if args.write:
        with certificate.open('x', encoding='utf-8') as f:
            f.write(json.dumps(result, indent=2) + '\n')
    else:
        need(result == json.loads(certificate.read_text(encoding='utf-8')), 'certificate differs')
    print('PASS_R439_JOINT_LATE_ENTRANCE_BOUND columns=661 supports=4954 survivors=2 joint_rank_max=1 separating_targets=8 controls=4 basis_changes=6 no_new_kappa')


if __name__ == '__main__':
    main()
