#!/usr/bin/env python3
"""Independent algebraic audit of PR628's radix-9 coefficient interface.

Standard library only. No floating-point arithmetic, pi, trigonometry, or
predecessor arithmetic is used for the independent enclosures/certificates.
The vendored Taylor engine is loaded only as the subject of comparison.
"""
from __future__ import annotations

import argparse
import copy
from fractions import Fraction as F
import hashlib
import importlib.util
import json
from math import isqrt
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
PRECISION = 2048
SEED = 73
EMBEDDINGS = (1, 2, 4, 5, 7, 8)
ZERO = (F(0),) * 6
ONE = (F(1),) + (F(0),) * 5
X = (F(0), F(1)) + (F(0),) * 4


class AuditError(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise AuditError(message)


def fadd(a, b):
    return tuple(x + y for x, y in zip(a, b))


def fscale(a, s):
    return tuple(x * s for x in a)


def fmul(a, b):
    """Product in Q[X]/(X^6 + X^3 + 1), in the six-term power basis."""
    c = [F(0)] * 11
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            c[i + j] += x * y
    for j in range(10, 5, -1):
        c[j - 3] -= c[j]
        c[j - 6] -= c[j]
    return tuple(c[:6])


def fpow(a, n):
    result = ONE
    while n:
        if n & 1:
            result = fmul(result, a)
        a = fmul(a, a)
        n //= 2
    return result


def coefficients(embedding):
    """Divide successively by 1-u^j using a finite weighted geometric sum.

    If v^9=1 and v != 1, (1-v) * [-sum(t*v^t,t=1..8)/9] = 1.
    Every inverse and recurrence is checked exactly in the quotient field.
    This does not use the predecessor's backward tail-product construction.
    """
    require(embedding in EMBEDDINGS, 'nonprimitive embedding')
    u = fpow(X, embedding)
    require(fpow(u, 9) == ONE and fpow(u, 3) != ONE, 'primitive ninth root')
    result = [ONE]
    for j in range(1, 9):
        v = fpow(u, j)
        inverse = ZERO
        for t in range(1, 9):
            inverse = fadd(inverse, fscale(fpow(v, t), F(-t, 9)))
        denominator = fadd(ONE, fscale(v, -1))
        require(fmul(denominator, inverse) == ONE, 'geometric inverse identity')
        h = fmul(result[-1], inverse)
        require(fmul(denominator, h) == result[-1], 'kernel recurrence')
        result.append(h)
    require(result[-1] == fscale(ONE, F(1, 9)), 'leading coefficient')
    return result


def iadd(a, b):
    return a[0] + b[0], a[1] + b[1]


def ineg(a):
    return -a[1], -a[0]


def imul(a, b):
    values = [x * y for x in a for y in b]
    return min(values), max(values)


def cadd(a, b):
    return iadd(a[0], b[0]), iadd(a[1], b[1])


def cmul(a, b):
    return (iadd(imul(a[0], b[0]), ineg(imul(a[1], b[1]))),
            iadd(imul(a[0], b[1]), imul(a[1], b[0])))


def point(z):
    return (F(z[0]), F(z[0])), (F(z[1]), F(z[1]))


def algebraic_root(bits=PRECISION):
    """u=(t+i*sqrt(4-t*t))/2; t is the root in (3/2,8/5).

    p(t)=t^3-3t+1 is strictly increasing for t>1. Integer bisection
    returns adjacent dyadics; isqrt then gives directed sqrt bounds.
    """
    require(type(bits) is int and bits >= 8, 'root precision')
    scale = 1 << bits
    lo, hi = 3 * scale // 2, (8 * scale + 4) // 5

    def numerator(t):
        return t**3 - 3 * t * scale**2 + scale**3

    require(scale < lo < hi < 2 * scale, 'positive cubic chart')
    require(numerator(lo) < 0 < numerator(hi), 'cubic isolating bracket')
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if numerator(mid) < 0:
            lo = mid
        else:
            hi = mid
    require(numerator(lo) < 0 < numerator(hi), 'strict final root bracket')
    slo = isqrt(4 * scale**2 - hi**2)
    shi = isqrt(4 * scale**2 - lo**2) + 1
    require(slo**2 <= 4 * scale**2 - hi**2, 'sqrt lower bound')
    require(shi**2 > 4 * scale**2 - lo**2, 'sqrt upper bound')
    return ((F(lo, 2 * scale), F(hi, 2 * scale)),
            (F(slo, 2 * scale), F(shi, 2 * scale)))


def evaluate(poly, root):
    result = point((0, 0))
    for a in reversed(poly):
        result = cadd(cmul(result, root), point((a, 0)))
    return result


def kernel_boxes(embedding, root):
    return [evaluate(h, root) for h in coefficients(embedding)]


def require_contained(inner, outer):
    require(len(inner) == len(outer) == 9, 'coefficient count')
    for j, (small, large) in enumerate(zip(inner, outer)):
        for axis in (0, 1):
            a, b = small[axis]
            c, d = large[axis]
            require(c <= a <= b <= d, f'coefficient enclosure j={j} axis={axis}')


def zmul(a, b):
    return a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0]


def zadd(a, b):
    return a[0] + b[0], a[1] + b[1]


def norm2(a):
    return a[0]**2 + a[1]**2


def power2(exponent):
    return F(1 << exponent) if exponent >= 0 else F(1, 1 << -exponent)


def upper_power2(value):
    """Smallest integer e with positive value <= 2**e, using only integers."""
    require(value > 0, 'positive error bound')
    e = value.numerator.bit_length() - value.denominator.bit_length()
    if power2(e) < value:
        e += 1
    require(power2(e - 1) < value <= power2(e), 'dyadic upper bound')
    return e


def factor_certificate(row, boxes, normalize=True):
    require(row['radix'] == 9 and row['embedding'] in EMBEDDINGS, 'factor domain')
    beta = F(row['beta'])
    w, p, fb = row['working_bits'], row['target_bits'], row['factor_bits']
    require(0 < beta < 1, 'margin domain')
    require(all(type(v) is int and v > 0 for v in (w, p, fb)), 'precision domain')
    require(fb <= 1024, 'factor precision cap')
    raw = row['roots']
    require(len(raw) == 8 and all(len(z) == 2 for z in raw), 'factor count')
    roots = [tuple(F(v) for v in z) for z in raw]
    q = [(F(1), F(0))]
    inner = 0
    for z in roots:
        require(all(v.denominator & (v.denominator - 1) == 0 and
                    v.denominator <= 1 << fb for v in z), 'dyadic factor')
        radius = norm2(z)
        inside = radius < 1
        inner += inside
        stable_radius = radius if inside else 1 / radius
        require(stable_radius <= (1 - beta)**2, 'stable factor margin')
        next_q = [(F(0), F(0))] * (len(q) + 1)
        for j, a in enumerate(q):
            next_q[j] = zadd(next_q[j], zmul((-z[0], -z[1]), a))
            next_q[j + 1] = zadd(next_q[j + 1], a)
        q = next_q
    if normalize:
        q = [(a / 9, b / 9) for a, b in q]
    require(len(q) == len(boxes) == 9, 'polynomial degree')
    residual = sum(max(abs(qj[axis] - end) for end in box[axis])
                   for qj, box in zip(q, boxes) for axis in (0, 1))
    # Round bounds upward to powers of two for compact, exact public receipts.
    residual_exponent = upper_power2(residual)
    epsilon = power2(residual_exponent)
    A = F(9) / beta**8
    require(A * epsilon < 1, 'Neumann residual admission')
    perturbation = A * A * epsilon / (1 - A * epsilon)
    u = power2(-w)
    require(u <= beta**2 / 2, 'periodic closure precision')
    # Closed sum solving E_j=alpha*E_(j-1)+7u/beta^3*(9 beta^-(j-1)+1).
    # No predecessor budget function or execution routine is imported.
    alpha = 1 / beta + 7 * u / beta**3
    error = 7 * u / beta**3 * sum(
        alpha**(7 - j) * (9 / beta**j + 1) for j in range(8))
    error_exponent = upper_power2(error)
    total = perturbation + power2(error_exponent)
    require(total <= power2(-p), 'complete target error')
    return {
        'embedding': row['embedding'], 'inner_factors': inner, 'outer_factors': 8 - inner,
        'beta': str(beta), 'factor_bits': fb, 'working_bits': w, 'target_bits': p,
        'coefficient_residual_le_power2': residual_exponent,
        'rounded_execution_error_le_power2': error_exponent,
        'total_error_le_power2': upper_power2(total),
        'inverse_norm_bound': str(A),
        'scope': 'Coefficient interface and inherited norm/rounding inequalities; no scan replay.'
    }


def verify_sources(base=ROOT):
    manifest = json.loads((base / 'SOURCE.json').read_text(encoding='utf-8'))
    for name, info in manifest['files'].items():
        path = (base / name).resolve()
        require(path.is_relative_to(base.resolve()), 'source path containment')
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        require(digest == info['sha256'], f'source drift: {name}')
    return manifest


def load_subject(base=ROOT):
    spec = importlib.util.spec_from_file_location('pr628_audit_subject', base / 'vendor/interval_kernel.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def rejected(name, call, expected):
    try:
        call()
    except AuditError as error:
        require(expected in str(error), f'wrong failure for {name}: {error}')
        return {'name': name, 'rejected_by': str(error)}
    raise AuditError(f'accepted negative control: {name}')


def audit(base=ROOT):
    manifest = verify_sources(base)
    root = algebraic_root()
    algebraic = {k: kernel_boxes(k, root) for k in EMBEDDINGS}
    # Independent kernel coefficients/enclosures precede the subject import.
    subject = load_subject(base)
    comparisons = []
    subject_boxes = {}
    for k in EMBEDDINGS:
        outer = subject.kernel(9, k)
        subject_boxes[k] = outer
        require_contained(algebraic[k], outer)
        comparisons.append({'embedding': k, 'coefficients': 9, 'real_intervals': 18,
                            'independent_enclosures_contained': True})
    rows = [row for row in json.loads((base / 'vendor/FACTORS.json').read_text(encoding='utf-8'))
            if row['radix'] == 9]
    require([r['embedding'] for r in rows] == [1, 2], 'pinned factor inventory')
    certificates = [factor_certificate(row, algebraic[row['embedding']]) for row in rows]
    # Exact coefficient conjugation is an algebraic identity, not interval overlap.
    conjugate = fpow(X, 8)
    for k in (1, 2, 4):
        for h, expected in zip(coefficients(k), coefficients(9-k)):
            actual = ZERO
            for a in reversed(h):
                actual = fadd(fmul(actual, conjugate), fscale(ONE, a))
            require(actual == expected, 'exact coefficient conjugation')
    positives = []
    for row in rows:
        reverse = copy.deepcopy(row)
        reverse['roots'].reverse()
        require(factor_certificate(reverse, algebraic[row['embedding']]) ==
                factor_certificate(row, algebraic[row['embedding']]), 'factor reorder invariance')
        conj = copy.deepcopy(row)
        conj['embedding'] = 9 - row['embedding']
        conj['roots'] = [[z[0], str(-F(z[1]))] for z in row['roots']]
        proof = factor_certificate(conj, algebraic[conj['embedding']])
        positives.append({'control': 'conjugated factors', **proof})
    controls = []
    controls.append(rejected('wrong embedding enclosure',
                             lambda: require_contained(algebraic[2], subject_boxes[1]),
                             'coefficient enclosure'))
    controls.append(rejected('omitted conjugation',
                             lambda: require_contained(algebraic[8], subject_boxes[1]),
                             'coefficient enclosure'))
    changed = copy.deepcopy(algebraic[1])
    j = SEED % 9
    changed[j] = (iadd(changed[j][0], (F(1, 1 << 256),) * 2), changed[j][1])
    controls.append(rejected('seed-selected coefficient perturbation',
                             lambda: require_contained(changed, subject_boxes[1]),
                             'coefficient enclosure'))
    for row in rows:
        k = row['embedding']
        for name, expected in [('unit root', 'stable factor margin'),
                               ('missing root', 'factor count'),
                               ('insufficient precision', 'complete target error'),
                               ('changed root', 'Neumann residual admission'),
                               ('wrong factor embedding', 'Neumann residual admission')]:
            bad = copy.deepcopy(row)
            if name == 'unit root':
                bad['roots'][SEED % 8] = ['1', '0']
            elif name == 'missing root':
                bad['roots'].pop(SEED % 8)
            elif name == 'insufficient precision':
                bad['working_bits'] = 128
            elif name == 'changed root':
                bad['roots'][SEED % 8][0] = str(F(bad['roots'][SEED % 8][0]) + F(1, 16))
            elif name == 'wrong factor embedding':
                bad['embedding'] = 9 - k
            controls.append(rejected(f'k={k}: {name}',
                lambda b=bad: factor_certificate(b, algebraic[b['embedding']]), expected))
        controls.append(rejected(f'k={k}: omitted 1/r normalization',
            lambda r=row: factor_certificate(r, algebraic[r['embedding']], normalize=False),
            'Neumann residual admission'))
    return {
        'status': 'PASS_RADIX9_ALGEBRAIC_AUDIT', 'contributor': 'William Lawyer',
        'assignment_seed': SEED, 'base_commit': manifest['base_commit'],
        'predecessor_head': manifest['predecessor_head'],
        'root_isolation_bits': PRECISION, 'field_modulus': [1, 0, 0, 1, 0, 0, 1],
        'root_rectangle': [[str(endpoint) for endpoint in interval] for interval in root],
        'primitive_embeddings': list(EMBEDDINGS),
        'exact_coefficients_power_basis': {
            str(k): [[str(a) for a in h] for h in coefficients(k)] for k in EMBEDDINGS
        },
        'exact_geometric_inverse_identities': 48,
        'exact_recurrence_identities': 48, 'exact_conjugation_identities': 27,
        'coefficient_comparisons': comparisons, 'factor_certificates': certificates,
        'positive_conjugation_controls': positives, 'factor_reordering_controls': 2,
        'mathematical_negative_controls': controls,
        'scope': 'Finite radix-9 audit; conditional on PR628 scan and operator analysis. '
                 'No new kappa, complete multiplication proof, or all-radix claim.'
    }


def encoded(result):
    return (json.dumps(result, indent=2, ensure_ascii=True) + '\n').encode('utf-8')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, help='Write a fresh deterministic receipt; never overwrite.')
    parser.add_argument('--check', type=Path, default=ROOT / 'EXPECTED.json')
    parser.add_argument('--generate', action='store_true', help='Authoring only: skip expected-receipt comparison.')
    args = parser.parse_args()
    if args.output:
        require(not args.output.exists(), 'output already exists')
    result = audit()
    payload = encoded(result)
    if not args.generate:
        require(args.check.read_bytes() == payload, 'expected evidence differs')
    if args.output:
        with args.output.open('xb') as out:
            out.write(payload)
    print(f"{result['status']}: 6 embeddings; 54 coefficient enclosures; "
          f"2 submitted factor certificates; {len(result['mathematical_negative_controls'])} rejected controls")


if __name__ == '__main__':
    sys.dont_write_bytecode = True
    try:
        main()
    except (AuditError, OSError, KeyError, TypeError, ZeroDivisionError) as error:
        print(f'FAIL_RADIX9_ALGEBRAIC_AUDIT: {error}', file=sys.stderr)
        sys.exit(1)
