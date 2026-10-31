"""One finite parent readback of observer+outer-time records; outside tail is open.

No targets are imported or repeated. A passing readback exposes conservative
full-command canonical policy charge, never just the observer's inner timer.
"""
import argparse
import math
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from custody import need, pin, read_json, write_json


def main():
    parser = argparse.ArgumentParser()
    for name in ('admission', 'admission-sha256', 'observer-record', 'outer-time', 'report'):
        parser.add_argument('--' + name, required=True)
    args = parser.parse_args()
    admission = read_json(Path(args.admission), args.admission_sha256)
    observer = read_json(Path(args.observer_record))
    outer = read_json(Path(args.outer_time))
    state = {'schema': 'o03-one-parent-readback-v2', 'status': 'STARTED', 'errors': [],
             'tail_cost': 'OPEN_NOT_ZERO', 'publication_cost': 'OPEN_NOT_ZERO',
             'readback_operations': 1, 'observer_record': pin(Path(args.observer_record)),
             'outer_time_record': pin(Path(args.outer_time)), 'canonical_ledger_written_here': False}
    try:
        need(observer['admission_sha256'] == args.admission_sha256 and
             observer['operation'] == 'complete-fixed-o03' and observer['status'] == 'PASS', 'observer did not pass exact admitted operation')
        need(observer.get('cpu_accounting') == 'COMPLETE_FOR_SOURCE_FIXED_REAPED_SUCCESS_TREE', 'CPU accounting did not close fixed reaped tree')
        need(outer['exit'] == 0, 'outer command exit failed')
        for name in ('wall_seconds', 'user_seconds', 'system_seconds', 'kernel_individual_maxrss_kib'):
            need(type(outer[name]) in (int, float) and math.isfinite(outer[name]) and outer[name] >= 0, 'invalid outer measurement: ' + name)
        need(outer['kernel_individual_maxrss_kib'] * 1024 <= 1073741824, 'outer kernel individual maxRSS exceeds1GiB')
        need(observer['inclusive_sampled_simultaneous_tree_rss_bytes'] <= 1073741824 and
             not observer['inclusive_sampler_errors'] and observer['inclusive_samples'] > 0, 'inclusive sampler invalid')
        # GNU time %e has hundredth-second textual precision; charge a complete
        # upper rounding quantum to avoid undercharging the full outer span.
        charge = outer['wall_seconds'] + 0.01
        state['full_outer_wall_seconds_reported'] = outer['wall_seconds']
        state['outer_wall_rounding_allowance_seconds'] = 0.01
        state['canonical_policy_charge_seconds'] = charge
        need(observer['inclusive_wall_seconds'] <= charge, 'outer timer shorter than observed core')
        need(charge <= 180 and admission['canonical_ledger']['spent_seconds'] + charge <= 2400,
             'full outer command or aggregate policy cap exceeded')
        observed_cpu = sum(observer['cpu_seconds'].values())
        need(outer['user_seconds'] + outer['system_seconds'] + 0.03 >= observed_cpu,
             'outer CPU excludes declared observer/descendant CPU')
        state['full_outer_cpu_seconds_reported'] = outer['user_seconds'] + outer['system_seconds']
        state['individual_maxrss_kib'] = outer['kernel_individual_maxrss_kib']
        state['simultaneous_sampled_rss_bytes'] = observer['inclusive_sampled_simultaneous_tree_rss_bytes']
        state['outside_tail'] = observer['outside_tail']
        state['qualification'] = 'Measurement/readback eligibility only; independent P5/O03 adjudication and canonical ledger reconciliation remain required.'
    except BaseException as error:
        state['errors'].append({'type': type(error).__name__, 'message': str(error)})
    state['status'] = 'PASS' if not state['errors'] else 'STOP'
    write_json(Path(args.report), state)
    if state['status'] != 'PASS':
        raise SystemExit(1)


if __name__ == '__main__':
    main()
