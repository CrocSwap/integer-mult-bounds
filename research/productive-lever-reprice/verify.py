#!/usr/bin/env python3
"""Re-price the one-at-a-time lever table of #1240 on the productive-helper invoices of #4470.

Model (#4470 PROOF.md section 5): a supplier's raw saving C is the root of
    sum_r T_r r^(1-C) = sum_r P_r r^(1-C)
over its complete target (productive) and paid profiles.  Complex profiles are
research/joint-helper-lattice/RESULT.json; the BIT profile is the unchanged
research/query-thinned-controllers/RESULT.json bit_invoice.  kappa is limited by
min(complex, BIT).  Every lever is an ideal relaxation, like the #1240 table:
the changed work is removed or merged with no new charge.

Checks, with exact interval arithmetic (mixed_target_probe log/exp series, rounded outward):
1. Both complete profiles are rebuilt from their physical parts: 18 full local
   calls, 15 query-only shears (one rank-one job per port), whole-idle stages,
   and for complex the 8 rank-8 owned-centre jobs per call.
2. Baseline raw roots: complex 0.0030201660 (#4470 bracket), BIT 0.0034642490.
3. Paid-moment shares of each part at t = 1 - C.
4. Raw roots of every lever on each side, with certified brackets.
Roots: a float bisection proposes the first sign change, and exact interval
moments certify the sign on both ends of a 1e-10 bracket.  Uniqueness of the
root is not certified.  "No root below 1/6" means the certified surplus is still
positive at C = 1/6 (the interval engine needs C log r < 1).
Controls: an empty lever reproduces the baseline bracket; one extra paid
rank-one job lowers the complex root.
Standard library only. Prepared by Matarener with Claude Code assistance.
Apache-2.0.
"""
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path
import importlib.util
import json
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PORTS = {'complex': 112, 'bit': 111}
CAP = Q(1, 6)  # h_interval needs C*log(r) < 1 for r <= 145


def need(ok, why):
    if not ok:
        raise SystemExit('FAIL: ' + why)


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


E = load(ROOT/'research/kappa-rebuild/architecture/mixed_target_probe.py', 'lever_probe')


def ints(d):
    return Counter({int(k): v for k, v in d.items()})


SCALE = 2**128


def outward(x, up):
    n = x*SCALE
    k = n.numerator//n.denominator
    return Q(k+(1 if up and k != n else 0), SCALE)


def h_interval(r, c):
    """Enclosure of r^(1-c) from mixed_target_probe's log/exp series, rounded outward to 2^-128."""
    if r in (0, 1):
        return Q(r), Q(r)
    a, b = E.log_interval(r)
    lo_x, hi_x = outward(c*a, False), outward(c*b, True)
    low, _ = E.exp_interval(lo_x)
    _, high = E.exp_interval(hi_x)
    return outward(Q(r)/high, False), outward(Q(r)/low, True)


def moment(prof, c):
    low = high = Q(0)
    for r, n in prof.items():
        if n:
            a, b = h_interval(r, c)
            low += n*(a if n >= 0 else b)
            high += n*(b if n >= 0 else a)
    return low, high


def surplus(T, P, c):
    a, b = moment(T, c), moment(P, c)
    return a[0]-b[1], a[1]-b[0]


def float_surplus(T, P, c):
    return (sum(float(n)*r**(1-c) for r, n in T.items() if n)
            - sum(float(n)*r**(1-c) for r, n in P.items() if n))


def root(T, P, width=Q(1, 10**10)):
    """Certified bracket (pos, neg) of the raw root, or None when the surplus stays positive at C=CAP.

    A float bisection proposes the root; exact interval moments then certify the sign on
    both ends of a bracket of the given width.
    """
    need(surplus(T, P, Q(0))[0] > 0, 'surplus positive at C=0')
    if surplus(T, P, CAP)[0] > 0:
        return None
    lo, hi = 0.0, float(CAP)
    for _ in range(80):
        mid = (lo+hi)/2
        lo, hi = (mid, hi) if float_surplus(T, P, mid) > 0 else (lo, mid)
    guess = Q(lo).limit_denominator(10**13)
    pos, neg = max(Q(0), guess-width/2), guess+width/2
    need(surplus(T, P, pos)[0] > 0 and surplus(T, P, neg)[1] < 0, 'certified root bracket')
    return pos, neg


def merge(prof, size):
    out = Counter({r: n for r, n in prof.items() if r >= size})
    out[size] += Q(sum(r*n for r, n in prof.items() if r < size), size)
    return out


def complex_parts():
    d = json.loads((ROOT/'research/joint-helper-lattice/RESULT.json').read_text())
    T, P = ints(d['targets']), ints(d['paid'])
    calls, shears = d['full_calls'], d['query_shears']
    lp = ints(d['local_paid'])
    need((calls, shears) == (18, 15), 'complex: 18 full calls and 15 query shears')
    parts = {'centre': Counter({8: calls*lp[8]}),
             'local': Counter({r: calls*n for r, n in lp.items() if r != 8}),
             'shears': Counter({1: shears*PORTS['complex']})}
    idle = Counter(P)
    for p in parts.values():
        idle.subtract(p)
    parts['idle'] = +idle
    need(min(idle.values()) >= 0 and min(parts['idle']) >= 16, 'complex idle ranks are the whole-idle 16..72')
    helpers = Counter({r: calls*n for r, n in ints(d['local_helpers']).items()})
    main = Counter(T)
    main.subtract(helpers)
    need(min(main.values()) >= 0 and all((r-1) % 8 == 0 for r in +main), 'complex main targets have rank 1+8k')
    return T, parts


def bit_parts():
    d = json.loads((ROOT/'research/query-thinned-controllers/RESULT.json').read_text())['bit_invoice']
    T, P = ints(d['targets']), ints(d['paid'])
    idle = ints(d['whole_idle'])
    shears = Counter({1: d['thin_queries']})
    need((d['thick_calls'], d['thin_queries']) == (18, 15*PORTS['bit']), 'BIT: 18 thick calls and 15 x 111 queries')
    local = Counter(P)
    local.subtract(idle)
    local.subtract(shears)
    local = +local
    need(local == Counter({r: 18*n for r, n in {1: 1323, 2: 1342, 3: 79, 4: 44, 5: 102, 6: 11, 7: 19}.items()}),
         'BIT local paid = 18 x PR589 local profile')
    need(T[8] == 18*439, 'BIT helpers: 18 x 439 of rank 8')
    return T, {'centre': Counter(), 'local': local, 'shears': shears, 'idle': idle}


def assemble(parts, **change):
    P = Counter()
    for k, p in parts.items():
        P.update(change.get(k, p))
    return +P


LEVERS = {
    'centre_free': lambda p: {'centre': Counter()},
    'centre_shared_by_two_calls': lambda p: {'centre': Counter({r: Q(n, 2) for r, n in p['centre'].items()})},
    'rank16_local_children': lambda p: {'local': merge(p['local'], 16)},
    'two_unpaid_coordinates_per_idle_family': lambda p: {'idle': Counter({r-2: n for r, n in p['idle'].items()})},
    'centre_free_and_rank16_children': lambda p: {'centre': Counter(), 'local': merge(p['local'], 16)},
    'query_shears_free': lambda p: {'shears': Counter()},
    'idle_stages_free': lambda p: {'idle': Counter()},
    'no_rank1_local_jobs_merge_to_rank2': lambda p: {'local': merge(p['local'], 2)},
}
EXPECTED_BASE = {'complex': '0.0030201659', 'bit': '0.0034642489'}


def fmt(r):
    return None if r is None else [f'{float(r[0]):.10f}', f'{float(r[1]):.10f}']


def main():
    out = {'model': 'raw root of sum T r^(1-C) = sum P r^(1-C); ideal levers, no new charges', 'sides': {}}
    for side, (T, parts) in (('complex', complex_parts()), ('bit', bit_parts())):
        P = assemble(parts)
        base = root(T, P)
        need(fmt(base)[0].startswith(EXPECTED_BASE[side]), f'{side} baseline root')
        if side == 'complex':
            need(base[0] <= Q('0.0030201659771') and base[1] >= Q('0.0030201659770'), 'complex bracket meets #4470 root')
            extra = Counter(P)
            extra[1] += 1
            need(root(T, extra)[1] <= base[1] and root(T, extra)[0] < base[0], 'one extra paid job lowers the root (control)')
        need(root(T, assemble(parts, **{})) == base, f'{side}: empty lever reproduces baseline (control)')
        t = 1-base[0]
        total = moment(P, base[0])[0]
        shares = {k: f'{float(moment(p, base[0])[0]/total):.4%}' for k, p in parts.items() if p}
        mass = {k: int(sum(r*n for r, n in p.items())) for k, p in parts.items()}
        levers = {}
        for name, f in LEVERS.items():
            if side == 'bit' and 'centre' in name and name != 'centre_free_and_rank16_children':
                continue
            r = root(T, assemble(parts, **f(parts)))
            levers[name] = {'raw_root_bracket': fmt(r), 'no_root_below_one_sixth': r is None,
                            'ratio_to_baseline': None if r is None else f'{float(r[0]/base[0]):.3f}'}
        out['sides'][side] = {'baseline_root_bracket': fmt(base), 'paid_parts_mass': mass,
                              'paid_moment_share': shares, 'surplus_mass': int(sum(r*n for r, n in T.items()) - sum(r*n for r, n in P.items())),
                              'levers': levers}
        print(side, fmt(base), shares, flush=True)
        for k, v in levers.items():
            print('  ', k, v, flush=True)
    need(out['sides']['complex']['surplus_mass'] == 752 and out['sides']['bit']['surplus_mass'] == 753, 'surplus masses 752/753')
    need(all(out['sides'][x]['levers']['idle_stages_free']['no_root_below_one_sixth'] for x in out['sides']),
         'free idle stages keep the surplus positive through C = 1/6 on both sides (reported)')
    (HERE/'RESULT.json').write_text(json.dumps(out, indent=2, sort_keys=True)+'\n', newline='\n')
    print('PASS_PRODUCTIVE_LEVER_REPRICE', flush=True)


if __name__ == '__main__':
    main()
