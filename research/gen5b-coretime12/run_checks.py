"""Reproduce the independently authored changed-stage checks and exact pricing."""
import argparse
import hashlib
import json
from pathlib import Path

import assembly_arithmetic as arithmetic
import baseline_arithmetic as baseline
import chart_bounds
import check_bank_assignment
import check_complete_suffix
import check_coretime
import check_suffix_frames
import reprice
import finite_bill
import scalar_norm_transport
import source_data

HERE = Path(__file__).resolve().parent


def compact_charts(value):
    value = dict(value)
    programs = value.pop('factor_programs')
    value['chart_summaries'] = []
    for program in programs:
        summary = {key: item for key, item in program.items()
                   if key not in ('basis_columns', 'factors')}
        data = json.dumps(arithmetic.serial(program), sort_keys=True,
                          separators=(',', ':')).encode()
        summary['factor_program_sha256'] = hashlib.sha256(data).hexdigest()
        value['chart_summaries'].append(summary)
    return value


def run(output_dir=None, write_streams=False):
    source_data.verify_all()
    local = check_coretime.run(minimal=True)
    suffix = check_complete_suffix.run(output_dir if write_streams else None)
    frames = check_suffix_frames.run()
    transport = scalar_norm_transport.run()
    charts = chart_bounds.run()
    banks = check_bank_assignment.run(output_dir)
    priced = reprice.reprice(frames['local_histogram_delta'],
                            local['residual_rank_count_delta'])
    assert banks['family_counts'] == {rank:count//60 for rank,count in priced['packing']['demand'].items()}
    assert banks['literal_stock'] == priced['literal_stock']
    pins = source_data.read_json('expected/kernel-pins.json')
    assert priced['literal_stock'] == pins['literal_stock'] + local['literal_stock_delta']
    assert transport['source_hashes']['original_suffix'] == suffix['original_suffix_sha256']
    assert transport['source_hashes']['modified_suffix'] == suffix['modified_suffix_sha256']
    assert charts['selector_calls_bound'] < 2 ** 40
    assert transport['payload_upper'] < 2 ** 104
    assert priced['kappa'] == arithmetic.F(749906929903449, 10 ** 18)
    priced['source_head'] = source_data.HEAD
    priced['binding'] = 'Measured chronological frame delta and exact selected endpoint residual changes.'
    priced['prior_kappa'] = arithmetic.F(pins['kappa'])
    priced['kappa_gain'] = priced['kappa'] - priced['prior_kappa']
    finite = finite_bill.run(charts, transport, arithmetic.serial(priced))
    results = {'local': local, 'suffix': suffix, 'frames': frames,
               'scalar-transport': transport, 'charts': compact_charts(charts),
               'pricing': priced, 'finite-bill': finite, 'banks': banks}
    results['summary'] = {
        'status': 'PASS_CHANGED_STAGE_CHECKS_CONDITIONAL_ON_PINNED_BASE',
        'source_head': source_data.HEAD,
        'new_restorations': local['selected'],
        'old_restorations_undone': local['undone_old_restorations'],
        'kappa': str(priced['kappa']),
        'kappa_decimal': priced['kappa_decimal'],
        'literal_stock': priced['literal_stock'],
        'paid_calls': priced['calls'],
        'rank_mass': priced['rank_mass'],
        'deficit': str(priced['deficit']),
        'full_inherited_admission_replayed': False,
        'all_size_theorem_verified': False,
        'verification_limits': [
            'The pinned PR299 unchanged prefix and its original admission remain hypotheses.',
            'Unchanged finite compiler, weighted chart, routing, prime and setup contracts are inherited.',
            'Changed charts, selector bound and scalar payload bound are checked here; the complete inherited finite compiler is not rerun.',
            'Outer positive literal and row-gap inputs remain conditional on the inherited finite bridge.',
            'No full all-size or machine-verification claim is made.'
        ]}
    for name, result in results.items():
        result.pop('seconds', None)
        # Normalize integer map keys to their JSON representation before comparing.
        results[name] = json.loads(json.dumps(arithmetic.serial(result)))
    if output_dir is not None:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        for name, result in results.items():
            (output_dir / (name + '.json')).write_text(json.dumps(result, indent=2) + '\n')
        (output_dir / 'chart-factor-programs.json').write_text(
            json.dumps(arithmetic.serial(charts['factor_programs']), indent=2) + '\n')
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path)
    parser.add_argument('--write-streams', action='store_true')
    parser.add_argument('--check', action='store_true',
                        help='Compare every regenerated receipt with the committed certificates')
    args = parser.parse_args()
    if args.write_streams and args.output_dir is None:
        parser.error('--write-streams requires --output-dir')
    results = run(args.output_dir, args.write_streams)
    if args.check:
        for name, actual in results.items():
            expected = json.loads((HERE / 'certificates' / (name + '.json')).read_text())
            if actual != expected:
                raise ValueError('Certificate drift: ' + name)
    print(json.dumps(results['summary'], indent=2))


if __name__ == '__main__':
    main()
