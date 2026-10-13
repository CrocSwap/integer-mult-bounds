#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Check the exact bound and the frozen finite construction."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--main', type=Path, default=HERE.parents[1])
    parser.add_argument('--local', type=Path, default=HERE / 'inputs/local')
    parser.add_argument('--work', type=Path, required=True)
    args = parser.parse_args()
    if args.work.exists():
        raise ValueError('Choose a new check directory')
    if sys.flags.optimize:
        raise ValueError('Retained checks require assertions')
    args.work.mkdir(parents=True)
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', OPENBLAS_NUM_THREADS='1',
               OMP_NUM_THREADS='1')
    commands = [
        ['verify.py', '--out', args.work / 'BOUND.json'],
        ['controls.py', '--out', args.work / 'BOUND-CONTROLS.json'],
        ['construct.py', '--out', args.work / 'construction'],
        ['replay.py', '--main', args.main, '--local', args.local,
         '--work', args.work / 'replay'],
    ]
    for script, *arguments in commands:
        subprocess.run([sys.executable, '-B', str(HERE / script), *map(str, arguments)],
                       env=env, check=True)
    receipt = json.loads((args.work / 'replay/RESULT.json').read_text())
    if receipt['status'] != 'PASS_R480_T37_STRICT_FINITE_CONSTRUCTION':
        raise ValueError('Strict construction replay did not pass')
    print('PASS_K8_JOINT_X54_T37_ALL_REPLICA_OPTIMUM_AND_ATTAINING_CONSTRUCTION',
          receipt['kappa_decimal'])


if __name__ == '__main__':
    main()
