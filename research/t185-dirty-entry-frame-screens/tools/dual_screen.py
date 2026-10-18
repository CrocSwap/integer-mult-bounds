# SPDX-License-Identifier: Apache-2.0
"""Float sensitivity screen for the #2863 fixed packing model (screening only, not certification).

Uses #2863's published symbolic dual prices (research/shared-kernel-packing/review/PROOF.md, section 4) and its
per-replica model: bins {8:672,16:448,32:448,48:448}, nine calls of the inventory {4:26,5:2,7:62,8:84,9:234},
local profile 2394H1+642H2+266H3+128H4+26H5+8H8 per call, normalisation 896*73^p. First-order kappa changes
use d(total)/d(alpha) = sum n_r r^p ln(73/r) over the optimal profile and assume the LP basis is unchanged.

Prepared for digitalis-p with Claude (Anthropic) assistance. Apache-2.0.
"""
import json
from math import log

ALPHA = 0.001720100805416886
P = 1 - ALPHA


def H(r):
    return r ** P if r > 0 else 0.0


def model():
    q = (H(3) - H(48)) / 5
    c = H(5) - 3 * q
    lam = {8: c / 4, 16: c / 2, 32: c, 48: H(48)}
    mu = {4: H(1) - H(5), 5: -H(5), 7: -c / 2 - q, 8: -c / 4, 9: q}
    bins = {8: 672, 16: 448, 32: 448, 48: 448}
    inv = {4: 26, 5: 2, 7: 62, 8: 84, 9: 234}
    native = {1: 2394, 2: 642, 3: 266, 4: 128, 5: 26, 8: 8}
    idle = sum(bins[k] * lam[k] for k in bins) + 9 * sum(inv[w] * mu[w] for w in inv)
    total = 9 * sum(n * H(r) for r, n in native.items()) + idle
    phi = total / (896 * 73 ** P)
    prof = {1: 21780, 2: 5778, 3: 12402 / 5, 4: 1152, 5: 354, 8: 72, 48: 1808 / 5}
    slope = sum(n * H(r) * log(73 / r) for r, n in prof.items())
    return mu, phi, slope


def rows():
    mu, phi, slope = model()

    def dk(per_call):
        return -9 * per_call / slope

    out = {}
    for name, nat, w0, w1 in [('staged 9->8 rewrite (3H1-2H2), PR2857 type', {1: 3, 2: -2}, 9, 8),
                              ('dirt-entry 9->8 (5H1-3H2), PR2853 type', {1: 5, 2: -3}, 9, 8),
                              ('width 9->8 with no native change', {}, 9, 8),
                              ('enter at first frame dim 1 (-H1, 9->8)', {1: -1}, 9, 8),
                              ('enter at first frame dim 2 (-H2, 9->7)', {2: -1}, 9, 7)]:
        per_call = sum(n * H(r) for r, n in nat.items()) + mu[w1] - mu[w0]
        out[name] = dict(per_call=per_call, dkappa_first_order=dk(per_call))
    for name, nat in [('merge 2H1->H2', {1: -2, 2: 1}), ('merge 2H2->H4', {2: -2, 4: 1}),
                      ('merge 8H1->H8', {1: -8, 8: 1})]:
        per_call = sum(n * H(r) for r, n in nat.items())
        out[name] = dict(per_call=per_call, dkappa_first_order=dk(per_call))
    return dict(phi_at_root=phi, slope_per_replica=slope, break_even_split_cost_dim1=1 - (mu[8] - mu[9]),
                rows=out)


if __name__ == '__main__':
    print(json.dumps(rows(), indent=1))
