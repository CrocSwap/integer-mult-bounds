#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Sequential cold baseline and composition, with unchanged scientific checks.

Only process time budgets are larger than the predecessor convenience wrapper.
Every source command and the original final baseline checker remain unchanged.
"""
import argparse
import importlib.util
import os
import subprocess
import sys
from pathlib import Path

import verify as v


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--work', type=Path, required=True)
    args = parser.parse_args()
    work = args.work.resolve()
    v.need(not work.exists(), 'fresh CI work root')
    work.mkdir()
    v.authenticate()
    v.baseline_modules()
    path = v.ROOT / 'research/rank7-t740-release/reproduce.py'
    spec = importlib.util.spec_from_file_location('original_baseline_harness', path)
    original = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(original)
    baseline = work / 'baseline'
    prepared = original.execute(v.ROOT, baseline, True)
    v.need(prepared['status'] == 'PREFLIGHT_ONLY_NOT_A_RELEASE', 'original baseline preflight')
    recipe = v.read(baseline / 'RECIPE.json')['commands']
    v.need([name for name, _ in recipe] == original.RECIPE_NAMES, 'every original source command')
    stages = v.read(baseline / 'STAGES.json')
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONINTMAXSTRDIGITS='0',
               OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1')
    for name in ['PYTHONOPTIMIZE', 'PYTHONPATH', 'WITNESS_SPEC', 'WITNESS_RECORD', 'WITNESS_DISCOVER']:
        env.pop(name, None)
    for name, command in recipe:
        original.run_stage(name, command, baseline, env, stages, 7200)
    result = original.check_release(baseline, baseline / 'pr3015', prepared['fill_sha256'], stages)
    original.save(baseline / 'RESULT.json', result)
    v.need(result['status'] == 'PASS_T740_R1_COMPLETE_RELEASE', 'completed original baseline gate')
    print('PASS_COMPLETE_COLD_BASELINE', flush=True)
    composition = work / 'composition'
    subprocess.run([sys.executable, '-B', str(v.P / 'reproduce.py'), '--repo', str(v.ROOT),
                    '--baseline-work', str(baseline), '--work', str(composition)], check=True, env=env)
    subprocess.run([sys.executable, '-B', str(v.P / 'seal.py'), '--baseline', str(baseline),
                    '--composition', str(composition)], check=True, env=env)
    subprocess.run([sys.executable, '-B', str(v.P / 'finalize.py')], check=True, env=env)


if __name__ == '__main__':
    main()
