"""Complement-polynomial control of every rounded inverse prefix."""
from fractions import Fraction as F
from math import gcd, isqrt


def need(ok, label):
    if not ok: raise ValueError(label)


def ceil_log2(n):
    need(type(n) is int and n > 0, 'positive integer')
    return (n-1).bit_length()


def prime_power(r):
    if type(r) is not int or r < 3: return False
    p = next((d for d in range(2, isqrt(r)+1) if r % d == 0), r)
    value = r
    while value % p == 0: value //= p
    return value == 1


def uniform(r, target_bits, coarse_bits, magnitude_bits=0):
    """All-size exponent budgets; no enormous powers of two are built.

    Source norm is <=2^magnitude_bits. Prior analytic inputs: PR621 circle
    bound and Fourier inverse bound, and PR628 approximate factorization.
    """
    need(prime_power(r), 'prime-power radix >=3')
    need(type(target_bits) is int and target_bits >= 1, 'target precision')
    need(type(coarse_bits) is int and coarse_bits >= 0, 'coarse precision')
    need(type(magnitude_bits) is int and magnitude_bits >= 0, 'magnitude precision')
    n = r-1
    phi = sum(gcd(j, r) == 1 for j in range(1, r))
    ell, c = ceil_log2(r), ceil_log2(n)
    d = 1+2*ell+r*n*phi
    a = 2*d+r+2
    g = d+ell+2*r+2
    h = a+2*r
    e = max(d+1, a+1, target_bits+2*a+magnitude_bits+3)
    factor_bits = max(n*ell, e+r+3)
    j = c+2*h+3*g+ell+magnitude_bits+5
    v = 3*r+ell
    w = j+max(target_bits+2, coarse_bits+v+3)
    # The old all-size working budget, for comparison at D<=1 and no
    # coarse restoration requirement. This is not a matched contract.
    old = max(2*g+ceil_log2(14*n),
              target_bits+(n+2)*g+ceil_log2(28*n*(r+1)))
    return dict(radix=r, n=n, phi=phi, ell=ell, c=c, circle_exponent=d,
                full_inverse_exponent=a, margin_exponent=g,
                partial_inverse_exponent=h, coefficient_error_exponent=e,
                factor_bits=factor_bits, execution_error_exponent=j,
                forward_product_exponent=v, working_bits=w,
                target_bits=target_bits, coarse_bits=coarse_bits,
                magnitude_bits=magnitude_bits, old_neighbor_working_bits=old)


def prefix_error(n, beta, scale, bound, qnorm, inverse_bound, bits):
    """inverse_bound certifies ||Q(U)^-1|| for a shared isometry U.

    Q = scale^-1 product_j(z-rho_j), n is its degree. B bounds every
    subproduct inverse, including the identity. This avoids multiplying
    beta^-1 once per factor when propagating rounding errors.
    """
    need(n > 0 and 0 < beta <= 1 and scale > 0 and bound >= 0, 'prefix parameters')
    need(qnorm > 0 and inverse_bound > 0, 'norm certificates')
    u = F(1, 1 << bits)
    need(u <= beta*beta/2, 'closure precision')
    B = max(F(1), (1 << n)*qnorm*inverse_bound)
    t = n*B*7*u/beta**3
    need(t < 1, 'prefix contraction')
    error = t*(scale*B*bound+1)/(1-t)
    return error, B, t


def recovery_bound(error, factors, scale, bits):
    u = F(1, 1 << bits)
    result = error
    for rho, _, _, _ in reversed(factors):
        result = (1+abs(rho[0])+abs(rho[1]))*result+u
    return result/scale+u


def choose(factors, scale, bound, qnorm, inverse_bound, coarse_bits, target_bits):
    need(factors, 'nonempty factors')
    phase, direction = factors[0][2:]
    need(all(f[2] is phase and f[3] == direction for f in factors), 'shared shift required')
    beta = min(f[1] for f in factors)
    bits = max(coarse_bits, target_bits)
    while True:
        try:
            error, B, t = prefix_error(len(factors), beta, scale, bound, qnorm, inverse_bound, bits)
        except ValueError as exc:
            if str(exc) not in ('closure precision', 'prefix contraction'): raise
            bits += 1
            continue
        recovery = recovery_bound(error, factors, scale, bits)
        if error <= F(1, 1 << target_bits) and recovery < F(1, 1 << (coarse_bits+1)):
            return bits, error, recovery, B, t
        bits += 1
