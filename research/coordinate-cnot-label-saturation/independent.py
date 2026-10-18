#!/usr/bin/env python3
"""Code-disjoint faithful regular-operator corroboration; Apache-2.0.

Written in the same Codex session. Imports no primary or predecessor engine.
Independence means a different implementation, not independent human review.
"""
from collections import defaultdict
import hashlib
import itertools
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read(path):
    def pairs(items):
        result = {}
        for k, v in items:
            require(k not in result, 'duplicate key')
            result[k] = v
        return result

    def constant(_):
        raise ValueError('nonfinite value')

    return json.loads(path.read_text(), object_pairs_hook=pairs, parse_constant=constant)


def encoded(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False)


def same(a, b):
    require(encoded(a) == encoded(b), 'independent receipt mismatch')


def compose(p, q):
    return tuple(p[x-1] for x in q)


def rows_from_permutation(p):
    # The images of basis vectors 1 and 2 are the two binary matrix columns.
    return ((p[0] & 1) | ((p[1] & 1) << 1),
            ((p[0] >> 1) & 1) | (p[1] & 2))


PERMS = tuple(sorted(itertools.permutations((1, 2, 3)), key=rows_from_permutation))
INDEX = {p: i for i, p in enumerate(PERMS)}
ONE = INDEX[(1, 2, 3)]
# a(x,y)=(x+y,y), b(x,y)=(x,x+y), s(x,y)=(y,x).
ADDRESS = {'a': (1, 3, 2), 'b': (3, 2, 1), 's': (2, 1, 3)}
REGULAR = {label: tuple(INDEX[compose(p, h)] for h in PERMS)
           for label, p in ADDRESS.items()}


def unit(n):
    return tuple(1 << i for i in range(n))


def endpoint(r, t):
    rows = list(unit(6*r))
    for register in range(t):
        for h in range(6):
            rows[6*register+h] = 1 << (6*register+REGULAR['s'][h])
    return tuple(rows)


def generators(r):
    # Enumerate binary scalar matrices and filter rank one/idempotence,
    # separately from the primary u,v enumeration.
    out = []
    for rows in itertools.product(range(1 << r), repeat=r):
        nonzero = set(rows)-{0}
        if len(nonzero) != 1:
            continue
        v = next(iter(nonzero))
        u = sum((row != 0) << i for i, row in enumerate(rows))
        if sum(((u >> i) & 1)*((v >> i) & 1) for i in range(r)) % 2 != 1:
            continue
        out.extend([(label, u, v) for label in ('a', 'b')])
    return sorted(out)


def apply(state, gate, r):
    label, u, v = gate
    require(label in ('a', 'b'), 'address alphabet')
    require(type(u) is int and type(v) is int and 0 < u < 2**r and 0 < v < 2**r,
            'projector domain')
    require(sum(((u >> i) & 1)*((v >> i) & 1) for i in range(r)) % 2 == 1,
            'projector idempotence')
    mixed = [0]*6
    for j in range(r):
        if v >> j & 1:
            for h in range(6):
                mixed[h] ^= state[6*j+h]
    delta = [mixed[h] ^ mixed[REGULAR[label][h]] for h in range(6)]
    result = list(state)
    for i in range(r):
        if u >> i & 1:
            for h in range(6):
                result[6*i+h] ^= delta[h]
    return tuple(result)


def run(word, r):
    state = unit(6*r)
    for gate in word:
        state = apply(state, gate, r)
    return state


def coefficients(state, r):
    # The identity-basis column of a left-regular block is its full formal
    # coefficient vector. This extraction is injective on constructed blocks.
    return tuple(sum(((state[6*i+h] >> (6*j+ONE)) & 1) << (6*j+h)
                     for j in range(r) for h in range(6)) for i in range(r))


def census(r, depth):
    alphabet = generators(r)
    layer = {0: {unit(6*r)}}
    receipt = []
    for q in range(depth+1):
        digest = hashlib.sha256()
        hits = []
        total = 0
        for na, states in sorted(layer.items()):
            total += len(states)
            formal_rows = sorted(coefficients(state, r) for state in states)
            require(len(set(formal_rows)) == len(states), 'faithful extraction collision')
            for rows in formal_rows:
                digest.update(bytes([na]))
                for row in rows:
                    digest.update(row.to_bytes(r, 'little'))
            for t in range(1, r+1):
                if endpoint(r, t) in states:
                    hits.append({'targets': t, 'counts': [na, q-na]})
        receipt.append({'length': q, 'states_with_label_count': total,
                        'sha256': digest.hexdigest(), 'target_hits': hits})
        if q == depth:
            break
        following = {}
        for na, states in layer.items():
            for state in states:
                for gate in alphabet:
                    following.setdefault(na+(gate[0] == 'a'), set()).add(apply(state, gate, r))
        layer = following
    return {'registers': r, 'depth': depth, 'layers': receipt}


def attainers():
    alphabet = generators(2)
    first = defaultdict(list)
    for word in itertools.product(alphabet, repeat=3):
        first[run(word, 2)].append(word)
    words = []
    counts = {2: 0, 3: 0, 4: 0}
    for backwards in itertools.product(alphabet, repeat=3):
        state = endpoint(2, 2)
        for gate in backwards:
            state = apply(state, gate, 2)
        for prefix in first.get(state, []):
            word = prefix+tuple(reversed(backwards))
            a_count = sum(g[0] == 'a' for g in word)
            require(a_count in counts, 'attainer label count')
            counts[a_count] += 1
            words.append(word)
    return {'half_words_each': len(alphabet)**3, 'total': len(words), 'by_a_count': counts,
            'saturated_proof_traces': counts[2]+counts[4],
            'words_sha256': hashlib.sha256(encoded(sorted(words)).encode()).hexdigest()}


def main():
    result = read(HERE/'RESULT.json')
    expected_domains = sorted(
        [(t, t+extra, label, 3*t) for t in range(1, 6)
         for extra in (0, 1) for label in ('a', 'b')]
        + [(t, t+1, 'a', 3*t+2) for t in range(1, 6)])
    actual_domains = sorted((w['targets'], w['registers'], w['saturated_label'], len(w['word']))
                            for w in result['witnesses'])
    same(actual_domains, expected_domains)
    columns = mutations = 0
    for w in result['witnesses']:
        r, t, word = w['registers'], w['targets'], w['word']
        require(type(r) is int and type(t) is int and 1 <= t <= r <= 6, 'witness domain')
        require(sum(gate[0] == w['saturated_label'] for gate in word) == t,
                'saturated label count')
        same(run(word, r), endpoint(r, t))
        same(run(list(reversed(word)), r), endpoint(r, t))
        columns += 12*r  # All faithful columns, forward and reverse.
        for i in range(len(word)):
            require(run(word[:i]+word[i+1:], r) != endpoint(r, t), 'omitted call accepted')
            mutations += 1
    same([census(1, 5), census(2, 6)], result['censuses'])
    same(attainers(), result['two_swap_attainers'])
    # Explicit literal rank-one/trace near misses, computed without primary code.
    rows = [[int((u >> i) & 1) for i in range(3)] for u in (1, 2, 4, 7)]
    require(all(sum(row) % 2 == 1 for row in rows), 'zero-sum near-miss legality')
    require(all(sum(row[i] for row in rows) % 2 == 0 for i in range(3)), 'zero sum')
    require(len(set(tuple(row) for row in rows)) == 4, 'near-miss rows')
    print(f'PASS_INDEPENDENT_LABEL_SATURATION faithful_columns={columns} '
          f'omission_controls={mutations} complete_censuses=2 attainers=1296 no_new_kappa')


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, KeyError, TypeError) as exc:
        print('REJECT_INDEPENDENT_LABEL_SATURATION:', exc, file=sys.stderr)
        raise SystemExit(1)
