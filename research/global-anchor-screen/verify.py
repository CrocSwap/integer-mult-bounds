#!/usr/bin/env python3
"""Rebuild the selected paid live-anchor word and its exact finite certificate.

Uses the attributed PR57/60/62 checkers and fixed-profile formulas. Prepared
with substantial OpenAI Codex assistance; inherited theorem assumptions remain.
"""
import sys

if sys.flags.optimize:
    raise ValueError('Assertions must remain enabled')
sys.dont_write_bytecode = True

from fractions import Fraction as Q
from hashlib import sha256
import json
import os
from pathlib import Path
import shlex
import subprocess
import tempfile

from selected_compile import compile_axis, replay
from binary_frame_profile_prepare import prepare
from evaluate import verify as inherited

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def read(path):
    return json.loads(path.read_text())


def main():
    manifest = read(HERE/'selected-manifest.json')
    for name, digest in manifest['files'].items():
        assert sha256((HERE/name).read_bytes()).hexdigest() == digest, name
    for name, digest in read(HERE/'SOURCE.json')['unchanged_consumed_sources'].items():
        assert sha256((ROOT/name).read_bytes()).hexdigest() == digest, name
    inherited.check_sources()
    profiles, words = [], {'axes': {}}
    with tempfile.TemporaryDirectory(prefix='global-anchor-verify-') as directory:
        work = Path(directory)
        profiler = work/'profiles'
        subprocess.run([*shlex.split(os.environ.get('CXX', 'c++')), '-O3', '-std=c++17',
                        '-I', str(inherited.INHERITED/'scripts/partial_swap'),
                        str(ROOT/'scripts/experiments/binary_frame_profiles.cpp'),
                        '-o', str(profiler)], check=True)
        for h in (23, 25):
            compile_axis(h, work)
            receipt = read(work/f'receipt-{h}.json')
            expected = read(HERE/'selected-reproduction.json')['axes'][str(h)]
            assert receipt == expected, f'h={h} compile/replay drift'
            words['axes'][str(h)] = receipt
            transitions = work/f'word-{h}.bin'
            prepare(work/f'word-{h}.json.gz', transitions)
            subprocess.run([str(profiler), str(transitions)], check=True)
            profile = read(Path(str(transitions)+'.profiles.json'))
            assert profile == read(HERE/f'selected-profiles-{h}.json'), f'h={h} profile drift'
            profiles.append(profile)
    profile = inherited.profile(profiles, words)
    certificate = read(HERE/'selected-arithmetic.json')
    assert inherited.arithmetic.js(profile) == certificate['profile']
    bit, kappa = Q(certificate['bit_saving']), Q(certificate['kappa'])
    assert (bit, kappa) == (Q(5103199, 10**11), Q(5102938, 10**11))
    moment = inherited.arithmetic.moment(profile['m'], profile['W'],
                                          profile['child_multiplicities'], bit)
    assert moment['strict_gap'] > 0
    assert inherited.arithmetic.js(moment) == certificate['exact_moment']
    next_bit = inherited.arithmetic.moment(profile['m'], profile['W'],
                                            profile['child_multiplicities'], bit+Q(1, 10**11))
    assert next_bit['lower'] > 1
    assert str(next_bit['lower']) == certificate['next_bit_grid_lower']
    bridge = read(inherited.OLD/'certificate.json')['finite_bridge']
    bridge['bit']['W'] = profile['W']
    assembly = inherited.balanced.assembly(bridge, bit, kappa)
    assert len(assembly['constraints']) == 47 and len(assembly['margins']) == 7
    assert inherited.arithmetic.js(assembly) == certificate['assembly']
    try:
        inherited.balanced.assembly(bridge, bit, kappa+Q(1, 10**11))
    except inherited.balanced.InvalidAssembly:
        pass
    else:
        raise AssertionError('Next kappa grid point unexpectedly passes')
    prior = read(ROOT/'research/rank-pair/screen-certificate.json')['bit']
    comparison = read(HERE/'comparison-pr63.json')
    for key in ('m', 'W', 'child_multiplicities'):
        assert comparison[key] == prior[key], key
    assert kappa > Q(20411033624901463, 400000000000000000000)
    assert kappa > Q(12757157778919, 250000000000000000)
    subprocess.run([sys.executable, str(HERE/'check_dominance.py')], check=True)
    print('PASS selected words, dirty replay, paid profiles, 47 constraints, seven margins, and next-grid rejection')
    print(f'PASS conditional kappa={kappa}; bit saving={bit}')


if __name__ == '__main__':
    main()
