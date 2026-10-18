#!/usr/bin/env python3
"""Exact finite corroboration of the written full-occupancy theorem.
Apache-2.0. Ross Richardson with substantial OpenAI Codex assistance.
"""
import argparse
import hashlib
import itertools
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


class Invalid(ValueError):
    pass


def need(ok, message):
    if not ok:
        raise Invalid(message)


def read_json(path):
    def unique(items):
        out = {}
        for k, v in items:
            need(k not in out, 'duplicate JSON key')
            out[k] = v
        return out
    def invalid(x):
        raise Invalid('nonfinite JSON')
    return json.loads(Path(path).read_text(), object_pairs_hook=unique, parse_constant=invalid)


def canonical(x):
    return json.dumps(x, sort_keys=True, separators=(',', ':'), ensure_ascii=True)


def digest(x):
    return hashlib.sha256(canonical(x).encode()).hexdigest()


def mat2(a, b):
    return sum((((a >> (2*i)) & 1)*((b >> j) & 1) ^
                ((a >> (2*i+1)) & 1)*((b >> (2+j)) & 1)) << (2*i+j)
               for i in range(2) for j in range(2))


G = tuple(x for x in range(16) if (((x & 1)*((x >> 3) & 1)) ^ (((x >> 1) & 1)*((x >> 2) & 1))))
INDEX = {x: i for i, x in enumerate(G)}
E, A, B, S = 9, 11, 13, 6
ONE = 1 << INDEX[E]


def rmul(a, b):
    out = 0
    for i, x in enumerate(G):
        if (a >> i) & 1:
            for j, y in enumerate(G):
                if (b >> j) & 1:
                    out ^= 1 << INDEX[mat2(x, y)]
    return out


RMUL = tuple(tuple(rmul(a, b) for b in range(64)) for a in range(64))


def mul(x, y):
    r = len(x)
    out = [[0] * r for _ in range(r)]
    for i in range(r):
        for k in range(r):
            if x[i][k]:
                table = RMUL[x[i][k]]
                for j in range(r):
                    out[i][j] ^= table[y[k][j]]
    return out


def target(r, t):
    return [[((1 << INDEX[S]) if i < t else ONE) if i == j else 0 for j in range(r)] for i in range(r)]


def projectors(r):
    return [(u, v) for u in range(1, 1 << r) for v in range(1, 1 << r)
            if (u & v).bit_count() % 2]


def validate(word, r):
    need(type(r) is int and 1 <= r <= 6, 'roles')
    need(type(word) is list, 'word type')
    for call in word:
        need(type(call) is list and len(call) == 3, 'call shape')
        g, u, v = call
        need(type(g) is str and g in ('a', 'b'), 'paid label')
        need(type(u) is int and type(v) is int and 0 < u < 1 << r and 0 < v < 1 << r, 'vector domain')
        need((u & v).bit_count() % 2 == 1, 'idempotence')


def factor(call, r):
    validate([call], r)
    g, u, v = call
    coeff = ONE ^ (1 << INDEX[A if g == 'a' else B])
    return [[(ONE if i == j else 0) ^ (coeff if ((u >> i) & (v >> j) & 1) else 0)
             for j in range(r)] for i in range(r)]


def replay(word, r):
    validate(word, r)
    value = target(r, 0)
    for call in word:
        value = mul(factor(call, r), value)
    return value


def rotate(word, k):
    need(type(k) is int and 0 <= k <= len(word), 'cut')
    return [x[:] for x in word[k:]] + [['b' if g == 'a' else 'a', u, v] for g, u, v in word[:k]]


def binary_inverse(rows):
    n = len(rows)
    a = [rows[i] | (1 << (n+i)) for i in range(n)]
    for col in range(n):
        pivot = next((i for i in range(col, n) if (a[i] >> col) & 1), None)
        need(pivot is not None, 'singular basis')
        a[col], a[pivot] = a[pivot], a[col]
        for i in range(n):
            if i != col and (a[i] >> col) & 1:
                a[i] ^= a[col]
    return [row >> n for row in a]


def conjugate(word, rows):
    inverse = binary_inverse(rows)
    out = []
    for g, u, v in word:
        new_u = sum(((row & u).bit_count() % 2) << i for i, row in enumerate(rows))
        new_v = 0
        for i, row in enumerate(inverse):
            if (v >> i) & 1:
                new_v ^= row
        out.append([g, new_u, new_v])
    return out


def fixtures():
    result = []
    for r in range(1, 7):
        direct = [[g, 1 << i, 1 << i] for i in range(r) for g in 'aba']
        mixed = [[g, 1 << i, 1 << i] for i in reversed(range(r)) for g in ('aba' if i % 2 else 'bab')]
        rows = [(1 << i) | (1 << (i+1) if i+1 < r else 0) for i in range(r)]
        basis = conjugate(mixed, rows)
        pair = ['a', (1 << r)-1, 1]
        coupled = [pair[:], pair[:]] + basis
        result.extend({'roles': r, 'word': w} for w in (direct, mixed, basis, coupled))
    return result


def label_screen():
    rows = []
    checked = 0
    for t in range(1, 7):
        for q in range(min(3*t, 17)):
            if (q-t) % 2:
                continue
            floor = saturated = survivors = 0
            for bits in range(1 << q):
                checked += 1
                a = bits.bit_count()
                b = q-a
                if min(a, b) < t:
                    continue
                floor += 1
                if min(a, b) == t:
                    continue
                saturated += 1
                walk = 0
                low, high = t+1-b, a-t-1
                good = low <= 0 <= high
                for k in range(q):
                    walk += 1 if (bits >> k) & 1 else -1
                    good &= low <= walk <= high
                if good:
                    survivors += 1
                    need(q >= 2*t+3, 'cut width bound')
                    if q == 2*t+3:
                        need(all(((bits >> k) ^ (bits >> (k+1))) & 1 for k in range(q-1)), 'alternating boundary')
            rows.append({'targets': t, 'calls': q, 'floor': floor,
                         'after_saturation': saturated, 'after_cuts': survivors})
    need(next(x['after_cuts'] for x in rows if x['targets'] == 4 and x['calls'] == 10) == 0, 'four-target residual')
    need(next(x['after_cuts'] for x in rows if x['targets'] == 5 and x['calls'] == 13) == 2, 'five-target boundary')
    return {'patterns': checked, 'rows': rows}


def source_check():
    pins = read_json(HERE / 'PINS.json')
    for record in pins['files']:
        path = HERE / record['local_path']
        need(path.is_file(), 'missing source input')
        need(hashlib.sha256(path.read_bytes()).hexdigest() == record['sha256'], 'source bytes changed')
    return pins


def reject(action, label):
    try:
        action()
    except (Invalid, ValueError, TypeError):
        return label
    raise Invalid('control accepted: '+label)


def compute():
    source_check()
    conjugations = []
    for r in range(1, 7):
        ts = target(r, r)
        count = 0
        values = []
        for u, v in projectors(r):
            for g in ('a', 'b'):
                f = factor([g, u, v], r)
                value = mul(mul(ts, f), ts)
                need(value == factor(['b' if g == 'a' else 'a', u, v], r), 'full conjugation')
                need(mul(f, f) == target(r, 0), 'paid involution')
                values.append(value)
                count += 1
        conjugations.append({'roles': r, 'projectors': len(projectors(r)), 'checks': count, 'sha256': digest(values)})
    words = fixtures()
    cuts = omitted = 0
    rotations = []
    for fixture in words:
        r, word = fixture['roles'], fixture['word']
        need(replay(word, r) == target(r, r), 'positive word')
        for k in range(len(word)+1):
            rotated = rotate(word, k)
            need(replay(rotated, r) == target(r, r), 'chronological rotation')
            rotations.append(rotated)
            cuts += 1
        for k in range(len(word)):
            need(replay(word[:k]+word[k+1:], r) != target(r, r), 'omission accepted')
            omitted += 1
    # One active/dirty-coupled projector, embedded at the actual four-target boundary.
    r, t = 5, 4
    boundary = target(r, t)
    coupled = ['a', 17, 1]
    conjugated = mul(mul(boundary, factor(coupled, r)), boundary)
    alphabet = [factor([g, u, v], r) for u, v in projectors(r) for g in ('a', 'b')]
    need(conjugated not in alphabet, 'partial-target conjugation escaped control')
    need(conjugated != factor(['b', 17, 1], r), 'false workspace flip')
    controls = []
    for word, label in [([['s',1,1]],'expanded-label'),([['a',3,3]],'nilpotent'),
                        ([['a',True,1]],'boolean-vector'),([['a',1.0,1]],'float-vector')]:
        controls.append(reject(lambda word=word: validate(word, 2), label))
    actual = [[g,1<<i,1<<i] for i in range(4) for g in 'aba']
    need(replay(actual[1:]+actual[:1],4) != target(4,4), 'unflipped rotation should fail')
    controls += ['unflipped-rotation', 'partial-target-not-in-alphabet']
    return {'schema_version':1, 'claim':{'targets':4,'roles':4,'minimum':12,'extra_dirty_roles':0,'no_new_kappa':True},
            'conjugations':conjugations, 'fixtures':words, 'cut_checks':cuts,
            'rotations_sha256':digest(rotations), 'omission_controls':omitted,
            'label_screen':label_screen(),
            'workspace_boundary':{'roles':5,'targets':4,'call':coupled,'conjugate':conjugated,'alphabet_size':len(alphabet)},
            'controls':controls}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--write', action='store_true')
    args = ap.parse_args()
    actual = compute()
    if args.write:
        (HERE / 'RESULT.json').write_text(json.dumps(actual,indent=2)+'\n')
    else:
        need(canonical(actual) == canonical(read_json(HERE / 'RESULT.json')), 'receipt mismatch')
    print('PASS_FOUR_SWAP_FULL_OCCUPANCY minimum=12 roles=4 extra_dirty_roles=0 no_new_kappa')
    print(json.dumps({'conjugations':sum(x['checks'] for x in actual['conjugations']),
                      'cuts':actual['cut_checks'],'omissions':actual['omission_controls'],
                      'label_patterns':actual['label_screen']['patterns']}))


if __name__ == '__main__':
    main()
