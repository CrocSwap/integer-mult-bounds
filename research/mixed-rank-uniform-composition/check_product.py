"""Exercise the joined Gaussian, ring, CRT and carry maps at small sizes."""

import cmath
import math
import sys
from fractions import Fraction
from functools import cache
from itertools import product
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_group import five
from check_synthetic import rounds
from gaussian_pages import admitted_row, recovery_diagonal


SIDES = (5, 7)
TARGET = (8, 8)
BASE = 256
SCALE = 1 << 96
DIVISOR = 64


def demand(condition, reason):
    if not condition:
        raise ValueError(reason)


@cache
def page(axis):
    r, t = SIDES[axis], TARGET[axis]
    slots = [(2 * t * j + r) // (2 * r) for j in range(r)]
    selected = set(slots)
    broad = [[Fraction(0) for _ in range(t)] for _ in range(t)]
    narrow = [[Fraction(0) for _ in range(t)] for _ in range(t)]
    diagonal = []
    for v in range(t):
        diagonal.append(Fraction(recovery_diagonal(6, 96, r, t, v), SCALE))
        for col, _, wide, thin in admitted_row(6, 96, r, t, v, 96):
            broad[v][col] += Fraction(wide, SCALE)
            narrow[v][col] += Fraction(thin, SCALE)
    # Both cuts contain a real interior and a nonempty exterior.
    interior = sorted(selected)[1:3]
    return slots, broad, narrow, diagonal, interior


def coordinates(k):
    slow, fast = SIDES
    return (k * pow(fast, -1, slow)) % slow, k % fast


def all_pos(sides):
    return product(*(range(t) for t in sides))


def grouped(field, inverse):
    for axis in range(2):
        _, broad, narrow, diagonal, interior = page(axis)
        matrix = narrow if inverse else broad
        for fixed in range(TARGET[1-axis]):
            line = [(fixed, j) if axis else (j, fixed) for j in range(TARGET[axis])]
            result = five(matrix, interior, [field[pos] for pos in line], inverse)
            for j, pos in enumerate(line):
                field[pos] = complex(result[j]) * (diagonal[j] if inverse else 1) / DIVISOR
    return field


def grid(z):
    return round(z.real*SCALE), round(z.imag*SCALE)


def signed_product(left, right, r):
    # Store one exact signed linear convolution in a single integer product.
    # The base exceeds twice the largest possible accumulated coefficient.
    bound = r * max(map(abs, left)) * max(map(abs, right))
    radix = 1 << (2*bound+1).bit_length()
    def pack(values):
        total = 0
        for v in reversed(values):
            total = total * radix + v
        return total
    encoded = pack(left) * pack(right)
    coefficients = []
    for _ in range(2*r-1):
        residue = (encoded+radix//2) % radix - radix//2
        encoded = (encoded-residue)//radix
        coefficients.append(residue)
    demand(encoded == 0, "signed carry escaped polynomial")
    return [coefficients[i] - (coefficients[i+r] if i+r < len(coefficients) else 0)
            for i in range(r)]


def ring_product(left, right):
    r = len(left)
    a, b = zip(*left)
    c, d = zip(*right)
    ac, bd = signed_product(a,c,r), signed_product(b,d,r)
    ad, bc = signed_product(a,d,r), signed_product(b,c,r)
    return tuple((u-v, w+x) for u,v,w,x in zip(ac,bd,ad,bc))


def convolution(f, g):
    outer, r = TARGET
    twist = [cmath.exp(1j*math.pi*j/r) for j in range(r)]
    def forward(h):
        arrays = {(i,): tuple(grid(h[i,j]*twist[j]) for j in range(r)) for i in range(outer)}
        return rounds(arrays, (outer,), r)
    left, right = forward(f), forward(g)
    pairs = {k: ring_product(lv, right[k]) for k, lv in left.items()}
    returned = rounds(pairs, (outer,), r, opposite=True)
    # Two forwards and one opposite each divide by outer. The final shift multiplies by outer.
    divisor = SCALE**2 * outer**2 * r
    return {(i,j): complex(*returned[(i,)][j])*twist[j].conjugate()/divisor
            for i,j in all_pos(TARGET)}


def source_transform(data, opposite):
    slots = [page(axis)[0] for axis in range(2)]
    field = {pos: 0j for pos in all_pos(TARGET)}
    for k, val in enumerate(data):
        i, j = coordinates(k)
        field[slots[0][i],slots[1][j]] = val.conjugate() if opposite else val
    expanded = grouped(field, False)
    chirp = {x: cmath.exp(-1j*math.pi*sum(r*j*j/t for r,j,t in zip(SIDES,x,TARGET)))
             for x in field}
    middle = convolution(chirp, {x: chirp[x].conjugate()*v for x,v in expanded.items()})
    cropped = grouped({x: chirp[x].conjugate()*v for x,v in middle.items()}, True)
    output = []
    for k in range(len(data)):
        i, j = coordinates(k)
        z = cropped[slots[0][i],slots[1][j]] * DIVISOR**4
        output.append(z.conjugate() if opposite else z)
    return output


def multiply(left, right):
    count = math.prod(SIDES)
    def encode(n):
        digits = []
        for _ in range(count):
            n, digit = divmod(n, BASE)
            digits.append(complex(digit/(4*BASE)))
        demand(n == 0, "test input exceeds cyclic range")
        return digits
    fa, fb = (source_transform(encode(n), False) for n in (left,right))
    recovered = source_transform([x*y for x,y in zip(fa,fb)], True)
    values = [v*(count*4*BASE)**2 for v in recovered]
    coeffs = [round(v.real) for v in values]
    demand(all(c >= 0 and abs(v-c) < .25 for v,c in zip(values,coeffs)), "rounding radius")
    carry = total = 0
    for j,c in enumerate(coeffs):
        carry, digit = divmod(carry+c, BASE)
        total += digit << (8*j)
    total += carry << (8*count)
    return total, coeffs


if __name__ == "__main__":
    for left, right in [(741503,466013), (0,65535), (65535,65535), (256**4+1,255)]:
        result, coeffs = multiply(left,right)
        demand(result == left*right, "independent integer oracle")
        if left == 741503:
            demand(coeffs == [11811,10996,4152,868,77]+[0]*30, "pre-carry coefficients")
            print("741503 x 466013 =", result, "coefficients", coeffs[:5])
    print("PASS_JOINED_SMALL_GEOMETRY")
