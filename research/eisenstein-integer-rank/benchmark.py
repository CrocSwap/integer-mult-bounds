#!/usr/bin/env python3
"""Optional observed timing; exact output equality is required, speed is not."""
import argparse
from contextlib import redirect_stdout
from copy import deepcopy
import hashlib
import io
import json
from pathlib import Path
import platform
import statistics
import subprocess
import sys
import time
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import integer_rank
import retained


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--pairs', type=int, default=6)
    args = parser.parse_args()
    integer_rank.need(args.pairs >= 2, 'at least two timing pairs')
    old = retained.load()
    original = old.rank
    matrices = []
    def capture(matrix, field='K'):
        if field == 'K':
            matrices.append(deepcopy(matrix))
        return original(matrix, field)
    old.rank = capture
    with redirect_stdout(io.StringIO()):
        old.main()
    expected_ranks = [original(matrix) for matrix in matrices]
    integer_rank.need(len(matrices) == 359, 'complete actual K-call timing fixture')
    census = [[[[[str(a), str(b)] for a, b in row] for row in matrix], r]
              for matrix, r in zip(matrices, expected_ranks)]
    call_digest = hashlib.sha256(json.dumps(census, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    integer_rank.need(call_digest == json.loads((HERE/'RESULT.json').read_text())['K_call_digest'],
                      'timing fixture differs from verified actual-call census')
    full = {'original': [], 'integer': []}
    kernels = {'original': [], 'integer': []}
    expected_output = None
    order = []
    for pair in range(args.pairs+1):
        modes = ('original', 'integer') if pair % 2 == 0 else ('integer', 'original')
        for mode in modes:
            command = [sys.executable, '-I', '-O', '-B', str(HERE/'replay.py')]
            if mode == 'original':
                command.append('--original')
            start = time.perf_counter()
            done = subprocess.run(command, capture_output=True, timeout=180)
            elapsed = time.perf_counter()-start
            integer_rank.need(done.returncode == 0 and not done.stderr, 'full benchmark replay failed')
            if expected_output is None:
                expected_output = done.stdout
            integer_rank.need(done.stdout == expected_output, 'complete stdout bytes differ')
            engine = original if mode == 'original' else integer_rank.rank
            start = time.perf_counter()
            ranks = [engine(matrix) for matrix in matrices]
            kernel_elapsed = time.perf_counter()-start
            integer_rank.need(ranks == expected_ranks, 'timed K-call results differ')
            if pair:
                full[mode].append(elapsed)
                kernels[mode].append(kernel_elapsed)
                order.append([pair, mode])
    medians = {label: {mode: statistics.median(values) for mode, values in times.items()}
               for label, times in [('full', full), ('K_calls', kernels)]}
    result = {'python': platform.python_version(), 'implementation': platform.python_implementation(),
              'platform': platform.platform(), 'machine': platform.machine(),
              'source_base': json.loads((HERE/'SOURCES.json').read_text())['base_commit'],
              'pairs': args.pairs, 'unmeasured_warmup_pairs': 1, 'order': order,
              'full_seconds': full, 'K_call_seconds': kernels, 'median_seconds': medians,
              'median_speed_ratios': {label: times['original']/times['integer'] for label, times in medians.items()},
              'complete_stdout_bytes_sha256': hashlib.sha256(expected_output).hexdigest(),
              'complete_K_calls': 359,
              'K_call_digest': call_digest,
              'adapter_sha256': {name: hashlib.sha256((HERE/name).read_bytes()).hexdigest()
                                 for name in ('integer_rank.py', 'retained.py', 'replay.py', 'benchmark.py')},
              'scope': 'Full same-fixture fresh-process wall time including imports/authentication; separately all359 actual K calls. Alternating order, warmup excluded. Concurrent machine load uncontrolled; no universal speed guarantee.'}
    with args.output.open('x', encoding='utf-8', newline='\n') as out:
        out.write(json.dumps(result, indent=2, sort_keys=True)+'\n')
    print(json.dumps(result['median_speed_ratios'], sort_keys=True))


if __name__ == '__main__':
    main()
