"""Time complete offline commands on one immutable export; writes externally only."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import statistics
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def measure(script, archive, repetitions, cwd):
    env = dict(os.environ, PATH='', PYTHONDONTWRITEBYTECODE='1')
    env.pop('PYTHONPATH', None)
    env.pop('PYTHONHOME', None)
    argv = [sys.executable, '-W', 'error', '-B', str(script),
            'check', str(archive), '--check-inputs']
    values, outputs = [], []
    for _ in range(repetitions):
        start = time.perf_counter_ns()
        run = subprocess.run(argv, cwd=cwd, env=env, capture_output=True, timeout=60)
        elapsed = time.perf_counter_ns() - start
        if run.returncode or run.stderr:
            raise ValueError(f'command failed: {run.returncode}, {run.stderr!r}')
        prefix, raw = run.stdout.decode().strip().split(' ', 1)
        result = json.loads(raw)
        if prefix != 'PASS_RESEARCH_EXPORT' or 'declared_inputs_checked' not in result:
            raise ValueError('command did not complete declaration checking')
        values.append(elapsed)
        outputs.append(run.stdout)
    return values, outputs


def benchmark(archive, pairs, batch, cwd):
    scripts = [HERE / 'baseline/export_research_package.py',
               ROOT / 'scripts/export_research_package.py']
    before = hashlib.sha256(archive.read_bytes()).hexdigest()
    runs, outputs = [[], []], []
    for index in range(pairs):
        for side in (index % 2, 1 - index % 2):
            times, texts = measure(scripts[side], archive, batch, cwd)
            runs[side].append(times)
            outputs.extend(texts)
    if len(set(outputs)) != 1:
        raise ValueError('complete outputs differ')
    if hashlib.sha256(archive.read_bytes()).hexdigest() != before:
        raise ValueError('benchmark input changed')
    medians = [statistics.median([n for row in side for n in row]) for side in runs]
    return {'archive_sha256': before, 'archive_bytes': archive.stat().st_size,
            'pairs': pairs, 'commands_per_side_per_pair': batch,
            'elapsed_ns': runs, 'median_ns': medians,
            'wall_time_reduction': 1 - medians[1] / medians[0],
            'successful_commands': 2 * pairs * batch, 'errors': 0,
            'complete_stdout': outputs[0].decode(),
            'source_sha256': [hashlib.sha256(p.read_bytes()).hexdigest() for p in scripts]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--archive', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--pairs', type=int, default=9, choices=range(5, 21))
    parser.add_argument('--batch', type=int, default=5, choices=range(1, 11))
    args = parser.parse_args()
    archive, output = args.archive.resolve(), args.output.resolve()
    if output.is_relative_to(ROOT) or output.exists():
        raise ValueError('output must be a new external file')
    result = benchmark(archive, args.pairs, args.batch, output.parent)
    result['environment'] = {'python': sys.version, 'platform': platform.platform(),
                             'logical_cpus': os.cpu_count(), 'load': os.getloadavg()}
    with output.open('x') as stream:
        json.dump(result, stream, indent=2, sort_keys=True)
        stream.write('\n')
    print(json.dumps({k: result[k] for k in ('median_ns', 'wall_time_reduction',
                                           'successful_commands', 'errors')}))


if __name__ == '__main__':
    main()
