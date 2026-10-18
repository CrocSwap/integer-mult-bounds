#!/usr/bin/env python3
"""Independent exact finite checks; these are not a substitute for leancheck.py.

Apache-2.0. Prepared for ywz65 with OpenAI Codex assistance.
"""
import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def require(ok, why):
    if not ok:
        raise ValueError(why)


def authenticate():
    dependency = json.loads((HERE / 'DEPENDENCY.json').read_bytes())
    for row in dependency['files']:
        data = (HERE / row['retained']).read_bytes()
        require(hashlib.sha256(data).hexdigest() == row['sha256'], 'predecessor source pin')
        obj = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
        require(obj == row['git_blob'], 'predecessor blob pin')
    formal = json.loads((HERE / 'FORMAL-RESULT.json').read_bytes())
    require(hashlib.sha256((HERE / 'Coupling.lean').read_bytes()).hexdigest()
            == formal['source_sha256'], 'formal source receipt pin')
    require(formal['status'] == 'kernel-checked' and len(formal['audited_roots']) == 6,
            'formal receipt shape')


def field(p):
    def f(x):
        return Fraction(x) if not p else x % p
    def inv(x):
        return 1 / x if not p else pow(x, -1, p)
    return f, inv


def rank(a, p):
    f, inv = field(p)
    a = [[f(x) for x in row] for row in a]
    r = 0
    for c in range(len(a[0])):
        pivot = next((i for i in range(r, len(a)) if a[i][c]), None)
        if pivot is None:
            continue
        a[r], a[pivot] = a[pivot], a[r]
        scale = inv(a[r][c])
        a[r] = [f(x * scale) for x in a[r]]
        for i in range(len(a)):
            if i != r:
                scale = a[i][c]
                a[i] = [f(x - scale * y) for x, y in zip(a[i], a[r])]
        r += 1
        if r == len(a):
            break
    return r


def mul(a, b, p):
    f, _ = field(p)
    return [[f(sum(x * y for x, y in zip(row, col))) for col in zip(*b)] for row in a]


def identity(n):
    return [[int(i == j) for j in range(n)] for i in range(n)]


def check():
    count = one_extra = 0
    for p in (0, 2, 3, 5):
        f, inv = field(p)
        for t in range(1, 5):
            for extra in range(4):
                m = t + extra
                for seed in range(7):
                    a = [[f((i + 2) * (j + 3) + seed - 4) for j in range(extra)] for i in range(t)]
                    b = [[f((i + 3) * (j + 1) - seed + 2) for j in range(t)] for i in range(extra)]
                    ab = mul(a, b, p) if extra else [[f(0)] * t for _ in range(t)]
                    x = [row + ar for row, ar in zip(identity(t), a)]
                    yt = [[f(int(i == j) - ab[i][j]) for j in range(t)] for i in range(t)] + b
                    require(mul(x, yt, p) == identity(t), 'fixture exactness')
                    k = mul(yt, x, p)
                    d = [[f(int(i == j) - k[i][j]) for j in range(m)] for i in range(m)]
                    require(rank(x, p) == t and rank(k, p) == t and rank(d, p) == extra,
                            'rank/corank interface')
                    require(mul(k, k, p) == k and mul(d, d, p) == d, 'idempotence')
                    if extra == 1:
                        i, j = next((i, j) for i in range(m) for j in range(m) if d[i][j])
                        u = [d[q][j] for q in range(m)]
                        w = [f(d[i][q] * inv(d[i][j])) for q in range(m)]
                        require([[f(v * z) for z in w] for v in u] == d, 'outer product')
                        require(f(sum(v * z for v, z in zip(w, u))) == 1, 'normalization')
                        require(all(k[i][j] == f(-u[i] * w[j]) for i in range(m) for j in range(m) if i != j),
                                'off-diagonal formula')
                        one_extra += 1
                    count += 1
    # The finite-field control explains why trace alone is not the rank proof.
    require(rank(identity(3), 2) == 3 and sum(identity(3)[i][i] for i in range(3)) % 2 == 1,
            'trace-one rank-three control')
    require(rank([[0, 0], [0, 0]], 0) != 1, 'exactness omission control')
    require(rank(identity(2), 0) != 1, 'two-extra complement control')
    require(mul([[1, 1], [0, 0]], [[1, 1], [0, 0]], 0) == [[1, 1], [0, 0]],
            'nonsymmetric idempotent positive control')
    return dict(schema_version=1, exact_fixtures=count, one_extra_fixtures=one_extra,
                fields=['Q', 'F2', 'F3', 'F5'], dimensions=[1, 2, 3, 4],
                excess_columns=[0, 1, 2, 3], semantic_controls=4,
                scope='finite checks and retained formal receipt; Lean replay is separate')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    if args.out:
        require(not args.out.exists(), 'output already exists')
    authenticate()
    receipt = check()
    if args.out:
        with args.out.open('x', encoding='utf-8') as stream:
            stream.write(json.dumps(receipt, indent=2) + '\n')
    else:
        require(receipt == json.loads((HERE / 'RESULT.json').read_bytes()), 'finite receipt differs')
    print('PASS_OC_FINITE:', receipt['exact_fixtures'], 'fixtures;', receipt['one_extra_fixtures'], 'one-extra')


if __name__ == '__main__':
    main()
