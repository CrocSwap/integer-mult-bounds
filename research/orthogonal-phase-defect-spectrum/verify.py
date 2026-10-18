#!/usr/bin/env python3
"""Independent finite checks for the written all-dimension phase-defect proof.
No predecessor executable code is imported. All arithmetic is exact.
"""
from collections import Counter
from pathlib import Path
import argparse
import hashlib
import json
import math
import random

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]

def require(ok, message):
    if not ok:
        raise ValueError(message)

def dot(x, y):
    return (x & y).bit_count() & 1

def apply(columns, x):
    y = 0
    for j, c in enumerate(columns):
        if x >> j & 1:
            y ^= c
    return y

def transpose(columns):
    return tuple(sum(((c >> j) & 1) << i for i, c in enumerate(columns))
                 for j in range(len(columns)))

def compose(a, b):
    return tuple(apply(a, c) for c in b)

def identity(n):
    return tuple(1 << j for j in range(n))

def orthogonal(s):
    n = len(s)
    return (all(type(c) is int and 0 <= c < 1 << n for c in s)
            and all(dot(a, b) == (i == j)
                    for i, a in enumerate(s) for j, b in enumerate(s)))

def defect(s):
    """PR1255 convention: q(S^t x)-q(x)=2 d(S).x mod4."""
    require(orthogonal(s), 'defect requires an orthogonal matrix')
    return sum((((row.bit_count() - 1) // 2) & 1) << j
               for j, row in enumerate(transpose(s)))

def transvection(n, v):
    require(type(v) is int and 0 <= v < 1 << n, 'invalid transvection vector')
    require(v.bit_count() % 2 == 0, 'transvection needs even weight')
    return tuple((1 << j) ^ (v if v >> j & 1 else 0) for j in range(n))

def representative(n, d):
    require(type(d) is int and 0 <= d < 1 << n, 'invalid defect vector')
    require(d.bit_count() % 4 == 0, 'unattainable defect weight')
    return transvection(n, d)

def normalize(s):
    return compose(representative(len(s), defect(s)), s)

def first_column_map(n, u):
    """A deterministic orthogonal transversal, unrelated to predecessor DFS."""
    require(0 < u < 1 << n and u.bit_count() % 2 == 1, 'first column not unit')
    if u == 1:
        return identity(n)
    require(u != (1 << n) - 1, 'characteristic vector cannot extend')
    if not u & 1:
        return transvection(n, u ^ 1)
    k = next(j for j in range(1, n) if not u >> j & 1)
    w = 1 << k
    return compose(transvection(n, u ^ w), transvection(n, w ^ 1))

def group(n):
    """Orbit/stabilizer enumeration, each matrix once by its first column."""
    if n == 0:
        yield ()
        return
    smaller = list(group(n - 1))
    for u in range(1, 1 << n):
        if not u.bit_count() & 1 or (n > 1 and u == (1 << n) - 1):
            continue
        t = first_column_map(n, u)
        for h in smaller:
            yield compose(t, (1,) + tuple(c << 1 for c in h))

def order(n):
    value = 1
    for k in range(2, n + 1):
        value *= (1 << (k - 1)) - (k & 1)
    return value

def spectrum(n):
    defects = sum(math.comb(n, k) for k in range(0, n + 1, 4))
    total = order(n)
    require(total % defects == 0, 'nonintegral fiber')
    return dict(dimension=n, orthogonal_matrices=total, attainable_defects=defects,
                matrices_per_defect=total // defects,
                permitted_weights=list(range(0, n + 1, 4)))

def gaussian_mul(a, b):
    return (a[0]*b[0]-a[1]*b[1], a[0]*b[1]+a[1]*b[0])

def gaussian_power(z, n):
    a = (1, 0)
    for _ in range(n):
        a = gaussian_mul(a, z)
    return a

def kernel(columns, sign):
    """Literal group-algebra convolution, common denominator 2**n."""
    v = [(0, 0)] * (1 << len(columns))
    v[0] = (1, 0)
    for q in columns:
        out = [(0, 0)] * len(v)
        for x, a in enumerate(v):
            b = v[x ^ q]
            left = gaussian_mul(a, (1, sign))
            right = gaussian_mul(b, (1, -sign))
            out[x] = (left[0] + right[0], left[1] + right[1])
        v = out
    return v

def source_check():
    src = json.loads((HERE / 'SOURCES.json').read_text())
    for f in src['files']:
        if f['usage'] == 'input':
            require(hashlib.sha256((ROOT / f['path']).read_bytes()).hexdigest() == f['sha256'],
                    'live input digest mismatch')
    pred = json.loads((HERE / 'PREDECESSOR.json').read_text())
    raw = (HERE / pred['retained_as']).read_bytes()
    require(hashlib.sha256(raw).hexdigest() == pred['sha256'], 'predecessor receipt mismatch')
    require(hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
            == pred['git_blob'], 'predecessor Git blob mismatch')
    require(pred['head'] == 'add1e2673ef000c097ec0fd70058e644af048d6b', 'wrong predecessor')
    return json.loads(raw)

def census_checks(pred):
    result = []
    previous = {r['dimension']: r for r in pred['orthogonal_census']}
    for n in range(1, 7):
        matrices = list(group(n))
        require(len(set(matrices)) == len(matrices) == order(n), 'group census count')
        hist = Counter()
        normalization_count = 0
        for s in matrices:
            d = defect(s)
            hist[d] += 1
            st = transpose(s)
            for x in range(1 << n):
                require((apply(st, x).bit_count() - x.bit_count() - 2*dot(d, x)) % 4 == 0,
                        'exact phase identity')
            h = normalize(s)
            require(defect(h) == 0 and compose(representative(n, d), h) == s,
                    'single-transvection normalization')
            normalization_count += 1
        want = {d: spectrum(n)['matrices_per_defect'] for d in range(1 << n)
                if d.bit_count() % 4 == 0}
        require(dict(hist) == want, 'complete defect fibers')
        require({str(k): v for k, v in sorted(hist.items())} == previous[n]['defect_histogram'],
                'independent census differs from PR1255')
        result.append(dict(dimension=n, matrices=len(matrices), histogram=want,
                           normalized=normalization_count))
    return result

def witness_checks():
    witnesses = phase_checks = gaussian_checks = 0
    for n in range(1, 10):
        baseline = {sign: kernel(identity(n), sign) for sign in (-1, 1)}
        g = gaussian_power((1, 1), n)
        for d in range(1 << n):
            # Independent direct character sum; necessity does not use row counts.
            acc = [0, 0]
            for x in range(1 << n):
                e = (x.bit_count() + 2*dot(d, x)) % 4
                z = ((1, 0), (0, 1), (-1, 0), (0, -1))[e]
                acc[0] += z[0]; acc[1] += z[1]
            require((tuple(acc) == g) == (d.bit_count() % 4 == 0), 'Gauss necessity')
            gaussian_checks += 1
            if d.bit_count() % 4:
                continue
            s = representative(n, d)
            require(orthogonal(s) and defect(s) == d and compose(s, s) == identity(n),
                    'constructive representative')
            for sign in (-1, 1):
                actual = kernel(s, sign)
                for x, a in enumerate(actual):
                    factor = -1 if dot(d, x) else 1
                    b = baseline[sign][x]
                    require(a == (factor*b[0], factor*b[1]), 'literal convolution phase')
                    phase_checks += 1
            witnesses += 1
    return dict(witnesses=witnesses, literal_coefficients=phase_checks,
                direct_gaussian_sums=gaussian_checks)

def cocycle_checks():
    pairs = 0
    g4 = list(group(4))
    for a in g4:
        for b in g4:
            require(defect(compose(a, b)) == defect(a) ^ apply(a, defect(b)), 'cocycle')
            pairs += 1
    rng = random.Random(75)
    for n in range(5, 10):
        for _ in range(100):
            a = b = identity(n)
            for _ in range(10):
                v = rng.randrange(1 << n)
                v ^= (v.bit_count() & 1)
                a = compose(transvection(n, v), a)
                v = rng.randrange(1 << n)
                v ^= (v.bit_count() & 1)
                b = compose(transvection(n, v), b)
            require(defect(compose(a, b)) == defect(a) ^ apply(a, defect(b)), 'larger cocycle')
            require(defect(normalize(a)) == 0, 'larger normalization')
            pairs += 1
    return pairs

def controls():
    names = []
    def rejected(name, fn):
        try:
            fn()
        except ValueError:
            names.append(name)
        else:
            raise ValueError('control not rejected: ' + name)
    rejected('odd transvection', lambda: transvection(4, 1))
    rejected('weight-two prescribed defect', lambda: representative(4, 3))
    rejected('out-of-range defect', lambda: representative(4, 16))
    rejected('dependent matrix', lambda: defect((1, 1, 4, 8)))
    rejected('unextendible characteristic vector', lambda: first_column_map(5, 31))
    t = transvection(4, 3)
    require(orthogonal(t) and defect(t) == 0, 'weight-two is not a weight-two defect')
    names.append('even weight alone insufficient')
    bad = representative(4, 15)
    def convolution_square(k):
        out = []
        for z in range(len(k)):
            acc = [0, 0]
            for x, a in enumerate(k):
                term = gaussian_mul(a, k[z ^ x])
                acc[0] += term[0]; acc[1] += term[1]
            out.append(tuple(acc))
        return out
    bad_kernel = kernel(bad, 1)
    good_kernel = kernel(identity(4), 1)
    require(bad_kernel != good_kernel
            and convolution_square(bad_kernel) == convolution_square(good_kernel),
            'square blind spot')
    names.append('orthogonality and equal operator square do not certify phase')
    # A permutation transports d; dropping this action gives a false cocycle.
    a = (2, 1, 4, 8, 16)
    b = representative(5, 30)
    require(defect(compose(a, b)) != defect(a) ^ defect(b), 'untwisted cocycle control')
    names.append('untwisted cocycle false')
    # Fibers are cosets, not a vector space of attainable defects.
    require((15 ^ 23).bit_count() == 2, 'nonlinear spectrum control')
    names.append('attainable defects not an additive subspace')
    return names

def build():
    pred = source_check()
    return dict(status='PASS_ORTHOGONAL_PHASE_DEFECT_SPECTRUM', seed=75,
                spectrum=[spectrum(n) for n in range(1, 10)],
                selected_widths=sorted(map(int, pred['selected']['roles_by_width'])),
                complete_censuses=census_checks(pred), constructive=witness_checks(),
                cocycle_pairs=cocycle_checks(), controls=controls(),
                scope='Written universal theorem plus independent finite checks; no physical admission or new kappa.')

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--write', action='store_true')
    ap.add_argument('--receipt', type=Path, default=HERE / 'CERTIFICATE.json')
    args = ap.parse_args()
    result = build()
    encoded = json.dumps(result, indent=2, sort_keys=True) + '\n'
    if args.write:
        args.receipt.write_text(encoded)
    else:
        # Strict canonical JSON comparison also rejects booleans masquerading as counts.
        require(args.receipt.read_text() == encoded, 'certificate mismatch')
    print(result['status'], 'matrices=23817',
          'literal_coefficients=' + str(result['constructive']['literal_coefficients']),
          'controls=' + str(len(result['controls'])), 'no_new_kappa')

if __name__ == '__main__':
    main()
