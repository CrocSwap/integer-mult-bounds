#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Scoped idle-mass stability checks; reuses credited exact interval pricing."""
import argparse
from fractions import Fraction as Q
import hashlib
from functools import lru_cache
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
spec = importlib.util.spec_from_file_location('credited_ceiling', ROOT / 'research/complex-local-word-ceiling/ceiling.py')
C = importlib.util.module_from_spec(spec)
spec.loader.exec_module(C)


def require(ok, message):
    if not ok:
        raise ValueError(message)


def validate(idle, mass, R):
    require(isinstance(mass, int) and mass >= 0 and isinstance(R, int) and R > 0, 'mass/cap domain')
    require(all(isinstance(r, int) and 1 <= r <= R and isinstance(n, int) and n >= 0 for r, n in idle.items()), 'idle rank/count domain')
    require(sum(r*n for r, n in idle.items()) == mass, 'idle mass mismatch')


def optimal_histogram(mass, R):
    validate({}, 0, R)
    require(isinstance(mass, int) and mass >= 0, 'mass domain')
    q, s = divmod(mass, R)
    return {r: n for r, n in ((R, q), (s, 1 if s else 0)) if n}


@lru_cache(None)
def cost(r, m, a):
    return C.child_cost(r, m, a)


def moment(hist, m, a):
    require(0 <= a < 1, 'saving domain')
    lo = hi = Q(0)
    for r, n in hist.items():
        l, u = cost(r, m, a)
        lo += n*l
        hi += n*u
    return lo, hi


def mass_budget(local_total, mass, W, m, R, a, K):
    """Certified upper bound for mass in idle ranks <= K; not a feasibility test."""
    require(0 < a < 1 and 1 <= K < R < m, 'stability domain')
    local = moment(local_total, m, a)
    cr = C.child_cost(R, m, a)
    ck = C.child_cost(K, m, a)
    delta = ck[0]/K - cr[1]/R
    require(delta > 0, 'precision cannot separate rank prices')
    headroom = W - local[0] - Q(mass, R)*cr[0]
    require(headroom >= 0, 'fractional relaxation already rules out acceptance')
    return headroom / delta


def exhaustive_control():
    # All unordered integer histograms of total mass <= 24, cap <= 7.
    def partitions(mass, cap):
        if cap == 0:
            if mass == 0:
                yield {}
            return
        for n in range(mass//cap + 1):
            for h in partitions(mass-cap*n, cap-1):
                yield dict(h, **{str(cap): n}) if n else h
    checked = 0
    for R in range(2, 8):
        for mass in range(25):
            best = optimal_histogram(mass, R)
            blo, bhi = moment(best, 9, Q(1, 10))
            for raw in partitions(mass, R):
                h = {int(r): n for r,n in raw.items()}
                validate(h, mass, R)
                if h != best:
                    require(moment(h, 9, Q(1, 10))[0] > bhi, 'integer optimum counterexample')
                checked += 1
    return checked


def run():
    pins = json.loads((HERE/'SOURCES.json').read_text())
    for f in pins['files']:
        if f['usage'] == 'input':
            require(hashlib.sha256((ROOT/f['path']).read_bytes()).hexdigest() == f['sha256'], 'source pin mismatch: '+f['path'])
    asm = json.loads((ROOT/'research/community-frontier1094-audit/ASSEMBLY.json').read_text())
    ind = json.loads((ROOT/'research/community-frontier1094-audit/INDEPENDENT1094.json').read_text())
    full = {int(r): n for r,n in asm['complex_profile'].items()}
    idle = {int(r): n for r,n in ind['owner']['idle'].items()}
    require(full == {int(r): n for r,n in ind['owner']['profile'].items()}, 'invoice mismatch')
    N, W, m, R = ind['price']['calls'], ind['price']['live'], 73, 51
    require(N == 144 and W == 14336, 'template mismatch')
    require(sum(r*n for r,n in full.items()) == 72*W+64*N, 'coverage mismatch')
    local = {r: n-idle.get(r,0) for r,n in full.items() if n-idle.get(r,0)}
    require(all(n >= 0 and n % N == 0 for n in local.values()), 'local decomposition')
    mass = sum(r*n for r,n in idle.items())
    validate(idle, mass, R)
    best = optimal_histogram(mass, R)
    validate(best, mass, R)
    rows = []
    for a in [Q(asm['complex_lower']), Q('0.00168'), Q('0.00169')]:
        local_cost = moment(local,m,a)
        ideal = C.child_cost(R,m,a)
        discrete = moment(best,m,a)
        current = moment(idle,m,a)
        raw_budgets = {K: mass_budget(local,mass,W,m,R,a,K) for K in [1,3,7,16,32,48]}
        budgets = {str(K): float(v) for K,v in raw_budgets.items()}
        integer_caps = {str(K): v.numerator // v.denominator for K,v in raw_budgets.items()}
        # Verify the stronger pointwise inequality on the actual histogram.
        for K in [1,3,7,16,32,48]:
            small = sum(r*n for r,n in idle.items() if r <= K)
            ck = C.child_cost(K,m,a)
            rhs_hi = Q(mass,R)*ideal[1] + small*(ck[1]/K-ideal[0]/R)
            require(current[0] > rhs_hi, 'stability inequality fixture')
        require(current[0] > discrete[1], 'selected packing must exceed optimum')
        rows.append({'a': str(a), 'fractional_moment':float((local_cost[0]+Q(mass,R)*ideal[0])/W), 'integer_optimal_moment':float((local_cost[0]+discrete[0])/W), 'selected_moment':float((local_cost[0]+current[0])/W), 'necessary_mass_caps_by_rank':budgets, 'certified_integer_mass_caps':integer_caps})
    rejected = 0
    for f in [lambda:validate({52:1},52,R),lambda:validate({1:1},2,R),lambda:validate({1:Q(1,2)},1,R),lambda:mass_budget(local,mass,W,m,R,Q(0),7)]:
        try:
            f()
        except ValueError:
            rejected += 1
    require(rejected == 4, 'failure controls')
    return {'scope':'fixed selected local word; unrestricted integer idle histograms, not physical realizability or a new kappa', 'idle_mass':mass, 'integer_optimal_histogram':best, 'actual_idle_histogram':idle, 'rows':rows, 'exhaustive_histograms_checked':exhaustive_control(), 'semantic_rejections':rejected}


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--write',action='store_true')
    args = ap.parse_args()
    result = run()
    text = json.dumps(result,indent=2,sort_keys=True)+'\n'
    if args.write:
        (HERE/'RESULT.json').write_text(text)
    else:
        require(json.loads((HERE/'RESULT.json').read_text()) == json.loads(text), 'committed result mismatch')
    print(text)
    print('PASS_IDLE_PACKING_STABILITY')
