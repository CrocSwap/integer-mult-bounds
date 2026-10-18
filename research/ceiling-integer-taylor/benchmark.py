"""Alternating fresh-process timings; exact receipts, never a speed gate."""
import argparse
import json
import platform
from pathlib import Path
import statistics
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent


def measure(rounds=3):
    samples = {'baseline': [], 'optimized': []}
    expected = None
    order = []
    for i in range(rounds):
        for mode in (('baseline', 'optimized') if i % 2 == 0 else ('optimized', 'baseline')):
            command = [sys.executable, '-I', '-O', '-B', str(HERE/'adapter.py'),
                       '--mode', mode, '--fixture', 'levers']
            start = time.perf_counter()
            child = subprocess.run(command, capture_output=True, text=True, timeout=120)
            elapsed = time.perf_counter()-start
            if child.returncode:
                raise ValueError(child.stderr)
            observed = json.loads(child.stdout)
            if expected is None:
                expected = observed
            if observed != expected:
                raise ValueError('complete replay receipt changed')
            samples[mode].append(elapsed)
            order.append(mode)
    medians = {mode: statistics.median(values) for mode, values in samples.items()}
    return {'python': sys.version, 'platform': platform.platform(), 'rounds': rounds,
            'order': order, 'wall_seconds': samples, 'median_seconds': medians,
            'median_ratio': medians['baseline']/medians['optimized'],
            'exp_calls_per_replay': expected['exp_calls'],
            'complete_receipts_equal': True,
            'scope': 'Actual complete levers.py entry point, fresh process and authentication each run; concurrent host contention uncontrolled; no universal speedup or test gate.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--rounds', type=int, default=3)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if not 1 <= args.rounds <= 20:
        parser.error('rounds must be 1..20')
    result = measure(args.rounds)
    text = json.dumps(result, indent=2)+'\n'
    if args.output:
        with args.output.open('x', encoding='utf-8', newline='\n') as stream:
            stream.write(text)
    print(text)


if __name__ == '__main__':
    main()
