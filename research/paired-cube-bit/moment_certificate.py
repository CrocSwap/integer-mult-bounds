#!/usr/bin/env python3
"""Exact rational moment certificate for the paired-cube bit word under PR #144's bit accounting.

Accounting (PR #144 notes/paired-cube-bit.tex and scripts/paired_cube_network.py, bit_certificate):
  m = 3h, W = 2v + R per cover vertex; children = 3 x (local internal + source data + target data) + one
  exterior child of width 3*dim(sigma) per selected gauge + 2v final children of width 2 (read from the profile).
  Coarse saving a0 = k/10^10 passes iff, with rational upper bounds log_upper / exp_upper (32-term atanh series
  with geometric tail; exp(u) <= 1+u+u^2/(2(1-u/3)); both rounded up to the grid 2^-120),
      1 - sum_r n_r r/(W m) * exp_upper(a0 * log_upper(m/r)) - added > 0,
      added = 10^-16 * (32 m^2 * #children)/(W m) * exp_upper(a0 * log_upper(m))   (full local-ring fallback),
  and the rank moment also contracts.  Effective bit saving a_b = (1 - 10^-3) a0 + 10^-3 * 384599/10^10.
The certificate reports the largest k on the 10^-10 grid that passes and checks that k+1 is rejected.
log_upper / exp_upper / up are copied verbatim from PR #144 scripts/three_stage_cover_network.py (icekylinx,
Apache-2.0); with --tree REPO the copies are checked against the repository functions.
Usage: python3 moment_certificate.py out/profile_p12.json [--tree REPO] [--output cert.json]
"""
import argparse, json, sys
from fractions import Fraction as Q
from pathlib import Path

GRID = 1 << 120
BAD = Q(1, 10 ** 16)
ATOM = Q(1, 1000)
OLD = Q(384599, 10 ** 10)
STEP = 10 ** 10


def require(c, msg):
    if not c:
        raise SystemExit('FAIL: ' + msg)


def up(x):
    return Q((x.numerator * GRID + x.denominator - 1) // x.denominator, GRID)


def log_upper(x):
    power = 0
    while x >= 2:
        x /= 2
        power += 1

    def small(y):
        z = (y - 1) / (y + 1)
        return 2 * sum((z ** (2 * j + 1) / (2 * j + 1) for j in range(32)), Q(0)) + 2 * z ** 65 / (65 * (1 - z * z))
    return up(power * small(Q(2)) + small(x))


def exp_upper(u):
    require(0 <= u < 3, 'Exponential enclosure')
    return up(1 + u + u * u / (2 * (1 - u / 3)))


def test(profile, k, logs, logm):
    m, W = profile['m'], profile['W_per_vertex']
    H = {int(r): n for r, n in profile['child_histogram'].items()}
    a0 = Q(k, STEP)
    upper = sum(Q(n * r, W * m) * exp_upper(a0 * logs[r]) for r, n in H.items())
    edges = sum(H.values())
    fallback = 32 * m * m
    added = BAD * Q(fallback * edges, W * m) * exp_upper(a0 * logm)
    rank_upper = Q(sum(r * n for r, n in H.items())) + BAD * fallback * edges
    ok = 1 - upper - added > 0 and rank_upper < W * m
    return ok, dict(coarse=a0, moment_upper=upper, added_bad_moment_upper=added, strict_gap=1 - upper - added,
                    rank_mass_upper=rank_upper, fallback_children_per_edge=fallback, edge_count=edges)


def certify(profile):
    h, v, R, ell = (profile[k] for k in ('h', 'v', 'R', 'loss'))
    m, W = profile['m'], profile['W_per_vertex']
    require(m == 3 * h and W == 2 * v + R, 'PR144 bit accounting m=3h, W=2v+R')
    H = {int(r): n for r, n in profile['child_histogram'].items()}
    require(all(0 < r < m and n > 0 for r, n in H.items()), 'proper children')
    mass = sum(r * n for r, n in H.items())
    require(mass == profile['rank_per_vertex'] and W * m - mass == 2 * v - 3 * ell == profile['deficit_per_vertex'],
            'telescoping deficit 2v - 3 ell')
    logs = {r: log_upper(Q(m, r)) for r in H}
    logm = log_upper(Q(m))
    lo, hi = 0, 10 ** 7          # a0 in [0, 1e-3)
    require(test(profile, lo, logs, logm)[0], 'zero saving passes')
    require(not test(profile, hi, logs, logm)[0], 'upper bracket rejected')
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if test(profile, mid, logs, logm)[0]:
            lo = mid
        else:
            hi = mid
    ok, best = test(profile, lo, logs, logm)
    nok, nxt = test(profile, lo + 1, logs, logm)
    require(ok and not nok, 'largest grid point and rejected successor')
    a0 = Q(lo, STEP)
    ab = (1 - ATOM) * a0 + ATOM * OLD
    require(ATOM > ab and ATOM < 1 - ab, 'subordinate adapter and row tolls')
    require(Q(2 * m ** 3, 2 ** 80) < BAD, 'fixed prime bad-class allowance')
    s = lambda q: '%d/%d' % (q.numerator, q.denominator)
    return dict(h=h, v=v, R=R, loss=ell, m=m, W_per_vertex=W, rank_per_vertex=mass, deficit_per_vertex=W * m - mass,
                coarse_saving=s(a0), coarse_saving_float=float(a0), strict_gap=s(best['strict_gap']),
                strict_gap_float=float(best['strict_gap']), moment_upper=s(best['moment_upper']),
                added_bad_moment_upper=s(best['added_bad_moment_upper']), rank_mass_upper=s(best['rank_mass_upper']),
                next_grid_point=s(Q(lo + 1, STEP)), next_grid_gap_float=float(nxt['strict_gap']), next_grid_rejected=True,
                atom_exponent=s(ATOM), ordinary_leaf_saving=s(OLD), effective_bit_saving=s(ab), effective_bit_saving_float=float(ab),
                bad_fraction=s(BAD), fallback_children_per_edge=best['fallback_children_per_edge'], edge_count=best['edge_count'],
                logarithm_upper_bounds={str(r): s(logs[r]) for r in sorted(logs)}, rounding_denominator=GRID,
                method='PR144 bit_certificate: exact rational upper moment with full 32m^2 fallback on 1e-16 of every edge')


def main():
    require(not sys.flags.optimize, 'run without -O')
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('profile', type=Path)
    ap.add_argument('--tree', type=Path)
    ap.add_argument('--output', type=Path)
    a = ap.parse_args()
    if a.tree:
        sys.path.insert(0, str(a.tree / 'scripts'))
        import three_stage_cover_network as t
        for x in (Q(72, 5), Q(72), Q(66, 20), Q(78, 7)):
            require(t.log_upper(x) == log_upper(x), 'log_upper equals repository function')
        for u in (Q(1, 1000), Q(123, 10 ** 5)):
            require(t.exp_upper(u) == exp_upper(u), 'exp_upper equals repository function')
    cert = certify(json.loads(a.profile.read_text()))
    text = json.dumps(cert, indent=1, sort_keys=True) + '\n'
    if a.output:
        a.output.write_text(text)
    print('PASS coarse a0 = %s (%.10e), next grid point rejected; effective a_b = %s (%.10e)' % (
        cert['coarse_saving'], cert['coarse_saving_float'], cert['effective_bit_saving'], cert['effective_bit_saving_float']))


if __name__ == '__main__':
    main()
