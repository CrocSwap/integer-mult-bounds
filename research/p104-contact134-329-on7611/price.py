#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Two directed complete-invoice prices for the #7611 contact rechart.

Adapted from Ali Romman's #7605 price.py. The dyadic integer-power and
independent directed log/exp engines retain their upstream authors and notices.
A price certifies declared invoices only; the candidate word, physical and
application obligations are separate. Execute only with the project lease.
"""
import argparse
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
import runpy
import sys

HERE = Path(__file__).resolve().parent
CLAIM = '0.003652740309'
TESTED = '0.003652740309007'
BIT_CAP = '0.00376669'
BASE_INVOICE_SHA256 = '3e02c92a82e403154a33dc4ad7cc7b49e3add55ec9a1f8db330b3ac32007ccbb'
DELTA_PAID = {'1': -34, '2': 34, '3': -17, '4': -17, '5': 17}


def require(ok, message):
    if not ok:
        raise ValueError(message)


def certify():
    require(not sys.flags.optimize, 'retained interval assertions must be enabled')
    build = runpy.run_path(str(HERE / 'build.py'))
    engine = runpy.run_path(str(HERE / 'retained/pr7605/retained/pricing/evaluate_recursive_power.py'))
    interval = runpy.run_path(str(HERE / 'retained/pr7605/retained/role902/engines/interval_gate.py'))
    old_path = HERE / 'retained/pr7611/data/invoice-new.json'
    new_path = HERE / 'data/invoice-new.json'
    old, old_pin = engine['load_invoice'](old_path)
    new, new_pin = engine['load_invoice'](new_path)
    require(old_pin['sha256'] == BASE_INVOICE_SHA256, '#7611 invoice bytes')
    require(new == build['invoice'](), 'candidate complete invoice differs from builder')
    comp = engine['compare_invoices'](old, new)
    require(comp['delta_paid'] == DELTA_PAID and comp['delta_targets'] == {}, 'complete invoice delta')
    require(comp['classification'] == 'uniformly_better', 'concave-order control')
    require(sum(old['paid'].values()) == 110281 and sum(new['paid'].values()) == 110264, 'paid calls')
    require(sum(new['targets'].values()) == 22461, 'productive calls')
    mass = lambda h: sum(int(r) * n for r, n in h.items())
    require(mass(new['targets']) - mass(new['paid']) == 1424, 'rank surplus')
    zero = dict(new, paid={}, targets={})

    def signed(inv):
        return {int(r): inv['targets'].get(r, 0) - inv['paid'].get(r, 0)
                for r in inv['targets'].keys() | inv['paid'].keys()}

    def sign_interval(inv, k):
        lo, hi = interval['moment'](signed(inv), k)
        require(lo > 0 or hi < 0, 'log/exp sign unresolved')
        return 1 if lo > 0 else -1

    def bracket(inv):
        # Exact rational bisection; neither a published decimal nor the proposed
        # claim is assumed to be a crossing. Both endpoints are then independently
        # checked by the dyadic engine as well as by the log/exp engine.
        lo, hi = Q('0.00365'), Q('0.00366')
        require(sign_interval(inv, lo) == 1 and sign_interval(inv, hi) == -1,
                'crossing outside bounded search interval')
        for _ in range(24):
            mid = (lo + hi) / 2
            if sign_interval(inv, mid) > 0:
                lo = mid
            else:
                hi = mid
        return lo, hi

    def point(label, inv, k, positive):
        power = engine['evaluate'](zero, inv, 1 - k, bits=256)
        wanted = 'new_cost_lower' if positive else 'new_cost_higher'
        require(power['classification'] == wanted, label + ': dyadic sign')
        lower, upper = interval['moment'](signed(inv), k)
        require(lower > 0 if positive else upper < 0, label + ': log/exp sign')
        return {'point': str(k), 'integer_power': power,
                'independent_moment': [str(Q(x, interval['B'])) for x in (lower, upper)]}

    def derivative(inv):
        total = (0, 0)
        for rank, count in signed(inv).items():
            endpoint = Q(BIT_CAP) if count >= 0 else Q(0)
            term = interval['mul'](interval['power'](rank, endpoint), interval['log'](rank))
            total = interval['add'](total, interval['smul'](term, -count))
        bound = Q(total[1], interval['B'])
        require(bound < 0, 'strictly decreasing full moment on BIT interval')
        return str(bound)

    old_lo, old_hi = bracket(old)
    new_lo, new_hi = bracket(new)
    claim, tested = Q(CLAIM), Q(TESTED)
    require(old_hi < claim < tested < new_lo < new_hi < Q(BIT_CAP), 'claim and crossing order')
    checks = {
        'old_lower': point('old lower', old, old_lo, True),
        'old_upper': point('old upper', old, old_hi, False),
        'candidate_at_old_upper': point('candidate at old upper', new, old_hi, True),
        'old_rejects_claim': point('old rejects claim', old, claim, False),
        'candidate_claim': point('candidate claim', new, claim, True),
        'candidate_tested': point('candidate tested', new, tested, True),
        'candidate_lower': point('candidate lower', new, new_lo, True),
        'candidate_upper': point('candidate upper', new, new_hi, False),
    }
    old_derivative, new_derivative = derivative(old), derivative(new)
    outer = interval['gate']({'T': new['targets'], 'P': new['paid']},
                             CLAIM, TESTED, str(new_lo), str(new_hi), BIT_CAP)
    require(outer['outer']['strict_count'] == 54 and outer['outer']['functional_count'] == 4,
            'all 58 outer predicates')
    return {
        'status': 'PASS_COMPLETE_DECLARED_INVOICE_PRICE',
        'claim': CLAIM, 'tested': TESTED, 'BIT_cap': BIT_CAP,
        'old_invoice': old_pin, 'candidate_invoice': new_pin,
        'comparison': comp, 'checks': checks,
        'old_fixed_invoice_ceiling': {'raw_bracket': [str(old_lo), str(old_hi)],
            'derivative_upper': old_derivative, 'interval': ['0', BIT_CAP], 'unique_crossing': True},
        'candidate_fixed_invoice_ceiling': {'raw_bracket': [str(new_lo), str(new_hi)],
            'derivative_upper': new_derivative, 'interval': ['0', BIT_CAP], 'unique_crossing': True,
            'headroom_over_claim_upper': str(new_hi - claim),
            'headroom_over_claim_lower': str(new_lo - claim),
            'scope': 'This exact complete invoice only; not an optimum over changed words, stock or callers.'},
        'gain_over_old_raw_upper': str(claim - old_hi), 'outer_gate': outer,
        'scope': 'Arithmetic on declared invoices; word legality, physical maps, complete application and premises are separate.'
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    report = certify()
    if args.write:
        (HERE / 'data/PRICE.json').write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
