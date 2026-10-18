"""Conditional commuting-factor budget; exact arithmetic, no supplier claim.
Philipp (@mightyOil), substantial OpenAI Codex assistance. Apache-2.0.
"""
from fractions import Fraction as F
from math import gcd, isqrt


def need(ok, message):
    if not ok:
        raise ValueError(message)


def clog(x):
    x = F(x)
    need(x > 0, 'positive logarithm')
    k = x.numerator.bit_length() - x.denominator.bit_length()
    return k + (x > F(2)**k)


def structure(n):
    need(type(n) is int and n >= 1, 'positive factor count')
    h = (n-1).bit_length()
    q = 1 << (n.bit_length()-1)
    return h, 3*q*n - 2*q*q, h+2


def execute(n, r, beta, G, D, W):
    need(all(type(x) in (int, F) for x in (r, beta, G, D))
         and r >= 1 and 0 < beta <= F(1, 2) and G >= 1 and D >= 0
         and type(W) is int and W >= 0, 'execution domain')
    h, N, C = structure(n)
    B, L = C*G, C*C*G
    a = 68*(r+1)/beta**5
    u = F(1, 1 << W)
    need(48*(clog(1/beta)+W.bit_length()+1)*u <= beta**3,
         'all-length admission')
    t = N*L*a*u
    need(t <= F(1, 2), 'feedback smallness')
    return dict(leaf_calls=N, dirty_arrays=h, coefficient_mass=C,
                prefix_bound=B, interval_bound=L, local_error=a,
                feedback=t, boundary_magnitude=2*B*D+1,
                error=2*t*(B*D+1),
                internal_magnitude=1024*(r+1)*(r+2)*(B*D+1)/beta**8)


def choose(n, r, beta, G, D, p, incoming):
    need(all(type(x) is int and x >= 0 for x in (p, incoming)), 'precision domain')
    need(all(type(x) in (int, F) for x in (r, beta, G, D))
         and r >= 1 and 0 < beta <= F(1, 2) and G >= 1 and D >= 0, 'budget domain')
    _, N, C = structure(n)
    B, L, a = C*G, C*C*G, 68*(r+1)/beta**5
    W = max(incoming, 4*clog(1/beta)+16,
            p+2+clog(N*L*a*(B*D+1)))
    row = execute(n, r, beta, G, D, W)
    row.update(working_bits=W, integer_bits=clog(row['internal_magnitude'])+2)
    need(row['error'] <= F(1, 1 << (p+1)), 'execution error target')
    return row


def prime_power(r):
    if type(r) is not int or r < 3:
        return False
    p = next((j for j in range(2, isqrt(r)+1) if r % j == 0), r)
    while r % p == 0:
        r //= p
    return r == 1


def uniform(r, p, m, incoming):
    need(prime_power(r), 'prime-power radix >= 3')
    need(all(type(x) is int and x >= 0 for x in (p, m, incoming)), 'precision domain')
    n = r-1
    h, N, C = structure(n)
    ell = clog(r)
    phi = sum(gcd(i, r) == 1 for i in range(1, r))
    d0 = 1+2*ell+r*n*phi
    a0 = 2*d0+r+2
    g = d0+ell+2*r+2
    e = max(d0+1, a0+1, p+2*a0+m+4)
    K, c = a0+2*r+ell, clog(C)
    J, H = K+c, K+2*c
    A = 5*g+clog(68*(r+1))
    W = max(incoming, 4*g+16, p+3+clog(N)+A+m+J+H)
    I = J+m+8*g+2*ell+16
    return dict(radix=r, target_bits=p, magnitude_bits=m, incoming_bits=incoming,
                factors=n, depth=h, leaf_calls=N, coefficient_mass=C, phi=phi,
                circle_exponent=d0, inverse_exponent=a0, margin_exponent=g,
                preparation_error_exponent=e, factor_bits=max(n*ell,e+r+3),
                subset_exponent=K, coefficient_exponent=c, prefix_exponent=J,
                interval_exponent=H, local_error_exponent=A,
                working_bits=W, integer_bits=I)
