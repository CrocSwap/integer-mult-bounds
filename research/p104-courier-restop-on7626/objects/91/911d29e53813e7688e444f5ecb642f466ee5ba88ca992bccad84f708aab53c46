"""Run only production source-free control modes in the verified job."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
EXPECTED = {
    'build.py': {'missing_incident', 'changed_literal', 'boolean_edit_key', 'boolean_origin',
                 'negative_origin', 'boolean_reverse', 'boolean_manifest_edit'},
    'exact.py': {'dirty_copy_before_write', 'inactive_owned_read', 'negative_operand', 'unknown_opcode',
                 'coframe', 'nonstrict_move', 'boolean_origin', 'negative_origin', 'boolean_reverse',
                 'boolean_edit', 'changed_normalized_row', 'empty_observations', 'empty_source_inventory',
                 'missing_observation', 'duplicate_observation', 'boolean_observation_clock',
                 'negative_observation_clock', 'changed_clear', 'changed_owned_interface',
                 'full_rank_identity_endpoint'},
    'proof.py': {'bad_source_index', 'bad_source_literal', 'wrong_origin', 'missing_owned_observation',
                 'duplicate_owned_observation', 'altered_clear_row', 'altered_clear_event', 'empty_census',
                 'old_source_proof', 'boolean_origin', 'boolean_reverse', 'negative_origin',
                 'boolean_edit_index', 'negative_edit_index', 'empty_expected_inventory',
                 'production_clear_row', 'identity_public_endpoint', 'boolean_observation_clock',
                 'altered_scalar'} | {field + '_' + mode
                    for field in ('clears', 'interfaces', 'copy_guards', 'owned_stream')
                    for mode in ('both_empty_expected', 'both_empty', 'missing_original',
                                 'missing_candidate', 'duplicate_original', 'duplicate_candidate')},
    'certificates.py': {'witness_coefficient', 'delete_witness_term', 'corrupt_erased_row', 'wrong_event',
                        'wrong_owner', 'wrong_init_event', 'wrong_lifetime', 'wrong_chart',
                        'falsified_other_rank', 'final_rank_loss_with_fabricated_metadata',
                        'dirty_fresh_INIT', 'external_reload', 'owned_provider', 'missing_zero_clear',
                        'duplicate_zero_clear_same_count', 'dirty_COPY', 'negative_provider',
                        'boolean_provider', 'final_public_nonidentity', 'missing_204_zero',
                        'duplicate_204_zero_same_count'},
}


def need(ok, message):
    if not ok:
        raise ValueError(message)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    need(not args.out.exists(), 'fresh controls receipt required')
    results = []
    try:
        for module in ('build.py', 'exact.py', 'proof.py', 'certificates.py'):
            for optimize in (False, True):
                cache = args.out.parent / 'controls-pycache' / (module + ('-O' if optimize else '-normal'))
                argv = [sys.executable, '-I', '-B', '-X', 'pycache_prefix=' + str(cache)]
                if optimize:
                    argv.append('-O')
                argv += [str(HERE / module), '--controls-only']
                start = time.monotonic()
                done = subprocess.run(argv, capture_output=True, text=True, check=False, timeout=20)
                row = {'module': module, 'optimized': optimize, 'argv': argv,
                       'exit_code': done.returncode, 'seconds': time.monotonic() - start,
                       'stdout': done.stdout, 'stderr': done.stderr}
                results.append(row)
                need(done.returncode == 0 and not done.stderr, 'control interpreter failed: ' + module)
                obj = json.loads(done.stdout)
                need(obj['status'].startswith('PASS'), 'control status failed')
                rejected = obj.get('rejected', obj.get('controls'))
                if isinstance(rejected, dict):
                    rejected = rejected.get('rejected')
                need(isinstance(rejected, list) and all(type(x) is str for x in rejected), 'control name types')
                need(len(rejected) == len(set(rejected)) == len(EXPECTED[module]) and
                     set(rejected) == EXPECTED[module], 'incomplete production control inventory')
                if module == 'exact.py':
                    need(obj['positive'] == ['dirty_init_zero', 'clean_copy_assignment', 'clear',
                                             'changed_public_operator'], 'exact positive witnesses missing')
                if module == 'certificates.py':
                    need(obj['controls']['public_rank_counterexample'] ==
                         'accepted remaining-live rank 2, public rank 1 at cut; final rank 2',
                         'public-rank counterexample positive witness missing')
                row['control_count'] = len(rejected)
                row['result'] = obj
        need(len(results) == 8 and all(r['control_count'] > 0 for r in results), 'control population')
        report = {'status': 'PASS_SOURCE_FREE_CONTROLS', 'runs': results,
                  'scope': 'Production fixture controls under normal and optimized Python; not actual-source qualification.'}
    except BaseException as error:
        report = {'status': 'INCOMPLETE', 'runs': results, 'error_type': type(error).__name__, 'error': str(error)}
    args.out.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    print(json.dumps({'status': report['status'], 'runs': len(results)}, sort_keys=True), flush=True)
    return 0 if report['status'] == 'PASS_SOURCE_FREE_CONTROLS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
