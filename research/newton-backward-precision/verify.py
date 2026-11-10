"""Check exact suffix demands against literal perturbed Newton words.

Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.
"""
from fractions import Fraction as Q
from hashlib import sha1, sha256
import json
from math import comb, lcm
from pathlib import Path
from runpy import run_path

ROOT = Path(__file__).resolve().parent
P = run_path(str(ROOT/'precision.py'))
ZERO = (Q(0), Q(0))
ONE = (Q(1), Q(0))


def need(ok, message):
    if not ok:
        raise ValueError(message)


def plus(x, y):
    return (x[0]+y[0], x[1]+y[1])


def times(x, y):
    return (x[0]*y[0]-x[1]*y[1], x[0]*y[1]+x[1]*y[0])


def scalar(x, q):
    return (q*x[0], q*x[1])


def pow_g(x, k):
    value = ONE
    for _ in range(k):
        value = times(value, x)
    return value


def val(z):
    denominator = lcm(z[0].denominator, z[1].denominator)
    a, b = int(z[0]*denominator), int(z[1]*denominator)
    if a == b == 0:
        return None
    count = 0
    while (a-b) % 2 == 0:
        a, b = (a+b)//2, (b-a)//2
        count += 1
    while denominator % 2 == 0:
        denominator //= 2
        count -= 2
    return count


def literal(x, n, a, degree, errors):
    old, total = list(x), list(x)
    for h in range(1, degree+1):
        new = []
        for r in range(1 << n):
            acc = scalar(old[r], n)
            for bit in range(n):
                acc = plus(acc, scalar(old[r ^ (1 << bit)], -1))
                acc = plus(acc, errors.get((h, r, bit), ZERO))
            new.append(plus(scalar(acc, Q(1, 2*h)), scalar(old[r], -Q(a+h-1, h))))
        coefficient = pow_g((Q(-1), Q(1)), h)
        total = [plus(t, times(coefficient, z)) for t, z in zip(total, new)]
        old = new
    phase = pow_g((Q(0), Q(1)), a)
    return [times(phase, z) for z in total]


counts = {'source_pins': 0, 'kernel_stages': 0, 'literal_columns': 0,
          'sharp_witnesses': 0, 'full_event_checks': 0, 'joint_error_words': 0,
          'rejections': 0}
for origin in json.loads((ROOT/'ORIGINS.json').read_text()):
    raw = (ROOT/origin['local']).read_bytes()
    need(sha256(raw).hexdigest() == origin['sha256'], 'Source SHA256 differs')
    need(sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest() == origin['git_blob'],
         'Source blob differs')
    need(sha256(raw+b'!').hexdigest() != origin['sha256'], 'Source mutation missed')
    counts['source_pins'] += 1

for n in range(1, 11):
    for degree in range(1, n+1):
        for a in range(n-degree+1):
            kernels = P['kernels'](n, a, degree)
            plan = P['plan'](n, a, degree, n)
            for row in plan['demands']:
                h = row['stage']
                values = [val(z) for z in kernels[h]]
                minimum = min(v for v in values if v is not None)
                need(minimum == row['minimum_valuation'], 'Exact closed demand differs')
                need(values[row['witness_distance']] == minimum, 'Largest-maximizer witness differs')
                need(row['digits'] >= row['shell_floor'], 'Outer-shell floor failed')
                counts['kernel_stages'] += 1
                if n <= 5:
                    actual = literal([ZERO]*(1 << n), n, a, degree, {(h, 0, n-1): ONE})
                    need(actual == [kernels[h][r.bit_count()] for r in range(1 << n)],
                         'Literal suffix column differs')
                    counts['literal_columns'] += 1
                    for p in [0, 1, n]:
                        q = max(0, p-minimum)
                        safe = [times(pow_g((Q(1), Q(1)), q), z) for z in actual]
                        need(all(val(z) is None or val(z) >= p for z in safe), 'Safe local digits failed')
                        if q:
                            error = pow_g((Q(1), Q(1)), q-1)
                            bad = times(error, actual[(1 << row['witness_distance'])-1])
                            need(val(bad) == p-1, 'One fewer digit did not fail')
                            counts['sharp_witnesses'] += 1
            need(plan['minimum_neighbor_precision_mass'] >= n*(1 << n)*degree*(n+1),
                 'All-degree p=n bound failed')

for n in [16, 32, 64, 128]:
    for degree in sorted({1, 2, n//2, n-1, n}):
        a = (n-degree)//2
        kernels = P['kernels'](n, a, degree)
        for row in P['plan'](n, a, degree, n)['demands']:
            need(min(v for z in kernels[row['stage']] if (v := val(z)) is not None)
                 == row['minimum_valuation'], 'Large radial demand differs')
            counts['kernel_stages'] += 1

n, a, degree, p = 3, 1, 2, 4
x = [(Q(r-4), Q(2*r-5)) for r in range(1 << n)]
base = literal(x, n, a, degree, {})
kernels = P['kernels'](n, a, degree)
plan = P['plan'](n, a, degree, p)
for row in plan['demands']:
    h, q = row['stage'], row['digits']
    for r in range(1 << n):
        for bit in range(n):
            output = literal(x, n, a, degree, {(h, r, bit): ONE})
            delta = [plus(z, scalar(b, -1)) for z, b in zip(output, base)]
            need(delta == [kernels[h][(s ^ r).bit_count()] for s in range(1 << n)],
                 'Actual internal ADD has a different suffix')
            counts['full_event_checks'] += 1

for n in range(1, 5):
    for degree in range(1, n+1):
        for a in range(n-degree+1):
            p = n
            plan = P['plan'](n, a, degree, p)
            errors = {}
            for row in plan['demands']:
                h, q = row['stage'], row['digits']
                for r in range(1 << n):
                    for bit in range(n):
                        errors[h, r, bit] = times(pow_g((Q(1), Q(1)), q),
                                                  pow_g((Q(0), Q(1)), (h+r+bit) % 4))
            actual = literal([ZERO]*(1 << n), n, a, degree, errors)
            need(all(val(z) is None or val(z) >= p for z in actual), 'Joint error schedule failed')
            counts['joint_error_words'] += 1

for n, a, degree, p, expected in [(8, 0, 7, 8, 155648), (8, 1, 7, 8, 155648),
                                 (16, 0, 15, 16, 310378496)]:
    need(P['plan'](n, a, degree, p)['minimum_neighbor_precision_mass'] == expected,
         'Example precision mass differs')

for bad in [(0, 0, 1, 1), (2, 0, 0, 1), (2, 0, 3, 1), (2, -1, 1, 1),
            (2, 2, 1, 1), (2, 0, 1, -1), (True, 0, 1, 1), (129, 0, 1, 1)]:
    try:
        P['plan'](*bad)
    except ValueError:
        counts['rejections'] += 1
    else:
        raise ValueError('Invalid plan accepted')

need(P['plan'](8, 0, 7, 8)['demands'][0]['digits'] == 16, 'Interior degree is required')
need(P['plan'](8, 0, 7, 8)['demands'][0]['shell_floor'] == 15, 'Outer-shell control differs')
print(json.dumps({'status': 'PASS_NEWTON_BACKWARD_PRECISION', **counts}, sort_keys=True))
