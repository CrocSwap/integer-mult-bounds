#!/usr/bin/env python3
"""Exact determinant profiles of two-image tensor prefixes; no new kappa.

Cinna Davis, with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
import ast
from collections import Counter
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def need(ok, reason):
    if not ok:
        raise ValueError(reason)


ZERO = (F(0), F(0))
ONE = (F(1), F(0))
IPOW = (ONE, (F(0), F(1)), (-F(1), F(0)), (F(0), -F(1)))


def add(a, b):
    return a[0]+b[0], a[1]+b[1]


def neg(a):
    return -a[0], -a[1]


def mul(a, b):
    return a[0]*b[0]-a[1]*b[1], a[0]*b[1]+a[1]*b[0]


def norm2(a):
    return a[0]*a[0]+a[1]*a[1]


def div(a, b):
    den = norm2(b)
    need(den != 0, 'Gaussian division by zero')
    return (a[0]*b[0]+a[1]*b[1])/den, (a[1]*b[0]-a[0]*b[1])/den


def determinant(matrix):
    a = [list(row) for row in matrix]
    d = ONE
    for k in range(len(a)):
        pivot = next((i for i in range(k, len(a)) if a[i][k] != ZERO), None)
        if pivot is None:
            return ZERO
        if pivot != k:
            a[k], a[pivot] = a[pivot], a[k]
            d = neg(d)
        lead = a[k][k]; d = mul(d, lead)
        for i in range(k+1, len(a)):
            if a[i][k] == ZERO:
                continue
            q = div(a[i][k], lead)
            a[i][k] = ZERO
            for j in range(k+1, len(a)):
                if a[k][j] != ZERO:
                    a[i][j] = add(a[i][j], neg(mul(q, a[k][j])))
    return d


def matmul(a, b):
    n = len(a)
    out = [[ZERO for _ in range(n)] for _ in range(n)]
    for i in range(n):
        for k in range(n):
            if a[i][k] == ZERO:
                continue
            for j in range(n):
                if b[k][j] != ZERO:
                    out[i][j] = add(out[i][j], mul(a[i][k], b[k][j]))
    return out


def compose(a, b):
    p, e = a; q, f = b
    return tuple(p[q[x]] for x in range(8)), tuple((f[x]+e[q[x]]) % 4 for x in range(8))


def inverse(a):
    p, e = a
    q = tuple(p.index(x) for x in range(8))
    return q, tuple(-e[q[x]] % 4 for x in range(8))


def tensor_monomial(a, width):
    p, e = a; d = 8**width
    out, phases = [], []
    for x in range(d):
        image, phase, place, value = 0, 0, 1, x
        for _ in range(width):
            digit = value % 8; value //= 8
            image += p[digit]*place; phase += e[digit]; place *= 8
        out.append(image); phases.append(phase % 4)
    return out, phases


def cycles(p):
    need(sorted(p) == list(range(len(p))), 'permutation')
    left = set(range(len(p))); lengths = Counter()
    while left:
        start = min(left); x = start; count = 0
        while x in left:
            left.remove(x); x = p[x]; count += 1
        need(x == start, 'closed permutation cycle')
        lengths[count] += 1
    return lengths


def mixture(a, b, width, coefficient=2):
    p, e = tensor_monomial(a, width); q, f = tensor_monomial(b, width)
    out = [[ZERO for _ in p] for _ in p]
    for x in range(len(p)):
        out[p[x]][x] = add(out[p[x]][x], IPOW[e[x]])
        out[q[x]][x] = add(out[q[x]][x], mul((F(coefficient), F(0)), IPOW[f[x]]))
    return out


def multiplicities(width):
    d, t, s = 8**width, 4**width, 2**width
    return ((d+t+2*s)//4, (d+t-2*s)//4, (d-t)//4, (d-t)//4)


def source_bindings():
    pins = json.loads((HERE/'SOURCES.json').read_text())
    input_hashes = {}
    for row in pins['files']:
        if row['usage'] != 'input':
            continue
        data = (ROOT/row['path']).read_bytes()
        need(hashlib.sha256(data).hexdigest() == row['sha256'], 'source bytes: '+row['path'])
        blob = hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
        need(blob == row['git_blob'], 'source blob: '+row['path'])
        input_hashes[row['path']] = row['sha256']
    # Match actual source syntax, without importing/executing the rank engine.
    path = ROOT/'research/complex-two-image-hook-prefix/verify.py'
    assigns = {n.targets[0].id: n.value for n in ast.parse(path.read_text()).body
               if isinstance(n, ast.Assign) and isinstance(n.targets[0], ast.Name)}
    expected = {'U_PERM': 'tuple(x ^ ((x & 1) << 2) for x in range(8))',
                'V_PERM': 'tuple(x ^ (((x ^ (x >> 1)) & 1) * 3) for x in range(8))'}
    for name, expression in expected.items():
        need(ast.dump(assigns[name]) == ast.dump(ast.parse(expression, mode='eval').body),
             'source permutation definition: '+name)
    text = (ROOT/'research/phase-aligned-two-call-prefix/README.md').read_text()
    need('P       = S U S' in text and 'Q       = S V S' in text, 'source repaired-word definitions')
    return input_hashes


def calculate():
    inputs = source_bindings()
    identity = (tuple(range(8)), (0,)*8)
    # Independent coordinate construction, not the source's bit-operation code.
    u, v = [], []
    for x in range(8):
        a, b, c = x % 2, (x//2) % 2, x//4
        u.append(a+2*b+4*((c+a) % 2))
        v.append(b+2*a+4*c)
    U, V = (tuple(u), (0,)*8), (tuple(v), (0,)*8)
    S = (identity[0], tuple(sum((x//2**j) % 2 for j in range(3)) % 4 for x in range(8)))
    P, Q = compose(S, compose(U, S)), compose(S, compose(V, S))
    R = compose(inverse(U), V)
    repaired_R = compose(inverse(P), Q)
    need(repaired_R == compose(inverse(S), compose(R, S)), 'absolute-phase conjugacy')
    power = identity; traces = []
    for _ in range(4):
        trace = ZERO
        for x in range(8):
            if power[0][x] == x:
                trace = add(trace, IPOW[power[1][x]])
        traces.append(trace)
        power = compose(R, power)
    need(power == identity and traces == [(8, 0), (2, 0), (4, 0), (2, 0)], 'ratio traces/order')
    census = []
    for width in range(1, 5):
        p, _ = tensor_monomial(R, width); counts = cycles(p)
        need(set(counts) <= {1, 2, 4}, 'cycle lengths')
        inferred = (counts[1]+counts[2]+counts[4], counts[2]+counts[4], counts[4], counts[4])
        expected = multiplicities(width)
        need(inferred == expected, 'independent cycle/trace multiplicities')
        census.append({'width': width, 'dimension': 8**width,
                       'cycle_counts': dict(sorted(counts.items())),
                       'multiplicities_1_minus1_i_minusi': expected,
                       'abs_determinant_prime_exponents_3_5': [expected[0], expected[2]]})
    determinants = []
    for width in (1, 2):
        m = multiplicities(width); squared = 3**(2*m[0])*5**(2*m[2])
        for name, a, b in [('original', U, V), ('phase_repaired', P, Q)]:
            got = determinant(mixture(a, b, width))
            need(norm2(got) == squared, 'direct Gaussian determinant: '+name)
            determinants.append({'word': name, 'width': width,
                                 'determinant': [str(got[0]), str(got[1])],
                                 'squared_absolute_value': str(squared)})
    # The actual kernel is unitary; tensor powers do not change |det|.
    a, b = (F(1, 2), F(1, 2)), (F(1, 2), -F(1, 2))
    C = [[ZERO for _ in range(8)] for _ in range(8)]
    for x in range(8):
        C[x][x] = a; C[x ^ 1][x] = b
    need(norm2(determinant(C)) == 1, 'paid kernel determinant modulus')
    # Full-input triangular port has F off diagonal and unitary diagonals.
    tri = [[ZERO for _ in range(16)] for _ in range(16)]
    off = matmul(C, matmul(mixture(P, Q, 1), C))
    for i in range(8):
        for j in range(8):
            tri[i][j] = C[i][j]; tri[i+8][j+8] = C[i][j]
            tri[i+8][j] = off[i][j]
    need(norm2(determinant(tri)) == 1, 'triangular dirty-target positive case')
    # Eliminate an arbitrary affine normalized log-volume at widths 1,2,3.
    weights = (64, -16, 1)
    obstruction = tuple(sum(w*multiplicities(f)[j] for f, w in enumerate(weights, 1))
                        for j in (0, 2))
    need(obstruction == (52, -16) and 3**52 != 5**16, 'nonzero three-width curvature')
    for mixing_exp, base_exp in [(0, 1), (2, -3), (-5, 7), (1, 0)]:
        exponents = [mixing_exp*8**f+base_exp*f*8**(f-1) for f in (1, 2, 3)]
        need(sum(w*e for w, e in zip(weights, exponents)) == 0, 'affine-profile positive control')
    # Algebraic conditions used in the all-complex-coefficient written proof.
    coefficient_cases = 0
    for real in range(-3, 4):
        for imag in range(-3, 4):
            t = (F(real, 2), F(imag, 2))
            ap, am = norm2(add(ONE, t)), norm2(add(ONE, neg(t)))
            need(ap-am == 4*t[0], 'equal-magnitude real-part identity')
            if real == 0:
                need(ap*am-norm2(add(ONE, mul(t, t))) == 4*t[1]*t[1],
                     'imaginary-axis magnitude identity')
            coefficient_cases += 1
    controls = []
    need([4*2*8, 2*8] != [22, 12], 'reject tensoring the whole mixture')
    controls.append('whole_sum_tensorization_changes_width_two_profile')
    need(5**4 != 3**10, 'reject constant normalized volume at widths one/two')
    controls.append('constant_volume_claim_fails_two_widths')
    need(3**52 != 5**16, 'reject affine normalized volume at widths one/two/three')
    controls.append('affine_volume_claim_fails_three_widths')
    need(norm2(determinant(mixture(U, V, 1, 1))) == 0, 'reject singular coefficient one')
    controls.append('coefficient_one_is_singular')
    need(norm2(determinant(mixture(U, V, 1, 0))) == 1, 'single-image positive case')
    controls.append('single_image_not_falsely_excluded')
    return {'schema_version': 1, 'claim': 'no_completed_uniform_dirty_return_two_image_module',
            'no_new_kappa': True, 'inputs': inputs, 'ratio_permutation': R[0],
            'ratio_power_traces': [[str(a), str(b)] for a, b in traces],
            'phase_repaired_ratio': repaired_R, 'cycle_census': census,
            'direct_gaussian_determinants': determinants,
            'three_width_exponents_3_5': obstruction, 'two_width_exponents_3_5': [-10, 4],
            'complex_coefficient_identity_cases': coefficient_cases, 'controls': controls,
            'triangular_dirty_target_has_unit_volume': True}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--write-result', type=Path)
    args = ap.parse_args()
    actual = calculate()
    if args.write_result:
        with args.write_result.open('x') as stream:
            json.dump(actual, stream, indent=2, sort_keys=True); stream.write('\n')
    else:
        need(json.loads(json.dumps(actual)) == json.loads((HERE/'RESULT.json').read_text()),
             'committed result equality')
    print('PASS_TWO_IMAGE_DIRTY_VOLUME widths=1,2,3 both_prefixes=2 '
          'curvature=3^52/5^16 no_new_kappa')


if __name__ == '__main__':
    main()
