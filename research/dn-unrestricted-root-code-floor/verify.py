#!/usr/bin/env python3
"""Finite checks for the uniform written D_n root-code floor.

ywz65 with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
import ast
import hashlib
import itertools as it
import json
from fractions import Fraction as Q
from pathlib import Path
import random

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def need(value, message):
    if not value:
        raise ValueError(message)


def canonical(x):
    return json.dumps(x, sort_keys=True, separators=(',', ':'), allow_nan=False)


def authenticate():
    dependency = json.loads((HERE / 'DEPENDENCY.json').read_bytes())
    for row in dependency['files']:
        raw = (HERE / row['retained']).read_bytes()
        need(hashlib.sha256(raw).hexdigest() == row['sha256'], 'source SHA256: ' + row['retained'])
        need(hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest() == row['git_blob'], 'source blob')
    sources = json.loads((HERE / 'SOURCES.json').read_bytes())
    for row in sources['files']:
        if row['usage'] != 'input':
            continue
        raw = (ROOT / row['path']).read_bytes()
        need(hashlib.sha256(raw).hexdigest() == row['sha256'], 'input source SHA256')
        need(hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest() == row['git_blob'], 'input source blob')
    # Use only these three authenticated, pure source functions, not its search.
    path = HERE / 'references/PR2518-search.py'
    tree = ast.parse(path.read_bytes(), filename=str(path))
    nodes = [x for x in tree.body if isinstance(x, ast.FunctionDef) and x.name in ('canon', 'lines', 'D')]
    need([x.name for x in nodes] == ['canon', 'lines', 'D'], 'source D generator inventory')
    scope = {}
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(path), 'exec'), scope)
    return scope['D']


def binary_rank(rows):
    pivots = {}
    for row in rows:
        while row:
            pivot = row.bit_length() - 1
            if pivot in pivots:
                row ^= pivots[pivot]
            else:
                pivots[pivot] = row
                break
    return len(pivots)


def rank(matrix, prime=None):
    a = [[Q(x) if prime is None else int(x) % prime for x in row] for row in matrix]
    if not a:
        return 0
    pos = 0
    for c in range(len(a[0])):
        pivot = next((r for r in range(pos, len(a)) if a[r][c]), None)
        if pivot is None:
            continue
        a[pos], a[pivot] = a[pivot], a[pos]
        inv = 1 / a[pos][c] if prime is None else pow(a[pos][c], -1, prime)
        a[pos] = [v * inv if prime is None else v * inv % prime for v in a[pos]]
        for r in range(pos + 1, len(a)):
            q = a[r][c]
            a[r] = [v - q * w if prime is None else (v - q * w) % prime for v, w in zip(a[r], a[pos])]
        pos += 1
        if pos == len(a):
            break
    return pos


def dot(x, y, prime=None):
    value = sum(a * b for a, b in zip(x, y))
    return value if prime is None else value % prime


def roots(n):
    return [tuple((1 if k == i else s if k == j else 0) for k in range(n))
            for i in range(n) for j in range(i + 1, n) for s in (1, -1)]


def pairing(rr):
    return [sum(1 << j for j, y in enumerate(rr) if i == j or dot(x, y) == 0)
            for i, x in enumerate(rr)]


def support(rr, x, prime=None):
    return sum(1 << i for i, r in enumerate(rr) if dot(r, x, prime))


def rectangle(bb, s, t):
    return binary_rank([row & t for i, row in enumerate(bb) if s >> i & 1])


def axis(x):
    indices = [i for i, v in enumerate(x) if v]
    return indices[0] if len(indices) == 1 else None


def expected_term(n, x, y):
    if n % 2 == 0:
        return n - 1
    a, b = axis(x), axis(y)
    if a is None and b is None:
        return n
    return n - 2 if a is not None and b is not None and a != b else n - 1


def patterns(n):
    out = set()
    for size in (1, 2, 3):
        for indices in it.combinations(range(n), size):
            for values in it.product((-1, 1, 2), repeat=size):
                x = [0] * n
                for i, v in zip(indices, values):
                    x[i] = v
                out.add(tuple(x))
    out.add(tuple(range(1, n + 1)))
    out.add((1,) * n)
    return sorted(out)


def finite_support_checks(source_d):
    reports = []
    for n in range(4, 13):
        rr = roots(n)
        need(source_d(n) == [tuple(2 * x for x in r) for r in rr], 'source root binding')
        bb = pairing(rr)
        h = n if n % 2 else n - 1
        need(binary_rank(bb) == h, 'full binary rank parity')
        need(rank(rr) == n, 'rational root injection')
        # Every codeword in the label description, with radical duplicates removed.
        words = set()
        isolated = []
        for a in (0, 1):
            for s in range(1 << n):
                if s.bit_count() % 2:
                    continue
                word = 0
                for k, r in enumerate(rr):
                    i, j = [i for i, v in enumerate(r) if v]
                    if a ^ (s >> i & 1) ^ (s >> j & 1):
                        word |= 1 << k
                words.add(word)
        need(len(words) == 1 << h, 'full code cardinality')
        for word in words - {0}:
            touched = {i for k, r in enumerate(rr) if word >> k & 1 for i, v in enumerate(r) if v}
            missing = sorted(set(range(n)) - touched)
            need(not missing or (n % 2 and len(missing) == 1), 'isolated vertex classification')
            if missing:
                isolated.extend(missing)
            if n <= 8:
                need(rank([r for k, r in enumerate(rr) if word >> k & 1], 3) == len(touched), 'actual F3 zero-root rank')
        need(sorted(isolated) == (list(range(n)) if n % 2 else []), 'exact deficient axis classes')
        reports.append({'n': n, 'roots': len(rr), 'binary_rank': h, 'codewords': len(words), 'isolated_classes': len(isolated)})
    # All distinct supports of the bounded vector list, over three exact fields.
    pairs = []
    for n in range(4, 8):
        rr, bb = roots(n), pairing(roots(n))
        for prime in (None, 3, 5):
            representatives = {}
            for x in patterns(n):
                v = x if prime is None else tuple(a % prime for a in x)
                representatives.setdefault(support(rr, v, prime), v)
            count = 0
            for s, x in representatives.items():
                for t, y in representatives.items():
                    need(rectangle(bb, s, t) == expected_term(n, x, y), 'exact support tariff')
                    count += 1
            pairs.append({'n': n, 'field': 'Q' if prime is None else f'F{prime}', 'supports': len(representatives), 'pairs': count})
    return reports, pairs


def factor_fixtures():
    rng = random.Random(22772518)
    reports = []
    for n in range(4, 10):
        rr, bb = roots(n), pairing(roots(n))
        for prime in (None, 3, 5):
            for extra in range(4):
                for trial in range(5):
                    # X=[I,A], Y^T=[I-A B;B] is exact at arbitrary term counts.
                    a = [[rng.randrange(-2, 3) for _ in range(extra)] for _ in range(n)]
                    b = [[rng.randrange(-2, 3) for _ in range(n)] for _ in range(extra)]
                    xrows = [[int(i == j) for j in range(n)] + a[i] for i in range(n)]
                    yt = [[int(i == j) - sum(a[i][k] * b[k][j] for k in range(extra)) for j in range(n)]
                          for i in range(n)] + b
                    xs = [list(col) for col in zip(*xrows)]
                    ys = [list(row) for row in yt]
                    # Simultaneous inverse-transpose shear preserves identity,
                    # and exposes factors beyond the fixed coordinate family.
                    for _ in range(trial):
                        u, v = rng.sample(range(n), 2)
                        scalar = rng.choice((-2, -1, 1, 2))
                        for x, y in zip(xs, ys):
                            x[u] += scalar * x[v]
                            y[v] -= scalar * y[u]
                    if prime is not None:
                        xs = [[v % prime for v in x] for x in xs]
                        ys = [[v % prime for v in y] for y in ys]
                    else:
                        # Nonintegral reciprocal term scaling preserves each
                        # outer product but tests actual rational supports.
                        for k in range(len(xs)):
                            scale = Q((-1) ** k * (k + 2), k + 3)
                            xs[k] = [scale * v for v in xs[k]]
                            ys[k] = [v / scale for v in ys[k]]
                    terms = [(x, y) for x, y in zip(xs, ys) if any(x) and any(y)]
                    actual = [[sum(x[i] * y[j] for x, y in terms) for j in range(n)] for i in range(n)]
                    if prime:
                        actual = [[v % prime for v in row] for row in actual]
                    need(actual == [[int(i == j) for j in range(n)] for i in range(n)], 'exact Gram factorization')
                    bill = sum(rectangle(bb, support(rr, x, prime), support(rr, y, prime)) for x, y in terms)
                    m = len(terms)
                    cheap = sum(expected_term(n, x, y) == n - 2 for x, y in terms) if n % 2 else 0
                    need(bill >= n * (n - 1), 'all-term floor')
                    need(m == n or bill > n * (n - 1), 'overcomplete strictness')
                    need(not (n % 2 and m == n + 1) or cheap <= 2, 'one-extra cheap bound')
                    reports.append({'n': n, 'field': 'Q' if prime is None else f'F{prime}', 'extra': extra,
                                    'shears': trial, 'nonzero_terms': m, 'cheap_terms': cheap, 'cost': bill})
    # Explicit cancelling off-diagonal pair: exercises two cheap terms in an
    # exact, overcomplete word rather than relying on generic random fixtures.
    for n in (5, 7, 9):
        es = [[int(i == j) for i in range(n)] for j in range(n)]
        terms = list(zip(es, es)) + [(es[0], es[1]), (es[0], [-a for a in es[1]])]
        bb, rr = pairing(roots(n)), roots(n)
        bill = sum(rectangle(bb, support(rr, x), support(rr, y)) for x, y in terms)
        need(bill == n * (n - 1) + 2 * (n - 2), 'actual cancelling cheap terms')
        reports.append({'n': n, 'field': 'Q', 'fixture': 'cancelling_unmatched_axes', 'nonzero_terms': n + 2, 'cheap_terms': 2, 'cost': bill})
        # I_2=E_12+E_21+(e_1-e_2)(e_1-e_2)^T, giving an
        # actual one-extra fixture with two cheap terms, the proved cap.
        u = [a - b for a, b in zip(es[0], es[1])]
        terms = [(es[0], es[1]), (es[1], es[0]), (u, u)] + list(zip(es[2:], es[2:]))
        need([[sum(x[i] * y[j] for x, y in terms) for j in range(n)] for i in range(n)] ==
             [[int(i == j) for j in range(n)] for i in range(n)], 'two-cheap one-extra exact identity')
        bill = sum(rectangle(bb, support(rr, x), support(rr, y)) for x, y in terms)
        need(bill == n * n - 2, 'two-cheap one-extra actual bill')
        reports.append({'n': n, 'field': 'Q', 'fixture': 'one_extra_two_cheap', 'nonzero_terms': n + 1, 'cheap_terms': 2, 'cost': bill})
    return reports


def controls():
    rr, bb = roots(5), pairing(roots(5))
    x, y = (1, 0, 0, 0, 0), (0, 1, 0, 0, 0)
    sx, sy = support(rr, x), support(rr, y)
    need(support(rr, (1,) * 5, 2) == 0 and rank(rr, 2) < 5, 'char-two injection control')
    need(rectangle(bb, sx, sy) == 3 < 4, 'unmatched axis is really cheaper')
    need(rectangle(bb, sx, sx) == 4 != 3, 'matched axis is not cheap')
    sparse = [1 << i for i in range(len(rr))]
    need(rectangle(sparse, sx, sx) == 8 != 4, 'mask change affects actual cost')
    need(rank([[a * b for b in y] for a in x]) == 1 != 5, 'single cheap term fails exact identity')
    need(binary_rank(bb) == 5 != 4, 'wrong parity rank rejected')
    need((3 + 2) * (3 - 2) == 5 < 3 * (3 - 1), 'excluded small dimension count')
    return ['characteristic_two_root_kernel', 'unmatched_axis_cheaper', 'matched_axis_not_cheap',
            'sparse_mask_changes_tariff', 'inexact_cheap_term', 'wrong_parity_rank', 'n3_count_boundary']


def run():
    source_d = authenticate()
    code, pairs = finite_support_checks(source_d)
    factors = factor_fixtures()
    return {'status': 'PASS_DN_UNRESTRICTED_ROOT_CODE_FLOOR', 'binary_code_checks': code,
            'support_pair_checks': pairs, 'factorizations': factors, 'controls': controls(),
            'scope': 'finite cross-checks of written all-n>=4, all-finite-m root-code theorem; no native or formal verification'}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if args.output is not None and args.output.exists():
        raise ValueError('output already exists')
    result = run()
    if args.output:
        with args.output.open('x', encoding='utf-8') as stream:
            json.dump(result, stream, indent=2, allow_nan=False)
            stream.write('\n')
    else:
        need(canonical(result) == canonical(json.loads((HERE / 'RESULT.json').read_bytes())), 'typed receipt mismatch')
    print(result['status'])
    print('support pairs:', sum(row['pairs'] for row in result['support_pair_checks']),
          'exact factorizations:', len(result['factorizations']), 'controls:', len(result['controls']))


if __name__ == '__main__':
    main()
