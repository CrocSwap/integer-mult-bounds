"""All-replica signed-dual bound for the X54 joint-entrance k8 whole-owner family.

Adapted from k8-joint-entrances/independent/all_t_bound.py (tomdif/Codex, PR1148): the only changes are
the pinned provider plan (the rebound X54 plan, local profile {3:+2,4:-4,5:+2}) and the source root argument.

Adapted from jon314159's PR942 all_t_bound.py, with the joint-entrance k8 inventory.
Dual prices: chafreaky's PR795/890. See ../NOTICE.md. Apache-2.0.
Two exact rational engines certify the inequalities and endpoint signs.
This is an upper relaxation only: it does not establish physical feasibility.
"""
import argparse
import gzip
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
ROOT = None
ENGINE = 'research/complex-k492-owner-repair/vendor/multicold/engines/'
PINS = {'research/complex-k492-owner-repair/vendor/multicold/engines/moment.py': '81cbc864e106418fc7854322746f72180cb8110ff39f74450a3b8d55a82c1482', 'research/complex-k492-owner-repair/vendor/multicold/engines/base_two_moment.py': 'aee70c242a2f1d225528fabe2002e1564d1dc884797c07d28a831c7878ee9098', }
PLAN_SHA256 = 'd6b0609e9329ba9dbfe5f0cc64210ca8199308cccf8addccd79b19b6bf370ff1'
WIDTHS = (4, 5, 7, 8, 9)
PRICES = (-1, -20, -8, -2, 4)
CAPACITIES = {8: (672, 2), 16: (448, 4), 32: (448, 8), 48: (448, -13)}
INVENTORY = {4: 44, 5: 44, 7: 38, 8: 114, 9: 240}


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


def main(out, root, plan_path):
    global ROOT
    ROOT = root.resolve()
    for relative, expected in PINS.items():
        need(hashlib.sha256((ROOT/relative).read_bytes()).hexdigest() == expected, 'source drift: '+relative)
    need(hashlib.sha256(plan_path.read_bytes()).hexdigest() == PLAN_SHA256, 'source drift: X54 provider plan')
    M = load(ENGINE+'moment.py', 'retained_mercator')
    B = load(ENGINE+'base_two_moment.py', 'retained_atanh')
    plan = json.loads(gzip.decompress(plan_path.read_bytes()))
    provider = plan['provider_registry']['gauge44']
    local = {int(r): n for r, n in provider['actual_paid_profile'].items()}
    need(Counter(provider['widths']) == INVENTORY, 'fixed helper inventory')
    actual_caps = Counter(v[0] for v in plan['windows'].values())
    need({c: n*112//plan['T'] for c, n in actual_caps.items()} ==
         {c: n for c, (n, _) in CAPACITIES.items()}, 'fixed bin inventory per replica')
    upper, vectors = dual_tables()
    mass = sum(c*n for c, (n, _) in CAPACITIES.items())-9*sum(r*n for r, n in INVENTORY.items())
    signed = sum(n*p for n, p in CAPACITIES.values())+9*sum(INVENTORY[r]*p for r, p in zip(WIDTHS, PRICES))
    need((mass, signed, upper[0], upper[48]) == (14778, -3568, 0, -13), 'fixed-family coefficients')
    credit = 48*signed+13*mass
    need(credit == 20850 and Q(credit, 925) == Q(834, 37), 'dual credit demand')
    T = 37
    idle = {1: 834, 48: 11374}
    need(sum(r*n for r, n in idle.items()) == mass*T, 'formal relaxed idle mass')
    need(sum(upper[r]*n for r, n in idle.items()) == signed*T, 'dual equality')
    profile = Counter({r: 9*T*n for r, n in local.items()})
    profile.update(idle)
    live = 896*T
    need(73*live-sum(r*n for r, n in profile.items()) == 320*T, 'rank deficit')
    root = M.certify(profile, 73, live, False)
    lo, hi = Q(root['lower']), Q(root['upper'])
    signs = {}
    for name, z in [('lower', lo), ('upper', hi)]:
        first = M.moment(profile, 73, live, z)
        second = B.moment(73, live, list(profile.items()), z)
        need(first[1] < 1 and second[1] < 1 if name == 'lower' else first[0] > 1 and second[0] > 1,
             'two exact moment signs at '+name)
        signs[name] = dict(endpoint=str(z), mercator=[str(x-1) for x in first],
                           atanh=[str(x-1) for x in second])
    certs = {kind: ratio_certificate(engine, kind, upper, hi)
             for kind, engine in [('mercator', M), ('atanh', B)]}
    # The retained outer recipe always has a < b and kappa < a/(1+a).
    # Therefore b < hi implies kappa < hi/(1+hi), without assuming that
    # this formal relaxed profile can pass any finite or physical admission.
    ceiling = hi/(1+hi)
    ticks = ceiling*10**18
    grid = Q((ticks.numerator-1)//ticks.denominator, 10**18)
    result = dict(status='PASS_ALL_T_K8_JOINT_X54_SIGNED_DUAL_UPPER_RELAXATION',
                  scope='All positive integer replica counts, fixed X54 joint-entrance local word and widths, nine calls and 896 live wires per replica, whole helpers and fixed 8/16/32/48 bin inventory. Geometry, time windows, finite invoice and physical realization are relaxed. This does not construct a supplier at the upper bound and does not cover different circuits, split helpers, banks or recursion geometries.',
                  dual_bin_vectors=vectors, upper=upper, mass_per_replica=mass,
                  signed_price_per_replica=signed, credit_per_replica=credit,
                  normalized_idle={'1': '834/37', '48': '11374/37'},
                  equality_requires_replica_count_multiple_of=37,
                  formal_profile=dict(replicas=T, idle=idle, profile=dict(sorted(profile.items())),
                                      live=live, deficit=320*T),
                  root=root, two_engine_signs=signs, supporting_inequalities=certs,
                  kappa_strict_rational_upper=str(ceiling), kappa_strict_upper_decimal=M.decimal(ceiling),
                  all_T_grid_upper=str(grid), all_T_grid_upper_decimal=M.decimal(grid),
                  source_sha256=dict(PINS, x54_provider_plan=PLAN_SHA256))
    need(not out.exists(), 'output preservation: choose a new file')
    out.write_text(json.dumps(result, indent=2)+'\n')
    print(result['status'], result['all_T_grid_upper_decimal'])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--plan', type=Path, required=True)
    a = parser.parse_args()
    main(a.out, a.root, a.plan)
