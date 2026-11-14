#!/usr/bin/env python3
"""Certified full-invoice comparison; circuit admission is checked separately.

Hao Yan (@FanPUYen), substantial OpenAI Codex assistance. Apache-2.0.
Retains the exact integer-power bounds of aliromman and predecessor credits.
"""
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
import runpy
import sys

HERE = Path(__file__).resolve().parent
# Authenticate executable retained sources before importing them. The registered
# launcher also provides a fresh bytecode-cache namespace.
for row in json.loads((HERE / 'SOURCE-VERSIONS.json').read_bytes())['files']:
    if hashlib.sha256((HERE / row['path']).read_bytes()).hexdigest() != row['sha256']:
        raise ValueError('retained source mismatch: ' + row['path'])
sys.path.insert(0, str(HERE / 'retained/pricing'))
from compare_recursive_invoices import compare_invoices, load_invoice, require
from evaluate_recursive_power import evaluate
sys.path.pop(0)


def main():
    versions = json.loads((HERE / 'SOURCE-VERSIONS.json').read_bytes())
    for row in versions['files']:
        require(hashlib.sha256((HERE / row['path']).read_bytes()).hexdigest() == row['sha256'],
                'retained source mismatch: ' + row['path'])
    prior, _ = load_invoice(HERE / 'data/invoice-7603.json')
    new, _ = load_invoice(HERE / 'data/invoice-new.json')
    zero = dict(new, paid={}, targets={})
    comparison = compare_invoices(prior, new)
    require(comparison['delta_paid'] == {'1': -34, '2': 17}, 'paid delta')
    require(comparison['delta_targets'] == {}, 'productive targets unchanged')
    require(comparison['classification'] == 'uniformly_better', 'strict concave gain')
    require(comparison['power_moment']['new_minus_old_sign'] == 'strictly_negative', 'power gain')
    points = [
        ('prior_upper', prior, '0.003650000454084', 'new_cost_higher'),
        ('claim', new, '0.0036502223357', 'new_cost_lower'),
        ('claim_plus_seven_1e14_gaps', new, '0.00365022233577', 'new_cost_lower'),
        ('root_lower', new, '0.0036502223358272', 'new_cost_lower'),
        ('root_upper', new, '0.0036502223358273', 'new_cost_higher'),
    ]
    certificates = []
    for label, invoice, point, expected in points:
        report = evaluate(zero, invoice, 1 - Q(point), bits=256)
        require(report['classification'] == expected, label + ': ' + report['classification'])
        certificates.append({'label': label, 'kappa': point, 'certificate': report})
    # The negative control restores the omitted two rank-1 costs and
    # removes the fused rank-2 jobs, recovering the predecessor exactly.
    restored = dict(new, paid=dict(new['paid']))
    for rank, delta in [('1', 34), ('2', -17)]:
        restored['paid'][rank] += delta
    require(restored == prior, 'cost-restoration control')
    control = evaluate(zero, restored, 1 - Q('0.0036502223357'), bits=256)
    require(control['classification'] == 'new_cost_higher', 'old invoice must reject new claim')
    ceiling = runpy.run_path(str(HERE / 'ceiling.py'))['certify']()
    require(ceiling == json.loads((HERE / 'data/CEILING.json').read_bytes()),
            'fresh derivative and scoped ceiling certificate')
    print(json.dumps({'status': 'PASS_ROLE315_DIRECTED_PRICE',
                      'claim': '0.0036502223357',
                      'gain_over_prior_certified_upper': str(Q('0.0036502223357')-Q('0.003650000454084')),
                      'comparison': comparison, 'power_certificates': certificates,
                      'restored_cost_control': control,
                      'scoped_ceiling': ceiling}, indent=2))


if __name__ == '__main__':
    main()
