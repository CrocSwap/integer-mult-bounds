"""All-replica signed-dual relaxation bound for the fixed U8 whole-owner family.

This arithmetic component alone does not establish owner feasibility; the
package's separate construction and admission checks do. PR890 supplies the fixed inventory and signed
prices; this script independently enumerates bin patterns and proves an all-T
moment lower bound at the certified T37 upper endpoint.
The two retained rational engines are reused for numerical certificates only.
"""
import argparse
from collections import Counter
from fractions import Fraction as Q
import hashlib
import importlib.util
import itertools
import json
from pathlib import Path
import sys

if sys.flags.optimize:
    raise RuntimeError('Retained arithmetic assertions must stay enabled; do not use Python -O')

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
ENGINE = 'research/complex-k492-owner-repair/vendor/multicold/engines/'
PINS = {
    ENGINE+'moment.py': '81cbc864e106418fc7854322746f72180cb8110ff39f74450a3b8d55a82c1482',
    ENGINE+'base_two_moment.py': 'aee70c242a2f1d225528fabe2002e1564d1dc884797c07d28a831c7878ee9098',
    ENGINE+'outer.py': 'c1ebb52163a7219504c728a5c2b098bf1e50bf20148a2879c5a74c3cadc7c03c',
    'research/complex-t21-owners/vendor/pr870/independent/price_profile_t16.py': '53f8e62dcf27bee032c1bee0245d126a9c8a12ebcf24f6aaff65ea3122fffe29',
    'research/complex-t21-owners/data/CLAIM.json': '433d7bc4a371aaffeee35c12a1db6ea974722a85b799233626e1a57dcfdcb121',
    'research/complex-t21-owner-bound/PROOF.md': '2aa0aa6ec1d87402138564c38749b5ca0f058c16817efdf58a2685d2d90cb417',
}
WIDTHS = (4, 5, 7, 8, 9)
PRICES = (-1, -20, -8, -2, 4)
CAPACITIES = {8: (672, 2), 16: (448, 4), 32: (448, 8), 48: (448, -13)}
INVENTORY = {4: 80, 5: 32, 7: 54, 8: 122, 9: 216}


def need(ok, message):
    if not ok:
        raise ValueError(message)


def load(relative, name):
    spec = importlib.util.spec_from_file_location(name, ROOT/relative)
    obj = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj


def dual_tables():
    """Cartesian product enumeration and independently programmed recurrence."""
    upper, count = {}, 0
    for cap, (_, bonus) in CAPACITIES.items():
        for vector in itertools.product(*(range(cap//w+1) for w in WIDTHS)):
            used = sum(w*n for w, n in zip(WIDTHS, vector))
            if used > cap:
                continue
            count += 1
            r = cap-used
            value = bonus+sum(p*n for p, n in zip(PRICES, vector))
            upper[r] = max(upper.get(r, -10**6), value)
    alt = {}
    for cap, (_, bonus) in CAPACITIES.items():
        scores = [None]*(cap+1)
        scores[0] = 0
        for fill in range(cap+1):
            if scores[fill] is None:
                continue
            for width, price in zip(WIDTHS, PRICES):
                nxt = fill+width
                if nxt <= cap:
                    proposal = scores[fill]+price
                    if scores[nxt] is None or proposal > scores[nxt]:
                        scores[nxt] = proposal
        for fill, value in enumerate(scores):
            if value is not None:
                alt[cap-fill] = max(alt.get(cap-fill, -10**6), value+bonus)
    need(upper == alt and count == 1163, 'two independently structured dual enumerations')
    return upper, count


def phi_pair(engine, kind, r, z):
    if kind == 'mercator':
        a, b = engine.logarithm(Q(73, r))
        a, b = engine.exponential(z*a, z*b)
    else:
        a, b = engine.log_bounds(Q(73, r))
        a, b = engine.exp_bounds(z*a)[0], engine.exp_bounds(z*b)[1]
    return r*a, r*b


def ratio_certificate(engine, kind, upper, z):
    phi = {r: phi_pair(engine, kind, r, z) for r in upper if r}
    cost = {r: (48*lo-r*phi[48][1], 48*hi-r*phi[48][0])
            for r, (lo, hi) in phi.items() if r < 48}
    credit = {r: 48*upper[r]+13*r for r in cost}
    need(credit[1] == 925, 'rank-one credit')
    need(all(a > 0 for a, b in cost.values()), 'positive non48 costs')
    # c(r)-v(r)*c(1)/925 > 0 at every r != 1, so a single
    # multiplier gives a supporting inequality for every count vector.
    margins = {}
    for r, (lo, hi) in cost.items():
        if r == 1:
            continue
        c = credit[r]
        rhs = c*cost[1][1 if c >= 0 else 0]/925
        margins[r] = lo-rhs
        need(margins[r] > 0, 'rank-one strictly optimal cost/credit ratio: '+str(r))
    return dict(credit=credit, multiplier_interval=[str(cost[1][0]/925), str(cost[1][1]/925)],
                strict_margin_by_rank={r: str(x) for r, x in margins.items()},
                minimum_strict_margin=str(min(margins.values())))


def main(out):
    need(not sys.flags.optimize, 'retained arithmetic assertions must stay enabled')
    for relative, expected in PINS.items():
        need(hashlib.sha256((ROOT/relative).read_bytes()).hexdigest() == expected, 'source drift: '+relative)
    M = load(ENGINE+'moment.py', 'retained_mercator')
    B = load(ENGINE+'base_two_moment.py', 'retained_atanh')
    A = load(ENGINE+'outer.py', 'retained_outer')
    O = load('research/complex-t21-owners/vendor/pr870/independent/price_profile_t16.py', 'retained_outer_driver')
    claim = json.loads((ROOT/'research/complex-t21-owners/data/CLAIM.json').read_text())
    local = {int(r): n for r, n in claim['local_profile'].items()}
    upper, vectors = dual_tables()
    mass = sum(c*n for c, (n, _) in CAPACITIES.items())-9*sum(r*n for r, n in INVENTORY.items())
    signed = sum(n*p for n, p in CAPACITIES.values())+9*sum(INVENTORY[r]*p for r, p in zip(WIDTHS, PRICES))
    need((mass, signed, upper[0], upper[48]) == (14382, -3892, 0, -13), 'fixed-family coefficients')
    need(48*signed+13*mass == 150, 'dual credit demand per replica')
    T = 37
    idle = {48: 11086, 1: 6}
    need(sum(r*n for r, n in idle.items()) == mass*T, 'T37 idle mass')
    need(sum(upper[r]*n for r, n in idle.items()) == signed*T, 'T37 signed dual equality')
    need(Q(150, 925) == Q(6, 37), 'equality ratio')
    profile = Counter({r: 9*T*n for r, n in local.items()})
    profile.update(idle)
    live = 896*T
    need(73*live-sum(r*n for r, n in profile.items()) == 320*T, 'profile deficit')
    root = M.certify(profile, 73, live)
    lo, hi = Q(root['lower']), Q(root['upper'])
    signs = {}
    for name, z in [('lower', lo), ('upper', hi)]:
        first = M.moment(profile, 73, live, z)
        second = B.moment(73, live, list(profile.items()), z)
        need(first[1] < 1 and second[1] < 1 if name == 'lower' else first[0] > 1 and second[0] > 1,
             'two exact moment signs at '+name)
        signs[name] = dict(endpoint=str(z), mercator=[str(x-1) for x in first], atanh=[str(x-1) for x in second])
    certs = {kind: ratio_certificate(engine, kind, upper, hi)
             for kind, engine in [('mercator', M), ('atanh', B)]}
    price_lower = O.outer47(Q(claim['bit_lower']), lo, A)
    price_upper = O.outer47(Q(claim['bit_lower']), hi, A)
    need(price_lower['kappa'] == price_upper['kappa'], 'one kappa grid tick encloses complete relaxed root')
    old_k, new_k = Q(claim['kappa']), Q(price_upper['kappa'])
    result = dict(status='PASS_ALL_T_U8_SIGNED_DUAL_RELAXATION_BOUND',
                  scope='All positive integer replica counts, unchanged U8 local paid profile and helper widths, unchanged 8/16/32/48 capacity inventory, whole helpers, native no-surcharge complex moment and retained outer recipe. Time windows, bin count realizability, owner geometry, payload/invoice admission and physical execution are relaxed in this arithmetic component. The package separately certifies its T37 construction and finite admission; this upper bound alone does not establish feasibility.',
                  dual_bin_vectors=vectors, upper=upper, mass_per_replica=mass, signed_price_per_replica=signed,
                  credit_per_replica=150, equality_replica_counts='positive multiples of 37 only',
                  normalized_idle={'1': '6/37', '48': '11086/37'},
                  smallest_integral_relaxed_profile=dict(replicas=T, idle=idle, profile=dict(sorted(profile.items())), live=live, deficit=320*T),
                  root=root, two_engine_signs=signs, supporting_inequalities=certs,
                  relaxed_outer_lower=price_lower, relaxed_outer_upper=price_upper,
                  baseline_kappa=str(old_k), all_T_grid_upper=str(new_k),
                  maximum_grid_headroom=str(new_k-old_k), maximum_grid_headroom_decimal=M.decimal(new_k-old_k),
                  source_sha256=PINS)
    need(not out.exists(), 'output preservation: choose a new file')
    out.write_text(json.dumps(result, indent=2)+'\n')
    print(result['status'], 'kappa_grid_upper='+price_upper['kappa_decimal'],
          'headroom='+result['maximum_grid_headroom_decimal'], 'component=all_T_upper_bound')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    main(parser.parse_args().out)
