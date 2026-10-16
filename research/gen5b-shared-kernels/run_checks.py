"""Reproduce the 70-pivot headline and 72-pivot fallback with every binding."""
import argparse
import json
from pathlib import Path

import assembly_arithmetic as arithmetic
import source_data as sd
import run_coretime12 as core
import chart_bounds
import check_shared_kernel as bridge72
import check_scalar_bounds as norm72
import check_kernel_bank_assignment as banks72
import check_pr300_composition as composition72
import kernel72_pricing as price72
import kernel72_charts as charts72
import kernel72_finite_bill as bill72
import check_kernel70 as bridge70
import check_kernel70_norm as norm70
import check_kernel70_bank_assignment as banks70
import check_pr300_kernel70_composition as composition70
import kernel70_pricing as price70
import kernel70_charts as charts70
import kernel70_finite_bill as bill70
import check_pr300_bases

HERE = Path(__file__).resolve().parent


def canonical(value):
    if isinstance(value, dict):
        value = {key: canonical(item) for key, item in value.items() if key != 'seconds'}
    elif isinstance(value, (list, tuple)):
        value = [canonical(item) for item in value]
    return json.loads(json.dumps(arithmetic.serial(value)))


def run(output_dir=None, write_streams=False):
    count = sd.verify_all()
    output = Path(output_dir) if output_dir is not None else None
    final12 = core.run(output / 'coretime12' if output else None, write_streams)
    full_final_charts = chart_bounds.run()
    results = {'coretime12/' + key: value for key, value in final12.items()}
    results['pr300-bases'] = check_pr300_bases.run()
    full_programs = {}
    for case, bridge, norm, banks, composition, price, charts, bill in (
        ('kernel72', bridge72, norm72, banks72, composition72, price72, charts72, bill72),
        ('kernel70', bridge70, norm70, banks70, composition70, price70, charts70, bill70),
    ):
        b = bridge.run(selection='union72') if case == 'kernel72' else bridge.run()
        n = norm.run()
        bank = banks.run(output / case if output else None)
        comp = composition.run()
        if case == 'kernel72':
            priced = price.run(b, final12['frames'], final12['local'])
        else:
            priced = price.run(b, final12['frames'], final12['local'], comp)
        assert arithmetic.F(bank['unreplicated_stock']) == arithmetic.F(priced['unreplicated_stock'])
        c = charts.run(b, full_final_charts, literal_stock=priced['literal_stock'])
        finite = bill.run(c, n, priced, b, bank, final12['suffix'],
                          composition=comp if case == 'kernel70' else None)
        for name, value in {'bridge': b, 'norm': n, 'banks': bank,
                            'composition': comp, 'pricing': priced,
                            'charts': core.compact_charts(c), 'finite-bill': finite}.items():
            results[case + '/' + name] = value
        full_programs[case] = c['factor_programs']
        if case == 'kernel72':
            pin = sd.MANIFEST['files']['pr300/descent2-selection.json']
            overlay = price.price_additional_histogram(
                priced, sd.read_bytes('pr300/descent2-selection.json'), pin)
            overlay_bill = bill.run(c, n, overlay, b, bank, final12['suffix'], composition=comp)
            results['kernel72/pr300-pricing'] = overlay
            results['kernel72/pr300-finite-bill'] = overlay_bill
    headline = results['kernel70/pricing']
    headline_bill = results['kernel70/finite-bill']
    results['summary'] = dict(
        status='PASS_UNIFIED_CHANGED_STAGE_CHECKS_UNDER_RETAINED_INTERFACES',
        verified_source_files=count,
        baseline_head=sd.HEAD,
        additional_head=results['kernel70/composition']['source_head'],
        headline_case='PR300 + final12 + 70 shared-donor pivots',
        kappa=headline['kappa'], kappa_decimal=headline['kappa_decimal'],
        literal_stock=headline['literal_stock'], calls=headline['calls'],
        rank_mass=headline['rank_mass'], deficit=headline['deficit'],
        displayed_finite_coefficient=headline_bill['displayed_finite_coefficient'],
        payload_upper=headline_bill['conservative_payload_upper'],
        payload_strict_gap=headline_bill['payload_strict_gap'],
        fallback_PR300_kernel72_kappa=results['kernel72/pr300-pricing']['kappa'],
        checkpoint_PR299_kernel72_kappa=results['kernel72/pricing']['kappa'],
        all_changed_role_bank_assignments=results['kernel70/banks']['total_stage_assignments'],
        inherited_assumptions=headline_bill['inherited_assumptions'],
        full_inherited_admission_replayed=False, all_size_theorem_verified=False,
        global_optimality_or_priority_claimed=False,
        verification_limits=[
            'The shared-kernel F2 all-column proof is compositional under the inherited old decoder, not a full physical-word replay.',
            'PR300 complete chronological/source-span admission remains inherited; scalar incidences, support disjointness and exact selected basis determinants are checked here.',
            'Original row bounds and unchanged compiler, chart, normalizer, routing, prime, setup, complex-supplier and all-size interfaces remain hypotheses.',
            'Displayed finite bounds do not supply unknown retained constants inside C_full.'
        ])
    results = {name: canonical(value) for name, value in results.items()}
    if output:
        for name, value in results.items():
            path = output / (name + '.json')
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(value, indent=2) + '\n')
        for case, programs in full_programs.items():
            (output / case / 'chart-factor-programs.json').write_text(
                json.dumps(canonical(programs), indent=2) + '\n')
    return results


def check_certificates(results):
    expected_names = {path.relative_to(HERE / 'certificates').as_posix()[:-5]
                      for path in (HERE / 'certificates').rglob('*.json')}
    if expected_names != set(results):
        raise ValueError('Committed certificate set differs from generated set')
    for name, actual in results.items():
        expected = json.loads((HERE / 'certificates' / (name + '.json')).read_text())
        if actual != expected:
            raise ValueError('Certificate drift: ' + name)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path)
    parser.add_argument('--write-streams', action='store_true')
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    if args.write_streams and args.output_dir is None:
        parser.error('--write-streams requires --output-dir')
    results = run(args.output_dir, args.write_streams)
    if args.check:
        check_certificates(results)
    print(json.dumps(results['summary'], indent=2))


if __name__ == '__main__':
    main()
