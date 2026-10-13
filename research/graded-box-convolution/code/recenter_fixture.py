"""Exact finite tensor recentering experiment; no asymptotic cost claim.

The tensor triangular convolution is executed by four signed-split integer
products with carry-safe mixed-radix padding. Dense rational matrices provide
an independent oracle. The rational geometry is an analogue, not a legal
instance of every Gaussian source hypothesis.
"""
from fractions import Fraction as Q
from itertools import product
from math import prod
import json


def pow2(e):
    return Q(2**e) if e >= 0 else Q(1, 2**(-e))


def rnd(x, bits):
    if bits is None:
        return x
    s = 1 << bits
    return Q((1 if x >= 0 else -1)*(abs(x.numerator)*s//x.denominator), s)


def coordinates(shape):
    return list(product(*(range(n) for n in shape)))


def setup(shape):
    u = 20
    q = pow2(-u-1)
    fs = []
    aa = []
    ee = []
    centres = [(n-1)//2 for n in shape]
    for n, c in zip(shape, centres):
        f = [Q(1)]
        for k in range(1, n):
            f.append(f[-1]*(1-q**(2*k)))
        err = [Q(4+j % 4, 8) for j in range(n)]
        fs.append(f)
        aa.append([err[j]*pow2(-u*j+j*j) for j in range(n)])
        ee.append([err[j]*pow2((j-c)**2) for j in range(n)])
    return q, fs, aa, ee, centres


def dense(shape, upper):
    q, fs, aa, _, _ = setup(shape)
    coords = coordinates(shape)
    out = []
    for i in coords:
        row = []
        for j in coords:
            ks = [b-a if upper else a-b for a, b in zip(i, j)]
            row.append(Q(0) if min(ks) < 0 else prod(
                aa[d][i[d]]/aa[d][j[d]]*(-q)**k/fs[d][k]
                for d, k in enumerate(ks)))
        out.append(row)
    return out


def prepare(shape, upper, bits, mutation=None):
    q, fs, _, ee, centres = setup(shape)
    coords = coordinates(shape)
    eff = [pow2(-(1+2*c) if upper else -(41-2*c)) for c in centres]
    if mutation == 'wrong_slope':
        eff = [q for _ in shape]
    kernel = [rnd(prod((-eff[d])**k/fs[d][k] for d, k in enumerate(v)), bits)
              for v in coords]
    weights = [prod(ee[d][j] for d, j in enumerate(v)) for v in coords]
    if mutation == 'missing_residual':
        weights = [Q(1)]*len(coords)
    radices = list(shape) if mutation == 'missing_padding' else [2*n-1 for n in shape]
    strides = [prod(radices[:d]) for d in range(len(shape))]
    index = lambda v: sum(j*s for j, s in zip(v, strides))
    slots = [index(v) for v in coords]
    output_slots = [index(tuple(n-1-j for n, j in zip(shape, v))) if upper else index(v)
                    for v in coords]
    return kernel, weights, slots, output_slots, prod(radices)


def packed_apply(table, x, bits, upper, counts, mutation=None):
    kernel, weights, slots, output_slots, padded = table
    s = 1 << bits
    transformed = [rnd(v/w, bits) for v, w in zip(x, weights)]
    hh = [int(v*s) for v in kernel]
    xx = [int(v*s) for v in transformed]
    width = max(1, (len(x)*max(map(abs, hh))*max(map(abs, xx))).bit_length()+1)
    def pack(vals, positions, sign):
        return sum(max(sign*v, 0) << (width*k) for v, k in zip(vals, positions))
    input_slots = output_slots if upper else slots
    hp, hm = pack(hh, slots, 1), pack(hh, slots, -1)
    xp, xm = pack(xx, input_slots, 1), pack(xx, input_slots, -1)
    products = [(hp*xp, 1), (hm*xm, 1), (hp*xm, -1), (hm*xp, -1)]
    if mutation == 'missing_signed_cross_terms':
        products = products[:2]
    mask = (1 << width)-1
    values = [rnd(Q(sum(sign*((v >> (width*k)) & mask) for v, sign in products), s*s), bits)
              for k in output_slots]
    counts['integer_products'] += len(products)
    counts['convolutions'] += 1
    counts['max_operand_bits'] = max(counts['max_operand_bits'], *(v.bit_length() for v in (hp, hm, xp, xm)))
    counts['padded_slots'] = padded
    return [rnd(v*w, bits) for v, w in zip(values, weights)]


def run_case(shape, bits, upper):
    matrix = dense(shape, upper)
    n = len(matrix)
    table = prepare(shape, upper, bits)
    counts = dict(integer_products=0, convolutions=0, max_operand_bits=0)
    # Every basis column, followed by two signed dense input vectors.
    vectors = [[Q(int(j == k)) for j in range(n)] for k in range(n)]
    vectors += [[Q((-1)**j*(j % 7+1), 8) for j in range(n)],
                [Q((j*13) % 17-8, 8) for j in range(n)]]
    worst = Q(0)
    for x in vectors:
        expected = [sum((a*b for a, b in zip(row, x)), Q(0)) for row in matrix]
        got = packed_apply(table, x, bits, upper, counts)
        worst = max(worst, max(abs(a-b) for a, b in zip(expected, got)))
    assert worst < pow2(-12), (shape, bits, upper, float(worst))
    # Explicit finite rounding budget for this algorithm and |x| <= 1:
    # predivide <= eta; kernel <= eta; convolution rounding <= eta;
    # final scaling/rounding <= Emax*eta + eta.
    kernel, weights, *_ = table
    eta = pow2(-bits)
    hbound = prod(Q(15, 14) for _ in shape)
    bound = max(weights)*(n*(hbound*eta+eta/min(weights)+eta*eta)+eta)+eta
    assert worst <= bound and bound < pow2(-12)
    return dict(shape=shape, bits=bits, orientation='upper' if upper else 'lower',
                vectors=len(vectors), matrix_entries=n*n, worst_error=float(worst),
                error_bound=float(bound), **counts)


def main():
    identity_entries = 0
    for shape in ([3]*4, [3, 2, 4]):
        coords = coordinates(shape)
        for upper in (False, True):
            expected = dense(shape, upper)
            kernel, weights, *_ = prepare(shape, upper, None)
            by_delta = dict(zip(coords, kernel))
            for i, a in enumerate(coords):
                for j, b in enumerate(coords):
                    delta = tuple(y-x if upper else x-y for x, y in zip(a, b))
                    actual = Q(0) if min(delta) < 0 else weights[i]*by_delta[delta]/weights[j]
                    assert actual == expected[i][j]
                    identity_entries += 1
    results = [run_case(shape, bits, upper) for shape in ([3]*4, [3, 2, 4])
               for bits in (32, 64) for upper in (False, True)]
    shape = [3]*4
    q, fs, aa, _, _ = setup(shape)
    raw = prod((-q)/f[1] for f in fs)
    weighted = raw*prod(a[0]/a[1] for a in aa)
    assert rnd(raw, 64) == 0 and weighted > pow2(-12)
    controls = {}
    matrix = dense(shape, True)
    for mutation in ('wrong_slope', 'missing_residual', 'missing_padding', 'missing_signed_cross_terms'):
        table = prepare(shape, True, 64, mutation)
        # Test every column and one signed dense vector to witness rejection.
        n = len(matrix)
        vectors = [[Q(int(j == k)) for j in range(n)] for k in range(n)]
        vectors.append([Q((-1)**j*(j % 7+1), 8) for j in range(n)])
        worst = Q(0)
        for x in vectors:
            counts = dict(integer_products=0, convolutions=0, max_operand_bits=0)
            got = packed_apply(table, x, 64, True, counts, mutation)
            expected = [sum((a*b for a, b in zip(row, x)), Q(0)) for row in matrix]
            worst = max(worst, max(abs(a-b) for a, b in zip(expected, got)))
        assert worst > pow2(-12), mutation
        controls[mutation] = dict(rejected=True, worst_error=float(worst))
    print(json.dumps(dict(scope='finite rational analogue; no global complexity or kappa claim',
                         exact_identity_entries=identity_entries,
                         cases=results, naive_kernel=dict(bits=64, rounds_to_zero=True,
                         weighted_entry=str(weighted), weighted_entry_float=float(weighted)),
                         mutation_controls=controls), indent=2))


if __name__ == '__main__':
    main()
