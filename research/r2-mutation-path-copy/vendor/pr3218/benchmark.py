#!/usr/bin/env python3
"""Fresh serial process benchmarks of the identical complete R2 audit.
Tekalign / OpenAI Codex, Apache-2.0. No acceptance timing threshold.
"""
import argparse
import json
from pathlib import Path
import platform
import statistics
import subprocess
import sys
import tempfile
import time

PACKAGE = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--rounds', type=int, default=3)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists() or not 1 <= args.rounds <= 9:
        raise ValueError('fresh output and 1..9 rounds required')
    rows = []
    reference = None
    orders = [('packed', 'cached', 'anchor'), ('anchor', 'cached', 'packed'),
              ('cached', 'anchor', 'packed')]
    with tempfile.TemporaryDirectory(prefix='anchor-benchmark-') as directory:
        for trial in range(args.rounds):
            for mode in orders[trial % len(orders)]:
                target = Path(directory) / f'{trial}-{mode}.json'
                command = [sys.executable, '-I', '-B', str(PACKAGE / 'replay.py'),
                           '--mode', mode, '--output', str(target)]
                start = time.perf_counter()
                process = subprocess.run(command, capture_output=True, text=True, timeout=180)
                elapsed = time.perf_counter() - start
                if process.returncode:
                    raise ValueError(process.stdout + process.stderr)
                result = json.loads(target.read_bytes())
                semantic = {k: result[k] for k in ('reference_result_sha256', 'call_multiset_sha256',
                                                  'calls', 'source_sha256', 'anchor_engine_sha256')}
                if reference is None:
                    reference = semantic
                elif semantic != reference:
                    raise ValueError('benchmark inputs, decisions or complete audit differ')
                rows.append({'round': trial, 'mode': mode, 'process_wall_seconds': elapsed,
                             'audit_wall_seconds': result['wall_seconds'],
                             'equality_engine_seconds': result['engine_seconds']})
                print(process.stdout.strip(), flush=True)
    medians = {mode: {field: statistics.median(x[field] for x in rows if x['mode'] == mode)
                      for field in ('process_wall_seconds', 'audit_wall_seconds', 'equality_engine_seconds')}
               for mode in orders[0]}
    report = {'scope': 'Complete retained PR3202 two-provider audit; native generation and full supplier admission excluded',
              'python': sys.version, 'platform': platform.platform(), 'rounds': args.rounds,
              'processes': 'fresh, sequential; alternating orders; OS caches not flushed; shared host',
              'semantic_identity': reference, 'samples': rows, 'medians': medians,
              'speedup_over': {mode: {field: medians[mode][field] / medians['anchor'][field]
                                     for field in medians[mode]} for mode in ('packed', 'cached')}}
    with args.output.open('x') as stream:
        json.dump(report, stream, sort_keys=True, indent=2)
        stream.write('\n')
    print('PASS_SAME_INPUT_R2_BENCHMARK', json.dumps(report['speedup_over'], sort_keys=True))


if __name__ == '__main__':
    main()
