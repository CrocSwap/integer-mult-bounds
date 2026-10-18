#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Optional: rediscover a multiplier certificate by float subgradient ascent (never imported by verify.py, which checks
the stored certificate exactly).

Usage: python3 -I -B research/k8-commutation-ceiling-seed26/discover.py OUT.json [a_factor=21/20] [iters=300] [step=3e-6]

L(lam) = sum_q min over stabbing chains of [chain cost + sum_items coef * dim(point)], coef = +lam_g on the target copy and
-lam_g on the source copy of free ADD gate g; a copy with coef > 0 is charged at its entry point, coef < 0 at its exit.
The subgradient for g is dim(target copy) - dim(source copy) at the argmin chains. The best lam is rounded to k/2^40.
"""
import collections
import json
import math
import sys
from fractions import Fraction as Q
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import model as Mo  # noqa: E402


def main():
    out = sys.argv[1]
    fac = Q(sys.argv[2]) if len(sys.argv) > 2 else Q(21, 20)
    iters = int(sys.argv[3]) if len(sys.argv) > 3 else 300
    step0 = float(sys.argv[4]) if len(sys.argv) > 4 else 3e-6
    I = Mo.load_1671()
    W = Mo.Word(I)
    lo, hi = W.intervals('trace')
    a = float(fac * Mo.BASE_HI)
    dim = I.dimension

    def c(d):
        return 0.0 if d == 0 else (d / 73) ** (1 - a)
    const = 8 * c(8) + (1646 / 51) * c(51)
    free = [i for i, e in enumerate(W.ops) if e[0] == 'add' and lo[('G', i)] != hi[('G', i)]]
    fidx = {g: k for k, g in enumerate(free)}
    regs_data = []
    for q in range(W.n):
        items = []
        for i in W.on.get(q, []):
            sign = (1 if W.ops[i][1] == q else -1) if i in fidx else 0
            items.append((lo[('G', i)], hi[('G', i)], i if sign else None, sign))
        if q in W.pins:
            items.append((W.fixed[('P', q)], W.fixed[('P', q)], None, 0))
        S, E = W.fixed[('S', q)], W.fixed[('E', q)]
        cand = {S, E}
        for l, h, _, _ in items:
            cand.update(Mo.subspaces_closure(I, l, h))
        cand = sorted(cand, key=lambda F: F.bit_count())
        inl = [sum(1 << k for k, it in enumerate(items) if it[0] & ~V == 0) for V in cand]
        inh = [sum(1 << k for k, it in enumerate(items) if V & ~it[1] == 0) for V in cand]
        dims = [dim(V) for V in cand]
        arcs = [[] for _ in cand]
        for j in range(len(cand)):
            for i2 in range(j):
                if cand[i2] & ~cand[j] or dims[i2] == dims[j]:
                    continue
                ent = inl[j] & ~inl[i2]
                if ent & ~inh[j]:
                    continue
                arcs[j].append((i2, c(dims[j] - dims[i2]), ent, inh[i2] & ~inh[j]))
        regs_data.append((dims, arcs, items, cand.index(S), cand.index(E), inl, inh))

    def solve(reg, lam):
        dims, arcs, items, s0, e0, inl, inh = reg
        K = len(items)
        coef = [lam[fidx[it[2]]] * it[3] if it[2] is not None else 0.0 for it in items]
        f = [math.inf] * len(dims)
        back = [None] * len(dims)
        f[s0] = sum(coef[k] * dims[s0] for k in range(K) if inl[s0] >> k & 1 and coef[k] > 0)
        for j in range(len(dims)):
            if j == s0:
                continue
            for i2, base, ent, ex in arcs[j]:
                if f[i2] == math.inf:
                    continue
                v = f[i2] + base + sum(coef[k] * dims[j] for k in range(K) if ent >> k & 1 and coef[k] > 0) \
                    + sum(coef[k] * dims[i2] for k in range(K) if ex >> k & 1 and coef[k] < 0)
                if v < f[j]:
                    f[j], back[j] = v, i2
        tot = f[e0] + sum(coef[k] * dims[e0] for k in range(K) if inh[e0] >> k & 1 and coef[k] < 0)
        path = [e0]
        while path[-1] != s0:
            path.append(back[path[-1]])
        path.reverse()
        chosen = {}
        for k, it in enumerate(items):
            if it[2] is None:
                continue
            ent = next(p for p in path if inl[p] >> k & 1)
            last = [p for p in path if inh[p] >> k & 1 and inl[p] >> k & 1][-1]
            chosen[k] = dims[last] if coef[k] < 0 else dims[ent]
        return tot, chosen

    lam = [0.0] * len(free)
    best, best_lam = -math.inf, list(lam)
    for it in range(iters):
        L, sub = 0.0, [0.0] * len(free)
        for reg in regs_data:
            tot, chosen = solve(reg, lam)
            L += tot
            for k, d in chosen.items():
                item = reg[2][k]
                sub[fidx[item[2]]] += item[3] * d
        if L > best:
            best, best_lam = L, list(lam)
        print('iter %d bill %.12f best %.12f' % (it, (L + const) * 9 / 896, (best + const) * 9 / 896), flush=True)
        if not any(sub):
            break
        step = step0 / math.sqrt(it + 1)
        lam = [x + step * g for x, g in zip(lam, sub)]
    k = {str(g): round(x * (1 << Mo.LAMBDA_BITS)) for g, x in zip(free, best_lam) if round(x * (1 << Mo.LAMBDA_BITS))}
    Path(out).write_text(json.dumps(dict(schema=1, word_sha256='c2b294300760e1fd6eeab8c22c4d13e4633dca40e52cac8da0d68163a76e3ca8',
                                         a_factor_of_base_hi=str(fac), denominator_bits=Mo.LAMBDA_BITS,
                                         note='discovered by discover.py; check exactly with verify.py',
                                         lam=dict(sorted(k.items(), key=lambda kv: int(kv[0])))), indent=0, sort_keys=True) + '\n')


if __name__ == '__main__':
    main()
