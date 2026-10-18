#!/usr/bin/env python3
"""Check the zero-row guard and benchmark seven alternating full replay pairs."""
import argparse
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import platform
import resource
import statistics
import subprocess
import sys
import time

PACKAGE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('cyclic_adapter', PACKAGE / 'replay.py')
adapter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(adapter)
require = adapter.require


def rejected(call, message):
    try:
        call()
    except ValueError:
        return
    raise ValueError(message)


def controls():
    original, fast = adapter.load(False), adapter.load(True)
    checks = 0
    for radix in (3, 4, 5):
        k = original['Field'](radix)
        z, o, u = k.zero, k.one, k.root(1)
        # Exact determinants cover sparse, swapped, dense, and singular inputs.
        fixtures = [([[o, z], [z, o]], o),
                    ([[z, o], [o, z]], k.scale(o, -1)),
                    ([[u, o], [o, u]], k.sub(k.mul(u, u), o)),
                    ([[o, u], [z, o]], o),
                    ([[o, u], [o, u]], z),
                    ([[z, z], [z, z]], z)]
        for matrix, determinant in fixtures:
            for boundary in (None, [k.root(94), k.scale(o, 94)]):
                before = copy.deepcopy((matrix, boundary))
                expected = original['eliminate'](k, matrix, boundary)
                result = fast['eliminate'](k, matrix, boundary)
                require(result == expected, 'Elimination differs from reference')
                require((matrix, boundary) == before, 'Elimination mutated its input')
                require(result[0] == determinant, 'Wrong independently computed determinant')
                if determinant == z or boundary is None:
                    require(result[1] is None, 'Unexpected solution')
                else:
                    for row, target in zip(matrix, boundary):
                        actual = z
                        for value, solution in zip(row, result[1]):
                            actual = k.add(actual, k.mul(value, solution))
                        require(actual == target, 'Solution does not satisfy the input system')
                checks += 1

    def work(namespace):
        k = namespace['Field'](3)
        multiply = k.mul
        calls = 0

        def counted(a, b):
            nonlocal calls
            calls += 1
            return multiply(a, b)

        k.mul = counted
        namespace['eliminate'](k, [[k.one, k.zero], [k.zero, k.one]], [k.one, k.one])
        return calls

    before, after = work(original), work(fast)
    require(after < before, 'Zero-row guard removed no arithmetic')
    source = (adapter.SOURCE / 'verify.py').read_bytes()
    rejected(lambda: adapter.prepare(source + b'\n', True), 'Changed source was admitted')
    # These faults skip necessary nonzero work, so an inherited identity must fail.
    guarded = adapter.prepare(source, True)
    for guard in ('if value != k.zero:', 'if True:'):
        namespace = {'__name__': 'mutated_cyclic_verifier'}
        exec(compile(guarded.replace('if value == k.zero:', guard), '<negative-control>', 'exec'), namespace)
        rejected(lambda: namespace['case'](3, 1), 'Incorrect row-skipping guard accepted')
    return {'matrix_checks': checks, 'source_mutations_rejected': 1,
            'guard_mutations_rejected': 2,
            'identity_matrix_multiplications': {'reference': before, 'guarded': after}}


def replay(path, expected):
    command = [sys.executable, '-I', '-B']
    if sys.flags.optimize:
        command.append('-O')
    usage = resource.getrusage(resource.RUSAGE_CHILDREN)
    start = time.perf_counter()
    result = subprocess.run(command + [str(path)], capture_output=True, check=True)
    wall = time.perf_counter() - start
    end_usage = resource.getrusage(resource.RUSAGE_CHILDREN)
    require(result.stdout == expected, 'Full replay differs from pinned EXPECTED.json')
    require(not result.stderr, 'Unexpected replay diagnostics')
    return {'wall_seconds': wall,
            'cpu_seconds': end_usage.ru_utime + end_usage.ru_stime - usage.ru_utime - usage.ru_stime}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, help='fresh JSON evidence path')
    args = parser.parse_args()
    if args.output is not None:
        require(not args.output.exists(), 'Use a fresh evidence path')
    expected = (adapter.SOURCE / 'EXPECTED.json').read_bytes()
    digest = hashlib.sha256(expected).hexdigest()
    require(digest == adapter.PINS['EXPECTED.json'], 'Predecessor receipt changed')
    evidence = {'status': 'PASS_CYCLIC_ZERO_ELIMINATION', 'assignment_seed': 94,
                'source_pins': adapter.PINS, 'controls': controls(),
                'python': sys.version, 'platform': platform.platform(),
                'optimized': bool(sys.flags.optimize), 'expected_sha256': digest,
                'cases_per_replay': len(json.loads(expected)['cases']),
                'samples': []}
    paths = {'reference': adapter.SOURCE / 'verify.py', 'guarded': PACKAGE / 'replay.py'}
    for pair in range(7):
        order = ('reference', 'guarded') if pair % 2 == 0 else ('guarded', 'reference')
        sample = {'pair': pair + 1, 'order': list(order)}
        for label in order:
            sample[label] = replay(paths[label], expected)
        evidence['samples'].append(sample)
    evidence['medians'] = {
        label: {metric: statistics.median(s[label][metric] for s in evidence['samples'])
                for metric in ('wall_seconds', 'cpu_seconds')}
        for label in paths}
    evidence['speedup'] = {
        metric: evidence['medians']['reference'][metric] / evidence['medians']['guarded'][metric]
        for metric in ('wall_seconds', 'cpu_seconds')}
    payload = json.dumps(evidence, indent=2) + '\n'
    if args.output is None:
        print(payload, end='')
    else:
        with args.output.open('x') as stream:
            stream.write(payload)
        print(evidence['status'])


if __name__ == '__main__':
    main()
