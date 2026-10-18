"""Floating bank-free packing relaxation; never a physical or theorem witness.

Adapted from the paired-chain inventory in larger-gain/stages/screen_stages.py.
Prepared with OpenAI Codex assistance; Apache-2.0. See ../NOTICE.md.
Geometry, execution windows and integrality are relaxed. No claim of a global
upper bound over different circuits, banked constructions or split rules.
"""
import argparse
from collections import Counter
import json
import math
from pathlib import Path

import numpy as np
from scipy.optimize import brentq, linprog

P = Path(__file__).resolve().parents[1]
ROOT = P.parents[1]


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    provider = json.loads((ROOT / 'research/gauge44-slots/data/PLAN.json').read_text())['provider_registry']['gauge44']
    profile = {int(r): n for r, n in provider['actual_paid_profile'].items()}
    inventory = Counter(provider['widths'])
    widths = sorted(inventory)
    results = []
    for pairs in range(2, 7):
        stages, m, live = 2*pairs+1, 16*pairs+9, 224*pairs
        capacities = {8: 224*(pairs-1)} | {16*p: 448 for p in range(1, pairs)}
        patterns = []

        def enumerate_bin(capacity, remainder, index=0, vector=()):
            if index == len(widths):
                patterns.append((capacity, vector, remainder))
                return
            w = widths[index]
            for n in range(remainder//w+1):
                enumerate_bin(capacity, remainder-n*w, index+1, vector+(n,))

        for cap in capacities:
            enumerate_bin(cap, cap)
        matrix = np.array([[int(cap == c) for cap, vec, r in patterns] for c in capacities]
                          + [[vec[i] for cap, vec, r in patterns] for i in range(len(widths))])
        limit = int(m/math.sqrt(2))

        def parts(r):
            return [r] if r <= limit else [limit, r-limit]

        def cost(r):
            return r*math.expm1(.00168*math.log(m/r))/.00168 if r else 0

        objective = [sum(cost(q) for q in parts(r)) for cap, vec, r in patterns]
        rhs = list(capacities.values()) + [stages*inventory[w] for w in widths]
        solve = linprog(objective, A_eq=matrix, b_eq=rhs, bounds=(0, None), method='highs')
        row = dict(K=pairs, L=stages, m=m, variables=len(patterns), success=solve.success)
        if solve.success:
            idle = Counter()
            for val, (cap, vec, r) in zip(solve.x, patterns):
                if val > 1e-8:
                    for q in parts(r):
                        if q:
                            idle[q] += float(val)
            combined = Counter({r: stages*n for r, n in profile.items()})
            combined.update(idle)
            root = brentq(lambda b: sum(n*(r/m)**(1-b) for r, n in combined.items())/live-1, 0, .005)
            row.update(complex_relaxed=root, kappa_relaxed=root/(1+root), idle=dict(idle))
        results.append(row)
        print(row, flush=True)
    args.out.write_text(json.dumps(dict(status='FLOATING_RELAXATION_ONLY_NOT_A_WITNESS', rows=results), indent=2)+'\n')


if __name__ == '__main__':
    main()
