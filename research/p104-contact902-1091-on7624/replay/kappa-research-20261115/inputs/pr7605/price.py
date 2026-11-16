#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Certify both complete prices and the fixed-invoice crossing.

Ali Romman, with substantial OpenAI Codex assistance. The two directed engines
retain their source credit. The derivative argument follows Hao Yan/7604.
"""
import argparse
from fractions import Fraction as Q
import json
from pathlib import Path
import runpy
import sys

HERE = Path(__file__).resolve().parent
BUILD = runpy.run_path(str(HERE / 'build.py'))
require = BUILD['require']
LOWER = '0.0036504442447168877'
UPPER = '0.0036504442447168879'
PRIOR_UPPER = '0.0036502223358273'
BIT_CAP = Q('0.00376669')


def certify():
    require(not sys.flags.optimize, 'retained interval assertions must be enabled')
    BUILD['authenticate']()
    engine = runpy.run_path(str(HERE / 'retained/pricing/evaluate_recursive_power.py'))
    interval = runpy.run_path(str(HERE / 'retained/role902/engines/interval_gate.py'))
    old, _ = engine['load_invoice'](HERE / 'retained/pr7604/invoice-new.json')
    new, _ = engine['load_invoice'](HERE / 'data/invoice-new.json')
    require(new == BUILD['invoice'](), 'exact complete invoice')
    comparison = engine['compare_invoices'](old, new)
    require(comparison['delta_paid'] == {'1': -34, '2': 17}, 'complete paid delta')
    require(comparison['delta_targets'] == {}, 'unchanged productive targets')
    require(comparison['classification'] == 'uniformly_better', 'strict concave saving')
    zero = dict(new, paid={}, targets={})
    points = [
        ('old_upper', old, PRIOR_UPPER, 'new_cost_higher'),
        ('claim', new, BUILD['CLAIM'], 'new_cost_lower'),
        ('claim_plus_slack', new, '0.00365044424467', 'new_cost_lower'),
        ('raw_lower', new, LOWER, 'new_cost_lower'),
        ('raw_upper', new, UPPER, 'new_cost_higher'),
    ]
    certificates = []
    for label, invoice, point, expected in points:
        result = engine['evaluate'](zero, invoice, 1 - Q(point), bits=256)
        require(result['classification'] == expected, label + ': directed integer-power sign')
        signed = {int(r): invoice['targets'].get(r, 0) - invoice['paid'].get(r, 0)
                  for r in invoice['targets'].keys() | invoice['paid'].keys()}
        lo, hi = interval['moment'](signed, Q(point))
        require(lo > 0 if expected == 'new_cost_lower' else hi < 0,
                label + ': independent log/exp sign')
        certificates.append(dict(label=label, kappa=point, integer_power=result,
                                 independent_moment=[str(Q(x, interval['B'])) for x in (lo, hi)]))
    control = engine['evaluate'](zero, old, 1 - Q(BUILD['CLAIM']), bits=256)
    require(control['classification'] == 'new_cost_higher', 'predecessor rejects new claim')
    signed = {int(r): new['targets'].get(r, 0) - new['paid'].get(r, 0)
              for r in new['targets'].keys() | new['paid'].keys()}
    require(sum(r * n for r, n in signed.items()) == 1424, 'rank surplus')
    derivative = (0, 0)
    for rank, count in signed.items():
        endpoint = BIT_CAP if count >= 0 else Q(0)
        term = interval['mul'](interval['power'](rank, endpoint), interval['log'](rank))
        derivative = interval['add'](derivative, interval['smul'](term, -count))
    bound = Q(derivative[1], interval['B'])
    require(bound < 0, 'strictly decreasing full moment on the BIT interval')
    gain = Q(BUILD['CLAIM']) - Q(PRIOR_UPPER)
    require(gain > 0 and 100 * gain / Q(PRIOR_UPPER) < 1, 'positive gain below one percent')
    return dict(status='PASS_HELPER757_COMPLETE_PRICE', claim=BUILD['CLAIM'],
                prior_crossing_upper=PRIOR_UPPER, gain_over_prior_upper=str(gain),
                paid_calls=110366, productive_calls=22461, rank_surplus=1424,
                comparison=comparison, certificates=certificates, restored_cost_control=control,
                fixed_invoice_ceiling=dict(raw_bracket=[LOWER, UPPER],
                                          interval=['0', str(BIT_CAP)], derivative_upper=str(bound),
                                          unique_crossing=True,
                                          headroom_over_claim_upper=str(Q(UPPER) - Q(BUILD['CLAIM'])),
                                          scope='This exact complete invoice only. No optimum over changed words or stock.'))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    report = certify()
    path = HERE / 'data/PRICE.json'
    if args.write:
        path.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
    require(report == json.loads(path.read_bytes()), 'deterministic price receipt')
    print(json.dumps(dict(status=report['status'], claim=report['claim'],
                         gain_over_prior_upper=report['gain_over_prior_upper'],
                         raw_bracket=report['fixed_invoice_ceiling']['raw_bracket'])))


if __name__ == '__main__':
    main()
