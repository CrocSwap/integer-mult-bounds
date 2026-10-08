#!/usr/bin/env python3
"""Regenerate dirty replay, literal paths, all exact profiles and paid arithmetic in scratch."""
import sys
if sys.flags.optimize:
    raise ValueError('Assertions must remain enabled')
sys.dont_write_bytecode = True
import argparse
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
import gzip
from itertools import combinations
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
from endpoints import verify_selection
from compose import compose

def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')

def equal_json(actual, expected):
    assert json.loads(actual.read_text()) == json.loads(expected.read_text()), expected.name

def strict_word(word):
    """Validate literal incidences before inherited Python indexing or GF(2) replay.

    In particular, cancelling extra scatter gates are not free and negative
    indices are not aliases for valid frame/slot identifiers.
    """
    h, v, R = word['h'], word['v'], word['R']
    assert type(h) is int and h in (23, 25)
    assert type(v) is int and type(R) is int and R > 0
    triples = list(combinations(range(h), 3))
    assert v == len(triples)
    frames = word['frames']
    def index(x, bound):
        assert type(x) is int and 0 <= x < bound, 'Negative or out-of-range identifier'
    for core, cover in frames:
        assert type(core) is int and type(cover) is int and 0 < core <= cover < 1 << h
        assert not core & ~cover
        assert core.bit_count() in (1, 2) or core == cover and core.bit_count() == 3
    sources = word['sources']
    assert set(sources) == {str(i) for i in range(v)}, 'Source indices must be canonical and complete'
    assert len(set(sources.values())) == v
    frame_index = {tuple(frame): i for i, frame in reversed(list(enumerate(frames)))}
    physical = [-1] * R
    expected_events = []
    def incidence(slot, frame):
        index(slot, R)
        index(frame, len(frames))
        expected_events.append([slot, physical[slot], frame])
        physical[slot] = frame
    for i, slot in sources.items():
        mask = sum(1 << j for j in triples[int(i)])
        incidence(slot, frame_index[mask, mask])
    for a, b, frame in word['ops']:
        assert a != b
        incidence(a, frame)
        incidence(b, frame)
    expected_scatter = Counter()
    output_keys, output_slots = [], set()
    triple_index = {t: i for i, t in enumerate(triples)}
    for slot, frame, common, target in word['outputs']:
        incidence(slot, frame)
        index(common, h)
        assert slot not in output_slots
        output_slots.add(slot)
        assert isinstance(target, list) and len(target) in (1, 3)
        for coordinate in target:
            index(coordinate, h)
        assert target == sorted(set(target)) and common in target
        output_keys.append((common, tuple(target)))
        indices = [i for i, t in enumerate(triples) if common in t] if len(target) == 1 else [triple_index[tuple(target)]]
        expected_scatter.update((v+i, 2*v+slot) for i in indices)
    expected_outputs = [(c, (c,)) for c in range(h)] + [(c, t) for t in triples for c in t]
    assert Counter(output_keys) == Counter(expected_outputs), 'Output incidence inventory differs'
    for a, b in word['scatter']:
        index(a, 2*v)
        index(b, 2*v+R)
        assert a >= v and b >= 2*v
    assert Counter(map(tuple, word['scatter'])) == expected_scatter, 'Literal scatter multiplicity differs'
    recorded_paths = [[] for _ in range(R)]
    expected_paths = [[] for _ in range(R)]
    for slot, old, new in expected_events:
        if not expected_paths[slot] or expected_paths[slot][-1] != new:
            expected_paths[slot].append(new)
    recorded_state = [-1] * R
    for slot, old, new in word['events']:
        index(slot, R)
        index(new, len(frames))
        assert type(old) is int and (old == -1 or 0 <= old < len(frames))
        assert old == recorded_state[slot], 'Invalid initial sentinel or stale previous frame'
        recorded_state[slot] = new
        if not recorded_paths[slot] or recorded_paths[slot][-1] != new:
            recorded_paths[slot].append(new)
    # The compiler can log extra zero frame raises while allocating a role.
    # Removing repeated identical frames preserves all nonzero paid residuals.
    assert recorded_paths == expected_paths and all(recorded_paths), 'Literal per-role frame chronology differs'
    return dict(scatter_incidents=sum(expected_scatter.values()), frame_events=len(expected_events))

def axis(job):
    h, work, executable, workers = job
    work = Path(work)
    word = work / f'word-{h}.json.gz'
    assert word.read_bytes() == (HERE / word.name).read_bytes(), 'Fresh physical word differs'
    equal_json(work / f'axis-{h}.json', HERE / f'axis-{h}.json')
    strict_word(json.loads(gzip.decompress(word.read_bytes())))
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
        path = target / f'selection-{h}.json'
        frozen_path = HERE / ('retirement' if retirement else '.') / path.name
        frozen = json.loads(frozen_path.read_text())
        selection = verify_selection(frozen, h, workers, work, retirement)
        path.write_text(json.dumps(selection, sort_keys=True, separators=(',', ':')) + '\n')
        equal_json(path, frozen_path)
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
