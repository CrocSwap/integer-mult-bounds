"""Evaluate a complete small multiplication with the compiled two-root word."""

from math import gcd, prod
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from root_gate_plan import load_compiler
from spectral import fourier_axis
from tensor_word import Grid, TensorWord, load_routes
from word_product import word_product
from square_geometry import controller_shape, select_squares, production_widths
from heterogeneous_crt import HeterogeneousCRT


def digits(index, radices):
    result = []
    for radix in radices:
        index, remainder = divmod(index, radix)
        result.append(remainder)
    if index:
        raise ValueError("The index exceeds the rectangle")
    return tuple(result)


def ordinal(pos, widths):
    acc = 0
    for j, side in reversed(tuple(zip(pos, widths, strict=True))):
        if not 0 <= j < side:
            raise ValueError("Coordinate outside the rectangle")
        acc = acc*side + j
    return acc


def rounded_ratio(x, scale):
    return (2*x+scale)//(2*scale)


class Multiplier:
    def __init__(self, sides, digit_bits=8, work_bits=136, source_root=None, scalar_product=word_product):
        self.sides = tuple(sides)
        d = len(sides)
        if not d or d & (d-1) or any(r < 2 or gcd(r,prod(sides[:i])) != 1
                                      for i,r in enumerate(sides)):
            raise ValueError("Use a power-of-two count of pairwise coprime cyclic sides")
        self.size = prod(sides)
        self.base = 1 << digit_bits
        self.public_bits = 6*digit_bits
        if self.size > self.base or digit_bits < 5 or work_bits < self.public_bits:
            raise ValueError("Insufficient public digit or work precision")
        root = Path(source_root) if source_root is not None else Path(__file__).resolve().parents[2]
        compiler = load_compiler(root)
        self.routes = load_routes(root)
        self.widths = tuple(1 << (r-1).bit_length() for r in sides)
        self.router = HeterogeneousCRT(sides, [(t-1).bit_length() for t in self.widths],
                                       self.routes.benes)
        self.scalar_product = scalar_product
        self.grid = Grid(work_bits, scalar_product)
        # The final grid pays for each table and arithmetic conversion.
        axes = [fourier_axis(compiler, r, t, -1, work_bits+8)
                for r,t in zip(self.sides, self.widths, strict=True)]
        self.transform = TensorWord(axes, compiler, self.routes, self.grid, self.public_bits)

    def public(self, x):
        shift = self.grid.bits-self.public_bits
        return tuple((1 if u >= 0 else -1)*((abs(u) >> shift) << shift) for u in x)

    def public_product(self, x, y):
        """Multiply the two represented words, then truncate once on the public grid."""
        a, b = x
        c, d = y
        re = self.scalar_product(a,c)-self.scalar_product(b,d)
        im = self.scalar_product(a,d)+self.scalar_product(b,c)
        shift = self.grid.bits-self.public_bits
        return tuple((1 if u >= 0 else -1)*((abs(u) >> (self.grid.bits+shift)) << shift)
                     for u in (re, im))

    def crt(self, field, reverse=False):
        out = [None]*len(field)
        for i, x in enumerate(field):
            pos = digits(i, self.widths)
            dest = self.router.route(pos, reverse=reverse)
            j = ordinal(dest, self.widths)
            if out[j] is not None:
                raise ValueError("CRT collision in padded coordinates")
            out[j] = x
        return out

    def operand(self, value):
        if value < 0:
            raise ValueError("The magnitude must be nonnegative")
        z = [(0,0)] * prod(self.widths)
        used = 0
        while value:
            if used == self.size:
                raise ValueError("Too many input digits for this transform")
            value, digit = divmod(value, self.base)
            z[ordinal(digits(used, self.sides), self.widths)] = (
                digit * (self.grid.unit//(4*self.base)), 0)
            used += 1
        return self.crt(z), used

    def convolution_grid(self, a, b):
        a = list(map(self.public, self.transform.apply(a)))
        b = list(map(self.public, self.transform.apply(b)))
        products = [self.public_product(x,y) for x,y in zip(a,b,strict=True)]
        return list(map(self.public, self.transform.apply(products, opposite=True)))

    def multiply(self, left, right):
        a, la = self.operand(abs(left))
        b, lb = self.operand(abs(right))
        if max(0, la+lb-1) > self.size:
            raise ValueError("Linear convolution would wrap on this geometry")
        recovered = self.convolution_grid(a, b)
        gain = (4*self.base*self.size)**2
        physical = [rounded_ratio(self.scalar_product(gain, z[0]), self.grid.unit) for z in recovered]
        original = self.crt(physical, reverse=True)
        coeffs = [original[ordinal(digits(i,self.sides),self.widths)] for i in range(self.size)]
        carry = 0
        result_digits = []
        for value in coeffs:
            carry, digit = divmod(value+carry, self.base)
            result_digits.append(digit)
        value = carry
        for digit in reversed(result_digits):
            value = (value << (self.public_bits//6)) + digit
        return (-value if (left<0) != (right<0) else value), coeffs


def production_precision(public_bits, side_widths):
    """Budget the physical intervals, table products and final public error."""
    intervals = 4096*sum(ell+6 for ell in side_widths)
    stages = 20000*(len(side_widths)+1)*(max(side_widths)+2)**6
    return 4*public_bits + 8*intervals + 4*(stages*(len(side_widths)+1)).bit_length() + 64


def multiply_uniform(left, right):
    n = max(abs(left).bit_length(), abs(right).bit_length())
    p, length, count, _ = controller_shape(n)
    if not count:
        return word_product(left, right)
    ws = production_widths(length, count)
    sides = select_squares(ws)
    if sides is None:
        return word_product(left, right)
    machine = Multiplier(sides, digit_bits=p//6, work_bits=production_precision(p, ws))
    return machine.multiply(left, right)[0]


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("left", type=int)
    parser.add_argument("right", type=int)
    parser.add_argument("--sides", type=int, nargs="+", help="run the gate path on a diagnostic geometry")
    args = parser.parse_args()
    if args.sides is None:
        print(multiply_uniform(args.left, args.right))
    else:
        machine = Multiplier(args.sides)
        result, coefficients = machine.multiply(args.left, args.right)
        print(result)
        print("coefficients", coefficients)
        print("complete H calls per transform", machine.transform.h_calls)
