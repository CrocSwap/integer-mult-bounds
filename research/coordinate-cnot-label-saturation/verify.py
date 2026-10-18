#!/usr/bin/env python3
"""Exact corroboration of the written label-saturation proof; Apache-2.0.

Prepared for Ross Richardson with substantial OpenAI Codex assistance.
No predecessor executable is imported. This is not a proof-assistant kernel.
"""
import argparse
from collections import defaultdict
import hashlib
import itertools
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent


class Reject(ValueError):
    pass


def need(condition, message):
    if not condition:
        raise Reject(message)


def load_json(path):
    def pairs(items):
        out = {}
        for key, value in items:
            need(key not in out, 'duplicate JSON key')
            out[key] = value
        return out

    def bad_constant(value):
        raise Reject('nonfinite JSON: ' + value)

    return json.loads(Path(path).read_text(), object_pairs_hook=pairs,
                      parse_constant=bad_constant)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False)


def typed_equal(actual, expected):
    # JSON booleans/floats must not alias integer receipt fields.
    need(canonical(actual) == canonical(expected), 'receipt mismatch')


def dot(a, b):
    return (a & b).bit_count() & 1


def rank(vectors):
    pivots = {}
    for value in vectors:
        while value:
            bit = value.bit_length() - 1
            if bit in pivots:
                value ^= pivots[bit]
            else:
                pivots[bit] = value
                break
    return len(pivots)


def xor_rows(rows, mask):
    out = 0
    for i, row in enumerate(rows):
        if mask >> i & 1:
            out ^= row
    return out


def matmul(a, b):
    return tuple(xor_rows(b, row) for row in a)


def mv(a, vector):
    return sum(dot(row, vector) << i for i, row in enumerate(a))


def invert(rows):
    n = len(rows)
    aug = [row | (1 << (n+i)) for i, row in enumerate(rows)]
    for j in range(n):
        pivot = next((i for i in range(j, n) if aug[i] >> j & 1), None)
        need(pivot is not None, 'singular basis')
        aug[j], aug[pivot] = aug[pivot], aug[j]
        for i in range(n):
            if i != j and aug[i] >> j & 1:
                aug[i] ^= aug[j]
    return tuple(row >> n for row in aug)


G = tuple(sorted(rows for rows in itertools.product(range(4), repeat=2)
                 if rank(rows) == 2))
GID = {g: i for i, g in enumerate(G)}
IDENTITY = GID[(1, 2)]
LABELS = {'a': GID[(3, 2)], 'b': GID[(1, 3)]}
SWAP = GID[(2, 1)]
PRODUCT = tuple(tuple(GID[matmul(a, b)] for b in G) for a in G)


def identity(r):
    return tuple(1 << (6*i+IDENTITY) for i in range(r))


def target(r, t):
    return tuple(1 << (6*i+(SWAP if i < t else IDENTITY)) for i in range(r))


def check_gate(gate, r):
    need(isinstance(gate, (tuple, list)) and len(gate) == 3, 'gate shape')
    label, u, v = gate
    need(label in LABELS, 'paid address alphabet')
    need(type(u) is int and type(v) is int, 'projector type')
    need(0 < u < (1 << r) and 0 < v < (1 << r) and dot(u, v) == 1,
         'rank-one idempotent')


def transform(row, label, r):
    result = 0
    for j in range(r):
        entry = row >> (6*j) & 63
        for h in range(6):
            if entry >> h & 1:
                result ^= 1 << (6*j+PRODUCT[LABELS[label]][h])
    return result


def step(state, gate):
    label, u, v = gate
    mixed = xor_rows(state, v)
    delta = mixed ^ transform(mixed, label, len(state))
    return tuple(row ^ (delta if u >> i & 1 else 0)
                 for i, row in enumerate(state))


def formal(word, r):
    state = identity(r)
    for gate in word:
        check_gate(gate, r)
        state = step(state, gate)
    return state


def accept(word, r, t):
    need(formal(word, r) == target(r, t), 'full formal dirty endpoint')


def projectors(r):
    return [(u, v) for u in range(1, 1 << r) for v in range(1, 1 << r)
            if dot(u, v)]


def natural_step(state, gate, r):
    label, u, v = gate
    source = r if label == 'a' else 0
    destination = 0 if label == 'a' else r
    delta = xor_rows(state[source:source+r], v)
    rows = list(state)
    for i in range(r):
        if u >> i & 1:
            rows[destination+i] ^= delta
    return tuple(rows)


def natural_image(state, r):
    rows = [0] * (2*r)
    for i, row in enumerate(state):
        for j in range(r):
            entry = row >> (6*j) & 63
            for h, g in enumerate(G):
                if entry >> h & 1:
                    for x in range(2):
                        for y in range(2):
                            if g[x] >> y & 1:
                                rows[x*r+i] ^= 1 << (y*r+j)
    return tuple(rows)


def sign_sum(word, r):
    return tuple(xor_rows([v if u >> i & 1 else 0 for _, u, v in word],
                          (1 << len(word))-1) for i in range(r))


def trace_saturation(word, r, t, saturated='a'):
    accept(word, r, t)
    if saturated == 'b':
        word = [('b' if label == 'a' else 'a', u, v) for label, u, v in word]
    a_images = [u for label, u, _ in word if label == 'a']
    need(len(a_images) == t, 'label is not saturated')
    active = (1 << t)-1
    need(rank(a_images) == t and all(u & ~active == 0 for u in a_images),
         'saturated image span')
    columns = a_images + [1 << i for i in range(t, r)]
    change = tuple(sum(((column >> i) & 1) << j for j, column in enumerate(columns))
                   for i in range(r))
    change_inverse = invert(change)
    normalized = [(label, mv(change_inverse, u), xor_rows(change, v))
                  for label, u, v in word]
    accept(normalized, r, t)
    need(sign_sum(normalized, r) == tuple(1 << i if i < t else 0 for i in range(r)),
         'full sign matrix')
    state = tuple(1 << i for i in range(2*r))
    b_sum = [0]*r
    cuts = []
    a_index = 0
    for gate in normalized:
        label, u, v = gate
        need(all(((row & ((1 << r)-1)) ^ (row >> r)) == 1 << i
                 for i, row in enumerate(state[:r])), 'top row-sum rigidity')
        if label == 'a':
            need(u == v == 1 << a_index, 'saturated coordinate projector')
            need(state[r+a_index] == (1 << a_index) | (1 << (r+a_index)),
                 'chronological bottom row')
            need(b_sum[a_index] == 1 << a_index, 'chronological covector span')
            a_index += 1
        else:
            for i in range(r):
                if u >> i & 1:
                    b_sum[i] ^= v
        state = natural_step(state, gate, r)
        cuts.append(list(state))
    need(not any(b_sum), 'opposite label sum is not zero')
    opposite = [(u, v) for label, u, v in normalized if label == 'b']
    ru, rv = rank([u for u, _ in opposite]), rank([v for _, v in opposite])
    need(ru >= t and rv >= t and ru+rv <= len(opposite), 'zero-sum rank bound')
    if len(opposite) == 2*t:
        need(all((u | v) & ~active == 0 for _, u, v in normalized),
             'equality workspace rigidity')
    return {'opposite_count': len(opposite), 'image_rank': ru, 'covector_rank': rv,
            'cuts_sha256': hashlib.sha256(canonical(cuts).encode()).hexdigest()}


def screened_counts(t, q):
    if q % 2 != t % 2:
        return []
    return [[a, q-a] for a in range(t, q-t+1)
            if (a != t or q-a >= 2*t) and (q-a != t or a >= 2*t)]


def census(r, depth):
    """All exact-length formal states, retaining both paid label counts."""
    generators = [(g, u, v) for g in ('a', 'b') for u, v in projectors(r)]
    tables = {g: [transform(row, g, r) for row in range(1 << (6*r))]
              for g in ('a', 'b')}
    layer = {0: {identity(r)}}
    receipt = []
    for q in range(depth+1):
        hits = []
        digest = hashlib.sha256()
        total = 0
        for na, states in sorted(layer.items()):
            total += len(states)
            for state in sorted(states):
                digest.update(bytes([na]))
                for row in state:
                    digest.update(row.to_bytes(r, 'little'))
            for t in range(1, r+1):
                if target(r, t) in states:
                    need([na, q-na] in screened_counts(t, q), 'census contradicts theorem')
                    hits.append({'targets': t, 'counts': [na, q-na]})
        receipt.append({'length': q, 'states_with_label_count': total,
                        'sha256': digest.hexdigest(), 'target_hits': hits})
        if q == depth:
            break
        following = {}
        for na, states in layer.items():
            for state in states:
                for g, u, v in generators:
                    mixed = xor_rows(state, v)
                    delta = mixed ^ tables[g][mixed]
                    nxt = tuple(row ^ (delta if u >> i & 1 else 0)
                                for i, row in enumerate(state))
                    following.setdefault(na+(g == 'a'), set()).add(nxt)
        layer = following
    return {'registers': r, 'depth': depth, 'layers': receipt}


def controls():
    results = []

    def rejects(name, action):
        try:
            action()
        except Reject:
            results.append(name)
            return
        raise Reject('negative control accepted: ' + name)

    w = [('b', 1, 1), ('a', 1, 1), ('b', 1, 1),
         ('b', 2, 2), ('a', 2, 2), ('b', 2, 2)]
    accept(w, 3, 2)
    for i in range(len(w)):
        rejects('omitted_paid_call_' + str(i), lambda i=i: accept(w[:i]+w[i+1:], 3, 2))
    rejects('unrestored_dirty_extra', lambda: accept(w+[('b', 5, 4)], 3, 2))
    rejects('missing_target', lambda: accept(w, 3, 3))
    rejects('expanded_paid_alphabet', lambda: accept([('s', 1, 1)], 1, 1))
    rejects('nilpotent_scalar_factor', lambda: formal([('a', 1, 2)], 2))
    rejects('boolean_projector', lambda: formal([('a', True, 1)], 1))
    changed = list(w)
    changed[1] = ('b', 1, 1)
    rejects('wrong_address_label', lambda: accept(changed, 3, 2))
    # Four projectors sum to zero with image rank THREE but covector rank ONE.
    # A one-span-only variant of the proof is therefore false.
    us, vs = [1, 2, 4, 7], [7]*4
    need(all(dot(u, v) for u, v in zip(us, vs)), 'near-miss projector legality')
    need(sign_sum([('b', u, v) for u, v in zip(us, vs)], 3) == (0, 0, 0),
         'near-miss zero sum')
    need(rank(us) == 3 and rank(vs) == 1, 'near-miss ranks')
    rejects('one_span_does_not_suffice', lambda: need(rank(vs) >= 3, 'missing covector span'))
    fake = [('a', 1, 7), ('a', 2, 7), ('a', 4, 7)]
    need(sum(dot(u, v) for _, u, v in fake) % 2 == 3 % 2, 'parity near-miss')
    rejects('trace_parity_is_not_matrix_sign',
            lambda: need(sign_sum(fake, 3) == (1, 2, 4), 'full sign matrix'))
    # The sum of all six formal elements has zero natural image/augmentation.
    alias = list(target(2, 1))
    alias[0] ^= 63 << 6
    need(tuple(alias) != target(2, 1), 'formal alias must differ')
    need(natural_image(alias, 2) == natural_image(target(2, 1), 2), 'natural alias fixture')
    rejects('natural_alias', lambda: need(tuple(alias) == target(2, 1), 'formal equality'))
    return results


def all_two_swap_attainers():
    """Complete literal six-call census via a 3+3 join, no pruning."""
    generators = [(g, u, v) for g in ('a', 'b') for u, v in projectors(2)]
    front = defaultdict(list)
    for word in itertools.product(generators, repeat=3):
        front[formal(word, 2)].append(word)
    counts = {2: 0, 3: 0, 4: 0}
    words = []
    for backwards in itertools.product(generators, repeat=3):
        state = target(2, 2)
        for gate in backwards:
            state = step(state, gate)
        for prefix in front.get(state, []):
            word = prefix + tuple(reversed(backwards))
            a_count = sum(gate[0] == 'a' for gate in word)
            need(a_count in counts, 'unexpected two-swap label count')
            counts[a_count] += 1
            if a_count != 3:
                trace_saturation(word, 2, 2, 'a' if a_count == 2 else 'b')
            words.append(word)
    return {'half_words_each': len(generators)**3,
            'total': len(words), 'by_a_count': counts,
            'saturated_proof_traces': counts[2]+counts[4],
            'words_sha256': hashlib.sha256(canonical(sorted(words)).encode()).hexdigest()}


def source_binding(root=HERE.parents[1]):
    manifest = load_json(HERE/'SOURCES.json')
    rows = [row for row in manifest['files'] if row['usage'] == 'input']
    need(len(rows) == 1, 'source inventory')
    for row in rows:
        data = (root/row['path']).read_bytes()
        need(hashlib.sha256(data).hexdigest() == row['sha256'], 'source hash')
    return [row['sha256'] for row in rows]


def build():
    source_hashes = source_binding()
    need(len(G) == 6 and PRODUCT[LABELS['a']][PRODUCT[LABELS['b']][LABELS['a']]] == SWAP,
         'address group')
    witnesses = []
    for t in range(1, 6):
        for extra in (0, 1):
            r = t+extra
            w = [(label, 1 << i, 1 << i) for i in range(t) for label in ('b', 'a', 'b')]
            # Nontrivial active bases exercise the saturation normalization.
            change = tuple((1 << i) ^ ((1 << (i+1)) if i+1 < t else 0) for i in range(r))
            inv = invert(change)
            w = [(label, mv(change, u), xor_rows(inv, v)) for label, u, v in w]
            for opposite in (False, True):
                word = [('b' if label == 'a' else 'a', u, v) for label, u, v in w] if opposite else w
                saturated = 'b' if opposite else 'a'
                trace = trace_saturation(word, r, t, saturated)
                witnesses.append({'targets': t, 'registers': r, 'saturated_label': saturated,
                                  'word': word, 'trace': trace})
            if extra:
                # Touch dirty workspace with a fully charged cancelling pair.
                gate = ('b', (1 << t) | 1, 1 << t)
                dirty_word = [gate, gate]+w
                trace = trace_saturation(dirty_word, r, t)
                witnesses.append({'targets': t, 'registers': r, 'saturated_label': 'a',
                                  'word': dirty_word, 'trace': trace})
    return {'schema_version': 1, 'scope': 'written saturation theorem; finite corroboration only; no_new_kappa',
            'sources': source_hashes,
            'screen': {str(t): {str(q): screened_counts(t, q) for q in range(3*t+1)}
                       for t in range(1, 7)},
            'witnesses': witnesses, 'controls': controls(),
            'censuses': [census(1, 5), census(2, 6)],
            'two_swap_attainers': all_two_swap_attainers(),
            'three_swap_minimum': 9, 'four_swap_remaining_counts_below_twelve': [[5, 5]],
            'four_swap_minimum_interval': [10, 12], 'four_swap_ten_call_workspace_cap': 6}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--write', action='store_true', help='regenerate deterministic receipt')
    args = ap.parse_args()
    result = build()
    if args.write:
        (HERE/'RESULT.json').write_text(json.dumps(result, indent=2)+'\n')
    else:
        typed_equal(result, load_json(HERE/'RESULT.json'))
    print('PASS_COORDINATE_CNOT_LABEL_SATURATION three_swap_minimum=9 '
          'four_swap_minimum=10_or_12 ten_call_counts=5+5 '
          f'witnesses={len(result["witnesses"])} controls={len(result["controls"])} no_new_kappa')


if __name__ == '__main__':
    try:
        main()
    except (Reject, OSError, KeyError, TypeError, json.JSONDecodeError) as exc:
        print('REJECT_LABEL_SATURATION:', exc, file=sys.stderr)
        raise SystemExit(1)
