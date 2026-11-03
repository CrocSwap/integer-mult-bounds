"""Quantize an exact Gaussian child and retain its input lattice coset."""


def phase(z, p):
    a, b = z
    p %= 4
    if p == 0:
        return a, b
    if p == 1:
        return -b, a
    if p == 2:
        return -a, -b
    return b, -a


def route(rec, h):
    if rec is None:
        return list(range(1 << h)), [0] * (1 << h)
    dest, phases = [], []
    for x in range(1 << h):
        dest.append(sum(((row & x).bit_count() % 2) << j
                        for j, row in enumerate(rec["matrix_rows"])) ^ rec["offset"])
        p = rec["phase"]
        for j in range(h):
            if x >> j & 1:
                p += rec["linear_Z4"][j]
                p += 2 * (((rec["quadratic_rows"][j] >> (j + 1))
                          & (x >> (j + 1))).bit_count() % 2)
        phases.append(p % 4)
    if sorted(dest) != list(range(1 << h)):
        raise ValueError("route must be a permutation")
    return dest, phases


class Codec:
    def __init__(self, recipe, h, f, k):
        r = recipe["rank"]
        if any(type(v) is not int for v in (r, h, f, k)) or not (h >= 1 and f >= 1 and 0 <= r <= h):
            raise ValueError("invalid native dimensions")
        self.h, self.f, self.k = h, f, k
        self.axes = [h * j + t for j in range(f) for t in range(r)]
        self.a = len(self.axes)
        self.d = (self.a + 1) // 2
        if k < self.d:
            raise ValueError("coarse inverse is not integral at this grid ratio")
        self.n = 1 << (h * f)
        self.seed_bits = k + self.d
        self.seed_count = 1 << self.seed_bits
        self.bits = 2 * k * self.n
        self.widths = [2 * k - self.a + 2 * sum((j >> b) & 1 for b in self.axes)
                       for j in range(self.n)]
        if min(self.widths) < 0 or sum(self.widths) != self.bits:
            raise ArithmeticError("incorrect quotient digit widths")
        self.left, self.right = route(recipe["left"], h), route(recipe.get("right"), h)

    def check(self, values, seed):
        if type(seed) is not int or not 0 <= seed < self.seed_count:
            raise ValueError("invalid uniform seed")
        if len(values) != self.n or any(len(z) != 2 or any(type(v) is not int for v in z) for z in values):
            raise ValueError("invalid Gaussian integer field")

    def mono(self, values, routing, inverse=False):
        out = [None] * self.n
        dest, phases = routing
        mask = (1 << self.h) - 1
        for src in range(self.n):
            digits, dst, p = src, 0, 0
            for axis in range(self.f):
                digit = digits & mask
                digits >>= self.h
                dst |= dest[digit] << (self.h * axis)
                p += phases[digit]
            if inverse:
                out[src] = phase(values[dst], -p)
            else:
                out[dst] = phase(values[src], p)
        return out

    def exact(self, values, inverse=False):
        """Return integer numerators over the common denominator 2**d."""
        out = self.mono(values, self.left if inverse else self.right, inverse)
        for axis in self.axes:
            stride = 1 << axis
            for start in range(0, self.n, 2 * stride):
                for low in range(stride):
                    p, q = start + low, start + stride + low
                    a, b = out[p]
                    c, d = out[q]
                    first = (a - b + c + d, a + b - c + d)
                    second = (a + b + c - d, -a + b + c + d)
                    out[p], out[q] = (second, first) if inverse else (first, second)
        out = self.mono(out, self.right if inverse else self.left, inverse)
        divisor = 1 << (self.a // 2)
        if any(a % divisor or b % divisor for a, b in out):
            raise ArithmeticError("Gaussian tensor numerator is not divisible")
        return [(a // divisor, b // divisor) for a, b in out]

    def triangular(self, values, inverse=False):
        out = list(values)
        for axis in reversed(self.axes) if inverse else self.axes:
            stride = 1 << axis
            for start in range(0, self.n, 2 * stride):
                for low in range(stride):
                    p, q = start + low, start + stride + low
                    a, b = out[p]
                    c, d = out[q]
                    out[q] = (c - b, d + a) if inverse else (c + b, d - a)
        return out

    def residue(self, values):
        transformed = self.triangular(self.mono(values, self.right))
        packed = bytearray((self.bits + 7) // 8)
        offset = 0
        for (a, b), width in zip(transformed, self.widths):
            for _ in range(width):
                digit = (a + b) % 2
                packed[offset // 8] |= digit << (offset % 8)
                a -= digit
                a, b = (a + b) // 2, (b - a) // 2
                offset += 1
        return bytes(packed)

    def representative(self, packed):
        if not isinstance(packed, bytes) or len(packed) != (self.bits + 7) // 8:
            raise ValueError("invalid residue byte count")
        if self.bits % 8 and packed[-1] >> (self.bits % 8):
            raise ValueError("nonzero residue padding")
        values = []
        offset = 0
        for width in self.widths:
            a = b = 0
            for bit in reversed(range(offset, offset + width)):
                digit = (packed[bit // 8] >> (bit % 8)) & 1
                a, b = a - b + digit, a + b
            values.append((a, b))
            offset += width
        return self.mono(self.triangular(values, True), self.right, True)

    def rounded(self, values, seed):
        self.check(values, seed)
        return [((a + seed) // self.seed_count, (b + seed) // self.seed_count)
                for a, b in self.exact(values)]

    def encode(self, values, seed):
        return self.rounded(values, seed), self.residue(values)

    def restore(self, coarse, packed, seed):
        self.check(coarse, seed)
        x0 = self.representative(packed)
        q0 = self.rounded(x0, seed)
        diff = [(a - c, b - d) for (a, b), (c, d) in zip(coarse, q0)]
        period = self.exact(diff, True)
        shift = self.k - self.d
        return [(a + (c << shift), b + (d << shift)) for (a, b), (c, d) in zip(x0, period)]
