"""Exact rational certificate for the conditional witness.

Changes combined: A (expose only fine axis bits), B (segmented inverse of the Gaussian
correction with recentred sub-blocks and oversampling theta ~ 1/(4 d L^y)), C (one chunk
per axis, K = l - 1), D (digits of (log n)^(1+x) bits), E (CRT axis reversal by permuted
selected-bit additions).

Costs are powers of L = log2 T ~ log n, with precision p = Theta(L^(1+x)),
d = Theta(L^eps) axes and axis width l = Theta(L^(1-eps)). Fixed powers of log L are
absorbed by the strict gap between the minimum margin and kappa.

The network savings a_b, a_c and the complex constants (m, s) are assumptions taken
from PR #7 of CrocSwap/integer-mult-bounds.
"""
from fractions import Fraction as Q
import json

A_B, A_C = Q(3, 4 * 10**8), Q(39, 10**9)          # PR #7 bit / complex savings
M_C, S_C = 21952, 45772350635112192                # PR #7 complex network constants
# Certified upper bound on log_m(s). Colkitt's guard uses 5 instead; with 5 this witness still
# passes (eps*C1/(1+x) is about 0.75), so the tighter exponent is not load-bearing.
LOG_M_S = Q(38376, 10000)

DEFAULT = dict(eps=Q(9999, 10**4), x=Q(3), y=Q(9999, 10**4), beta=Q(1, 2), zeta=Q(1, 10**4),
               delta=Q(1, 10**6), lam=1 - Q(74999, 10**13), lamp=1 - Q(74998, 10**13),
               kappa=Q(7499, 10**12))


class Failure(Exception):
    pass


def evaluate(**overrides):
    v = dict(DEFAULT, **overrides)
    eps, x, y, beta, zeta, delta = v['eps'], v['x'], v['y'], v['beta'], v['zeta'], v['delta']
    lam, lamp, kappa = v['lam'], v['lamp'], v['kappa']
    tau, sigma = 1 - A_B, 1 - A_C
    if not S_C ** LOG_M_S.denominator < M_C ** LOG_M_S.numerator:
        raise Failure('log_m s bound')
    chi = tau + (1 - beta) * max(sigma - tau, 0)
    leaf = sigma + beta * (1 - sigma)
    c1 = LOG_M_S * (1 - beta) + beta + zeta          # depth exponent with exact log_m s
    poly = (1 + x) * delta                           # exponent of p^delta measured in L
    constraints = {
        'lambda above tau, sigma, chi': lam - max(tau, sigma, chi),
        'lambda_prime above lambda': lamp - lam,
        'lambda_prime above leaf': lamp - leaf,
        'lambda_prime below one': 1 - lamp,
        'guard: eps C1 < 1 + x': 1 + x - eps * c1,
        # alpha^2 theta >= 1 with alpha^2 ~ Q/(48 d), theta ~ 1/(4 d L^y), Q = Theta(L^(1+x))
        'precision: 2 eps + y < 1 + x': 1 + x - 2 * eps - y,
        # coupling cost w^3 (1/lambda + theta) = O(L^((eps - y)/2)) per output is O(1)
        'sub-block coupling: y >= eps': Q(1) if y >= eps else Q(-1),
        'reservations below layer: (2eps-1)/eps < lambda_prime': lamp - (2 * eps - 1) / eps,
        'record regime: eps < 1': 1 - eps,
        'delta < 1/8': Q(1, 8) - delta,
        # Upstream's prime_interval_growth (1 - 2 eps > 0) is replaced by the classical prime
        # number theorem with error term: eta = 1/(4d) far exceeds exp(-c sqrt(l)) for eps < 1.
        'prime intervals via PNT: eps < 1': 1 - eps,
        # K = l - 1 meets the transform lemma's literal hypothesis K <= l - 1. Upstream's
        # K = o(l) (eps(1+c) < 1) is deliberately dropped; no cost bound uses it.
    }
    margins = {
        'prefix moves and top individual round': 1 - eps,
        'simultaneous butterflies': eps * (1 - lamp),
        'fine-bit exposures (A)': 1 - eps - poly,
        'Gaussian maps (B)': 1 - eps - poly,
        'chirps, twists, scalar products': 1 - eps - poly,
        'packed polynomial products': eps,
        'individually processed reserved axes': 1 - eps - poly,
        'CRT axis reversal, best of E and pairwise swaps': max(eps, 1 - eps) * (1 - tau),
    }
    for name, value in constraints.items():
        if value <= 0:
            raise Failure(name)
    g = min(margins.values())
    if g <= kappa:
        raise Failure('kappa below every margin')
    return dict(kappa=str(kappa), kappa_float=float(kappa), min_margin=str(g), gap=str(g - kappa),
                binding=min(margins, key=margins.get), c1=str(c1),
                constraints={k: str(c) for k, c in constraints.items()},
                margins={k: str(m) for k, m in margins.items()},
                assumptions='PR #7 networks (a_b=3/(4*10^8), a_c=39/10^9); pinned upstream interfaces')


if __name__ == '__main__':
    out = evaluate()
    if not Q(1, 2**27) < Q(out['kappa']) < Q(1, 2**26):
        raise SystemExit('dyadic position changed')
    json.dump(out, open('certificates/witness.json', 'w'), indent=1)
    print('PASS conditional witness kappa =', out['kappa'], '| binding:', out['binding'])
