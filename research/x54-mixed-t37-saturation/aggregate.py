#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Numerical screening (HiGHS via SciPy): is any demotion-count mix plus bin packing better than #1193's?

Relaxation. Each call uses a variant with k extra four-helper entrance groups relative to D3 (k in -3..3).
Following #1193/#1176, one group changes the local profile by -8H1+8H2+4H3-4H4 and turns four width-4 helpers
into width-5 helpers. k = 0, 1 are the admitted D3/D4 words; other k are hypothetical (linear extrapolation,
not admitted). Bins: the retained T37 capacities with their exact counts, every multiset of widths up to the
capacity, time windows and family rules ignored. Objective: the complex moment at #1193's root endpoint, with
the mass-linear part r/m removed (total mass is fixed by the coverage identity) and scaled by 1e6.

Outputs the integer optimum, the LP optimum and the LP dual prices. The dual width prices have the exact
structure pi_w = -lambda*w - mu*phi(w) with packing.py's phi, i.e. one price per unit of helper width and one
per unit of Phi. This is floating-point screening, not a certificate; packing.py carries the exact statement
for the incumbent mix.
"""
import argparse, itertools, json
from pathlib import Path
import numpy as np
from scipy.optimize import milp, linprog, LinearConstraint, Bounds

WIDTHS = (4, 5, 7, 8, 9)
PHI = {4: 0, 5: 3, 7: 1, 8: 0, 9: -1}
M, LIVE, CALLS = 73, 33152, 333
A_ROOT = 0.001678622735735992      # #1193 complex root
D3 = {1: 2358, 2: 504, 3: 410, 4: 130, 5: 82, 8: 8}
INV3 = {4: 44, 5: 44, 7: 38, 8: 114, 9: 240}
GROUP = {1: -8, 2: 8, 3: 4, 4: -4}
CAPS = {8: 24864, 16: 16576, 32: 16576, 48: 16576}
INCUMBENT = {1: 783552, 2: 169496, 3: 137362, 4: 42458, 5: 27306, 8: 2664, 48: 11374}
KS = range(-3, 4)


def cost(r, a=A_ROOT):
    return 0.0 if r == 0 else 1e6 * ((r / M) ** (1 - a) - r / M)


def local(k):
    return {r: D3.get(r, 0) + k * GROUP.get(r, 0) for r in set(D3) | set(GROUP)}


def inventory(k):
    return {4: 44 - 4 * k, 5: 44 + 4 * k, 7: 38, 8: 114, 9: 240}


def model():
    pats = [(c, p) for c in CAPS for n in range(13) for p in itertools.combinations_with_replacement(WIDTHS, n) if sum(p) <= c]
    obj = [sum(n * cost(r) for r, n in local(k).items()) for k in KS] + [cost(c - sum(p)) for c, p in pats]
    rows, rhs = [[1] * len(KS) + [0] * len(pats)], [CALLS]
    for c, n in CAPS.items():
        rows.append([0] * len(KS) + [int(cc == c) for cc, _ in pats]); rhs.append(n)
    for w in WIDTHS:
        rows.append([-inventory(k)[w] for k in KS] + [p.count(w) for _, p in pats]); rhs.append(0)
    return pats, np.array(obj), np.array(rows, float), np.array(rhs, float)


def run():
    pats, obj, A, b = model()
    incumbent = sum(n * cost(r) for r, n in INCUMBENT.items())
    ilp = milp(obj, constraints=LinearConstraint(A, b, b), integrality=np.ones(len(obj)), bounds=Bounds(0, np.inf),
               options=dict(time_limit=600, mip_rel_gap=1e-12))
    assert ilp.status == 0, ilp.message
    lp = linprog(obj, A_eq=A, b_eq=b, bounds=(0, None), method='highs')
    assert lp.status == 0, lp.message
    y = lp.eqlin.marginals
    pi = dict(zip(WIDTHS, y[1 + len(CAPS):]))
    lam = -pi[4] / 4
    mu = (-pi[5] - 5 * lam) / 3
    residual = max(abs(pi[w] + lam * w + mu * PHI[w]) for w in WIDTHS)
    used = lambda x: {str(k): round(v) for k, v in zip(KS, x[:len(KS)]) if v > 0.5}
    # dM/da at the root, to convert objective units into kappa: dkappa = -dObj / (1e6 * LIVE * dM/da) / (1 + a)^2
    dMda = sum(n * (r / M) ** (1 - A_ROOT) * np.log(M / r) for r, n in INCUMBENT.items()) / LIVE
    return dict(
        status='SCREENING_ONLY_FLOAT_HIGHS',
        incumbent_objective=incumbent, ilp_objective=ilp.fun, ilp_minus_incumbent=ilp.fun - incumbent,
        ilp_total_extra_groups=int(round(sum(k * v for k, v in zip(KS, ilp.x[:len(KS)])))), ilp_mix=used(ilp.x),
        lp_objective=lp.fun, lp_minus_incumbent=lp.fun - incumbent,
        lp_total_extra_groups=float(sum(k * v for k, v in zip(KS, lp.x[:len(KS)]))),
        dual_width_price={str(w): pi[w] for w in WIDTHS}, dual_bin_price={str(c): v for c, v in zip(CAPS, y[1:1 + len(CAPS)])},
        lambda_per_width_unit=lam, mu_per_phi_unit=mu, price_structure_residual=residual,
        dM_da=dMda, kappa_per_objective_unit=1 / (1e6 * LIVE * dMda) / (1 + A_ROOT) ** 2,
        patterns=len(pats), variants=list(KS))


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--out', type=Path)
    a = ap.parse_args()
    r = run()
    if a.out:
        a.out.write_text(json.dumps(r, indent=1, sort_keys=True) + '\n')
    print(json.dumps({k: r[k] for k in ('ilp_minus_incumbent', 'ilp_total_extra_groups', 'lp_minus_incumbent',
                                        'lambda_per_width_unit', 'mu_per_phi_unit', 'price_structure_residual')}))
