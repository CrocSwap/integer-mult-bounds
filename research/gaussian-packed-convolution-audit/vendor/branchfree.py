"""Two packed triangular convolutions for a rounded full-q Gaussian inverse.

Setup uses exact rationals. Online tables and completed operations use a
fixed dyadic grid. This is a local arithmetic prototype, not a tensor solver.
"""
from fractions import Fraction as Q


def rounded(x, bits):
    if bits is None:
        return x
    scale = 1 << bits
    k = abs(x.numerator*scale)//x.denominator
    return Q(k if x >= 0 else -k, scale)


def factors(q, n):
    assert 0 < q <= Q(1, 4) and n > 0
    f = [Q(1)]
    for j in range(1, n):
        f.append(f[-1]*(1-q**(2*j)))
    h = [(-q)**j/f[j] for j in range(n)]
    return f, h


def packed_lower(h, x, bits, count):
    n = len(x)
    assert len(h) == n
    if bits is None:
        return [sum((h[i-j]*x[j] for j in range(i+1)), Q(0)) for i in range(n)]
    scale = 1 << bits
    hh, xx = [a*scale for a in h], [a*scale for a in x]
    assert all(a.denominator == 1 for a in hh+xx)
    hh, xx = [int(a) for a in hh], [int(a) for a in xx]
    # Strict coefficient bound prevents any carry into the next slot.
    width = max(1, (n*max(map(abs, hh))*max(map(abs, xx))).bit_length()+1)
    mask = (1 << width)-1
    def pack(v, sign):
        return sum(max(sign*a, 0) << (width*i) for i, a in enumerate(v))
    hp, hm, xp, xm = pack(hh, 1), pack(hh, -1), pack(xx, 1), pack(xx, -1)
    products = [(hp*xp, 1), (hm*xm, 1), (hp*xm, -1), (hm*xp, -1)]
    count['integer_products'] += 4
    count['convolutions'] += 1
    count['max_operand_bits'] = max(count['max_operand_bits'], *(v.bit_length() for v in (hp, hm, xp, xm)))
    return [rounded(Q(sum(sign*((v >> (width*i)) & mask) for v, sign in products), scale*scale), bits)
            for i in range(n)]


def prepare(q, weights, bits):
    f, h = factors(q, len(weights))
    assert all(a > 0 for a in weights)
    r = lambda xs: [rounded(x, bits) for x in xs]
    return dict(f=r(f), invf=r([1/x for x in f]), h=r(h),
                weights=list(weights), inva=r([1/x for x in weights]), bits=bits)


def apply(table, b, count):
    bits = table['bits']
    def diagonal(d, x):
        count['diagonal_products'] += len(x)
        return [rounded(a*y, bits) for a, y in zip(d, x)]
    x = diagonal(table['inva'], b)
    x = diagonal(table['invf'], x)
    x = packed_lower(table['h'], x, bits, count)
    x = diagonal(table['f'], x)
    x = list(reversed(packed_lower(table['h'], list(reversed(x)), bits, count)))
    x = diagonal(table['invf'], x)
    return diagonal(table['weights'], x)


def counter():
    return dict(convolutions=0, integer_products=0, diagonal_products=0, max_operand_bits=0)
