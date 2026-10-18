"""Checked, arbitrary-precision signed integer lanes; no floating arithmetic.

Tekalign, substantial OpenAI Codex assistance. Apache-2.0.
"""
from functools import lru_cache
from dataclasses import dataclass


def need(ok, message):
    if not ok:
        raise ValueError(message)


class Context:
    def __init__(self, n, width):
        need(type(n) is int and 1 <= n <= 18 and type(width) is int and width >= 8, "packed context domain")
        self.n, self.size = n, 1 << n
        self.stride = (width + 2 * n + 16 + 7) // 8
        self.bits = 8 * self.stride - 1
        self.radix = 1 << self.bits
        self.ones = int.from_bytes((1).to_bytes(self.stride, 'little') * self.size, 'little')
        self.mask = (self.radix - 1) * self.ones
        self.signs = (self.radix >> 1) * self.ones
        self.zero = Vector(self, 0, 0)

    @lru_cache(maxsize=128)
    def rep(self, scalar):
        need(0 <= scalar < self.radix, "unsigned lane constant")
        return scalar * self.ones

    @lru_cache(maxsize=32)
    def axis(self, axis):
        need(type(axis) is int and 0 <= axis < self.n, "lane axis")
        step = 1 << axis
        return int.from_bytes((bytes(self.stride * step) + (self.radix - 1).to_bytes(self.stride, 'little') * step) * (self.size // (2 * step)), 'little')

    def pack(self, values):
        if isinstance(values, Vector):
            need(values.c is self, "same packed context")
            return values
        need(len(values) == self.size, "complete packed payload")
        limit = self.radix // 2
        need(all(type(a) is type(b) is int and -limit <= a < limit and -limit <= b < limit for a, b in values), "signed packed input range")
        def one(k):
            return int.from_bytes(b''.join((z[k] % self.radix).to_bytes(self.stride, 'little') for z in values), 'little')
        return Vector(self, one(0), one(1))

    def add(self, a, b):
        s = (a + b) & self.mask
        need(((a ^ s) & (b ^ s) & self.signs) == 0, "packed signed addition overflow")
        return s

    def sub(self, a, b):
        s = (a + (self.mask ^ b) + self.ones) & self.mask
        need(((a ^ b) & (a ^ s) & self.signs) == 0, "packed signed subtraction overflow")
        return s

    def shr(self, a, k):
        need(type(k) is int and 0 <= k < self.bits, "packed right-shift range")
        low = self.rep((1 << (self.bits - k)) - 1)
        fill = ((a & self.signs) >> (self.bits - 1)) * (((1 << k) - 1) << (self.bits - k))
        return ((a >> k) & low) | fill

    def shl(self, a, k):
        need(type(k) is int and 0 <= k < self.bits, "packed left-shift range")
        s = (a & self.rep((1 << (self.bits-k)) - 1)) << k
        need(self.shr(s, k) == a, "packed signed shift overflow")
        return s


@dataclass(frozen=True, slots=True, eq=False)
class Vector:
    c: Context
    real: int
    imag: int

    def __len__(self):
        return self.c.size

    def __iter__(self):
        c = self.c
        a = self.real.to_bytes(c.size * c.stride, 'little')
        b = self.imag.to_bytes(c.size * c.stride, 'little')
        for i in range(0, len(a), c.stride):
            x, y = int.from_bytes(a[i:i+c.stride], 'little'), int.from_bytes(b[i:i+c.stride], 'little')
            yield (x - c.radix if x >= c.radix // 2 else x, y - c.radix if y >= c.radix // 2 else y)

    def __eq__(self, other):
        if not isinstance(other, Vector):
            other = self.c.pack(other)
        return self.c is other.c and self.real == other.real and self.imag == other.imag

    def __add__(self, other):
        other = self.c.pack(other)
        need(not isinstance(self, Words) and not isinstance(other, Words), "decode words before arithmetic")
        return Vector(self.c, self.c.add(self.real, other.real), self.c.add(self.imag, other.imag))

    def __sub__(self, other):
        other = self.c.pack(other)
        need(not isinstance(self, Words) and not isinstance(other, Words), "decode words before arithmetic")
        return Vector(self.c, self.c.sub(self.real, other.real), self.c.sub(self.imag, other.imag))

    def __xor__(self, other):
        other = self.c.pack(other)
        return Vector(self.c, self.real ^ other.real, self.imag ^ other.imag)

    def quotient(self, g):
        return Vector(self.c, self.c.shr(self.real, g), self.c.shr(self.imag, g))

    def residue(self, g):
        need(type(g) is int and 0 <= g < self.c.bits, "packed residue range")
        mask = self.c.rep((1 << g) - 1)
        return Vector(self.c, self.real & mask, self.imag & mask)

    def shift(self, g):
        if g < 0:
            need(self.residue(-g) == self.c.zero, "exact guarded output shift")
            return self.quotient(-g)
        return Vector(self.c, self.c.shl(self.real, g), self.c.shl(self.imag, g))

    def encode(self, width):
        need(type(width) is int and width > 0, "encoding width")
        if width < self.c.bits:
            result = self.residue(width)
            need(result.decode(width) == self, "finite signed word headroom")
        # Sign-extension is implicit. The width remains an authenticated tag.
        return Words(self.c, self.real, self.imag, width)

    def decode(self, width):
        need(type(width) is int and width > 0, "decoding width")
        if width >= self.c.bits:
            need((self.real | self.imag) & self.c.signs == 0, "unsigned encoded word range")
            return self
        need(self.residue(width) == self, "unsigned encoded word range")
        bit = self.c.rep(1 << (width - 1))
        return Vector(self.c, self.c.sub(self.real, (self.real & bit) << 1),
                      self.c.sub(self.imag, (self.imag & bit) << 1))

    def rotate(self, mask, phase):
        phase %= 4
        if phase == 0:
            return self
        a, b, c = self.real & mask, self.imag & mask, self.c
        x, y = ((c.sub(0, b), a) if phase == 1 else
                (c.sub(0, a), c.sub(0, b)) if phase == 2 else (b, c.sub(0, a)))
        return Vector(c, (self.real & (c.mask ^ mask)) | (x & mask),
                      (self.imag & (c.mask ^ mask)) | (y & mask))


@dataclass(frozen=True, slots=True, eq=False)
class Words(Vector):
    """w-bit words stored by their signed value, with implicit sign extension."""
    width: int

    def __eq__(self, other):
        if isinstance(other, Words) and self.width != other.width:
            return False
        return super(Words, self).__eq__(other)

    def __iter__(self):
        for a, b in super(Words, self).__iter__():
            yield a % (1 << self.width), b % (1 << self.width)

    def decode(self, width):
        need(type(width) is int and width == self.width, "encoded word width tag")
        return Vector(self.c, self.real, self.imag)


def xor_words(left, right):
    tagged = left if isinstance(left, Words) else right
    need(isinstance(tagged, Words), "XOR has an encoded width")
    width = tagged.width
    a, b = left.decode(width), right.decode(width)
    result = a ^ b
    return result.encode(width)


def transform(values, axes, inverse=False, linear=False):
    c, result = values.c, values
    axes = tuple(axes)
    need(len(set(axes)) == len(axes) and all(type(a) is int and 0 <= a < c.n for a in axes), "distinct in-range packed axes")
    need(type(inverse) is bool, "Boolean packed direction")
    for axis in axes if linear or not inverse else reversed(axes):
        mask = c.mask ^ c.axis(axis)
        delta = (1 << axis) * c.stride * 8
        a = Vector(c, result.real & mask, result.imag & mask)
        b = Vector(c, (result.real >> delta) & mask, (result.imag >> delta) & mask)
        d = a - b
        turn = Vector(c, d.imag, c.sub(0, d.real)) if inverse else Vector(c, c.sub(0, d.imag), d.real)
        if linear:
            mean = a + b
            low, high = mean + turn, mean - turn
        else:
            mean = b + d.quotient(1)
            high = mean - turn.quotient(1)
            low = high + turn
        result = Vector(c, (low.real & mask) | ((high.real & mask) << delta),
                        (low.imag & mask) | ((high.imag & mask) << delta))
    return result


def character(values, controls, targets=None, negative=False):
    result, c = values, values.c
    if targets is None:
        for axis in controls:
            result = result.rotate(c.axis(axis), -1 if negative else 1)
    else:
        need(len(controls) == len(targets), "matched character axes")
        for a, b in zip(controls, targets, strict=True):
            result = result.rotate(c.axis(a) & c.axis(b), 2)
    return result


def recipe_phase(values, recipe, multiplicity, inverse=False):
    c, m = values.c, len(recipe['matrix_rows'])
    result = values.rotate(c.mask, (-1 if inverse else 1) * multiplicity * recipe['phase'])
    for col in range(multiplicity):
        for i in range(m):
            result = result.rotate(c.axis(i * multiplicity + col), (-1 if inverse else 1) * recipe['linear_Z4'][i])
            for j in range(i+1, m):
                if recipe['quadratic_rows'][i] >> j & 1:
                    result = result.rotate(c.axis(i * multiplicity + col) & c.axis(j * multiplicity + col), 2)
    return result
