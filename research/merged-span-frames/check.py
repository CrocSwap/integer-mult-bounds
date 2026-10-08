#!/usr/bin/env python3
"""Regenerate dirty replay, literal paths, all exact profiles and paid arithmetic in scratch."""
import sys
if sys.flags.optimize:
    raise ValueError('Assertions must remain enabled')
sys.dont_write_bytecode = True
import argparse
from concurrent.futures import ProcessPoolExecutor
import json
import os
from pathlib import Path
import shlex
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PR91 = ROOT / 'references/frame-compiler/pr91'
sys.path.insert(0, str(PR91 / 'scripts/experiments'))
from binary_frame_replay import replay
from binary_frame_profile_prepare import prepare
import binary_frame_math as arithmetic
from endpoints import select
from compose import compose

def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')

def equal_json(actual, expected):
    assert json.loads(actual.read_text()) == json.loads(expected.read_text()), expected.name

def axis(job):
    h, work, executable, workers = job
    work = Path(work)
    word = work / f'word-{h}.json.gz'
    assert word.read_bytes() == (HERE / word.name).read_bytes(), 'Fresh physical word differs'
    equal_json(work / f'axis-{h}.json', HERE / f'axis-{h}.json')
    actual = json.loads(json.dumps(replay(word)))
    assert actual['roles'] == json.loads((work / f'axis-{h}.json').read_text())['compiled']['roles']
    write_json(work / f'replay-{h}.json', actual)
    equal_json(work / f'replay-{h}.json', HERE / f'replay-{h}.json')
    transitions = json.loads(json.dumps(prepare(word, work / f'word-{h}.bin')))
    write_json(work / f'transitions-{h}.json', transitions)
    equal_json(work / f'transitions-{h}.json', HERE / f'transitions-{h}.json')
    subprocess.run([str(executable), str(work / f'word-{h}.bin')], check=True)
    physical = json.loads((work / f'word-{h}.bin.profiles.json').read_text())
    write_json(work / f'profile-{h}.json', physical)
    equal_json(work / f'profile-{h}.json', HERE / f'profile-{h}.json')
    assert physical['R'] == actual['roles'] and physical['crt_disagreements'] == 0
    arithmetic.exactness(h)
    for retirement in (False, True):
        target = work / 'retirement' if retirement else work
        target.mkdir(exist_ok=True)
        selection = select(h, workers, work, retirement)
        path = target / f'selection-{h}.json'
        path.write_text(json.dumps(selection, sort_keys=True, separators=(',', ':')) + '\n')
        equal_json(path, HERE / ('retirement' if retirement else '.') / path.name)
    print(f'PASS complete dirty replay, literal first/last paths, exact local and merged profiles h={h}', flush=True)

def generate(work, workers=4):
    work = Path(work)
    executable = work / 'profiles'
    environment = dict(os.environ)
    environment.pop('SDKROOT', None)
    subprocess.run([*shlex.split(os.environ.get('CXX', 'c++')), '-O3', '-std=c++17',
                    '-I', str(PR91 / 'references/frame-compiler/pr48/scripts/partial_swap'),
                    str(PR91 / 'scripts/experiments/binary_frame_profiles.cpp'), '-o', str(executable)],
                   env=environment, check=True)
    with ProcessPoolExecutor(max_workers=2) as pool:
        list(pool.map(axis, [(h, work, executable, workers) for h in (23, 25)]))
    for retirement in (False, True):
        target = work / 'retirement' if retirement else work
        expected = HERE / 'retirement' if retirement else HERE
        compose(target, work, executable)
        for name in ['certificate.json'] + [f'removed-{h}.bin.profiles.json' for h in (23, 25)]:
            equal_json(target / name, expected / name)
    print('PASS complete paid ledgers, exact moments, adjacent grids and dynamic bridge', flush=True)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--work', required=True, type=Path)
    parser.add_argument('--workers', type=int, default=4)
    args = parser.parse_args()
    generate(args.work, args.workers)
