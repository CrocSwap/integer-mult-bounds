#!/usr/bin/env python3
"""Alternating same-input kernel and fresh-process complete owner-check timings."""
import argparse
from fractions import Fraction
import hashlib
import importlib.util
import json
import platform
import statistics
import subprocess
import sys
import tempfile
from time import perf_counter
from pathlib import Path

import fast_exp
from run import HERE, PACKAGE, REFERENCE, check_sources


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pairs', type=int, default=15)
    parser.add_argument('--repeats', type=int, default=50,
                        help='repetitions of the 18-call native exponential batch')
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    if args.pairs < 3 or args.repeats < 1 or args.out.exists():
        parser.error('Use at least 3 pairs, positive repeats, and a fresh output file')
    check_sources()
    spec = importlib.util.spec_from_file_location('reference', REFERENCE)
    reference = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(reference)
    selected = json.loads((PACKAGE / 'data/SPEC.json').read_text())
    previous = json.loads((PACKAGE / 'comparison/PR623-SPEC.json').read_text())
    profile = selected['expected']['global_profile']
    endpoints = [Fraction(s['expected']['complex_lower']) for s in (previous, selected)]
    inputs = []
    for endpoint in endpoints:
        for width in sorted(map(int, profile)):
            low, high = reference.log(Fraction(73, width))
            inputs.append((endpoint * low, endpoint * high))
    expected = [reference.exp(*ab) for ab in inputs]
    if [fast_exp.exp(*ab) for ab in inputs] != expected:
        raise ValueError('Native exponential bounds differ')
    kernels = {'reference': reference.exp, 'integer': fast_exp.exp}
    kernel_times = {name: [] for name in kernels}
    replay_times = {name: [] for name in kernels}
    receipt_hashes = []
    with tempfile.TemporaryDirectory(prefix='exact-exp-benchmark-') as temp:
        for pair in range(args.pairs):
            order = ('reference', 'integer') if pair % 2 == 0 else ('integer', 'reference')
            for name in order:
                fn = kernels[name]
                start = perf_counter()
                for _ in range(args.repeats):
                    result = [fn(*ab) for ab in inputs]
                kernel_times[name].append(perf_counter() - start)
                if result != expected:
                    raise ValueError('Timed kernel bounds differ')
            outputs = []
            for name in order:
                out = Path(temp) / f'{pair}-{name}.json'
                start = perf_counter()
                subprocess.run([sys.executable, '-B', str(HERE / 'run.py'),
                                '--engine', name, '--out', str(out)],
                               check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                replay_times[name].append(perf_counter() - start)
                outputs.append(out.read_bytes())
            if outputs[0] != outputs[1]:
                raise ValueError('Complete owner-check receipts differ')
            receipt_hashes.append(hashlib.sha256(outputs[0]).hexdigest())

    def stats(times):
        medians = {name: statistics.median(values) for name, values in times.items()}
        return {'seconds': times, 'median_seconds': medians,
                'ratio_of_medians': medians['reference'] / medians['integer']}

    report = {
        'status': 'PASS_EXACT_EXP_BENCHMARK',
        'scope': 'Exact exponential kernel and archived-input independent owner check; no supplier rebuild or full frontier timing.',
        'environment': {'python': sys.version, 'platform': platform.platform(),
                        'machine': platform.machine()},
        'source_manifest_sha256': hashlib.sha256((HERE / 'SOURCE.json').read_bytes()).hexdigest(),
        'implementation_sha256': {name: hashlib.sha256((HERE / name).read_bytes()).hexdigest()
                                  for name in ('fast_exp.py', 'run.py', 'benchmark.py')},
        'pairs': args.pairs, 'order': 'reference-first for even pairs, integer-first for odd pairs',
        'native_batch_size': len(inputs), 'kernel_batch_repeats': args.repeats,
        'inputs_sha256': digest([[str(a), str(b)] for a, b in inputs]),
        'exact_output_sha256': digest([[str(a), str(b)] for a, b in expected]),
        'kernel': stats(kernel_times), 'complete_owner_check': stats(replay_times),
        'owner_receipt_sha256_each_pair': receipt_hashes,
    }
    with args.out.open('x') as stream:
        json.dump(report, stream, indent=2)
        stream.write('\n')
    print(report['status'])
    for name in ('kernel', 'complete_owner_check'):
        print(name, report[name]['median_seconds'], 'ratio', report[name]['ratio_of_medians'])


if __name__ == '__main__':
    main()
