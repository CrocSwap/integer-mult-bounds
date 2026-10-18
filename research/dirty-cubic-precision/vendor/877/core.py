"""Balanced dirty-word prefixes and exact execution-error budgets.

Gareth Davidson (@bitplane), substantial OpenAI Codex assistance; Apache-2.0.
See PROOF.md. No predecessor dispatcher is used in this module.
"""
from fractions import Fraction as Q
from functools import lru_cache


def need(ok, message):
    if not ok:
        raise ValueError(message)


@lru_cache(None)
def resources(n):
    need(type(n) is int and n >= 1, "positive integer factor count")
    if n == 1:
        return 0, 1, 1
    a, b = n//2, n-n//2
    ha, na, ea = resources(a)
    hb, nb, eb = resources(b)
    return 1+max(ha, hb), 2*(na+nb), n+max(a+eb, b+ea)


def word(n, sign=1, first=0, source=0, target=1, scratch=2):
    """Independent chronological word: (source, target, factor, sign)."""
    resources(n)
    need(type(sign) is int and sign in (-1, 1), "word sign")
    if n == 1:
        yield source, target, first, sign
        return
    a, b = n//2, n-n//2
    commands = [(a, first, source, scratch, 1),
                (b, first+a, scratch, target, 1),
                (a, first, source, scratch, -1),
                (b, first+a, scratch, target, -1)]
    if sign == -1:
        commands = [(m, j, s, t, -q) for m, j, s, t, q in reversed(commands)]
    for m, j, s, t, q in commands:
        yield from word(m, q, j, s, t, scratch+1)


def ceil_log2(value):
    value = Q(value)
    need(value > 0, "positive logarithm argument")
    power = value.numerator.bit_length()-value.denominator.bit_length()
    return power + (value > Q(2)**power)


def execution_parameters(n, K, a, D, bits):
    need(K >= 0 and a > 0 and D >= 0, "operator/error/magnitude bounds")
    need(type(bits) is int and bits >= 0, "fractional precision")
    _, calls, exponent = resources(n)
    B = (1+Q(K))**exponent
    delta = calls*B*B*Q(a)/2**bits
    need(delta <= Q(1, 2), "feedback smallness")
    magnitude = 2*B*D+1
    error = 2*delta*(B*D+1)
    return dict(calls=calls, exponent=exponent, prefix_bound=B,
                feedback=delta, magnitude_bound=magnitude, error_bound=error)


def working_bits(n, K, a, D, target_bits, input_bits=0):
    need(type(target_bits) is int and target_bits >= 0, "target bits")
    need(type(input_bits) is int and input_bits >= 0, "input grid")
    need(K >= 0 and a > 0 and D >= 0, "operator/error/magnitude bounds")
    _, calls, exponent = resources(n)
    B = (1+Q(K))**exponent
    bits = max(input_bits, 0, target_bits+ceil_log2(2*calls*B*B*a*(B*D+1)))
    result = execution_parameters(n, K, a, D, bits)
    need(result['error_bound'] <= Q(1, 2**target_bits), "execution target")
    return bits


def kernel_budget(radix, target_bits, magnitude_bits, inherited):
    """Integer exponents only; no exponentially large root-gap numbers."""
    need(type(magnitude_bits) is int and magnitude_bits >= 0, "magnitude bits")
    need(type(target_bits) is int and target_bits >= 1, "target bits")
    source = inherited.budgets(radix, target_bits+1+magnitude_bits)
    inherited.check(source)
    n, g = radix-1, source['g']
    scratch, calls, exponent = resources(n)
    A = 3*g+ceil_log2(13*(radix+1))
    H = g+ceil_log2(radix+1)
    w = max(A, 2*g+1, target_bits+3+ceil_log2(calls)+A+magnitude_bits+3*exponent*H)
    oldH = g+ceil_log2(radix+2)
    exact_count_old = max(A, 2*g+1, target_bits+2+ceil_log2(calls)+A+magnitude_bits+(calls-1)*oldH)
    return dict(radix=radix, target_bits=target_bits, initial_magnitude_bits=magnitude_bits,
                n=n, dirty_arrays=scratch, leaf_calls=calls, prefix_exponent=exponent,
                gap_bits=g, local_error_bits=A, shear_growth_bits=H,
                working_bits=w, old_exact_count_working_bits=exact_count_old,
                coefficient_target_bits=target_bits+1+magnitude_bits)


def check_kernel_budget(row, inherited):
    need(all(type(v) is int for v in row.values()), "integer budget fields")
    correct = kernel_budget(row['radix'], row['target_bits'], row['initial_magnitude_bits'], inherited)
    need(row == correct, "budget certificate mismatch")
    # Check the exponent inequality separately from certificate equality.
    n, E, N = row['n'], row['prefix_exponent'], row['leaf_calls']
    need(E <= 4*n-3, "linear prefix exponent")
    gap = row['working_bits']-row['target_bits']-3-row['local_error_bits']-row['initial_magnitude_bits']-3*E*row['shear_growth_bits']
    need(gap >= 0 and N <= 2**gap, "rounded execution inequality")
    need(row['working_bits'] >= 2*row['gap_bits']+1, "leaf closure precision")
    return True
