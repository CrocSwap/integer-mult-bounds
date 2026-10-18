#!/usr/bin/env python3
"""Exact formal F2[GL_2(F2)] coordinate-CNOT register census (stdlib only)."""

import argparse
import hashlib
import importlib.util
import itertools
import json
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location('cnot_independent', PACKAGE/'independent.py')
INDEPENDENT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(INDEPENDENT)
GROUP = tuple(itertools.permutations(range(3)))
INDEX = {g: i for i, g in enumerate(GROUP)}
MUL = tuple(tuple(INDEX[tuple(p[q[i]] for i in range(3))] for q in GROUP)
            for p in GROUP)
E = INDEX[(0, 1, 2)]
A = INDEX[(0, 2, 1)]
B = INDEX[(2, 1, 0)]
SWAP = INDEX[(1, 0, 2)]


def require(ok, message):
    if not ok:
        raise ValueError(message)


def read_json(path):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            require(key not in result, 'duplicate JSON key: '+key)
            result[key] = value
        return result
    return json.loads(path.read_text(), object_pairs_hook=unique)


def compare_receipt(actual, expected):
    # JSON types matter: Python equality alone equates True with 1.
    encode = lambda x: json.dumps(x, sort_keys=True, separators=(',', ':'), allow_nan=False)
    require(encode(actual) == encode(expected), 'fresh receipt differs from EXPECTED.json')


def translate(mask, g):
    """Multiply a formal coefficient by [g] on the right."""
    out = 0
    for h in range(6):
        if mask >> h & 1:
            out ^= 1 << MUL[h][g]
    return out


TRANSLATE = tuple(tuple(translate(mask, g) for mask in range(64))
                  for g in range(6))


def identity(r):
    return sum(1 << (6 * (i*r+i) + E) for i in range(r))


def entry(state, r, i, j):
    return state >> (6*(i*r+j)) & 63


def generators(r):
    return tuple((u, v, g)
                 for u in range(1, 1 << r)
                 for v in range(1, 1 << r)
                 if (u & v).bit_count() % 2
                 for g in (A, B))


def append(state, r, gate):
    """Right multiply by I+([g]+1)uv^T, retaining all formal coefficients."""
    u, v, g = gate
    out = state
    table = TRANSLATE[g]
    for i in range(r):
        val = 0
        for j in range(r):
            if u >> j & 1:
                val ^= entry(state, r, i, j)
        val ^= table[val]
        for j in range(r):
            if v >> j & 1:
                out ^= val << (6 * (i*r+j))
    return out


def word_state(r, word, gates):
    out = identity(r)
    for index in word:
        out = append(out, r, gates[index])
    return out


def target(r, active=2):
    return sum(1 << (6*(i*r+i) + (SWAP if i < active else E))
               for i in range(r))


def right_target(state, r, active=2):
    out = 0
    for i in range(r):
        for j in range(r):
            value = entry(state, r, i, j)
            out |= (TRANSLATE[SWAP][value] if j < active else value) << (6*(i*r+j))
    return out


def digest(states, r):
    width = (6*r*r + 7)//8
    h = hashlib.sha256()
    for state in sorted(states):
        h.update(state.to_bytes(width, 'little'))
    return h.hexdigest()


def census(r):
    gates = generators(r)
    ball = {identity(r): ()}
    layers = [[identity(r)]]
    layer_counts = [1]
    for depth in range(1, 4):
        new = []
        for state in layers[-1]:
            prefix = ball[state]
            for k, gate in enumerate(gates):
                nxt = append(state, r, gate)
                if nxt not in ball:
                    ball[nxt] = prefix + (k,)
                    new.append(nxt)
        layers.append(new)
        layer_counts.append(len(new))
    # Every gate is an involution, so reversing a word gives its exact inverse.
    ball2 = {state: word for state, word in ball.items() if len(word) <= 2}
    shifted = {right_target(word_state(r, word[::-1], gates), r): word
               for word in ball2.values()}
    hits = sorted(set(shifted).intersection(ball))
    independent, independent_receipt = INDEPENDENT.dense_ball(r)
    require(independent == set(ball), 'independent dense and formal balls differ')
    require(independent_receipt['exact_distance_layers_0_to_3'] == layer_counts,
            'independent distance layers differ')
    positive_minima = []
    for active in (0, 1):
        positive_shifted = {
            right_target(word_state(r, word[::-1], gates), r, active): word
            for word in ball2.values()}
        positive_hits = set(positive_shifted).intersection(ball)
        minimum = min(len(positive_shifted[h])+len(ball[h]) for h in positive_hits)
        require(minimum == 3*active, 'positive meet-in-the-middle control fails')
        positive_minima.append(minimum)
    direct = tuple(gates.index((1 << role, 1 << role, g))
                   for role in range(2) for g in (A, B, A))
    require(word_state(r, direct, gates) == target(r), 'direct formal word fails')
    return {
        'registers': r,
        'active_targets': 2,
        'restored_dirty_registers': r-2,
        'scalar_rank_one_idempotents': len(gates)//2,
        'paid_generators': len(gates),
        'exact_distance_layers_0_to_3': layer_counts,
        'ball2_size': len(ball2),
        'ball3_size': len(ball),
        'ball2_sha256': digest(ball2, r),
        'ball3_sha256': digest(ball, r),
        'inverse_ball2_times_target_sha256': digest(shifted, r),
        'intersections_through_five': len(hits),
        'minimum_paid_calls': 6 if not hits else min(
            len(shifted[h])+len(ball[h]) for h in hits),
        'independent_dense': independent_receipt,
        'positive_identity_and_one_swap_minima': positive_minima,
        'direct_six_call_word': [list(gates[k]) for k in direct],
    }


def controls():
    r = 3
    d = INDEPENDENT
    names = []
    direct = tuple((1 << role, 1 << role, g)
                   for role in range(2) for g in (A, B, A))

    def replay(word):
        value = identity(r)
        for gate in word:
            value = append(value, r, gate)
        return value

    # Every individual omission fails, with the complete dirty boundary tested.
    for i in range(6):
        require(replay(direct[:i]+direct[i+1:]) != target(r), 'omission accepted')
        names.append(f'omitted_call_{i}')
    wrong = list(direct)
    wrong[1] = (1, 1, A)
    require(replay(wrong) != target(r), 'wrong address label accepted')
    names.append('wrong_address_label')

    # Correct active outputs alone do not imply restoration of a dirty helper.
    unrestored = replay(direct+((4, 4, A),))
    require(all(entry(unrestored, r, i, j) == entry(target(r), r, i, j)
                for i in range(2) for j in range(r)), 'dirty control active map')
    require(unrestored != target(r), 'dirty helper change accepted')
    names.append('unrestored_dirty_register')

    # A scalar trailing shear leaks dirty input into the first active output,
    # but is invisible on the clean-only input subspace.
    leakage = target(r) ^ (1 << (6*2+SWAP))
    require(all(entry(leakage, r, i, j) == entry(target(r), r, i, j)
                for i in range(r) for j in range(2)), 'clean-only control')
    require(leakage != target(r), 'dirty-to-active leakage accepted')
    augmentation = tuple(sum(entry(leakage, r, i, j).bit_count()%2 << j
                             for j in range(r)) for i in range(r))
    require(augmentation != d.unit(r), 'nonidentity scalar residue accepted')
    names.extend(['clean_only_dirty_leakage', 'nonidentity_scalar_augmentation'])

    # A rank-two projector makes the two swaps in three calls. It must be
    # rejected as a unit call; its honest bill is two units per occurrence.
    rank_two = (1, 2, 0)
    wide = d.unit(18)
    for g in (d.A, d.B, d.A):
        wide = d.multiply(wide, d.represented_gate(rank_two, g))
    require(d.formal_encoding(wide, r) == target(r), 'rank-two scope fixture')
    require(d.rank(rank_two) == 2 and rank_two not in d.projectors(r),
            'rank-two call underpricing accepted')
    names.append('rank_two_projector_underpricing')

    # Adding S as an allowed address label makes the two-call word legal.
    expanded = replay(((1, 1, SWAP), (2, 2, SWAP)))
    require(expanded == target(r) and SWAP not in (A, B), 'expanded-label scope fixture')
    names.append('uncharged_address_alphabet_expansion')

    # The natural 2D representation loses formal information. Its kernel
    # contains the sum of all six group elements, even after augmentation.
    kernel_rows = tuple(0 for _ in range(2))
    for matrix in d.GROUP:
        kernel_rows = tuple(x ^ y for x, y in zip(kernel_rows, matrix))
    require(kernel_rows == (0, 0) and 6 % 2 == 0, 'natural-image kernel fixture')
    alias = target(r) ^ (63 << 6)  # add that kernel element at entry (0,1)
    require(alias != target(r), 'natural-image alias accepted as formal equality')
    names.append('nonfaithful_natural_representation')

    require(MUL[A][B] != MUL[B][A], 'noncommuting labels accidentally commute')
    names.append('address_multiplication_order')
    return names


def check_sources():
    sources = read_json(PACKAGE/'SOURCES.json')
    checked = []
    for item in sources['files']:
        if item['usage'] != 'input':
            continue
        path = Path(item['path'])
        require(not path.is_absolute() and '..' not in path.parts, 'invalid source path')
        actual = hashlib.sha256((PACKAGE.parents[1]/path).read_bytes()).hexdigest()
        require(actual == item['sha256'], 'source pin mismatch: '+str(path))
        checked.append(str(path))
    require(checked == ['research/bit-three-register-lower-bound/README.md'],
            'source input inventory changed')
    return checked


def build_result():
    return {'format': 'coordinate-cnot-register-bound-v1',
            'group_permutations': [list(p) for p in GROUP],
            'labels': {'identity': E, 'a': A, 'b': B, 'swap': SWAP},
            'censuses': [census(r) for r in (2, 3)],
            'symbolic_proof_checks': INDEPENDENT.proof_checks(),
            'scalar_normalization_checks': INDEPENDENT.scalar_checks(),
            'controls': controls(),
            'checked_context_inputs': check_sources()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--emit', action='store_true', help='print freshly computed receipt')
    args = parser.parse_args()
    result = build_result()
    if args.emit:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        expected = read_json(PACKAGE/'EXPECTED.json')
        compare_receipt(result, expected)
        print('PASS_COORDINATE_CNOT_REGISTER_BOUND minimum=6 '
              'dirty_registers=arbitrary census_r=2,3 symbolic_patterns=31 '
              f'controls={len(result["controls"])} no_new_kappa')


if __name__ == '__main__':
    main()
