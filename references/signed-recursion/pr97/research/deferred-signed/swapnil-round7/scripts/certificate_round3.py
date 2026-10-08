"""Exact rational certificate for the round-3 combinations.

Our stack (A, B, C, D, E) with separate bit and complex savings. Costs are powers of
L = log2 T ~ log n, with precision p = Theta(L^(1+x)), d = Theta(L^eps), l = Theta(L^(1-eps)).

Guard modes:
  'pathwise' uses the pathwise depth exponent C1 = 6/5 - beta/5 + zeta, which depends on a
             path-topology claim of the batched complex recursion.
  'crude'    needs no topology claim. Every child call of the batched recursion acts on at most
             (m-1)/m of its parent's axes (bulk children have a1 f <= (m-2h)e/m), and a node has at
             most s_c children in sequence, so the coefficient dependency depth satisfies
             A(e) <= E + s_c A((m-1)e/m), with leaves costing 8e < 8 d^beta. Over at most
             m(1-beta) ln d + 1 levels this gives A <= 2(E + 8 d^beta) s_c^(1 + m(1-beta) ln d), a fixed
             exponent at most m_c ln s_c + beta, covered by C1 = 1 + ceil(m_c ln s_c) + 1. Idea D then
             takes x with eps C1 < 1 + x. The exponent is huge but fixed, so the O() statement holds.
             With such an x, the record-regime hypothesis r >= 2^(p^mu) needs a fixed mu below
             (1-eps)/(1+x), which is tiny but fixed.
"""
from fractions import Fraction as Q
import math

GL = Q(1, 10**16)             # strict gaps tau < lambda < lambda'


def crude_c1(m_c, s_c):
    # upper bound 1 + m_c * ln(s_c), rounded up to an integer
    return Q(1 + math.ceil(m_c * math.log(s_c)) + 1)


def evaluate(a_b, a_c, beta, guard='pathwise', m_c=21952, s_c=45772350635112192, zeta=Q(1, 10**4)):
    tau, sigma = 1 - a_b, 1 - a_c
    chi = tau + (1 - beta) * max(sigma - tau, 0)
    leaf = sigma + beta * (1 - sigma)
    lam = max(tau, sigma, chi) + GL
    lamp = max(lam, leaf) + GL
    eps = Q(int(1 / (2 - lamp) * 10**16) - 1, 10**16)       # reservations force eps < 1/(2-lambda')
    c1 = (Q(6, 5) - beta / 5 + zeta) if guard == 'pathwise' else crude_c1(m_c, s_c)
    x = max(Q(3), math.ceil(eps * c1) + 1)                   # Idea D: any fixed x with eps C1 < 1 + x
    y = eps
    delta = Q(1, 10**22) / max(1, x)
    poly = (1 + x) * delta
    top = min(eps * (1 - lamp), 1 - eps - poly, max(eps, 1 - eps) * (1 - tau))
    kappa = Q(int(top * 10**17) - 1, 10**17)
    cons = {
        'lambda above tau, sigma, chi': lam - max(tau, sigma, chi),
        'lambda_prime above lambda and leaf': lamp - max(lam, leaf),
        'lambda_prime below one': 1 - lamp,
        'beta in (0,1)': min(beta, 1 - beta),
        'guard: eps C1 < 1 + x': 1 + x - eps * c1,
        'precision: 2 eps + y < 1 + x': 1 + x - 2 * eps - y,
        'sub-block coupling: y >= eps': Q(1) if y >= eps else Q(-1),
        'reservations: (2eps-1)/eps < lambda_prime': lamp - (2 * eps - 1) / eps,
        'record regime and primes: eps < 1': 1 - eps,
        'delta in (0, 1/8)': min(delta, Q(1, 8) - delta),
    }
    margins = {
        'prefix moves and top individual round': 1 - eps,
        'simultaneous butterflies': eps * (1 - lamp),
        'fine-bit exposures (A)': 1 - eps - poly,
        'Gaussian maps (B)': 1 - eps - poly,
        'chirps, twists, scalar products': 1 - eps - poly,
        'packed polynomial products': eps,
        'individually processed reserved axes': 1 - eps - poly,
        'CRT axis reversal (E)': max(eps, 1 - eps) * (1 - tau),
    }
    bad = [k for k, v in cons.items() if v <= 0]
    g = min(margins.values())
    return dict(ok=not bad and g > kappa, bad=bad, kappa=kappa, eps=eps, x=x, c1=c1,
                binding=min(margins, key=margins.get), gap=g - kappa)


SCENARIOS = [
    ('PR #10 networks', Q(246, 10**9), Q(7, 10**7)),
    ('PR #10 complex, our bit producer', Q(252, 10**9), Q(7, 10**7)),
    ('batched two-stage bit, PR #10 complex', Q(22157, 5 * 10**9), Q(7, 10**7)),
    # headline: PR #7 complex network fully batched (PR #15), rebuilt by independent/complex-network/fullbatch_*.py
    ('batched two-stage bit, fully batched PR #7 complex', Q(22157, 5 * 10**9), Q(1048009, 25 * 10**10)),
]

if __name__ == '__main__':
    for name, ab, ac in SCENARIOS:
        for guard in ('pathwise', 'crude'):
            r = evaluate(ab, ac, Q(1, 1000), guard)
            print('%-40s %-8s ok=%s kappa=%.6e (2^%.2f) C1=%s x=%s binding=%s %s' % (
                name, guard, r['ok'], float(r['kappa']), math.log2(float(r['kappa'])),
                r['c1'] if guard == 'pathwise' else int(r['c1']), r['x'], r['binding'], r['bad']))
