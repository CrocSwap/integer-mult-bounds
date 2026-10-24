"""Fixed-divisor bit-plane scan using bounded-word Boolean/shift/add operations."""
from dataclasses import dataclass


def need(ok, message):
    if not ok:
        raise ValueError(message)


@dataclass
class Machine:
    width: int
    operations: int = 0

    def __post_init__(self):
        need(type(self.width) is int and self.width >= 1, 'positive word width')
        self.mask = (1 << self.width) - 1

    def op(self, value):
        self.operations += 1
        need(type(value) is int and 0 <= value <= self.mask, 'word overflow')
        return value

    def band(self, a, b): return self.op(a & b)
    def bor(self, a, b): return self.op(a | b)
    def bxor(self, a, b): return self.op(a ^ b)
    def bnot(self, a): return self.op(a ^ self.mask)
    def shr(self, a, count):
        need(0 <= count < self.width, 'invalid shift')
        return self.op(a >> count)
    def shl(self, a, count):
        need(0 <= count < self.width, 'invalid shift')
        return self.op((a << count) & self.mask)
    def add(self, a, b): return self.op(a + b)
    def sub(self, a, b): return self.op(a - b)
    def ge(self, a, b):
        self.operations += 1
        return a >= b


def compare_constant(m, planes, constant):
    """A mask of lanes whose bit-plane value is at least constant."""
    greater, equal = 0, m.mask
    for bit in range(len(planes) - 1, -1, -1):
        value = planes[bit]
        if (constant >> bit) & 1:
            equal = m.band(equal, value)
        else:
            greater = m.bor(greater, m.band(equal, value))
            equal = m.band(equal, m.bnot(value))
    return m.bor(greater, equal)


def subtract_if(m, planes, constant, selected):
    borrow, result = 0, []
    for bit, value in enumerate(planes):
        part = selected if (constant >> bit) & 1 else 0
        result.append(m.bxor(m.bxor(value, part), borrow))
        borrow = m.bor(m.band(m.bnot(value), m.bor(part, borrow)),
                       m.band(part, borrow))
    need(borrow == 0, 'selected subtraction underflow')
    return result


def modular_add(m, a, b, divisor):
    carry, result = 0, []
    for left, right in zip(a, b):
        temporary = m.bxor(left, right)
        result.append(m.bxor(temporary, carry))
        carry = m.bor(m.band(left, right), m.band(temporary, carry))
    result.append(carry)
    selected = compare_constant(m, result, divisor)
    result = subtract_if(m, result, divisor, selected)
    need(result[-1] == 0, 'modular result too large')
    return result[:-1]


def modular_scale(m, planes, constant, divisor):
    result = [0] * len(planes)
    current = planes
    for bit in range(divisor.bit_length()):
        if (constant >> bit) & 1:
            result = modular_add(m, result, current, divisor)
        current = modular_add(m, current, current, divisor)
    return result


def scalar_modular_sum(m, a, b, divisor):
    gap = m.sub(divisor, b)
    if m.ge(a, gap): return m.sub(a, gap)
    return m.add(a, b)


def scalar_modular_product(m, a, b, divisor):
    """At most bit_length(divisor) ordinary shift/add reduction steps."""
    result, current = 0, a
    for bit in range(divisor.bit_length()):
        if (b >> bit) & 1:
            result = scalar_modular_sum(m, result, current, divisor)
        current = scalar_modular_sum(m, current, current, divisor)
    return result


def divide_unsigned(value, divisor, width, mutation=None):
    """Exact (quotient, remainder, operation count), no multiplication/division."""
    need(type(divisor) is int and divisor >= 1, 'positive fixed divisor')
    need(type(value) is int and 0 <= value < (1 << width), 'unsigned input')
    m = Machine(width)
    if divisor == 1: return value, 0, m.operations
    bits = divisor.bit_length()
    if bits > width: return 0, value, m.operations
    planes = [value] + [0] * (bits - 1)
    length, power = 1, 2
    if power >= divisor: power -= divisor
    stages = 0
    while length < width:
        upper = [m.shr(x, length) for x in planes]
        weighted = modular_scale(m, upper, 1 if mutation == 'wrong_weight' else power, divisor)
        planes = modular_add(m, planes, weighted, divisor)
        power = scalar_modular_product(m, power, power, divisor)
        length <<= 1
        stages += 1
    before = planes if mutation == 'wrong_suffix' else [m.shr(x, 1) for x in planes]
    quotient = compare_constant(m, [value] + before, divisor)
    remainder = 0
    for bit, plane in enumerate(planes):
        remainder = m.bor(remainder, m.shl(m.band(plane, 1), bit))
    need(stages == (width - 1).bit_length(), 'stage count')
    need(m.operations <= 100 * (bits + 1) ** 2 * (stages + 1), 'operation upper bound')
    return quotient, remainder, m.operations


def divide_signed(value, divisor, width, rounding='floor'):
    """Signed-magnitude input; magnitude fits width bits. Rounding is explicit."""
    need(type(value) is int and abs(value) < (1 << width), 'signed magnitude')
    need(rounding in ('floor', 'toward_zero', 'nearest_even'), 'rounding mode')
    q, r, count = divide_unsigned(abs(value), divisor, width)
    negative = value < 0
    if rounding == 'floor':
        result = -q - (r != 0) if negative else q
    elif rounding == 'toward_zero':
        result = -q if negative else q
    else:
        # Fixed thresholds avoid forming 2*r, even at the word boundary.
        half = divisor >> 1
        half_fits = half < (1 << width)
        above = half_fits and r > half
        tie = half_fits and not (divisor & 1) and r == half
        result = q + (above or (tie and bool(q & 1)))
        if negative: result = -result
    return result, count + 10


def fixed_rational(value, numerator, denominator, input_bits, rounding='nearest_even'):
    """Fixed numerator/denominator, additive guard bits and explicit rounding."""
    need(type(numerator) is int, 'fixed integer numerator')
    need(type(denominator) is int and denominator >= 1, 'positive fixed denominator')
    need(type(value) is int and abs(value) < (1 << input_bits), 'input magnitude')
    width = max(input_bits + abs(numerator).bit_length() + 1,
                denominator.bit_length() + 1, 3)
    m = Machine(width)
    product = 0
    for bit in range(abs(numerator).bit_length()):
        if (abs(numerator) >> bit) & 1:
            product = m.add(product, m.shl(abs(value), bit))
    negative = (value < 0) != (numerator < 0)
    result, count = divide_signed(-product if negative else product, denominator, width, rounding)
    return result, count + m.operations, width
