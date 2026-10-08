#!/usr/bin/env python3
"""Replay the pair-assembly frame words, actual fixed profiles and assembly.

Adapted from PR #57's verify_skip_frame.py and skip_frame_compose.py (eumemic,
with OpenAI Codex assistance), with the PR #57 compiler words replaced by the
pair-assembly words. Every XOR word, dirty basis column, frame incidence and
fixed-basis profile is checked; the unchanged data geometry and general
transfer proofs remain inherited dependencies, exactly as in PR #57.
Adapted with assistance from Claude (Anthropic).
Usage: python frame_verify.py [--record]
"""
import sys
sys.dont_write_bytecode = True
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from math import comb
from pathlib import Path
import argparse
import gzip
import importlib.util
import json
import os
import shlex
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
EXP = ROOT/'scripts/experiments'
sys.path.insert(0, str(EXP))
import binary_frame_math as arithmetic
from binary_frame_profile_prepare import prepare
from binary_frame_replay import replay

AB_S = 5101952
KAPPA_S = 5101691
WIRES_S = 137151806
MASS_S = 78860441550
INHERITED = ROOT/'references/frame-compiler/pr48'
OLD = INHERITED/'research/copied-fixed'
AB = Q(AB_S, 10**11)
KAPPA = Q(KAPPA_S, 10**11)
EXCLUDED_ABOVE = Q(AB_S+1, 10**11)
PLAIN_KAPPA = Q(4986133, 10**11)
PR57_KAPPA = Q(4669442391, 10**14)
PR53_KAPPA = Q(4498144, 10**11)

spec = importlib.util.spec_from_file_location('pair_frame_balanced_assembly', OLD/'balanced_assembly.py')
balanced = importlib.util.module_from_spec(spec)
spec.loader.exec_module(balanced)


def check_sources():
    document = json.loads((INHERITED/'SOURCE.json').read_text())
    for name, digest in document['files'].items():
        assert sha256((INHERITED/name).read_bytes()).hexdigest() == digest, name
    record = json.loads((HERE/'frame-compiler.json').read_text())
    graph = ROOT/record['source']['graph']
    assert sha256(graph.read_bytes()).hexdigest() == record['source']['graph_sha256'], 'pair_graph.py changed'
    return document, record


def profile(profiles, words):
    a, b = 23, 25
    m, N = a*b, comb(a, 3)*comb(b, 3)
    W = 2*N + sum(N//f['v']*f['R'] for f in profiles)
    L = sum(N//f['v']*f['loss'] for f in profiles)
    parts = {'data': Counter({1: 18*N, 21: 2*N, 17: 2*N, 481: 2*N}),
             'paid_endpoint_copy': Counter({1: N})}
    for f in profiles:
        h = f['h']
        rep, bank = N//f['v'], N//f['v']*f['R']
        replayed = words['axes'][str(h)]['replay']
        assert f['R'] == replayed['roles']
        assert f['v'] == comb(h, 3) and f['loss'] == h*(h-1)
        assert f['crt_disagreements'] == 0 and f['field_prime'] == 2**61-1
        assert sum(t*n for t, n in enumerate(f['blocks'])) == h*f['R']+f['loss'] == f['rank_sum'] == replayed['rank_mass']
        assert f['blocks'][h] == 0  # Copied centers already included.
        arithmetic.exactness(h)
        parts[f'internal_{h}'] = Counter({t: n*rep for t, n in enumerate(f['blocks']) if t and n})
        parts[f'exterior_{h}'] = Counter({h: bank, m-2*h: bank})
        parts[f'data_growth_{h}'] = Counter({1: 2*N, h-2: 2*N})
    rows = sum(parts.values(), Counter())
    mass = sum(t*n for t, n in rows.items())
    assert mass == m*W-N+L and max(rows) == 529 and all(0 < t < m for t in rows)
    assert (W, mass, m*W-mass) == (WIRES_S, MASS_S, 1846900)
    return dict(m=m, N=N, W=W, L=L, total_rank=mass, deficit=m*W-mass, maxchild=max(rows),
                child_multiplicities=dict(sorted(rows.items())), parts=parts, axes=profiles)


def compose(p, sources):
    exact = arithmetic.moment(p['m'], p['W'], p['child_multiplicities'], AB)
    excluded = arithmetic.moment(p['m'], p['W'], p['child_multiplicities'], EXCLUDED_ABOVE)
    assert exact['strict_gap'] > 0 and excluded['lower'] > 1
    controls = {}
    for name in ('pr53', 'pr57'):
        row = json.loads((HERE.parent/f'comparison-{name}.json').read_text())
        rows = {int(t): n for t, n in row['child_multiplicities'].items()}
        controls[name] = arithmetic.moment(row['m'], row['W'], rows, AB)['lower']
        assert controls[name] > 1, name+' network not excluded at stacked saving'
    prior = json.loads((OLD/'certificate.json').read_text())
    bridge = prior['finite_bridge']
    bridge['bit']['W'] = p['W']
    assert p['W'].bit_length() == bridge['bit']['wire_bits']
    assembled = balanced.assembly(bridge, AB, KAPPA, a_complex=Q(717, 10**7))
    assert len(assembled['constraints']) == 47 and len(assembled['margins']) == 7
    try:
        balanced.assembly(bridge, AB, KAPPA+Q(1, 10**11), a_complex=Q(717, 10**7))
        next_grid_fails = False
    except AssertionError:
        next_grid_fails = True
    assert next_grid_fails
    assert KAPPA > PLAIN_KAPPA > PR57_KAPPA > PR53_KAPPA > Q(1, 2**15) and KAPPA < Q(1, 2**14)
    local = [HERE/name for name in ('frame_compile.py', 'frame_verify.py')]+[
        EXP/name for name in ('binary_frame_compiler.py', 'binary_frame_math.py', 'binary_frame_replay.py',
                              'binary_frame_profile_prepare.py', 'binary_frame_profiles.cpp')]
    return dict(
        status='Conditional exact fixed-basis moment and balanced assembly; inherited transfer hypotheses remain assumed',
        kappa=KAPPA, bit_saving=AB, bit_saving_excluded_above=EXCLUDED_ABOVE,
        bit=dict(p, moment=exact, excluded_above_lower=excluded['lower']),
        controls=dict(PR53_bit_at_stacked_lower=controls['pr53'], PR57_bit_at_stacked_lower=controls['pr57']),
        assembly=assembled, eventual_bounds=balanced.cutoffs(bridge, assembled), finite_bridge=bridge,
        comparison=dict(plain_pair_assembly_kappa=PLAIN_KAPPA, ratio_plain=KAPPA/PLAIN_KAPPA,
                        pr57_kappa=PR57_KAPPA, ratio_pr57=KAPPA/PR57_KAPPA,
                        pr53_kappa=PR53_KAPPA, ratio_pr53=KAPPA/PR53_KAPPA, next_kappa_grid_fails=next_grid_fails),
        exactness=[arithmetic.exactness(h) for h in (23, 25)], sources=sources,
        local_source_sha256={str(x.relative_to(ROOT)): sha256(x.read_bytes()).hexdigest() for x in local},
        scope='Pair-assembly graph compiled by PR #57\'s unchanged joint frame compiler. Ordered affine residual '
              'compiler, fixed-tape recursion, finite scalar overhead, balanced transfer, analytic/routing/recovery '
              'interfaces and PR #57\'s compiler argument remain inherited.')


def verify(record_mode=False):
    inherited, words = check_sources()
    profiles = []
    with tempfile.TemporaryDirectory(prefix='pair-frame-verify-') as directory:
        work = Path(directory)
        profiler = work/'profiles'
        subprocess.run([*shlex.split(os.environ.get('CXX', 'c++')), '-O3', '-std=c++17',
                        '-I', str(INHERITED/'scripts/partial_swap'),
                        str(EXP/'binary_frame_profiles.cpp'), '-o', str(profiler)], check=True)
        for h in (23, 25):
            word = HERE/f'frame-word-{h}.json.gz'
            axis = words['axes'][str(h)]
            packed = word.read_bytes()
            assert sha256(packed).hexdigest() == axis['gzip_sha256']
            assert sha256(gzip.decompress(packed)).hexdigest() == axis['word_sha256']
            receipt = replay(word)
            assert json.loads(json.dumps(receipt)) == axis['replay']
            transitions = work/f'word{h}.bin'
            prepared = json.loads(json.dumps(prepare(word, transitions)))
            path = HERE/f'frame-transitions-{h}.json'
            if record_mode:
                path.write_text(json.dumps(prepared, indent=2)+'\n')
            assert prepared == json.loads(path.read_text())
            subprocess.run([str(profiler), str(transitions)], check=True, capture_output=True, text=True)
            prof = json.loads(Path(str(transitions)+'.profiles.json').read_text())
            path = HERE/f'frame-profiles-{h}.json'
            if record_mode:
                path.write_text(json.dumps(prof, indent=2)+'\n')
            assert prof == json.loads(path.read_text())
            profiles.append(prof)
            print(f'PASS h={h}: full dirty basis, exact frame path, every fixed-basis profile', flush=True)
    p = profile(profiles, words)
    result = compose(p, dict(inherited=inherited, compiler_record=words['source']))
    (HERE/'frame-certificate.json').write_text(json.dumps(arithmetic.js(result), indent=2, sort_keys=True)+'\n')
    print('PASS conditional stacked kappa='+str(KAPPA)+'; bit saving='+str(AB), flush=True)
    print('47 strict inequalities, seven margins, next grid values rejected, PR #53 and #57 excluded', flush=True)
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--record', action='store_true')
    verify(parser.parse_args().record)
