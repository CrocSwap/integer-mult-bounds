#!/usr/bin/env python3
"""Exact finite corroboration of the written all-register UT3 theorem.

steph4n-gh, with substantial OpenAI Codex assistance. Apache-2.0.
The universal lower bound is the README proof, not a finite search here.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import random


HERE = Path(__file__).resolve().parent


def require(condition, message):
    if not condition:
        raise ValueError(message)


def group_mul(g, h):
    x, y, z = g & 1, (g >> 1) & 1, (g >> 2) & 1
    X, Y, Z = h & 1, (h >> 1) & 1, (h >> 2) & 1
    return (x ^ X) | ((y ^ Y) << 1) | ((z ^ Z ^ (x & Y)) << 2)


def swap(g):
    x, y, z = g & 1, (g >> 1) & 1, (g >> 2) & 1
    return y | (x << 1) | ((z ^ (x & y)) << 2)


def coeff_mul(left, right):
    value = 0
    for g in range(8):
        if (left >> g) & 1:
            for h in range(8):
                if (right >> h) & 1:
                    value ^= 1 << group_mul(g, h)
    return value


def fid(r):
    return tuple(tuple(int(i == j) for j in range(r)) for i in range(r))


def fmul(left, right):
    r = len(left)
    out = [[0] * r for _ in range(r)]
    for i in range(r):
        for k in range(r):
            if left[i][k]:
                for j in range(r):
                    out[i][j] ^= coeff_mul(left[i][k], right[k][j])
    return tuple(map(tuple, out))


def bid(r):
    return tuple(1 << i for i in range(r))


def bmul(left, right):
    out = []
    for row in left:
        value = 0
        for i, source in enumerate(right):
            if (row >> i) & 1:
                value ^= source
        out.append(value)
    return tuple(out)


def bxor(left, right):
    return tuple(a ^ b for a, b in zip(left, right))


def rank(rows):
    pivots = {}
    for row in rows:
        while row:
            p = row.bit_length() - 1
            if p in pivots:
                row ^= pivots[p]
            else:
                pivots[p] = row
                break
    return len(pivots)


def projector(r, u, v):
    require(0 < u < 1 << r and 0 < v < 1 << r, 'projector dimensions')
    require((u & v).bit_count() % 2 == 1, 'projector is not idempotent')
    return tuple(v if (u >> i) & 1 else 0 for i in range(r))


def factor(r, call):
    label, u, v = call
    require(label in (1, 2), 'unpriced address label')
    n = projector(r, u, v)
    delta = (1 << label) ^ 1
    return tuple(tuple(int(i == j) ^ (delta if (n[i] >> j) & 1 else 0)
                       for j in range(r)) for i in range(r))


def word_matrix(r, word):
    out = fid(r)
    for call in word:
        out = fmul(out, factor(r, call))
    return out


def target(r, k):
    require(1 <= k <= r, 'target dimensions')
    return tuple(tuple((1 << 4 if i < k else 1) if i == j else 0
                       for j in range(r)) for i in range(r))


def scalar_form(rows):
    r = len(rows)
    return tuple(tuple((row >> j) & 1 for j in range(r)) for row in rows)


def bases(r):
    s, inv = bid(r), bid(r)
    if r > 1:
        for i in range(r):
            e = list(bid(r))
            e[i] ^= 1 << ((i + 1) % r)
            s = bmul(s, e)
            inv = bmul(e, inv)
    require(bmul(s, inv) == bid(r), 'basis inverse')
    return s, inv


def witness(r, k, mixed=False):
    s, inv = bases(r) if mixed else (bid(r), bid(r))
    word = []
    for i in range(k):
        u = sum(((s[j] >> i) & 1) << j for j in range(r))
        v = inv[i]
        word.extend((g, u, v) for g in (1, 2, 1, 2))
    expected = fmul(fmul(scalar_form(s), target(r, k)), scalar_form(inv))
    p = bmul(bmul(s, tuple(1 << i if i < k else 0 for i in range(r))), inv)
    return word, expected, p


def natural(g):
    return (1 | ((g & 1) << 1) | (((g >> 2) & 1) << 2),
            2 | (((g >> 1) & 1) << 2), 4)


def image(matrix, swapped=False):
    r = len(matrix)
    out = [0] * (3 * r)
    for i in range(r):
        for j in range(r):
            for g in range(8):
                if (matrix[i][j] >> g) & 1:
                    rep = natural(swap(g) if swapped else g)
                    for a in range(3):
                        for b in range(3):
                            if (rep[a] >> b) & 1:
                                out[a * r + i] ^= 1 << (b * r + j)
    return tuple(out)


def block(matrix, r, a, b):
    return tuple((matrix[a * r + i] >> (b * r)) & ((1 << r) - 1)
                 for i in range(r))


def rank_evidence(r, word, formal, expected_p=None):
    zero = (0,) * r
    sums = {1: zero, 2: zero}
    cross = {(1, 2): zero, (2, 1): zero}
    for g, u, v in word:
        n = projector(r, u, v)
        other = 3 - g
        cross[other, g] = bxor(cross[other, g], bmul(sums[other], n))
        sums[g] = bxor(sums[g], n)
    span_ranks = {}
    for g in (1, 2):
        calls = [(u, v) for label, u, v in word if label == g]
        x = tuple(sum(((u >> i) & 1) << j for j, (u, v) in enumerate(calls))
                  for i in range(r))
        y = tuple(v for u, v in calls)
        require(bmul(x, y) == sums[g], 'sum factorization')
        rx, ry = rank(x), rank(y)
        require(rx + ry <= len(calls) + rank(sums[g]), 'rank inequality')
        span_ranks[g] = (rx, ry, len(calls))
    for swapped in (False, True):
        a, b = (2, 1) if swapped else (1, 2)
        rep = image(formal, swapped)
        for i in range(3):
            for j in range(3):
                expected = (bid(r) if i == j else sums[a] if (i, j) == (0, 1)
                            else sums[b] if (i, j) == (1, 2)
                            else cross[a, b] if (i, j) == (0, 2) else zero)
                require(block(rep, r, i, j) == expected, 'representation block formula')
        require(rank(cross[a, b]) <= min(span_ranks[a][0], span_ranks[b][1]),
                'cross span bounds')
    if expected_p is not None:
        k = rank(expected_p)
        require(sums[1] == sums[2] == zero, 'target linear blocks')
        require(cross[1, 2] == cross[2, 1] == expected_p, 'target cross blocks')
        for g in (1, 2):
            rx, ry, count = span_ranks[g]
            require(rx >= k and ry >= k and count >= 2 * k, 'target call bound')
    return {str(g): list(span_ranks[g]) for g in (1, 2)}


def primary():
    for g in range(8):
        require(swap(swap(g)) == g, 'automorphism involution')
        for h in range(8):
            require(swap(group_mul(g, h)) == group_mul(swap(g), swap(h)), 'automorphism')
            for switched in (False, True):
                phi = lambda x: natural(swap(x) if switched else x)
                require(phi(group_mul(g, h)) == bmul(phi(g), phi(h)), 'homomorphism')
            for f in range(8):
                require(group_mul(group_mul(g, h), f) == group_mul(g, group_mul(h, f)),
                        'group associativity')
    require(group_mul(group_mul(group_mul(1, 2), 1), 2) == 4, 'central commutator')
    fixtures = []
    digest = hashlib.sha256()
    for r in range(1, 6):
        for k in range(1, r + 1):
            for mixed in (False, True):
                word, expected, p = witness(r, k, mixed)
                actual = word_matrix(r, word)
                require(actual == expected, 'formal dirty endpoint')
                ranks = rank_evidence(r, word, actual, p)
                require(len(word) == 4 * k, 'complete witness bill')
                digest.update(bytes(value for row in actual for value in row))
                fixtures.append({'r': r, 'k': k, 'mixed': mixed, 'calls': 4 * k,
                                 'a_b_span_ranks_and_counts': ranks})
    # Deterministic formula checks, not an optimality search or claimed coverage.
    rng = random.Random(14)
    for r in range(1, 6):
        for length in range(15):
            word = []
            for _ in range(length):
                u = rng.randrange(1, 1 << r)
                choices = [v for v in range(1, 1 << r) if (u & v).bit_count() % 2]
                word.append((rng.choice((1, 2)), u, rng.choice(choices)))
            rank_evidence(r, word, word_matrix(r, word))
    controls = []
    r, k = 4, 3
    word, expected, _ = witness(r, k, True)
    for i in range(len(word)):
        require(word_matrix(r, word[:i] + word[i + 1:]) != expected, 'omission accepted')
        controls.append('omit_call_' + str(i))
        changed = list(word)
        g, u, v = changed[i]
        changed[i] = (3 - g, u, v)
        require(word_matrix(r, changed) != expected, 'wrong label accepted')
        controls.append('wrong_label_' + str(i))
    for label, call in [('nonidempotent', (1, 1, 2)), ('unpriced_c', (4, 1, 1)),
                        ('zero_projector', (1, 0, 1)), ('out_of_range', (1, 16, 1))]:
        try:
            factor(r, call)
        except ValueError:
            controls.append(label)
        else:
            raise ValueError('invalid call accepted: ' + label)
    direct, expected, _ = witness(r, k)
    dirty = direct + [(g, 8, 8) for g in (1, 2, 1, 2)]
    require(word_matrix(r, dirty) != expected, 'dirty extra not restored')
    controls.append('unrestored_dirty_extra')
    lam = coeff_mul((1 << 1) ^ 1, (1 << 4) ^ 1)
    require(lam != 0, 'nonfaithfulness fixture vanished formally')
    mutation = [list(row) for row in fid(r)]
    mutation[3][0] ^= lam
    mutation = tuple(map(tuple, mutation))
    require(fmul(mutation, mutation) == fid(r), 'dirty shear invertibility')
    fake = fmul(expected, mutation)
    require(fake != expected, 'formal mutation accepted')
    for switched in (False, True):
        require(image(fake, switched) == image(expected, switched),
                'intended invisible representation control')
    controls.append('both_images_miss_formal_dirty_shear')
    # Exact counterexamples to dropping either alphabet/rank-one hypothesis.
    c_word = fid(r)
    for i in range(k):
        f = [list(row) for row in fid(r)]
        f[i][i] = 1 << 4
        c_word = fmul(c_word, tuple(map(tuple, f)))
    require(c_word == expected, 'expanded c-alphabet witness')
    higher_rank_word = fid(r)
    for g in (1, 2, 1, 2):
        f = tuple(tuple((1 << g if i < k else 1) if i == j else 0
                        for j in range(r)) for i in range(r))
        higher_rank_word = fmul(higher_rank_word, f)
    require(higher_rank_word == expected and k > 1, 'higher-rank-call witness')
    return {'method': 'formal group-algebra coefficients with triple group law',
            'group_associativity_cases': 512, 'homomorphism_cases_per_representation': 64,
            'fixtures': fixtures, 'formal_endpoint_sha256': digest.hexdigest(),
            'arbitrary_word_formula_fixtures': 75, 'formula_fixture_seed': 14,
            'negative_controls': controls, 'invisible_nonzero_coefficient_mask': lam,
            'hypothesis_boundary_witnesses': {
                'expanded_c_alphabet': {'r': r, 'k': k, 'calls': k},
                'rank_k_paid_projectors': {'r': r, 'k': k, 'calls': 4}},
            'proof_scope': 'README theorem is universal; these checks are finite corroboration'}


def run():
    spec = importlib.util.spec_from_file_location('ut3_independent', HERE / 'independent.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return {'schema_version': 1, 'primary': primary(), 'independent': module.run(),
            'statement': 'For every r>=k>=1, n_a>=2k and n_b>=2k; direct word attains4k.',
            'no_new_kappa': True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--emit', action='store_true', help='print receipt without writing files')
    args = parser.parse_args()
    receipt = run()
    if args.emit:
        print(json.dumps(receipt, sort_keys=True, indent=2))
    else:
        expected = json.loads((HERE / 'CERTIFICATE.json').read_text())
        require(receipt == expected, 'certificate differs; inspect exact evidence before updating')
        print('PASS_UT3_ALL_REGISTERS minimum=4k a_calls>=2k b_calls>=2k '
              'proof=all_r>=k>=1 finite_fixtures=see_certificate no_new_kappa')


if __name__ == '__main__':
    main()
