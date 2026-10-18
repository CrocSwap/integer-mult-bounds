"""Enclose the ideal phases and operators with rational intervals.

This checker does not use the production phase reduction, grid rotation,
finite differences, or Euclidean inverse program.
"""
from fractions import Fraction as F
from functools import lru_cache
from math import gcd


def outward(lo, hi, bits):
    scale = 1 << bits
    return F((lo*scale).__floor__(), scale), F((hi*scale).__ceil__(), scale)


def point(value):
    return F(value), F(value)


def plus(a, b, bits):
    return outward(a[0]+b[0], a[1]+b[1], bits)


def neg(a):
    return -a[1], -a[0]


def times(a, b, bits):
    values = (a[0]*b[0], a[0]*b[1], a[1]*b[0], a[1]*b[1])
    return outward(min(values), max(values), bits)


def scale(a, value, bits):
    return times(a, point(value), bits)


@lru_cache(maxsize=32)
def pi_interval(bits):
    def arctangent(denominator):
        total = F(0)
        power = denominator
        k = 0
        while True:
            total += (-1 if k % 2 else 1)*F(1, (2*k+1)*power)
            k += 1
            power *= denominator*denominator
            remainder = F(1, (2*k+1)*power)
            if remainder < F(1, 1 << (bits+8)):
                other = total+(-1 if k % 2 else 1)*remainder
                return min(total, other), max(total, other)
    a, b = arctangent(5), arctangent(239)
    return outward(16*a[0]-4*b[1], 16*a[1]-4*b[0], bits)


@lru_cache(maxsize=4096)
def phase(numerator, modulus, index, bits):
    residue = numerator*index*index % modulus
    if residue == 0:
        return point(1), point(0)
    angle = scale(pi_interval(bits), F(2*residue, modulus), bits)
    squared = times(angle, angle, bits)
    sine = sine_term = angle
    cosine = cosine_term = point(1)
    tail = F(7*7, 2)
    k = 1
    unit = F(1, 1 << bits)
    while True:
        sine_term = scale(times(sine_term, squared, bits), -F(1, 2*k*(2*k+1)), bits)
        cosine_term = scale(times(cosine_term, squared, bits), -F(1, (2*k-1)*2*k), bits)
        sine = plus(sine, sine_term, bits)
        cosine = plus(cosine, cosine_term, bits)
        tail *= F(49, (2*k+1)*(2*k+2))
        k += 1
        if tail < unit and k >= 4:
            sine_tail = tail*F(7, 2*k+1)
            return (outward(cosine[0]-tail, cosine[1]+tail, bits),
                    outward(sine[0]-sine_tail, sine[1]+sine_tail, bits))


def complex_point(value):
    return point(value[0]), point(value[1])


def complex_add(a, b, bits):
    return plus(a[0], b[0], bits), plus(a[1], b[1], bits)


def complex_mul(a, b, bits):
    return (plus(times(a[0], b[0], bits), neg(times(a[1], b[1], bits)), bits),
            plus(times(a[0], b[1], bits), times(a[1], b[0], bits), bits))


def rational_mul(a, b):
    return a[0]*b[0]-a[1]*b[1], a[0]*b[1]+a[1]*b[0]


def inverse(value):
    norm = value[0]*value[0]+value[1]*value[1]
    return value[0]/norm, -value[1]/norm


def cyclic(source, coefficient, stride, bits):
    length = len(source)
    cycle = length//gcd(length, stride)
    power = (F(1), F(0))
    for _ in range(cycle):
        power = rational_mul(power, coefficient)
    denominator_inverse = complex_point(inverse((1-power[0], -power[1])))
    result = []
    for i in range(length):
        total = complex_point((0, 0))
        power = (F(1), F(0))
        for j in range(cycle):
            total = complex_add(total, complex_mul(complex_point(power), source[(i-j*stride) % length], bits), bits)
            power = rational_mul(power, coefficient)
        result.append(complex_mul(total, denominator_inverse, bits))
    return result


def conjugate_input(source, numerator, modulus, bits):
    return [complex_mul((phase(numerator, modulus, i, bits)[0],
                         neg(phase(numerator, modulus, i, bits)[1])), complex_point(value), bits)
            for i, value in enumerate(source)]


def conjugate_output(source, numerator, modulus, bits):
    return [complex_mul(phase(numerator, modulus, i, bits), value, bits)
            for i, value in enumerate(source)]


def leaf(source, coefficient, stride, numerator, modulus, bits, multiplier=(F(1), F(0)), shift=0):
    transformed = conjugate_input(source, numerator, modulus, bits)
    solved = cyclic(transformed, coefficient, stride, bits)
    shifted = [complex_mul(complex_point(multiplier), solved[(i-shift) % len(source)], bits)
               for i in range(len(source))]
    return conjugate_output(shifted, numerator, modulus, bits)


def kernel(source, factors, tau, stride, numerator, modulus, bits):
    out = conjugate_input(source, numerator, modulus, bits)
    for inside, coefficient, factor_scale in factors:
        if inside:
            gauge = tau[0], -tau[1]
            b = rational_mul(coefficient, gauge)
            multiplier = gauge[0]*factor_scale, gauge[1]*factor_scale
            solved = cyclic(out, b, -stride, bits)
            out = [complex_mul(complex_point(multiplier), solved[(i+stride) % len(source)], bits)
                   for i in range(len(source))]
        else:
            b = rational_mul(coefficient, tau)
            multiplier = -coefficient[0]*factor_scale, -coefficient[1]*factor_scale
            out = [complex_mul(complex_point(multiplier), value, bits)
                   for value in cyclic(out, b, stride, bits)]
    return conjugate_output(out, numerator, modulus, bits)


def squared_distance_bound(actual, expected):
    return sum(max(abs(actual[i]-expected[i][0]), abs(actual[i]-expected[i][1]))**2 for i in range(2))


def polynomial(source, coefficients, stride, numerator, modulus, bits, tau):
    """Use exact Gaussian elimination for the polynomial matrix."""
    length = len(source)
    matrix = [[(F(0), F(0)) for _ in range(length)] for _ in range(length)]
    power = F(1), F(0)
    for j, coefficient in enumerate(coefficients):
        weight = rational_mul(coefficient, power)
        for i in range(length):
            column = (i-stride*j) % length
            old = matrix[i][column]
            matrix[i][column] = old[0]+weight[0], old[1]+weight[1]
        power = rational_mul(power, tau)
    rhs = conjugate_input(source, numerator, modulus, bits)
    for k in range(length):
        pivot = next(i for i in range(k, length) if matrix[i][k] != (0, 0))
        matrix[k], matrix[pivot] = matrix[pivot], matrix[k]
        rhs[k], rhs[pivot] = rhs[pivot], rhs[k]
        divisor = inverse(matrix[k][k])
        matrix[k] = [rational_mul(divisor, v) for v in matrix[k]]
        rhs[k] = complex_mul(complex_point(divisor), rhs[k], bits)
        for i in range(length):
            if i == k:
                continue
            weight = matrix[i][k]
            subtrahend = [rational_mul(weight, v) for v in matrix[k]]
            matrix[i] = [(v[0]-w[0], v[1]-w[1]) for v, w in zip(matrix[i], subtrahend)]
            rhs[i] = complex_add(rhs[i], complex_mul(complex_point((-weight[0], -weight[1])), rhs[k], bits), bits)
    return conjugate_output(rhs, numerator, modulus, bits)
