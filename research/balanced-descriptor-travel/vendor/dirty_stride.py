"""Add a cyclic inverse to a target and restore the source exactly.

This is a fixed-grid arithmetic model with two data tapes. Every data access
pays its head movement. See PROOF.md for the complete bill.
"""
from dataclasses import dataclass, field
from fractions import Fraction as F
from math import gcd

ZERO = (F(0), F(0))
ONE = (F(1), F(0))


def need(ok, message):
    if not ok:
        raise ValueError(message)


def add(a, b):
    return (a[0] + b[0], a[1] + b[1])


def sub(a, b):
    return (a[0] - b[0], a[1] - b[1])


def mul(a, b):
    return (a[0]*b[0] - a[1]*b[1], a[0]*b[1] + a[1]*b[0])


def norm2(a):
    return a[0]*a[0] + a[1]*a[1]


def div(a, b):
    d = norm2(b)
    need(d != 0, 'zero divisor')
    v = mul(a, (b[0], -b[1]))
    return (v[0]/d, v[1]/d)


def rnd(a, bits):
    """Use nearest dyadic rounding, with ties toward positive infinity."""
    scale = 1 << bits
    def component(v):
        t = v*scale + F(1, 2)
        return F(t.numerator // t.denominator, scale)
    return (component(a[0]), component(a[1]))


def trunc(a, bits):
    """Truncate each component toward zero. This cannot increase the norm."""
    scale = 1 << bits
    return tuple(F(int(v*scale), scale) for v in a)


@dataclass
class Meter:
    reads: int = 0
    writes: int = 0
    tape_moves: int = 0
    products: int = 0
    power_products: int = 0
    divisions: int = 0
    nodes: int = 0
    leaves: int = 0
    validation_reads: int = 0
    max_depth: int = 0
    heads: dict = field(default_factory=dict)
    layout: dict = field(default_factory=dict)

    def access(self, data, index, write=False):
        tape, start = self.layout[id(data)]
        position = start+index
        self.tape_moves += abs(position - self.heads.get(tape, 0)) + 1
        self.heads[tape] = position
        if write:
            self.writes += 1
        else:
            self.reads += 1

    def rewind(self):
        for tape, position in self.heads.items():
            self.tape_moves += position
            self.heads[tape] = 0


@dataclass(frozen=True)
class View:
    data: list
    start: int
    step: int
    length: int
    meter: Meter

    def index(self, i):
        need(0 <= i < self.length, 'view index')
        return (self.start + self.step*i) % len(self.data)

    def get(self, i):
        j = self.index(i)
        self.meter.access(self.data, j)
        return self.data[j]

    def put(self, i, value):
        j = self.index(i)
        self.meter.access(self.data, j, True)
        self.data[j] = value

    def part(self, first, length):
        need(0 <= first and first + length <= self.length, 'view interval')
        return View(self.data, self.start + self.step*first, self.step, length, self.meter)

    def reverse(self):
        return View(self.data, self.start + self.step*(self.length-1),
                    -self.step, self.length, self.meter)


def depth(length, stride):
    count = 0
    while True:
        stride %= length
        stride = min(stride, length-stride)
        if stride == 0:
            return count
        length, stride = stride, (-length) % stride
        count += 1


def admitted(beta, bits, levels):
    return (type(bits) is int and bits >= 0 and 0 < beta <= F(1, 2)
            and 48*(levels+1)*F(1, 1 << bits) <= beta**3)


def power(b, exponent, bits, meter):
    """Use a left-to-right binary product and scalar working storage."""
    need(exponent >= 1, 'positive exponent')
    result = b
    for k in range(exponent.bit_length()-2, -1, -1):
        result = trunc(mul(result, result), bits)
        meter.power_products += 1
        if (exponent >> k) & 1:
            result = trunc(mul(result, b), bits)
            meter.power_products += 1
    return result


@dataclass(frozen=True)
class Geometry:
    root: tuple
    divisor: int
    cycle: int
    inverse: int
    bits: int
    meter: Meter

    def exponents(self, length, stride, orientation):
        if stride == 0:
            return (self.cycle, self.cycle)
        def exponent(displacement):
            need(displacement % self.divisor == 0, 'cycle lattice')
            return ((displacement // self.divisor)*self.inverse) % self.cycle or self.cycle
        return (exponent(orientation*stride), exponent(orientation*(stride-length)))

    def coefficients(self, length, stride, orientation):
        a, b = self.exponents(length, stride, orientation)
        left = power(self.root, a, self.bits, self.meter)
        right = left if a == b else power(self.root, b, self.bits, self.meter)
        return (left, right)


def emit(target, i, value, multiplier, sign, bits):
    if multiplier != ONE:
        target.meter.products += 1
        value = rnd(mul(multiplier, value), bits)
    old = target.get(i)
    target.put(i, add(old, value) if sign == 1 else sub(old, value))


def swap(source, target):
    for i in range(source.length):
        left, right = source.get(i), target.get(i)
        source.put(i, right)
        target.put(i, left)


def causal(source, carrier, stride, geometry, undo=False):
    """Apply the causal lifts with block swaps; restore the dirty carrier."""
    a, _ = geometry.coefficients(source.length, stride, source.step)
    n = source.length
    if undo:
        swap(source, carrier)
        for first in range(((n-1)//stride)*stride, -1, -stride):
            size = min(stride, n-first)
            swap(source.part(first, size), carrier.part(first, size))
            if first:
                for i in range(first+size-1, first-1, -1):
                    value = rnd(mul(a, carrier.get(i-stride)), geometry.bits)
                    geometry.meter.products += 1
                    source.put(i, sub(source.get(i), value))
    else:
        for first in range(0, n, stride):
            size = min(stride, n-first)
            if first:
                for i in range(first, first+size):
                    value = rnd(mul(a, carrier.get(i-stride)), geometry.bits)
                    geometry.meter.products += 1
                    source.put(i, add(source.get(i), value))
            swap(source.part(first, size), carrier.part(first, size))
        swap(source, carrier)


def expand(source, target, stride, geometry, multiplier, sign):
    """Conjugate the seed injection by exact inverse causal grid maps."""
    causal(target, source, stride, geometry, undo=True)
    _, b = geometry.coefficients(source.length, stride, source.step)
    coefficient = mul(multiplier, b)
    geometry.meter.products += 1
    for i in range(stride):
        value = rnd(mul(coefficient, source.get(i)), geometry.bits)
        geometry.meter.products += 1
        emit(target, i, value, ONE, sign, geometry.bits)
    causal(target, source, stride, geometry)


def closure(source, target, stride, geometry, sign, level):
    """Move the child target to the other tape and restore the carrier."""
    borrowed = source.part(0, stride)
    carrier = target.part(0, stride)
    ends = source.part(source.length-stride, stride)
    swap(borrowed, carrier)
    solve(ends, carrier, (-source.length) % stride, geometry, sign=sign, level=level+1)
    swap(borrowed, carrier)


def diagonal(source, target, geometry, multiplier, sign):
    coefficient = power(geometry.root, geometry.cycle, geometry.bits, geometry.meter)
    denominator = sub(ONE, coefficient)
    for i in range(source.length):
        value = rnd(div(source.get(i), denominator), geometry.bits)
        geometry.meter.divisions += 1
        emit(target, i, value, multiplier, sign, geometry.bits)


def solve(source, target, stride, geometry, multiplier=ONE, sign=1, level=0):
    """Use integer metadata at each level; scalar temporaries stay in helpers."""
    length = source.length
    stride %= length
    if 2*stride > length:
        source, target, stride = source.reverse(), target.reverse(), length-stride
    geometry.meter.nodes += 1
    geometry.meter.max_depth = max(geometry.meter.max_depth, level)
    if stride == 0:
        diagonal(source, target, geometry, multiplier, sign)
        return
    causal(source, target, stride, geometry)
    if sign == 1:
        for i in range(length):
            emit(target, i, source.get(i), multiplier, 1, geometry.bits)
        closure(source, target, stride, geometry, 1, level)
        expand(source, target, stride, geometry, multiplier, 1)
        closure(source, target, stride, geometry, -1, level)
        expand(source, target, stride, geometry, multiplier, -1)
    else:
        expand(source, target, stride, geometry, multiplier, 1)
        closure(source, target, stride, geometry, 1, level)
        expand(source, target, stride, geometry, multiplier, -1)
        closure(source, target, stride, geometry, -1, level)
        for i in range(length):
            emit(target, i, source.get(i), multiplier, -1, geometry.bits)
    causal(source, target, stride, geometry, undo=True)


def lift(x, y, b, beta, bits, stride, sign=1, multiplier=ONE, shift=0, meter=None):
    """Add multiplier*(I-b Z^stride)^-1 x at output indices i+shift."""
    need(type(stride) is int and type(shift) is int and type(sign) is int
         and sign in (-1, 1), 'integer stride and sign')
    need(x is not y and len(x) == len(y) and len(x) > 0, 'distinct equal arrays')
    need(shift % len(x) in (0, stride % len(x)), 'output shift must be zero or the leaf stride')
    need(isinstance(b, tuple) and len(b) == 2 and norm2(b) <= (1-beta)**2, 'stable constant coefficient')
    need(isinstance(multiplier, tuple) and len(multiplier) == 2, 'constant multiplier')
    need(admitted(beta, bits, depth(len(x), stride)), 'precision admission')
    meter = meter if meter is not None else Meter()
    if not meter.layout:
        meter.layout = {id(x): (0, 0), id(y): (1, 0)}
    need(id(x) in meter.layout and id(y) in meter.layout
         and {meter.layout[id(x)][0], meter.layout[id(y)][0]} == {0, 1}, 'two distinct data tapes')
    for data in (x, y):
        for i in range(len(data)):
            meter.access(data, i)
            meter.validation_reads += 1
            value = data[i]
            need(rnd(value, bits) == value, 'fixed grid data')
    divisor = gcd(len(x), stride)
    cycle = len(x)//divisor
    inverse = pow((stride//divisor) % cycle, -1, cycle) if cycle > 1 else 0
    geometry = Geometry(b, divisor, cycle, inverse, bits, meter)
    solve(View(x, 0, 1, len(x), meter), View(y, shift, 1, len(y), meter),
          stride, geometry, multiplier, sign)
    meter.leaves += 1
    meter.rewind()
    return meter


def leaf_bound(bound, beta, bits, multiplier_bound=1):
    return (64*multiplier_bound*(bound+1)/beta**5 + 3)*F(1, 1 << bits)


def leaf_calls(count):
    need(type(count) is int and count >= 1, 'positive factor count')
    if count == 1:
        return 1
    return 2*leaf_calls(count//2) + 2*leaf_calls(count-count//2)


def compose(x, y, factors, scratch, tau, beta, bits, stride, sign=1, meter=None):
    """Use PR628's balanced dirty commutator with the new arbitrary-stride leaf."""
    need(factors and len(scratch) >= (len(factors)-1).bit_length(), 'dirty depth')
    arrays = [x, y] + scratch
    need(len({id(a) for a in arrays}) == len(arrays), 'all arrays distinct')
    need(len(x) > 0 and all(len(a) == len(x) for a in arrays), 'array lengths')
    need(isinstance(tau, tuple) and norm2(tau) == 1, 'immutable unit gauge')
    need(type(sign) is int and sign in (-1, 1) and type(stride) is int, 'integer stride and sign')
    need(admitted(beta, bits, depth(len(x), stride)), 'precision admission')
    for factor in factors:
        need(isinstance(factor, tuple) and len(factor) == 3, 'factor descriptor')
        inside, b, scale = factor
        need(type(inside) is bool and isinstance(b, tuple) and len(b) == 2
             and norm2(b) <= (1-beta)**2 and isinstance(scale, (int, F)), 'stable factor descriptor')
    meter = meter if meter is not None else Meter()
    if scratch:
        layout = {id(a): (0, i*len(x)) for i, a in enumerate(arrays[:-1])}
        layout[id(scratch[-1])] = (1, 0)
    else:
        layout = {id(x): (0, 0), id(y): (1, 0)}
    need(not meter.layout or meter.layout == layout, 'kernel tape layout')
    meter.layout = layout
    for data in arrays:
        for i in range(len(data)):
            meter.access(data, i)
            meter.validation_reads += 1
            value = data[i]
            need(rnd(value, bits) == value, 'fixed grid data')
    def run(src, dst, lo, hi, level, direction):
        if hi-lo == 1:
            inside, b, scale = factors[lo]
            phase = (tau[0], -tau[1]) if inside else tau
            coefficient = mul(b, phase)
            m = phase if inside else (-b[0], -b[1])
            m = (m[0]*scale, m[1]*scale)
            if meter.layout[id(src)][0] == meter.layout[id(dst)][0]:
                spare = scratch[-1]
                destination = View(dst, 0, 1, len(dst), meter)
                carrier = View(spare, 0, 1, len(spare), meter)
                swap(destination, carrier)
                lift(src, spare, coefficient, beta, bits, -stride if inside else stride,
                     direction, m, -stride if inside else 0, meter)
                swap(destination, carrier)
            else:
                lift(src, dst, coefficient, beta, bits, -stride if inside else stride,
                     direction, m, -stride if inside else 0, meter)
            return
        mid = (lo+hi)//2
        z = scratch[level]
        if direction == 1:
            run(src, z, lo, mid, level+1, 1)
            run(z, dst, mid, hi, level+1, 1)
            run(src, z, lo, mid, level+1, -1)
            run(z, dst, mid, hi, level+1, -1)
        else:
            run(z, dst, mid, hi, level+1, 1)
            run(src, z, lo, mid, level+1, 1)
            run(z, dst, mid, hi, level+1, -1)
            run(src, z, lo, mid, level+1, -1)
    run(x, y, 0, len(factors), 0, sign)
    meter.rewind()
    return meter


def ceil_log2(value):
    value = F(value)
    need(value > 0, 'positive logarithm')
    k = value.numerator.bit_length() - value.denominator.bit_length()
    power_of_two = F(2)**k
    return k if value <= power_of_two else k+1


def execution_bound(count, r, beta, initial_bound, bits):
    need(r >= 1 and initial_bound >= 0 and 0 < beta <= F(1, 2)
         and type(bits) is int and bits >= 0, 'execution budget domain')
    calls = leaf_calls(count)
    a = 68*(r+1)/beta**5
    growth = 2+F(r)/beta
    need(a*F(1, 1 << bits) <= 1, 'execution precision')
    return calls*a*(initial_bound+1)*F(1, 1 << bits)*growth**(calls-1)


def working_bits(count, r, beta, initial_bound, target_bits, incoming_bits, length, stride):
    need(r >= 1 and initial_bound >= 0 and 0 < beta <= F(1, 2)
         and type(target_bits) is int and target_bits >= 0
         and type(incoming_bits) is int and incoming_bits >= 0
         and type(length) is int and length > 0 and type(stride) is int, 'working budget domain')
    calls = leaf_calls(count)
    a = 68*(r+1)/beta**5
    growth = 2+F(r)/beta
    levels = depth(length, stride)
    return max(incoming_bits, target_bits+1+ceil_log2(calls*a*(initial_bound+1))
               +(calls-1)*ceil_log2(growth), ceil_log2(a),
               ceil_log2(48*(levels+1)/beta**3))
