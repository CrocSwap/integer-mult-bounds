#!/usr/bin/env python3
"""Independent exact enclosure, assembly and negative-control verification."""
import sys
sys.dont_write_bytecode = True
if sys.flags.optimize:
    raise ValueError('Assertions must remain enabled')
import argparse
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
import refine

ROOT = refine.ROOT
HERE = Path(__file__).resolve().parent


def log_interval(x):
    """Atanh expansion with independent 3/2 reduction and 60 exact terms."""
    assert x >= 1
    k = 0
    while x > Q(3, 2):
        x /= Q(3, 2)
        k += 1
    def small(y):
        z = (y-1)/(y+1)
        power, total = z, Q()
        for j in range(60):
            total += power/Q(2*j+1)
            power *= z*z
        return 2*total, 2*total+2*power/(121*(1-z*z))
    lo, hi = small(x)
    blo, bhi = small(Q(3, 2))
    return lo+k*blo, hi+k*bhi


def independent_moment(profile, saving, recorded_terms):
    low, high = Q(), Q()
    rows = {int(t): n for t, n in profile['child_multiplicities'].items()}
    for t, n in sorted(rows.items()):
        lo, hi = log_interval(Q(profile['m'], t))
        recorded = recorded_terms[str(t)]
        assert Q(recorded['log_lower']) <= lo <= hi <= Q(recorded['log_upper'])
        u, v = lo*saving, hi*saving
        assert 0 < u <= v < Q(1, 1000)
        # Directed rounding of input logs bounds rational denominator sizes.
        u = Q(refine.floor_scaled(u, 10**40), 10**40)
        v = Q(refine.ceiling_scaled(v, 10**40), 10**40)
        tlo, thi = Q(1), Q(1)
        elo, ehi = Q(1), Q(1)
        for j in range(1, 13):
            tlo, thi = tlo*u/j, thi*v/j
            elo, ehi = elo+tlo, ehi+thi
        # First omitted term is degree13; subsequent ratios <1/2.
        ehi += 2*thi*v/13
        weight = Q(t*n, profile['m']*profile['W'])
        low += weight*Q(refine.floor_scaled(elo, 10**40), 10**40)
        high += weight*Q(refine.ceiling_scaled(ehi, 10**40), 10**40)
    return low, high


def audit(certificate):
    profile_path = ROOT/certificate['profile_path']
    assert sha256(profile_path.read_bytes()).hexdigest() == certificate['profile_sha256']
    for name, digest in certificate['source_sha256'].items():
        assert sha256((ROOT/name).read_bytes()).hexdigest() == digest, name
    source = json.loads(profile_path.read_text())
    p = source['bit']
    assert sum(int(t)*n for t, n in p['child_multiplicities'].items()) == p['total_rank']
    accepted = independent_moment(p, Q(certificate['bit_saving']), certificate['accepted_moment']['terms'])
    rejected = independent_moment(p, Q(certificate['next_bit_saving']), certificate['accepted_moment']['terms'])
    assert accepted[1] < 1 < rejected[0]
    controls = {}
    for name, variant in [('preferred', certificate['preferred']), ('coarse_grid_control', certificate['coarse_grid_control'])]:
        params = variant['assembly']['parameters']
        result = refine.balanced.assembly(source['finite_bridge'], Q(params['a_bit']), Q(params['kappa']), h=Q(params['h']))
        assert refine.arithmetic.js(result) == variant['assembly']
        assert len(result['constraints']) == 47 and len(result['margins']) == 7
        assert all(v > 0 for v in result['constraints'].values())
        for label, kwargs in [('next_grid', dict(kappa=Q(variant['next_kappa']))),
                              ('zero_backoff', dict(h=Q())),
                              ('original_prefix', dict(original_prefix=True)),
                              ('old_guard', dict(old_guard=True)),
                              ('old_exposures', dict(old_exposures=True))]:
            call = dict(a_bit=Q(params['a_bit']), kappa=Q(params['kappa']), h=Q(params['h']))
            call.update(kwargs)
            try:
                refine.balanced.assembly(source['finite_bridge'], **call)
            except refine.balanced.InvalidAssembly as error:
                controls[name+'/'+label] = str(error)
            else:
                raise AssertionError('Negative control accepted: '+name+'/'+label)
    next_a = Q(certificate['next_bit_saving'])
    best = Q(certificate['preferred']['kappa'])
    cap = next_a/(1+next_a)
    assert cap > best
    return dict(status='PASS', independent_log_base='3/2', independent_log_terms=60,
        independent_exp_degree=12, independent_tail='twice first omitted term',
        independent_accepted_gap=1-accepted[1], independent_rejected_gap=rejected[0]-1,
        variants_reassembled=2, constraints_each=47, margins_each=7, controls=controls,
        fixed_profile_balanced_family_kappa_strict_upper=cap,
        remaining_possible_parameter_gain_upper=cap-best)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--certificate', type=Path, default=HERE/'certificate.json')
    parser.add_argument('--receipt', type=Path, default=HERE/'audit-receipt.json')
    parser.add_argument('--record', action='store_true')
    args = parser.parse_args()
    result = refine.arithmetic.js(audit(json.loads(args.certificate.read_text())))
    if args.record:
        args.receipt.write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    else:
        assert result == json.loads(args.receipt.read_text()), 'Independent receipt changed'
    print('PASS independent logarithm/exponential enclosures; 47 strict constraints; seven margins; ten assembly negative controls')


if __name__ == '__main__':
    main()
