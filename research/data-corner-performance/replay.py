#!/usr/bin/env python3
"""Source-pinned replay of the historical data-corner check.

After research/data-corner-production/, working
research/copied-fixed/data_corners.cpp already carries the cached-column loop.
This runner vendors the pairwise-era source as baseline.cpp and compares it to
production without re-applying the transform to the working tree.
"""
import argparse
from hashlib import sha256
import json
import os
from pathlib import Path
import platform
import resource
import shlex
import statistics
import subprocess
import tempfile
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
GUARD = '#ifdef NDEBUG\n#error "Data-corner replay requires assertions"\n#endif\n'
OLD_INVERSE = 'int inv=power(value,prime-2);'
NEW_INVERSE = OLD_INVERSE + '''
    int columns[d],length=0;
    for(int j=0;j<d;j++)if(available[j]&&M[i][j])columns[length++]=j;'''
OLD_UPDATE = 'for(int j=0;j<d;j++)if(available[j]&&M[i][j]){'
NEW_UPDATE = 'for(int k=0;k<length;k++){\n      int j=columns[k];'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def admitted_inputs(root=ROOT):
    manifest = json.loads((HERE / 'SOURCE.json').read_text())
    blobs = {}
    for name, expected in manifest['sha256'].items():
        data = (root / name).read_bytes()
        require(sha256(data).hexdigest() == expected, 'Source drift: ' + name)
        blobs[name] = data
    return manifest, blobs


def transform(source):
    for old, new in ((OLD_INVERSE, NEW_INVERSE), (OLD_UPDATE, NEW_UPDATE)):
        require(source.count(old) == 1, 'Expected exactly one update site')
        source = source.replace(old, new)
    return source


def compile_program(source, output, compiler):
    path = output.with_suffix('.cpp')
    path.write_text(GUARD + source)
    subprocess.run([*compiler, '-O3', '-std=c++17', str(path), '-o', str(output)],
                   check=True, capture_output=True)


def validate_receipt(stdout, expected):
    require(json.loads(stdout) == expected, 'Complete data-corner receipt differs')


def timed_run(executable, expected):
    before = resource.getrusage(resource.RUSAGE_CHILDREN)
    start = time.perf_counter()
    result = subprocess.run([str(executable)], capture_output=True, check=True)
    wall = time.perf_counter() - start
    after = resource.getrusage(resource.RUSAGE_CHILDREN)
    validate_receipt(result.stdout, expected)
    return result.stdout, dict(wall_seconds=wall,
        cpu_seconds=(after.ru_utime + after.ru_stime - before.ru_utime - before.ru_stime),
        stdout_sha256=sha256(result.stdout).hexdigest(),
        stderr_sha256=sha256(result.stderr).hexdigest())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--benchmark', type=int, metavar='PAIRS', default=0,
                        help='alternate complete original/optimized process pairs')
    parser.add_argument('--output', type=Path, help='write fresh JSON evidence file')
    args = parser.parse_args()
    require(args.benchmark >= 0, 'Negative benchmark pair count')
    require(not args.output or not args.output.exists(), 'Output already exists')
    manifest, blobs = admitted_inputs()
    baseline = blobs['research/data-corner-performance/baseline.cpp'].decode()
    production = blobs['research/copied-fixed/data_corners.cpp'].decode()
    require(production == transform(baseline),
            'production data_corners.cpp must equal transform(baseline.cpp)')
    expected = json.loads(blobs['research/copied-fixed/data-corners.json'])
    compiler = shlex.split(os.environ.get('CXX', 'c++'))
    version = subprocess.check_output([*compiler, '--version'], text=True)
    samples = []
    with tempfile.TemporaryDirectory(prefix='data-corner-') as directory:
        work = Path(directory)
        compile_program(production, work / 'optimized', compiler)
        if args.benchmark:
            compile_program(baseline, work / 'original', compiler)
        common_stdout = None
        for pair in range(args.benchmark or 1):
            modes = (['original', 'optimized'] if pair % 2 == 0 else
                     ['optimized', 'original']) if args.benchmark else ['optimized']
            for mode in modes:
                stdout, sample = timed_run(work / mode, expected)
                if common_stdout is not None:
                    require(stdout == common_stdout, 'Original/optimized bytes differ')
                common_stdout = stdout
                samples.append(dict(pair=pair, mode=mode, **sample))
                print(f'PASS pair={pair} {mode} wall={sample["wall_seconds"]:.3f}s', flush=True)
    evidence = dict(status='PASS_DATA_CORNER_REPLAY', base_commit=manifest['base_commit'],
        source_sha256=manifest['sha256'], implementation_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
        generated_source_sha256=sha256((GUARD + production).encode()).hexdigest(),
        platform=platform.platform(), python=platform.python_version(), compiler=compiler,
        compiler_version=version, flags=['-O3', '-std=c++17'],
        coverage={k: expected[k] for k in ('pairs', 'good', 'fallback', 'nonzero_pivots', 'ordered_zero_checks')},
        samples=samples)
    if args.benchmark:
        medians = {mode: statistics.median(s['wall_seconds'] for s in samples if s['mode'] == mode)
                   for mode in ('original', 'optimized')}
        evidence.update(wall_medians=medians, speedup=medians['original'] / medians['optimized'])
    if args.output:
        with args.output.open('x') as stream:
            stream.write(json.dumps(evidence, indent=2, sort_keys=True) + '\n')
    print('PASS_DATA_CORNER_REPLAY pairs=4073300 complete_receipts_equal=true')


if __name__ == '__main__':
    main()
