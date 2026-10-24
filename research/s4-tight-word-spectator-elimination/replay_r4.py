#!/usr/bin/env python3
"""Cold replay the unchanged PR3888 independent r=4 engine.
The primary engine is an optional additional sequential cross-check.

JoyboyBrian, with substantial OpenAI Codex assistance. Apache-2.0.
This is optional C++ replay; the registered Python check validates its receipt.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = ROOT / 'research/s4-mixed-tuple-tight-word-search'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--include-primary', action='store_true',
                        help='also run the redundant primary cross-check after the independent engine')
    args = parser.parse_args()
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=False)
    sources = json.loads((HERE / 'SOURCES.json').read_text())
    pins = {row['path']: row['sha256'] for row in sources['files']}
    for name in ('search.cpp', 'indep.cpp', 'RESULT.json'):
        path = SOURCE / name
        if sha(path.read_bytes()) != pins[str(path.relative_to(ROOT))]:
            raise ValueError('predecessor source mismatch: ' + name)
    expected = json.loads((SOURCE / 'RESULT.json').read_text())['full_replay_expectations']
    adapter = HERE / 'compat'
    if sys.platform == 'darwin':
        compiler = subprocess.check_output(['xcrun', '--find', 'clang++'], text=True).strip()
        sdk = subprocess.check_output(['xcrun', '--show-sdk-path'], text=True).strip()
        omp = Path(os.environ.get('S4_LIBOMP_PREFIX', '/opt/homebrew/opt/libomp'))
        flags = ['-O3', '-mcpu=native', '-std=c++17', '-isysroot', sdk, '-Xpreprocessor', '-fopenmp',
                 '-I' + str(adapter), '-I' + str(omp / 'include'),
                 '-L' + str(omp / 'lib'), '-lomp']
    else:
        compiler = os.environ.get('CXX', 'g++')
        flags = ['-O3', '-std=c++17', '-fopenmp', '-I' + str(adapter)]
    version = subprocess.check_output([compiler, '--version'], text=True).splitlines()[0]
    env = dict(os.environ, OMP_NUM_THREADS='1')
    for key in ('SYM', 'SYM_A', 'SYM_B', 'SYM_D', 'STOP_FIRST'):
        env.pop(key, None)
    receipt = {'scope': 'complete r=4 finite dependency only; not r=5 or the LP suite',
               'platform': platform.platform(), 'python': platform.python_version(),
               'base': sources['base_commit'], 'records': []}
    commands = [
        ('search', 'r4_primary', ['4', '0', '12', '4', '4', '4', '2143', '3142', '4231', '2143', '10']),
        ('indep', 'r4_indep', ['4', '4', '4', '4', '2143', '3142', '4231', '2143', 'all']),
    ]
    # Run the independent engine first; never run these CPU jobs concurrently.
    selected = list(reversed(commands)) if args.include_primary else [commands[1]]
    for engine, key, argv in selected:
        source, binary = SOURCE / (engine + '.cpp'), out / engine
        build_argv = [compiler] + flags + ['-o', str(binary), str(source)]
        build = subprocess.run(build_argv, text=True, capture_output=True, timeout=60)
        (out / (engine + '-build.stderr')).write_text(build.stderr)
        if build.returncode:
            raise RuntimeError('compile failed: ' + build.stderr)
        print('START_R4_REPLAY', engine, flush=True)
        start = time.monotonic()
        stdout_path, stderr_path = out / (engine + '.stdout'), out / (engine + '.stderr')
        try:
            with stdout_path.open('w') as stdout, stderr_path.open('w') as stderr:
                run = subprocess.run([str(binary)] + argv, text=True, stdout=stdout,
                                     stderr=stderr, env=env, timeout=900)
        except subprocess.TimeoutExpired:
            failure = {'engine': engine, 'source_sha256': sha(source.read_bytes()),
                       'compile_argv': build_argv, 'run_argv': [str(binary)] + argv,
                       'timeout_seconds': 900, 'status': 'TIMEOUT_NOT_A_PASS',
                       'elapsed_seconds': round(time.monotonic() - start, 3),
                       'stdout_sha256': sha(stdout_path.read_bytes()),
                       'stderr_sha256': sha(stderr_path.read_bytes())}
            (out / (engine + '.timeout.json')).write_text(json.dumps(failure, indent=2) + '\n')
            raise
        elapsed = time.monotonic() - start
        run.stdout, run.stderr = stdout_path.read_text(), stderr_path.read_text()
        final = run.stdout.splitlines()[-1] if run.stdout.splitlines() else ''
        if run.returncode or final != expected[key]:
            raise ValueError('finite replay result differs: ' + final)
        receipt['records'].append({
            'engine': source.name, 'source_sha256': sha(source.read_bytes()),
            'compiler': version, 'compile_argv': build_argv, 'run_argv': [str(binary)] + argv,
            'adapter_sha256': sha((adapter / 'bits/stdc++.h').read_bytes()),
            'OMP_NUM_THREADS': 1, 'timeout_seconds': 900,
            'elapsed_seconds': round(elapsed, 3), 'returncode': run.returncode,
            'result': final, 'stdout_sha256': sha(run.stdout.encode()),
            'stderr_sha256': sha(run.stderr.encode())})
        receipt['records'].sort(key=lambda item: item['engine'] != 'search.cpp')
        (out / 'REPLAY.json').write_text(json.dumps(receipt, indent=2) + '\n')
        print('PASS_R4_REPLAY', engine, round(elapsed, 3), final, flush=True)


if __name__ == '__main__':
    main()
