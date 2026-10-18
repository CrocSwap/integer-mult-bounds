#!/usr/bin/env python3
"""Exact bounded recurrence checks; see PROOF.md for the all-scale argument.

Ross Richardson, with substantial OpenAI Codex assistance. Apache-2.0.
No predecessor implementation or floating-point acceptance decisions.
"""
from fractions import Fraction as F
import json


def need(condition, message):
    if not condition:
        raise ValueError(message)


def exact_root(n, k):
    lo, hi = 0, n + 1
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if mid ** k <= n:
            lo = mid
        else:
            hi = mid
    need(lo ** k == n, 'power is not rational in this test')
    return lo


def power(q, p):
    raised = q ** p.numerator
    return F(exact_root(raised.numerator, p.denominator),
             exact_root(raised.denominator, p.denominator))


def moment(histogram, p, stock=1):
    return sum(F(n, stock) * power(F(r, 256), p)
               for r, n in histogram.items())


def product(a, b):
    return tuple(tuple(sum(a[i][k] * b[k][j] for k in range(2))
                       for j in range(2)) for i in range(2))


def vec(a, x):
    return tuple(sum(a[i][k] * x[k] for k in range(2)) for i in range(2))


def addq(x, y):
    return (x[0] + y[0], x[1] + y[1])


def mulq(x, y):
    return (x[0] * y[0] + 33 * x[1] * y[1],
            x[0] * y[1] + x[1] * y[0])


def signq(x):
    """Sign of a+b sqrt(33) by exact integer/rational square comparisons."""
    a, b = x
    if b == 0:
        return (a > 0) - (a < 0)
    if a == 0:
        return (b > 0) - (b < 0)
    if a > 0 and b > 0:
        return 1
    if a < 0 and b < 0:
        return -1
    square_difference = a * a - 33 * b * b
    if a > 0:
        return (square_difference > 0) - (square_difference < 0)
    return (square_difference < 0) - (square_difference > 0)


def recurrence(n, profiles):
    t = {-1: 1, 0: 1}
    for i in range(1, n + 1):
        h = profiles[(i - 1) % len(profiles)]
        t[i] = h.get(16, 0) * t[i - 1] + h.get(1, 0) * t[i - 2]
    return t


def run():
    a, b = {16: 1, 1: 2}, {16: 4, 1: 32}
    need(moment(a, F(1, 4)) == 1, 'A scalar root')
    need(moment(b, F(3, 4)) == 1, 'B scalar root')
    need((F(1, 4) + F(3, 4)) / 2 == F(1, 2), 'mean root')
    need(sum(r*n for r, n in a.items()) == 18, 'A full mass')
    need(sum(r*n for r, n in b.items()) == 96, 'B full mass')
    ca, cb = ((1, 2), (1, 0)), ((4, 32), (1, 0))
    p = product(cb, ca)
    need(p == ((36, 8), (1, 2)), 'two-level transfer')
    need(p[0][0] + p[1][1] == 38, 'trace')
    need(p[0][0]*p[1][1] - p[0][1]*p[1][0] == 64, 'determinant')
    lam = (19, 3)
    need(addq(addq(mulq(lam, lam), (-38*lam[0], -38*lam[1])), (64, 0)) == (0, 0),
         'exact eigenvalue polynomial')
    need(signq((lam[0]-32, lam[1])) > 0, 'p_eff greater than 5/8')
    need(signq((lam[0]-64, lam[1])) < 0, 'p_eff less than 3/4')
    cube = mulq(mulq(lam, lam), lam)
    need(signq((cube[0]-256**2,cube[1])) < 0, 'p_eff less than 2/3')
    w = ((17, 3), (1, 0))
    for j in range(2):
        left = addq((p[j][0]*w[0][0], p[j][0]*w[0][1]),
                    (p[j][1]*w[1][0], p[j][1]*w[1][1]))
        need(left == mulq(lam, w[j]), 'positive eigenvector')
    t = recurrence(240, (a, b))
    state = (1, 1)
    lpow = (1, 0)
    for k in range(1, 121):
        state = vec(p, state)
        lpow = mulq(lpow, lam)
        need(state == (t[2*k], t[2*k-1]), 'all retained children vs block transfer')
        need(t[2*k] == 38*t[2*k-2]-64*t[2*k-4] if k>1 else t[2*k]==44,
             'eliminated scalar recurrence')
        need(signq((t[2*k]-lpow[0], -lpow[1])) >= 0, 'lower growth bound')
        upper = mulq((17, 3), lpow)
        need(signq((upper[0]-t[2*k], upper[1])) >= 0, 'upper growth bound')
    need([t[i] for i in range(5)] == [1, 3, 44, 50, 1608], 'prefix')
    # det(I-M) with y=z^2=256^-p. Exact rational endpoint signs.
    def det_m(y):
        return 1 - 38*y + 64*y*y
    need(det_m(F(1, 32)) == F(-1, 8), 'lifted moment at p=5/8')
    need(det_m(F(1, 64)) == F(27, 64), 'lifted moment at p=3/4')
    need(moment(a, F(1, 2)) == F(3, 8), 'A at mean')
    need(moment(b, F(1, 2)) == 3, 'B at mean')
    need(F(1,8)*2-F(1,4)*1 == 0 and F(1,8)+2 == F(17,8),
         'phase moment radius at the mean')
    unit_toll = {-1:1,0:1}
    for i in range(1,241):
        h = (a,b)[(i-1)%2]
        unit_toll[i] = h[16]*unit_toll[i-1]+h[1]*unit_toll[i-2]+1
        need(t[i] <= unit_toll[i] <= F(3*t[i]-1,2), 'positive unit toll')
    # Positive homogeneous controls obey their own roots, with the same
    # terminal overshoot constants used in the comparison proof.
    for h, root in [(a, F(1, 4)), (b, F(3, 4))]:
        u = recurrence(120, (h,))
        for i in range(1, 121):
            xroot = 16 ** (i * root.numerator)  # compare after root.denominator power
            value = u[i] ** root.denominator
            need(xroot <= value <= 256 ** root.numerator * xroot,
                 'homogeneous root bound')
    # Extremal node-wise costs: min/max optimize each independent subtree.
    low, high = {-1:F(1),0:F(1)}, {-1:F(1),0:F(1)}
    for i in range(1, 81):
        low[i] = min(h[16]*low[i-1]+h[1]*low[i-2] for h in (a,b))
        high[i] = max(h[16]*high[i-1]+h[1]*high[i-2] for h in (a,b))
        need(low[i]**4 >= 16**i, 'finite-catalogue lower bound')
        need(high[i]**4 <= 256**3 * 16**(3*i), 'finite-catalogue upper bound')
    controls = {}
    controls['drop_B_rank1_child'] = moment({16:4}, F(3,4)) != 1
    controls['change_B_multiplicity'] = moment({16:4,1:31}, F(3,4)) != 1
    controls['wrong_stock'] = moment(b,F(3,4),stock=2) != 1
    controls['swap_phase_at_first_cut'] = recurrence(2,(b,a))[1] != t[1]
    controls['replace_by_average_root'] = t[2] != 16
    controls['erase_long_child'] = recurrence(4,({16:1},{16:4}))[4] != t[4]
    controls['wrong_eigenvalue'] = signq((lam[0]-16,lam[1])) != 0
    controls['wrong_quadratic_sign'] = mulq((19,-3),(19,-3)) != (38*lam[0]-64,38*lam[1])
    need(all(controls.values()), 'semantic control failed')
    return {'status':'PASS_SCALE_DEPENDENT_SEED_MOMENT_AUDIT',
            'profiles':{'A':a,'B':b},'base_width':256,'stock':1,
            'scalar_roots':['1/4','3/4'],'naive_mean':'1/2',
            'period_transfer':p,'dominant_eigenvalue':'19+3*sqrt(33)',
            'effective_root':'log(19+3*sqrt(33))/log(256)',
            'certified_effective_root_interval':['5/8','2/3'],
            'grid_prefixes':240,'block_powers':120,
            'homogeneous_cases':240,'homogeneous_max_index':120,
            'extremal_depths':80,'controls':controls,
            'scope':'exact finite replay plus separate all-scale written proof; no_new_kappa'}


if __name__ == '__main__':
    print(json.dumps(run(),sort_keys=True,indent=2))
