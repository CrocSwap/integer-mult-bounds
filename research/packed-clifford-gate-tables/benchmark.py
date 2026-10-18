#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Four fresh processes in baseline/candidate/candidate/baseline order.

Timings describe this shared host; correctness has no speed threshold.
"""
import argparse
import hashlib
import json
from pathlib import Path
import platform
import statistics
import subprocess
import sys
import time


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out-dir', type=Path, required=True)
    args = parser.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=False)
    here = Path(__file__).resolve().parent
    rows = []
    for index, mode in enumerate(('baseline', 'candidate', 'candidate', 'baseline')):
        destination = args.out_dir / f'{index}-{mode}.json'
        receipts = args.out_dir / f'{index}-{mode}.jsonl'
        command = [sys.executable, '-I', '-B', str(here/'adapter.py'), '--mode', mode,
                   '--out', str(destination), '--receipts', str(receipts)]
        start = time.perf_counter()
        run = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                             timeout=300, check=False)
        process_wall = time.perf_counter()-start
        (args.out_dir/f'{index}-{mode}.log').write_bytes(run.stdout)
        if run.returncode:
            raise SystemExit(f'failed {mode} process {index}: see log')
        record = json.loads(destination.read_bytes())
        record['process_wall_seconds'] = process_wall
        rows.append(record)
        print(f'{index} {mode} {process_wall:.3f}s', flush=True)
    for row in rows[1:]:
        for key in ('checker_stdout', 'source_sha256', 'adapter_sha256', 'legacy_result_sha256',
                    'legacy_receipts_sha256', 'legacy_receipt_header'):
            if row[key] != rows[0][key]:
                raise SystemExit('paired evidence differs: '+key)
    receipt_files = sorted(args.out_dir.glob('*.jsonl'))
    if any(p.read_bytes() != receipt_files[0].read_bytes() for p in receipt_files[1:]):
        raise SystemExit('receipt bytes differ')
    medians = {mode: statistics.median(r['process_wall_seconds'] for r in rows if r['mode']==mode)
               for mode in ('baseline', 'candidate')}
    result = dict(python=sys.version, platform=platform.platform(), processor=platform.processor(),
                  order=[r['mode'] for r in rows], runs=rows, median_process_wall_seconds=medians,
                  median_speed_ratio=medians['baseline']/medians['candidate'],
                  caveat='Four serial fresh processes on a shared host; no statistical or platform-independent speed guarantee.',
                  benchmark_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    (args.out_dir/'BENCHMARK.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(medians))


if __name__ == '__main__':
    main()
