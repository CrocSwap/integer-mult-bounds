#!/usr/bin/env python3
"""Replay complete selected words, paid profiles and exact conditional assembly."""
import argparse
from fractions import Fraction as Q
from hashlib import sha256
import importlib.util
import json
import os
from pathlib import Path
import shlex
import subprocess
import sys
import tempfile

if sys.flags.optimize:
    raise ValueError('Assertions must remain enabled')
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT/'scripts/experiments'))
import binary_frame_math as arithmetic
from binary_frame_profile_prepare import prepare
from binary_frame_replay import replay


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def generate(record=False):
    sources = json.loads((HERE/'SOURCE.json').read_text())
    for name, digest in sources['files'].items():
        assert sha256((ROOT/name).read_bytes()).hexdigest() == digest, name
    baseline = load('ordered_baseline', ROOT/'research/pair-assembly/frame/frame_verify.py')
    exact = load('ordered_exact', ROOT/'research/rank-pair-refinement/refine.py')
    baseline.check_sources()
    selection = json.loads((HERE/'selection.json').read_text())
    records, profiles = {}, []
    with tempfile.TemporaryDirectory(prefix='ordered-frame-replay-') as directory:
        work = Path(directory)
        profiler = work/'profiles'
        subprocess.run([*shlex.split(os.environ.get('CXX','c++')), '-O3', '-std=c++17',
                        '-I', str(baseline.INHERITED/'scripts/partial_swap'),
                        str(ROOT/'scripts/experiments/binary_frame_profiles.cpp'),
                        '-o', str(profiler)], check=True)
        for h in (23,25):
            axis = json.loads((HERE/f'axis-{h}.json').read_text())
            assert axis['configuration'] == selection['axes'][str(h)]
            word = HERE/f'frame-word-{h}.json.gz'
            assert sha256(word.read_bytes()).hexdigest() == axis['gzip_sha256']
            receipt = json.loads(json.dumps(replay(word)))
            assert receipt == axis['replay']
            records[str(h)] = axis
            path = work/f'word-{h}.bin'
            transitions = prepare(word, path)
            assert transitions['word_sha256'] == axis['word_sha256']
            subprocess.run([str(profiler), str(path)], check=True)
            profile = json.loads(Path(str(path)+'.profiles.json').read_text())
            assert profile['crt_disagreements'] == 0
            profile_path = HERE/f'frame-profiles-{h}.json'
            transition_path = HERE/f'frame-transitions-{h}.json'
            transitions = json.loads(json.dumps(transitions))
            if record:
                profile_path.write_text(json.dumps(profile, indent=2)+'\n')
                transition_path.write_text(json.dumps(transitions, indent=2)+'\n')
            else:
                assert profile == json.loads(profile_path.read_text())
                assert transitions == json.loads(transition_path.read_text())
            profiles.append(profile)
            print(f'PASS all dirty basis vectors, literal transitions and paid profiles h={h}', flush=True)
    width = 2*4073300 + sum(4073300//p['v']*p['R'] for p in profiles)
    baseline.WIRES_S = width
    baseline.MASS_S = 575*width-1846900
    paid = baseline.profile(profiles, dict(axes=records))
    assert paid['W'] == width
    rows = paid['child_multiplicities']
    lo, hi, grid = 1, 71700000000000, 10**18
    while lo+1 < hi:
        mid = (lo+hi)//2
        if exact.moment(arithmetic, 575, width, rows, Q(mid,grid))['upper'] < 1:
            lo = mid
        else:
            hi = mid
    a = Q(lo,grid)
    accepted = exact.moment(arithmetic, 575, width, rows, a)
    rejected = exact.moment(arithmetic, 575, width, rows, Q(hi,grid))
    assert accepted['upper'] < 1 < rejected['lower']
    old = json.loads((ROOT/'research/rank-pair/screen-certificate.json').read_text())
    bridge = old['finite_bridge']
    bridge['bit']['W'] = width
    preliminary = baseline.balanced.assembly(bridge, a, Q(old['kappa']), h=Q(1,grid))
    kappa = Q(exact.ceil(preliminary['minimum_margin']*grid)-1,grid)
    assembly = baseline.balanced.assembly(bridge, a, kappa, h=Q(1,grid))
    try:
        baseline.balanced.assembly(bridge, a, kappa+Q(1,grid), h=Q(1,grid))
    except baseline.balanced.InvalidAssembly:
        pass
    else:
        raise AssertionError('Next kappa grid point unexpectedly accepted')
    old_rows = {int(t):n for t,n in old['bit']['child_multiplicities'].items()}
    old_at_new = exact.moment(arithmetic, 575, old['bit']['W'], old_rows, a)
    assert old_at_new['lower'] > 1
    result = dict(
        status='Conditional exact finite construction; inherited general hypotheses',
        kappa=kappa, bit_saving=a, h=Q(1,grid),
        bit=dict(paid, accepted=accepted, next_saving=Q(hi,grid), rejected=rejected),
        assembly=assembly, eventual_bounds=baseline.balanced.cutoffs(bridge,assembly),
        comparison=dict(pr63_kappa=Q(old['kappa']),
                        absolute_gain=kappa-Q(old['kappa']),
                        relative_gain=kappa/Q(old['kappa'])-1,
                        pr63_network_at_new_bit_lower=old_at_new['lower'],
                        saved_wires=old['bit']['W']-width),
        sources=sources, axes=records,
        scope='Reordered scalar DAG, paid dependence selection and geometric '
              'relabeling. The OpenAI framework and all-size framed-word transfer, '
              'fixed-tape, analytic, precision, routing, prime and recovery '
              'hypotheses remain inherited. No practical runtime or global '
              'optimality claim.')
    return arithmetic.js(result)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--record', action='store_true')
    args = parser.parse_args()
    result = generate(args.record)
    path = HERE/'certificate.json'
    if args.record:
        path.write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    else:
        assert result == json.loads(path.read_text()), 'Certificate mismatch'
    print('PASS conditional kappa='+result['kappa']+'; bit saving='+result['bit_saving'],flush=True)
    print('47 strict assembly inequalities, seven margins; both next grid values rejected',flush=True)
