#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Fresh predecessor, changed local words, physical invoice and conditional outer.

No externally supplied baseline/native receipt is accepted. Sources must be
immutable Git exports; fetch_sources.py produces the required directories.
"""
import argparse
import os
import subprocess
import sys
import time
from pathlib import Path
from common import HERE, check_inputs, check_source, read, require, sha, write

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sources', type=Path, required=True)
    parser.add_argument('--main', type=Path, required=True)
    parser.add_argument('--work', type=Path, required=True)
    args = parser.parse_args()
    require(__debug__, 'Assertions must be enabled throughout the inherited chain')
    work = args.work.resolve()
    require(not work.exists(), 'Work directory must be new')
    sources = {number: args.sources.resolve() / ('pr' + number) / pin['package']
               for number, pin in read(HERE / 'PREDECESSORS.json')['sources'].items()}
    for number, package in sources.items():
        check_source(package, number)
    check_inputs()
    def execution_inputs():
        files = set(HERE.rglob('*.py')) | {p for p in (HERE / 'inputs').rglob('*') if p.is_file()}
        files.update(HERE / name for name in ('PREDECESSORS.json', 'SOURCE-PINS.json', 'BOUNDED-SOURCES.json'))
        return {p.relative_to(HERE).as_posix(): sha(p) for p in sorted(files)}
    execution_pins = execution_inputs()
    work.mkdir(parents=True)
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONPYCACHEPREFIX=str(work / 'pycache'),
               PYTHONINTMAXSTRDIGITS='0', OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1')
    for key in ('PYTHONOPTIMIZE', 'WITNESS_DISCOVER', 'WITNESS_RECORD', 'WITNESS_SPEC'):
        env.pop(key, None)
    stages = []

    def run(name, script, *arguments):
        start = time.monotonic()
        log = work / (name + '.log')
        command = [sys.executable, '-B', str(script), *map(str, arguments)]
        with log.open('w') as stream:
            process = subprocess.run(command, env=env, stdout=stream, stderr=subprocess.STDOUT)
        stages.append(dict(name=name, command=command, exit_code=process.returncode,
                           seconds=time.monotonic() - start, log_sha256=sha(log)))
        write(work / 'STAGES.json', stages)
        require(process.returncode == 0, name + ': ' + log.read_text()[-4000:])
        print('PASS', name, flush=True)

    run('generate', HERE / 'generator.py', '--source2462', sources['2462'],
        '--source2588', sources['2588'], '--out', work / 'generated')
    for tag in ('base', 'extra'):
        name = 'eight-alias-' + tag + '.json.gz'
        require(read(work / 'generated/candidate' / name) == read(HERE / 'inputs/candidate' / name),
                'Complete regenerated/publication word equality: ' + tag)
    run('baseline', sources['2588'] / 'verify_release.py', '--main', args.main.resolve(),
        '--work', work / 'baseline', '--jobs', 4)
    run('candidate', HERE / 'admit.py', '--source2462', sources['2462'],
        '--source2588', sources['2588'], '--baseline', work / 'baseline/verify',
        '--words', work / 'generated/candidate', '--work', work / 'candidate')
    result = read(work / 'candidate/RESULT.json')
    require(result['status'] == 'PASS_CHANGED_T74_FULL_CONDITIONAL_ADMISSION', 'Missing full candidate admission')
    result.update(reproduction_stages=stages, local_generation_sha256=sha(work / 'generated/RESULT.json'),
                  baseline_release_sha256=sha(work / 'baseline/RELEASE-RECEIPT.json'),
                  fresh_baseline=True, fresh_changed_natives=True, execution_inputs=execution_pins)
    for number, package in sources.items():
        check_source(package, number)
    check_inputs()
    require(execution_inputs() == execution_pins, 'Execution source/input bytes changed during full reproduction')
    write(work / 'RESULT.json', result)
    print(result['status'], result['kappa_decimal'], flush=True)

if __name__ == '__main__':
    main()
