"""Exact checks of the Gaussian correction structure used by the segmented inverse.

For s < t with sigma = t/s, q_j = floor(t j/s + 1/2) and beta_j = t j/s - q_j, the
exponent of N's entry (l, j) is X = (sigma j - q_l)^2 - beta_j^2. We check, in exact
rational arithmetic:
  1. X = n (n + 2 beta_j) with n = q_j - q_l;
  2. inside a wrap-free segment, X = (1+theta) h^2 - h + theta (v^2 - u^2), with
     h = j - l, u = l - l*, v = j - l*, and l* = l - (beta_l + 1/2)/theta;
  3. every pair in different segments (n != j - l) has X >= 2;
  4. for any centre c in the same segment as l and j, with u = l - c and v = j - c,
     X = sigma h^2 + 2 beta_c h + theta (v^2 - u^2).
"""
from fractions import Fraction as F
import json, math, sys


def check(s, t, periods=3, band=30):
    sig = F(t, s); th = sig - 1
    q = lambda j: math.floor(F(t * j, s) + F(1, 2))
    beta = lambda j: F(t * j, s) - q(j)
    counts = dict(closed_form=0, segment=0, cross=0)
    cross_min = None
    for l in range(periods * s):
        lstar = l - (beta(l) + F(1, 2)) / th
        for j in range(l - band, l + band + 1):
            if j == l:
                continue
            X = (sig * j - q(l)) ** 2 - beta(j) ** 2
            n = q(j) - q(l)
            if X != n * (n + 2 * beta(j)):
                raise AssertionError(f'closed form fails at s={s} t={t} l={l} j={j}')
            counts['closed_form'] += 1
            h, u, v = j - l, l - lstar, j - lstar
            if n == h:
                if X != (1 + th) * h * h - h + th * (v * v - u * u):
                    raise AssertionError(f'segment form fails at s={s} t={t} l={l} j={j}')
                counts['segment'] += 1
                for c in (l - 3, l - 1, l + 2):
                    if q(c) - c == q(l) - l and q(c) - c == q(j) - j:
                        uc, vc = l - c, j - c
                        if X != sig * h * h + 2 * beta(c) * h + th * (vc * vc - uc * uc):
                            raise AssertionError(f'recentred form fails at s={s} t={t} l={l} j={j} c={c}')
                        counts['recentred'] = counts.get('recentred', 0) + 1
            else:
                if X < 2:
                    raise AssertionError(f'cross-wrap bound fails at s={s} t={t} l={l} j={j}')
                cross_min = X if cross_min is None else min(cross_min, X)
                counts['cross'] += 1
    return dict(s=s, t=t, theta=str(th), checks=counts, min_cross_exponent=str(cross_min))


CASES = [(113, 128), (241, 256), (1009, 1024), (1019, 1024), (4093, 4096)]

if __name__ == '__main__':
    out = [check(s, t) for s, t in CASES]
    json.dump(out, open('certificates/identities.json', 'w'), indent=1)
    print('PASS exact identities for', ', '.join(f'(s,t)=({c["s"]},{c["t"]})' for c in out))
