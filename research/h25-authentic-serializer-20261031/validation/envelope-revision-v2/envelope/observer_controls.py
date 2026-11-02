"""Six fixed concrete observer controls. Run only under admitted outer guard."""
import argparse
import os
from pathlib import Path
import sys
import time
sys.path.insert(0, str(Path(__file__).resolve().parent))
from custody import need, write_json
from observer import observe, process_table

CASES = ('bounded-child-allocation', 'concurrent-parent-child-allocation', 'short-lived-child',
         'timeout-kill-reap', 'pid-membership-and-reaped-cleanup', 'sampled-cap-kill-reap')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output-root', required=True)
    parser.add_argument('--receipt', required=True)
    parser.add_argument('--runtime-manifest', required=True)
    parser.add_argument('--runtime-sha256', required=True)
    args = parser.parse_args()
    root = Path(args.output_root)
    root.mkdir(mode=0o700)
    fixture = str(Path(__file__).resolve().with_name('observer_fixture.py'))
    rows = []
    modes = ('allocation', 'concurrent', 'short', 'timeout', 'membership', 'allocation-cap')
    for index, (name, mode) in enumerate(zip(CASES, modes)):
        parent = None
        before_rss = process_table()[os.getpid()]['rss_bytes']
        if mode == 'concurrent':
            parent = bytearray(16 * 1024 * 1024)
            for offset in range(0, len(parent), 4096):
                parent[offset] = 1
        cap = before_rss + 24 * 1024 * 1024 if mode == 'allocation-cap' else 1073741824
        deadline = time.monotonic() + (0.08 if mode == 'timeout' else 5.0)
        row = observe([sys.executable, '-B', '-I', '-S', fixture, mode, args.runtime_manifest, args.runtime_sha256], str(root), root / ('case-%02d' % index),
                      deadline, rss_cap=cap)
        need(row['logs']['stderr']['size'] == 0, 'fixture stderr')
        if mode in ('allocation', 'concurrent', 'short'):
            need(row['exit'] == 0 and row['termination'] is None, name + ' failed')
        elif mode == 'timeout':
            need(row['termination'] == 'wall_or_aggregate_cap' and row['exit'] != 0, 'timeout not detected')
        elif mode == 'membership':
            need(row['exit'] == 0 and row['termination'] is None and len(row['tracked_identities']) >= 3,
                 'parent/child membership and waited cleanup not observed')
        else:
            need(row['termination'] == 'sampled_tree_rss_cap' and row['exit'] != 0, 'memory cap not detected')
        if mode == 'allocation':
            need(row['sampled_simultaneous_tree_rss_bytes'] >= before_rss + 16 * 1024 * 1024, 'child allocation missed')
        if mode == 'concurrent':
            need(row['sampled_simultaneous_tree_rss_bytes'] >= before_rss + 48 * 1024 * 1024, 'concurrent allocation missing')
            need(len(row['tracked_identities']) >= 3, 'grandchild membership missing')
        now = process_table()
        # Every membership fixture explicitly waits for its child; any live
        # same-identity descendant after return is a cleanup failure.
        survivors = [int(pid) for pid, tick in row['tracked_identities'].items()
                     if int(pid) != os.getpid() and int(pid) in now and
                     now[int(pid)]['start_ticks'] == tick and now[int(pid)]['rss_bytes'] > 0]
        need(not survivors, 'live fixture survived cleanup')
        rows.append({'case': name, 'status': 'PASS', 'measurement': row,
                     'short_peak_guaranteed_observed': False})
        del parent
    write_json(Path(args.receipt), {'schema': 'o03-observer-controls-v1', 'status': 'PASS',
        'case_count': 6, 'ordered_cases': list(CASES), 'cases': rows,
        'sampling_limits_exposed': True, 'synthetic_controls_are_full_serializer_evidence': False})


if __name__ == '__main__':
    main()
