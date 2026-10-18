#!/usr/bin/env python3
"""Construct exact binary stabilized charts and replay every dirty pilot input.

Apache-2.0. Prepared for ywz65 with OpenAI Codex assistance.
"""
import argparse
import hashlib
import itertools
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def require(ok, why):
    if not ok:
        raise ValueError(why)


def authenticate():
    for row in json.loads((HERE / 'SOURCES.json').read_bytes())['files']:
        if row['usage'] == 'input':
            require(hashlib.sha256((ROOT / row['path']).read_bytes()).hexdigest() == row['sha256'],
                    'source pin: ' + row['path'])


def rank(rows):
    basis = {}
    for value in rows:
        while value:
            k = value.bit_length() - 1
            if k not in basis:
                basis[k] = value
                break
            value ^= basis[k]
    return len(basis)


def apply(rows, value):
    return sum(((row & value).bit_count() & 1) << i for i, row in enumerate(rows))


def mul(a, b):
    return tuple(_xor(b[j] for j in range(len(b)) if row >> j & 1) for row in a)


def _xor(values):
    out = 0
    for value in values:
        out ^= value
    return out


def inverse(rows):
    n = len(rows)
    a = [row | 1 << (n + i) for i, row in enumerate(rows)]
    for col in range(n):
        pivot = next((i for i in range(col, n) if a[i] >> col & 1), None)
        require(pivot is not None, 'singular chart')
        a[pivot], a[col] = a[col], a[pivot]
        for i in range(n):
            if i != col and a[i] >> col & 1:
                a[i] ^= a[col]
    return tuple(row >> n for row in a)


def companion(rows, joint, h):
    current = list(rows)
    extra = []
    for row in joint:
        if rank(current + [row]) > rank(current):
            current.append(row)
            extra.append(row)
    require(len(extra) <= h, 'companion dimension')
    return tuple(extra + [0] * (h - len(extra)))


def from_columns(columns, size):
    return tuple(sum(((col >> i) & 1) << j for j, col in enumerate(columns)) for i in range(size))


def chart(b0, b1, n):
    require(len(b0) == len(b1), 'codomain dimension')
    r0, r1, r = rank(b0), rank(b1), rank(b0 + b1)
    h = r - min(r0, r1)
    d, e = companion(b0, b0 + b1, h), companion(b1, b0 + b1, h)
    f0, f1 = b0 + d, b1 + e
    q = len(f0)
    c0, c1 = [], []
    for j in range(n):
        v = apply(f0, 1 << j)
        if rank(c0 + [v]) > len(c0):
            c0.append(v)
            c1.append(apply(f1, 1 << j))
    require(len(c0) == r and rank(c1) == r, 'matched image bases')
    for cols in (c0, c1):
        for j in range(q):
            if rank(cols + [1 << j]) > len(cols):
                cols.append(1 << j)
        require(len(cols) == q, 'basis extension')
    transport = mul(from_columns(c1, q), inverse(from_columns(c0, q)))
    require(rank(transport) == q and mul(transport, f0) == f1, 'chart endpoint')
    return h, d, e, transport


def pilot():
    # Physical bit ports: x[0:4], z[4:8], w[8], y0[9:13], y1[13:17].
    b0, b1, d, e = (7, 15, 8, 15), (11, 15, 8, 15), (11,), (7,)
    a0, a1 = (3, 2, 4, 8), (1, 6, 4, 8)
    require(mul(a0, a1) != mul(a1, a0), 'noncommuting reader fixture')
    def add(rows, source, target, label):
        return [(source + j, target + i, label) for i, row in enumerate(rows)
                for j in range(4) if row >> j & 1]
    r0, r1 = add(a0, 4, 9, 'A0'), add(a1, 4, 13, 'A1')
    q0, q1 = add(b0, 0, 4, 'B0'), add(b1, 0, 4, 'B1')
    qd, qe = add(d, 0, 8, 'D'), add(e, 0, 8, 'E')
    swap = [(4, 8, 'R'), (8, 4, 'R'), (4, 8, 'R')]
    unswap = [(s, t, 'Rinv') for s, t, _ in swap]
    candidate = r0 + q0 + r0 + qd + swap + r1 + q1 + r1 + qe + unswap
    baseline = r0 + q0 + r0 + q0 + r1 + q1 + r1 + q1
    return dict(b0=b0, b1=b1, d=d, e=e, a0=a0, a1=a1,
                candidate=candidate, baseline=baseline)


def execute(word, value):
    for s, t, _ in word:
        value ^= ((value >> s) & 1) << t
    return value


def expected(data, value):
    x = value & 15
    return value ^ (apply(data['a0'], apply(data['b0'], x)) << 9) \
        ^ (apply(data['a1'], apply(data['b1'], x)) << 13)


def bill(word):
    # Home is just before bit zero. Every gate goes home -> max port -> home.
    travel = sum(2 * (max(s, t) + 1) for s, t, _ in word)
    return dict(xors=len(word), movement=travel, gate_access_control=5 * len(word),
                tariff=travel + 5 * len(word))


def check():
    histogram = {}
    for b0 in itertools.product(range(4), repeat=2):
        for b1 in itertools.product(range(4), repeat=2):
            h, d, e, r = chart(b0, b1, 2)
            histogram[h] = histogram.get(h, 0) + 1
    # A deterministic larger check of all ranks and unequal kernels, not a full census.
    for seed in range(512):
        b0 = tuple((seed >> (3 * i)) & 7 for i in range(3))
        b1 = tuple(((seed * 53 + 117) >> (3 * i)) & 7 for i in range(3))
        chart(b0, b1, 3)
    data = pilot()
    require(rank(data['b0']) == 2 and rank(data['b1']) == 3 and
            rank(data['b0'] + data['b1']) == 3, 'pilot rank boundary')
    f0, f1 = data['b0'] + data['d'], data['b1'] + data['e']
    require(mul((16, 2, 4, 8, 1), f0) == f1, 'literal swap signal transport')
    for value in range(1 << 17):
        target = expected(data, value)
        require(execute(data['candidate'], value) == target, 'complete dirty candidate')
        require(execute(data['baseline'], value) == target, 'closed-echo comparator')
        require(execute(list(reversed(data['candidate'])), target) == value, 'dirty inverse')
    controls = {}
    for omitted in ('D', 'E', 'R', 'Rinv', 'B1'):
        word = [gate for gate in data['candidate'] if gate[2] != omitted]
        witness = next((1 << i for i in range(17)
                        if execute(word, 1 << i) != expected(data, 1 << i)), None)
        require(witness is not None, 'missing semantic mutant witness: ' + omitted)
        controls[omitted] = witness
    return dict(schema_version=1, all_binary_2x2_pairs=256, helper_histogram=histogram,
                larger_binary_pairs=512, dirty_inputs=1 << 17, inverse_inputs=1 << 17,
                pilot={k: v for k, v in data.items() if k not in ('candidate', 'baseline')},
                candidate_bill=bill(data['candidate']), baseline_bill=bill(data['baseline']),
                semantic_counterexamples=controls, literal_word=data['candidate'])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    if args.out:
        require(not args.out.exists(), 'output already exists')
    authenticate()
    result = check()
    text = json.dumps(result, indent=2, sort_keys=True) + '\n'
    if args.out:
        with args.out.open('x', encoding='utf-8') as stream:
            stream.write(text)
    else:
        require(json.dumps(json.loads(text), sort_keys=True) ==
                json.dumps(json.loads((HERE / 'RESULT.json').read_bytes()), sort_keys=True),
                'receipt differs')
    print('PASS_STABILIZED_CHART: 768 chart pairs; 131072 dirty inputs/inverses; 56 versus 68 XORs')


if __name__ == '__main__':
    main()
