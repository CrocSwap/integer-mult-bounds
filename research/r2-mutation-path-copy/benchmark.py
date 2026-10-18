#!/usr/bin/env python3
"""Fresh serial same-fixture time and peak-RSS measurements; no timing gate.
Tekalign / OpenAI Codex, Apache-2.0.
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
    samples, reference = [], None
    orders = [('deepcopy', 'marshal', 'paths'), ('paths', 'marshal', 'deepcopy'),
              ('marshal', 'paths', 'deepcopy')]
    with tempfile.TemporaryDirectory(prefix='r2 mutation benchmark ') as directory:
        for trial in range(args.rounds):
            for mode in orders[trial % len(orders)]:
                target = Path(directory) / f'{trial}-{mode}.json'
                command = [sys.executable, '-I', '-B', str(PACKAGE / 'replay.py'),
                           '--mode', mode, '--output', str(target)]
                start = time.perf_counter()
                process = subprocess.run(command, capture_output=True, text=True, timeout=180)
                wall = time.perf_counter() - start
                if process.returncode:
                    raise ValueError(process.stdout + process.stderr)
                result = json.loads(target.read_bytes())
                semantic = {k: result[k] for k in ('reference_result_sha256', 'call_multiset_sha256',
                            'decisions', 'providers', 'source_sha256', 'adapter_sha256',
                            'executed_replay_sha256', 'executed_audit_sha256')}
                if reference is None:
                    reference = semantic
                elif semantic != reference:
                    raise ValueError('different input, mutant footprints, decisions or complete receipt')
                samples.append({'round': trial, 'mode': mode, 'process_wall_seconds': wall,
                                **{k: result[k] for k in ('wall_seconds', 'copy_seconds', 'peak_rss_bytes')}})
                print(process.stdout.strip(), flush=True)
    fields = ('process_wall_seconds', 'wall_seconds', 'copy_seconds', 'peak_rss_bytes')
    medians = {m: {k: statistics.median(r[k] for r in samples if r['mode'] == m) for k in fields}
               for m in orders[0]}
    result = {'python': sys.version, 'platform': platform.platform(), 'rounds': args.rounds,
              'scope': 'Complete retained PR3218/PR3202 R2 audit, including all 32 mutants; producer generation excluded',
              'method': 'Fresh sequential processes, alternating order; OS caches not flushed; shared host; all modes include identical provider-immutability guards',
              'semantic_identity': reference, 'samples': samples, 'medians': medians,
              'ratios_over_paths': {m: {k: medians[m][k] / medians['paths'][k] for k in fields}
                                    for m in ('deepcopy', 'marshal')}}
    with args.output.open('x') as stream:
        json.dump(result, stream, indent=2, sort_keys=True)
        stream.write('\n')
    print('PASS_R2_MUTATION_BENCHMARK', json.dumps(result['ratios_over_paths'], sort_keys=True))


if __name__ == '__main__':
    main()
