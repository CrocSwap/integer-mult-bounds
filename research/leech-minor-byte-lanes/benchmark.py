#!/usr/bin/env python3
"""Alternating fresh-process timings, including complete certificate checking."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import platform
import statistics
import subprocess
import sys
import tempfile
import time

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from replay import ROOT, check_pins, require


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--rounds', type=int, default=3)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    require(not sys.flags.optimize, 'Assertions must remain enabled')
    require(args.rounds >= 1, 'At least one timing pair required')
    require(not args.output.exists(), 'Output already exists')
    pins = check_pins()
    samples = []
    expected = (ROOT / 'certificates/affine-vector-screens.json').read_bytes()
    with tempfile.TemporaryDirectory(prefix='leech-lanes-') as temporary:
        for round_index in range(args.rounds):
            modes = ('baseline', 'lanes') if round_index % 2 == 0 else ('lanes', 'baseline')
            for mode in modes:
                output = Path(temporary) / f'{round_index}-{mode}.json'
                command = [sys.executable, '-I', '-B', str(HERE / 'replay.py'),
                           '--mode', mode, '--output', str(output)]
                started = time.perf_counter()
                process = subprocess.run(command, text=True, capture_output=True, check=True)
                seconds = time.perf_counter() - started
                require(output.read_bytes() == expected, 'Timed certificate changed')
                receipt = json.loads(process.stdout)
                require(receipt['status'] == 'PASS_AFFINE_VECTOR_REPLAY', 'Missing replay success')
                samples.append({'round': round_index + 1, 'mode': mode,
                                'wall_seconds': seconds, 'receipt': receipt})
                print(f'{mode} round {round_index + 1}: {seconds:.6f}s', flush=True)
    medians = {mode: statistics.median(s['wall_seconds'] for s in samples if s['mode'] == mode)
               for mode in ('baseline', 'lanes')}
    result = {'status': 'PASS_IDENTICAL_COMPLETE_CERTIFICATES',
              'base_commit': pins['base_commit'], 'python': sys.version,
              'platform': platform.platform(), 'machine': platform.machine(),
              'samples': samples, 'median_wall_seconds': medians,
              'median_speedup': medians['baseline'] / medians['lanes'],
              'certificate_sha256': sha256(expected).hexdigest(),
              'adapter_sha256': {name: sha256((HERE / name).read_bytes()).hexdigest()
                                 for name in ('lanes.py', 'replay.py', 'benchmark.py', 'PINS.json')},
              'scope': 'Complete nine-screen historical affine-vector audit; process startup, source admission, all checks and output included. No timing threshold.'}
    with args.output.open('x') as out:
        out.write(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(result['status'], f"median_speedup={result['median_speedup']:.3f}")


if __name__ == '__main__':
    main()
