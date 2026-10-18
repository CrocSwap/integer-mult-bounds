"""Independent pattern census and mixed-variant cost DP.

PR855 supplies lambda and residue potentials. Every obligation is replayed
using the new binomial interval engine and a Cartesian-product census.
"""
from fractions import Fraction as Q
from itertools import product
from construct import require
from binomial import power_bounds, SCALE

CAPACITY_SCORES = {8: 6, 16: 12, 32: 24, 48: 37}
WIDTH_SCORES = {4: 3, 5: 3, 7: 5, 8: 6, 9: 7}


def patterns():
    widths = tuple(sorted(WIDTH_SCORES))
    result = []
    for capacity in sorted(CAPACITY_SCORES):
        for counts in product(*(range(capacity//w+1) for w in widths)):
            used = sum(w*n for w, n in zip(widths, counts))
            if used <= capacity:
                result.append((capacity-used, CAPACITY_SCORES[capacity]-
                               sum(WIDTH_SCORES[w]*n for w, n in zip(widths, counts))))
    require(len(result) == 1163, 'Independent pattern domain')
    return result


def verify(model, certificate):
    b = Q(model['endpoint'])
    require(Q(certificate['endpoint']) == b and certificate['potential_scale'] == 10**16,
            'Potential source endpoint/scale')
    lam, potentials = certificate['lambda_units_1e30'], certificate['potentials']
    require(type(lam) is int and lam < 0 and len(potentials) == 37 and
            all(type(x) is int for x in potentials) and potentials[0] == 0, 'Potential domain')
    unit = SCALE//10**16
    intervals = {r: power_bounds(r, b) for r in range(74)}
    for leftover, score in patterns():
        require(score >= 0, 'Negative pattern score')
        reduced = intervals[leftover][0] - leftover*SCALE - lam*score
        require(reduced >= 0, 'Pattern dual inequality')
        for residue in range(37):
            require((potentials[(residue+score)%37]-potentials[residue])*unit <= reduced,
                    'Pattern potential inequality')
    threshold = model['live'] * intervals[model['m']][1]
    baseline_upper = sum(n*intervals[r][1] for r, n in model['global'].items())
    require(baseline_upper < model['live']*intervals[model['m']][0], 'Original supplier positive control')
    mass = sum(c*n for c, n in model['capacities'].items())
    base_idle = mass - sum(w*n for w, n in model['widths'].items())
    score = sum(CAPACITY_SCORES[c]*n for c, n in model['capacities'].items()) - sum(
        WIDTH_SCORES[w]*n for w, n in model['widths'].items())
    base = sum(n*intervals[r][0] for r, n in model['local'].items()) + base_idle*SCALE + lam*score
    require(sum(r*n for r,n in model['local'].items()) + base_idle == model['rank_mass'], 'Baseline conservation')
    names = sorted(model['variants'])
    costs = {}
    for name in names:
        delta = model['variants'][name]
        idle_change = -sum(w*n for w,n in delta['widths'].items())
        score_change = -sum(WIDTH_SCORES[w]*n for w,n in delta['widths'].items())
        require(sum(r*n for r,n in delta['profile'].items()) + idle_change == 0, 'Variant conservation: ' + name)
        costs[name] = (sum(n*intervals[r][0 if n >= 0 else 1] for r,n in delta['profile'].items()) +
                       idle_change*SCALE + lam*score_change, score_change)
    # These endpoint inequalities certify nonnegative inventories for every
    # four-way mix of at most 72 calls, before relaxing labels and windows.
    for kind in ('profile', 'widths'):
        initial = model['local'] if kind == 'profile' else model['widths']
        for r,n in initial.items():
            require(n + model['calls']*min(0, *(d[kind].get(r,0) for d in model['variants'].values())) >= 0,
                    'Mixed inventory can become negative')
    state = {score%37: (0, (0,)*len(names))}
    minima = []
    for changed in range(1, model['calls']+1):
        following = {}
        for residue,(cost,counts) in state.items():
            for i,name in enumerate(names):
                price,shift = costs[name]
                next_residue = (residue+shift)%37
                new_counts = list(counts);new_counts[i] += 1
                candidate = (cost+price,tuple(new_counts))
                if next_residue not in following or candidate < following[next_residue]:
                    following[next_residue] = candidate
        state = following
        for residue,(cost,counts) in state.items():
            minima.append((base+cost+potentials[residue]*unit-threshold, changed, residue, counts))
    margin,changed,residue,counts = min(minima)
    return dict(patterns=1163, potential_inequalities=43031, dp_states=len(minima),
                modified_calls=changed, residue=residue, minimum_margin=str(Q(margin,SCALE)),
                minimum_counts=dict(zip(names,counts)), excluded=margin>0,
                power_engine='7000-term positive binomial with integer outward rounding and geometric tail')
