#!/usr/bin/env python3
"""Regenerate paid profiles and exact screen for rank-first PR62 composition.

Uses PR62's profile construction, eumemic's PR57 word/profile checkers and
Chafik Boukhalfa's PR60 rank-first compiler. Prepared by Dominik Scholz with
substantial OpenAI GPT-6 Astra assistance. Apache-2.0; inherited notices apply.
This is a research screen, not a claim of formal verification.
"""
import sys

if sys.flags.optimize:
    raise ValueError('Assertions must remain enabled')
sys.dont_write_bytecode = True

from fractions import Fraction as Q
from hashlib import sha256
import importlib.util
import json
import os
from pathlib import Path
import shlex
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
EXP = ROOT / 'scripts/experiments'
sys.path.insert(0, str(EXP))
import binary_frame_math as arithmetic
from binary_frame_profile_prepare import prepare
from binary_frame_replay import replay
from frame_compile import COMPILER_SHA256, GRAPH_SHA256

spec = importlib.util.spec_from_file_location(
    'pair_frame_verifier', ROOT / 'research/pair-assembly/frame/frame_verify.py')
baseline = importlib.util.module_from_spec(spec)
spec.loader.exec_module(baseline)


def main():
    records = json.loads((HERE / 'frame-compiler.json').read_text())
    assert records['source']['compiler_sha256'] == COMPILER_SHA256
    assert records['source']['graph_sha256'] == GRAPH_SHA256
    assert sha256((EXP/'rank_pair_compiler.py').read_bytes()).hexdigest() == records['source']['compiler_sha256']
    assert sha256((ROOT/records['source']['graph']).read_bytes()).hexdigest() == records['source']['graph_sha256']
    baseline.check_sources()
    profiles = []
    profiler = HERE / 'profiles'
    subprocess.run([*shlex.split(os.environ.get('CXX', 'c++')), '-O3', '-std=c++17', '-I',
                    str(baseline.INHERITED / 'scripts/partial_swap'),
                    str(EXP / 'binary_frame_profiles.cpp'), '-o', str(profiler)], check=True)
    for h in (23, 25):
        path = HERE / f'frame-word-{h}.json.gz'
        packed = path.read_bytes()
        assert sha256(packed).hexdigest() == records['axes'][str(h)]['gzip_sha256']
        receipt = replay(path)
        assert json.loads(json.dumps(receipt)) == records['axes'][str(h)]['replay']
        transitions = HERE / f'word{h}.bin'
        prepared = prepare(path, transitions)
        (HERE / f'frame-transitions-{h}.json').write_text(json.dumps(prepared, indent=2)+'\n')
        subprocess.run([str(profiler), str(transitions)], check=True)
        profile = json.loads(Path(str(transitions)+'.profiles.json').read_text())
        (HERE / f'frame-profiles-{h}.json').write_text(json.dumps(profile, indent=2)+'\n')
        profiles.append(profile)
        print(f'PASS physical replay and fixed profiles h={h}, roles={profile["R"]}', flush=True)
    # The unchanged profile constructor validates the literal rank identity.
    baseline.WIRES_S = 2*4073300 + sum(4073300//f['v']*f['R'] for f in profiles)
    baseline.MASS_S = 575*baseline.WIRES_S - 1846900
    profile = baseline.profile(profiles, records)
    rows = profile['child_multiplicities']
    low, high = 1, 7170000
    while low+1 < high:
        mid = (low+high)//2
        test = arithmetic.moment(575, profile['W'], rows, Q(mid, 10**11))
        if test['strict_gap'] > 0:
            low = mid
        else:
            high = mid
    ab = Q(low, 10**11)
    accepted = arithmetic.moment(575, profile['W'], rows, ab)
    rejected = arithmetic.moment(575, profile['W'], rows, Q(high, 10**11))
    assert accepted['strict_gap'] > 0 and rejected['lower'] > 1
    bridge = json.loads((baseline.OLD/'certificate.json').read_text())['finite_bridge']
    bridge['bit']['W'] = profile['W']
    preliminary = baseline.balanced.assembly(bridge, ab, Q(1, 10**11))
    scaled = preliminary['minimum_margin'] * 10**11
    kappa = Q(-(-scaled.numerator//scaled.denominator)-1, 10**11)
    assembled = baseline.balanced.assembly(bridge, ab, kappa)
    try:
        baseline.balanced.assembly(bridge, ab, kappa+Q(1, 10**11))
    except baseline.balanced.InvalidAssembly:
        pass
    else:
        raise AssertionError('Next assembly grid point unexpectedly passed')
    prior = json.loads((ROOT/'research/pair-assembly/frame/frame-certificate.json').read_text())
    old_rows = {int(t): n for t,n in prior['bit']['child_multiplicities'].items()}
    old_at_new = arithmetic.moment(575, prior['bit']['W'], old_rows, ab)
    result = dict(
        status='Exact finite screen; retained analytic and fixed-tape hypotheses unchanged',
        kappa=kappa, bit_saving=ab, next_bit_saving=Q(high, 10**11),
        bit=dict(profile, moment=accepted, excluded_above_lower=rejected['lower']),
        assembly=assembled, finite_bridge=bridge,
        eventual_bounds=baseline.balanced.cutoffs(bridge, assembled),
        comparison=dict(pr62_kappa=Q(5101691,10**11),
                        difference=kappa-Q(5101691,10**11),
                        ratio=kappa/Q(5101691,10**11),
                        pr61_head='afb7cb67d1858641315cfbf4ac768ee64a8eff3a',
                        pr61_kappa=Q(25508460085039,500000000000000000),
                        difference_pr61=kappa-Q(25508460085039,500000000000000000),
                        ratio_pr61=kappa/Q(25508460085039,500000000000000000),
                        pr62_network_at_new_bit_lower=old_at_new['lower']),
        source=dict(records=records['source'], compiler_sha256=sha256((EXP/'rank_pair_compiler.py').read_bytes()).hexdigest(),
                    inherited_verifier_sha256=sha256((ROOT/'research/pair-assembly/frame/frame_verify.py').read_bytes()).hexdigest()))
    (HERE/'screen-certificate.json').write_text(json.dumps(arithmetic.js(result), indent=2, sort_keys=True)+'\n')
    print('EXACT SCREEN', json.dumps(arithmetic.js(dict(kappa=kappa, bit=ab, W=profile['W'],
          comparison=result['comparison']))), flush=True)


if __name__ == '__main__':
    main()
