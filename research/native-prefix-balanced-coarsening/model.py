"""Finite exact reference for the prefix-balanced native codec.

The rounding and codec substitution are the contribution. Gaussian Smith
coordinates are the cited PR6540 premise, instantiated for canonical C axes.
"""

from dataclasses import dataclass

Gaussian = tuple[int, int]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def balanced(numerators: tuple[int, ...], denominator: int, seed: int) -> tuple[int, ...]:
    require(1 <= len(numerators) <= 1024, "coordinate limit")
    require(1 <= denominator <= 1 << 24, "denominator limit")
    require(0 <= seed < denominator, "seed range")
    require(all(type(value) is int and value.bit_length() <= 8192 for value in numerators),
            "numerator payload limit")
    carry = seed
    output = []
    for value in numerators:
        quotient, carry = divmod(value + carry, denominator)
        require(0 <= carry < denominator, "carry invariant")
        output.append(quotient)
    return tuple(output)


def flatten(values: tuple[Gaussian, ...]) -> tuple[int, ...]:
    return tuple(component for value in values for component in value)


def gaussian(values: tuple[int, ...]) -> tuple[Gaussian, ...]:
    require(len(values) % 2 == 0, "Gaussian component count")
    return tuple((values[j], values[j + 1]) for j in range(0, len(values), 2))


@dataclass(frozen=True)
class Native:
    size: int
    active: int
    precision: int

    def __post_init__(self) -> None:
        require(2 <= self.size <= 512 and self.size.bit_count() == 1, "size limit")
        require(0 <= self.active <= 8 and self.active < self.size.bit_length(), "active-axis range")
        require((self.active + 1) // 2 <= self.precision <= 16, "precision range")

    @property
    def scale(self) -> int:
        return 1 << ((self.active + 1) // 2)

    @property
    def denominator(self) -> int:
        return (1 << self.precision) * self.scale

    @property
    def label_bits(self) -> int:
        return 2 * self.precision * self.size

    def check(self, values: tuple[Gaussian, ...]) -> None:
        require(len(values) == self.size, "field size")
        require(all(type(v) is int and v.bit_length() <= 4096 for z in values for v in z),
                "integer payload limit")

    def numerators(self, values: tuple[Gaussian, ...], inverse: bool = False) -> tuple[Gaussian, ...]:
        self.check(values)
        work = list(values)
        for axis in range(self.active):
            bit = 1 << axis
            for j in range(self.size):
                if j & bit:
                    continue
                p, q = work[j]
                r, s = work[j | bit]
                first = (p - q + r + s, p + q - r + s)
                second = (p + q + r - s, -p + q + r + s)
                work[j], work[j | bit] = (second, first) if inverse else (first, second)
        divisor = 1 << (self.active // 2)
        require(all(v % divisor == 0 for z in work for v in z), "native denominator")
        return tuple((p // divisor, q // divisor) for p, q in work)

    def period(self, values: tuple[Gaussian, ...]) -> tuple[Gaussian, ...]:
        factor = (1 << self.precision) // self.scale
        return tuple((factor * p, factor * q) for p, q in self.numerators(values, True))

    def triangular(self, values: tuple[Gaussian, ...], inverse: bool = False) -> tuple[Gaussian, ...]:
        self.check(values)
        work = list(values)
        axes = range(self.active - 1, -1, -1) if inverse else range(self.active)
        sign = 1 if inverse else -1
        for axis in axes:
            bit = 1 << axis
            for j in range(self.size):
                if j & bit:
                    continue
                p, q = work[j]
                r, s = work[j | bit]
                work[j | bit] = (r - sign * q, s + sign * p)
        return tuple(work)

    def exponents(self) -> tuple[int, ...]:
        mask = (1 << self.active) - 1
        return tuple(2 * self.precision - self.active + 2 * (j & mask).bit_count()
                     for j in range(self.size))

    def label(self, values: tuple[Gaussian, ...]) -> int:
        label = 0
        offset = 0
        for (p, q), width in zip(self.triangular(values), self.exponents(), strict=True):
            for _ in range(width):
                digit = (p + q) % 2
                label |= digit << offset
                p, q = (p - digit + q) // 2, (q - p + digit) // 2
                offset += 1
        require(offset == self.label_bits, "label capacity")
        return label

    def representative(self, label: int) -> tuple[Gaussian, ...]:
        require(type(label) is int and 0 <= label < 1 << self.label_bits, "label range")
        values = []
        offset = 0
        for width in self.exponents():
            p, q = 0, 0
            for bit in range(width - 1, -1, -1):
                digit = (label >> (offset + bit)) & 1
                p, q = p - q + digit, p + q
            values.append((p, q))
            offset += width
        return self.triangular(tuple(values), True)

    def quantize(self, values: tuple[Gaussian, ...], seed: int) -> tuple[Gaussian, ...]:
        return gaussian(balanced(flatten(self.numerators(values)), self.denominator, seed))

    def encode(self, values: tuple[Gaussian, ...], seed: int) -> tuple[tuple[Gaussian, ...], int]:
        return self.quantize(values, seed), self.label(values)

    def decode(self, coarse: tuple[Gaussian, ...], label: int, seed: int) -> tuple[Gaussian, ...]:
        self.check(coarse)
        representative = self.representative(label)
        rounded = self.quantize(representative, seed)
        difference = tuple((p - r, q - s) for (p, q), (r, s) in zip(coarse, rounded, strict=True))
        correction = self.period(difference)
        return tuple((p + r, q + s) for (p, q), (r, s) in zip(representative, correction, strict=True))
