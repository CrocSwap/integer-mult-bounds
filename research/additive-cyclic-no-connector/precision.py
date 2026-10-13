"""Direct rational width selection, without a precision-sized search loop."""
from fractions import Fraction as F
from gaussian import G, rounded
from weighted import require
from gaussian import power


def ceil_log2(value):
    value = F(value)
    require(value > 0, 'positive logarithm argument')
    n, d = value.numerator, value.denominator
    exponent = n.bit_length()-d.bit_length()
    greater = n > (d << exponent) if exponent >= 0 else (n << -exponent) > d
    return exponent+int(greater)


def extra(value):
    return max(0, ceil_log2(value)) if value > 0 else 0


def round_polynomial(q, K, D, bits):
    k = len(q)-1
    width = max(bits, extra(2*K*k), bits+extra(2*K*K*k*D))
    delta, u = F(k, 1 << width), F(1, 1 << bits)
    require(K*delta <= F(1, 2) and 2*K*K*delta*D <= u, 'direct polynomial width')
    out = [G(1)]+[rounded(value, width) for value in q[1:]]
    actual = sum((v-w).modulus_upper() for v, w in zip(q, out))
    require(actual <= delta, 'actual polynomial rounding')
    return out, K/(1-K*delta), width, actual


def preparation(c, phases, bits, K, S, D, bounded_windows=True):
    require(bounded_windows, 'this bound charges rounded coefficient windows')
    k, length = len(c), len(phases)
    u = F(1, 1 << bits)
    coefficient = 4*(length-1)*S*S*k+length*S
    width = max(bits, extra(length), extra(2*(length-1)*S*k), extra(2*S*coefficient),
                bits+extra(4*S**3*coefficient*K*(D+u)))
    us = F(1, 1 << width)
    power_error = 2*(length-1)*S*S*k*us
    phase_error = length*us
    error = (1+phase_error)*power_error+phase_error*S
    require(phase_error <= 1 and (length-1)*S*k*us <= F(1, 2)
            and error <= 1/(2*S) and 4*S**3*error*K*(D+u) <= u,
            'direct closure width')
    phase = G(1)
    for value in phases:
        phase = rounded(value*phase, width)
    M = power(c, length, width)
    return [[phase*value for value in row] for row in M], error, width


def window_precision(q, K, S, D, bits):
    u = F(1, 1 << bits)
    R = len(q)-1+sum(j*v.upper() for j, v in enumerate(q))
    sensitivity = 2*K*K*(D+u)+8*S**3*K*(D+u)+8*S*S*u
    width = max(bits, extra(2*K*R), extra(2*S*R), bits+extra(R*sensitivity))
    error = R*F(1, 1 << width)
    require(K*error <= F(1, 2) and S*error <= F(1, 2) and error*sensitivity <= u,
            'direct recurrence-window width')
    return width, error


def gauge_precision(k, K, S, D, bits):
    u = F(1, 1 << bits)
    width = max(bits, extra(k), bits+extra(12*S*S*K*(D+u)*k))
    error = k*F(1, 1 << width)
    require(error <= 1 and 12*S*S*K*(D+u)*error <= u, 'direct gauge width')
    return width, error
