"""Precision bounds for the constant-coefficient PR985 word.

The common-operator hypotheses are mathematical inputs. See PROOF.md.
"""
from fractions import Fraction as F
from math import gcd, isqrt


def need(ok, label):
    if not ok:
        raise ValueError(label)


def ceil_log2(value):
    value = F(value)
    need(value > 0, 'positive logarithm')
    k = value.numerator.bit_length() - value.denominator.bit_length()
    return k + (value > F(2)**k)


def prime_power(r):
    if type(r) is not int or r < 3:
        return False
    p = next((d for d in range(2, isqrt(r)+1) if r % d == 0), r)
    while r % p == 0:
        r //= p
    return r == 1


def resources(count):
    need(type(count) is int and count >= 1, 'positive factor count')
    h = (count-1).bit_length()
    q = 1 << (count.bit_length()-1)
    return h, 3*q*count-2*q*q, 2*3**h


def execution(count, scale, beta, subset_bound, initial_bound, bits):
    """Bound both signs of the complete rounded dirty word."""
    need(type(bits) is int and bits >= 0 and scale >= 1
         and 0 < beta <= F(1, 2) and subset_bound >= 1
         and initial_bound >= 0, 'execution domain')
    h, calls, mass = resources(count)
    prefix = mass*subset_bound
    local = 68*(scale+1)/beta**5
    unit = F(1, 1 << bits)
    g = ceil_log2(1/beta)
    active = g+bits.bit_length()
    need(48*(active+1)*unit <= beta**3, 'all-length admission')
    feedback = calls*prefix**2*local*unit
    need(feedback <= F(1, 2), 'feedback smallness')
    boundary = 2*prefix*initial_bound+1
    peak = 1024*(scale+1)*(scale+2)*(prefix*initial_bound+1)/beta**8
    return dict(leaf_calls=calls, dirty_arrays=h, prefix_bound=prefix,
                effective_depth=active, local_error_coefficient=local,
                feedback=feedback, boundary_magnitude=boundary,
                internal_magnitude=peak,
                error=2*feedback*(prefix*initial_bound+1))


def choose(count, scale, beta, subset_bound, initial_bound, target_bits, incoming_bits):
    """Choose sufficient precision without a length or stride input."""
    need(all(type(v) is int and v >= 0 for v in (target_bits, incoming_bits)),
         'integer precision')
    need(scale >= 1 and 0 < beta <= F(1, 2) and subset_bound >= 1
         and initial_bound >= 0, 'budget domain')
    _, calls, mass = resources(count)
    prefix = mass*subset_bound
    local = 68*(scale+1)/beta**5
    bits = max(incoming_bits, 4*ceil_log2(1/beta)+16,
               target_bits+2+ceil_log2(calls*prefix**2*local*(prefix*initial_bound+1)))
    result = execution(count, scale, beta, subset_bound, initial_bound, bits)
    need(result['error'] <= F(1, 1 << (target_bits+1)), 'execution target')
    result['working_bits'] = bits
    result['integer_bits'] = ceil_log2(result['internal_magnitude'])+2
    return result


def uniform(r, target_bits, magnitude_bits, incoming_bits):
    """Use the inherited prime-power preparation bounds as exponents."""
    need(prime_power(r), 'prime-power radix >=3')
    need(all(type(v) is int and v >= 0 for v in
             (target_bits, magnitude_bits, incoming_bits)), 'integer precision')
    n = r-1
    h, calls, mass = resources(n)
    ell = (r-1).bit_length()
    phi = sum(gcd(j, r) == 1 for j in range(1, r))
    d0 = 1+2*ell+r*n*phi
    a0 = 2*d0+r+2
    g = d0+ell+2*r+2
    e = max(d0+1, a0+1, target_bits+2*a0+magnitude_bits+4)
    factor_bits = max(n*ell, e+r+3)
    prefix = a0+2*r+ell+1+2*h
    local = 5*g+ceil_log2(68*(r+1))
    bits = max(incoming_bits, 4*g+16,
               target_bits+3+ceil_log2(calls)+local+magnitude_bits+3*prefix)
    integer = prefix+magnitude_bits+8*g+2*ell+16
    return dict(radix=r, target_bits=target_bits, magnitude_bits=magnitude_bits,
                incoming_bits=incoming_bits, factors=n, depth=h, leaf_calls=calls,
                coefficient_mass=mass, phi=phi, circle_exponent=d0,
                inverse_exponent=a0, margin_exponent=g,
                preparation_error_exponent=e, factor_bits=factor_bits,
                prefix_exponent=prefix, local_error_exponent=local,
                working_bits=bits, integer_bits=integer)


def check_uniform(row):
    """Check a supplied exponent certificate with exact integer bounds."""
    need(all(type(v) is int for v in row.values()), 'integer certificate')
    r, p, m, incoming = (row[k] for k in
                         ('radix', 'target_bits', 'magnitude_bits', 'incoming_bits'))
    need(row == uniform(r, p, m, incoming), 'certificate fields')
    w, g, j, a, calls = (row[k] for k in
                          ('working_bits', 'margin_exponent', 'prefix_exponent',
                           'local_error_exponent', 'leaf_calls'))
    need(w >= incoming and w >= 4*g+16, 'input grid and all-length admission')
    exponent = w-p-m-3*j-a-3
    need(exponent >= 0 and calls <= 1 << exponent, 'execution exponent')
    need(w <= max(p, incoming)+m+18*r**3, 'fractional cubic bound')
    need(row['integer_bits'] <= m+15*r**3, 'integer cubic bound')
    need(row['factor_bits'] <= p+m+7*r**3, 'preparation cubic bound')
