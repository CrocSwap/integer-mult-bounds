#!/usr/bin/env python3
"""Reproduce nine candidate-math corruptions and the PR265 exact regression.

Consumes receipts from an already completed source-bound replay. It performs
no native compilation or physical-word replay and does not replace those checks.
"""
import argparse
import copy
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

if not __debug__:
    raise SystemExit('assertions required')
sys.dont_write_bytecode = True


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load(path):
    return json.loads(Path(path).read_text())


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--package', type=Path, required=True,
                    help='crosscut-response-pairs source directory')
    ap.add_argument('--baseline', type=Path, required=True,
                    help='completed PR265 replay directory, with candidate-certificate.json')
    ap.add_argument('--candidate', type=Path, required=True,
                    help='completed candidate directory, with native price and invoice')
    ap.add_argument('--primitives', type=Path,
                    help='retained fixed_prime_math.py; default is adjacent inherited package')
    ap.add_argument('--output', type=Path, required=True)
    a = ap.parse_args()
    assert not a.output.exists(), 'use a fresh output path'
    module_path = a.package / 'candidate_math.py'
    primitives = a.primitives or a.package.parent / 'multicut-kernel-condensation-descent-fixed-prime/fixed_prime_math.py'
    spec = importlib.util.spec_from_file_location('audited_candidate_math', module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    paths = {
        'candidate_math': module_path,
        'retained_primitives': primitives,
        'baseline_certificate': a.baseline / 'candidate-certificate.json',
        'baseline_native_price': a.baseline / 'lead/COHORT-EXACT-PRICE.json',
        'baseline_finite_invoice': a.baseline / 'temporal/COHORT-FINITE-INVOICE.json',
        'candidate_native_price': a.candidate / 'COHORT-EXACT-PRICE.json',
        'candidate_finite_invoice': a.candidate / 'COHORT-FINITE-INVOICE.json',
    }
    baseline = load(paths['baseline_certificate'])
    original = baseline['mathematics']
    regression = module.compute(load(paths['baseline_native_price']),
                                load(paths['baseline_finite_invoice']), a.baseline,
                                primitives, original, require_improvement=False)
    assert regression['kappa'] == original['kappa']
    assert regression['coarse_rate'] == original['coarse_rate']
    assert regression['assembly'] == original['assembly']
    for key in ('initial', 'levels', 'chain', 'gaps'):
        assert regression['ordinary_bootstrap'][key] == original['ordinary_bootstrap'][key]
    assert regression['finite_admission']['finite_cutoff_checks'] == baseline['finite_admission']['finite_cutoff_checks']
    for key in ('delta_tau', 'delta_linear'):
        assert regression['finite_admission'][key] == baseline['finite_admission']['moment_gaps'][key]

    price = load(paths['candidate_native_price'])
    invoice = load(paths['candidate_finite_invoice'])
    valid = module.compute(price, invoice, a.baseline, primitives, original)
    mutations = {
        'literal_stock': ('invoice', ('literal_stock',), int(invoice['literal_stock']) + 1),
        'literal_histogram': ('invoice', ('literal_histogram', next(iter(invoice['literal_histogram']))),
                              int(invoice['literal_histogram'][next(iter(invoice['literal_histogram']))]) + 1),
        'coefficient': ('invoice', ('full_counted_primitive_coefficient',), str(2**80)),
        'selectors': ('invoice', ('extra_selector_calls',), str(2**40)),
        'chart_bound': ('invoice', ('new_chart_factor_max',), 549),
        'payload': ('invoice', ('payload_signed_prefix_upper',), str(2**104)),
        'profile_count': ('price', ('cohort_candidate', 'calls'), int(price['cohort_candidate']['calls']) + 1),
        'profile_rank': ('price', ('cohort_candidate', 'rank_mass'), int(price['cohort_candidate']['rank_mass']) + 1),
        'native_baseline': ('price', ('baseline', 'kappa'), '0'),
    }
    rejected = {}
    for name, (target, path, value) in mutations.items():
        bad_price, bad_invoice = copy.deepcopy(price), copy.deepcopy(invoice)
        node = bad_price if target == 'price' else bad_invoice
        for key in path[:-1]:
            node = node[key]
        node[path[-1]] = value
        try:
            module.compute(bad_price, bad_invoice, a.baseline, primitives, original)
        except AssertionError as error:
            rejected[name] = dict(target=target, field=list(path), replacement=value,
                                  error=str(error))
        else:
            raise AssertionError('corrupted receipt admitted: ' + name)
    result = dict(
        status='PASS_EXACT_ARITHMETIC_REGRESSION_AND_CORRUPTION_CONTROLS',
        full_physical_replay_claimed=False,
        baseline_coarse_intervals_identical=True,
        baseline_all_47_constraints_and_7_margins_identical=True,
        baseline_eight_levels_and_cutoffs_identical=True,
        valid_candidate_kappa=valid['kappa'],
        retained_engine_hashes=valid['retained_engine_hashes'],
        negative_controls_rejected=list(rejected), controls=rejected,
        sources={key: dict(path=str(path.resolve()), sha256=sha(path)) for key, path in paths.items()},
    )
    a.output.write_text(json.dumps(result, sort_keys=True, indent=2) + '\n')
    print(json.dumps({key: result[key] for key in ('status', 'valid_candidate_kappa', 'negative_controls_rejected')}))


if __name__ == '__main__':
    main()
