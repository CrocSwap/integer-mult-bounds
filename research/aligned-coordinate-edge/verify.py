#!/usr/bin/env python3
"""Replay adjacent coordinate transpositions of the immutable PR91 words.

Only the coordinate action changes. PR91's producer is inherited, not recompiled
by this verifier. Exact moment and balanced assembly code remain unchanged.
Maxime Fleury with Codebuff assistance; inherited Apache-2.0 notices apply.
"""
import sys
if sys.flags.optimize:
    raise ValueError('Assertions must remain enabled')
sys.dont_write_bytecode = True
import argparse
from collections import Counter
from fractions import Fraction as Q
import gzip
from hashlib import sha256
import json
from math import comb
import os
from pathlib import Path
import shlex
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
EXP = ROOT/'scripts/experiments'
sys.path.insert(0,str(EXP))
from aligned_composition_nodeops import relabel
from binary_frame_replay import replay
from binary_frame_profile_prepare import prepare
from split_pair_arithmetic import refine, audit
import binary_frame_math as arithmetic

TARGET = Q(52789616935221,10**18)
LATEST_TARGET = Q(13197726684911,250000000000000000)
EXPECTED = Q(13197734464639,250000000000000000)


def save(path,value):
    path.write_text(json.dumps(arithmetic.js(value),indent=2,sort_keys=True)+'\n')


def sources():
    local = json.loads((HERE/'SOURCE.json').read_text())
    required = {str(p.relative_to(ROOT)) for p in HERE.iterdir()
                if p.is_file() and p.name not in ('SOURCE.json','certificate.json')}
    required.add('.github/workflows/aligned-coordinate-edge.yml')
    required.add('research/aligned-composition/SOURCE.json')
    required.add('certificates/aligned-composition-kappa.json')
    assert required <= set(local['files']), 'Incomplete local source closure'
    for name,digest in local['files'].items():
        assert sha256((ROOT/name).read_bytes()).hexdigest() == digest, name
    inherited = json.loads((ROOT/'research/aligned-composition/SOURCE.json').read_text())
    for name,digest in inherited['files'].items():
        assert sha256((ROOT/name).read_bytes()).hexdigest() == digest, name
    return sha256((HERE/'SOURCE.json').read_bytes()).hexdigest()


def permutation(h):
    value = json.loads((HERE/f'permutation-{h}.json').read_text())
    expected = list(range(h)); expected[5],expected[6] = expected[6],expected[5]
    if h == 25:
        expected[22],expected[23] = expected[23],expected[22]
    assert value == expected, 'Only the frozen adjacent transpositions are certified'
    return value


def regenerate(h):
    parent = ROOT/f'certificates/aligned-composition-word-{h}.json.gz'
    word = json.loads(gzip.decompress(parent.read_bytes()))
    word = relabel(word,permutation(h))
    raw = (json.dumps(word,separators=(',',':'))+'\n').encode()
    assert raw == gzip.decompress((HERE/f'word-{h}.json.gz').read_bytes()), 'Coordinate word changed'
    return raw


def paid_profile(profiles):
    assert sorted(p['h'] for p in profiles) == [23,25]
    N,m = comb(23,3)*comb(25,3),575
    W = 2*N+sum(N//p['v']*p['R'] for p in profiles)
    L = sum(N//p['v']*p['loss'] for p in profiles)
    rows = Counter({1:19*N,21:2*N,17:2*N,481:2*N})
    for p in profiles:
        h = p['h']; rep = N//p['v']; bank = rep*p['R']
        assert p['crt_disagreements'] == 0 and p['field_prime'] == 2**61-1
        assert p['v'] == comb(h,3) and p['loss'] == h*(h-1)
        assert p['blocks'][0] == p['blocks'][h] == 0
        assert sum(t*n for t,n in enumerate(p['blocks'])) == h*p['R']+p['loss'] == p['rank_sum']
        rows.update({t:rep*n for t,n in enumerate(p['blocks']) if t and n})
        rows[h] += bank; rows[m-2*h] += bank
        rows[1] += 2*N; rows[h-2] += 2*N
    mass = sum(t*n for t,n in rows.items())
    assert mass == m*W-N+L and m*W-mass == 1846900
    assert all(0 < t < m and n > 0 for t,n in rows.items())
    return dict(m=m,N=N,W=W,L=L,total_rank=mass,deficit=m*W-mass,
                child_multiplicities=dict(sorted(rows.items())))


def score(profiles):
    bit = paid_profile(profiles)
    rows,width,m = bit['child_multiplicities'],bit['W'],bit['m']
    denominator = 10**18
    low,high = 1,refine.floor_scaled(Q(717,10**7),denominator)
    assert refine.exact_moment(m,width,rows,Q(low,denominator))['upper'] < 1
    assert refine.exact_moment(m,width,rows,Q(high,denominator))['lower'] > 1
    while low+1 < high:
        mid = (low+high)//2
        enclosure = refine.exact_moment(m,width,rows,Q(mid,denominator))
        if enclosure['upper'] < 1:
            low = mid
        elif enclosure['lower'] > 1:
            high = mid
        else:
            raise ArithmeticError('Inconclusive rational enclosure')
    saving = Q(low,denominator)
    accepted = refine.exact_moment(m,width,rows,saving)
    rejected = refine.exact_moment(m,width,rows,Q(high,denominator))
    assert accepted['upper'] < 1 < rejected['lower']
    independent = audit.independent_moment(arithmetic.js(bit),saving,arithmetic.js(accepted['terms']))
    independent_next = audit.independent_moment(arithmetic.js(bit),Q(high,denominator),arithmetic.js(rejected['terms']))
    assert independent[1] < 1 < independent_next[0]
    parent = json.loads((ROOT/'certificates/aligned-composition-kappa.json').read_text())
    assert Q(parent['kappa']) == TARGET
    assert (width,bit['total_rank']) == (parent['bit']['W'],parent['bit']['total_rank'])
    bridge = parent['finite_bridge']
    assembled = refine.assemble(bridge,saving,Q(1,10**12),denominator)
    kappa = assembled['kappa']
    coarse_saving = Q(refine.floor_scaled(saving,10**11),10**11)
    coarse = refine.assemble(bridge,coarse_saving,Q(1,10**12),10**11)
    assert refine.exact_moment(m,width,rows,coarse_saving)['upper'] < 1
    oldrows = {int(t):n for t,n in parent['bit']['child_multiplicities'].items()}
    parent_at_new = refine.exact_moment(m,width,oldrows,saving)
    assert len(assembled['assembly']['constraints']) == 47
    assert all(v > 0 for v in assembled['assembly']['constraints'].values())
    assert len(assembled['assembly']['margins']) == 7
    return dict(kappa=kappa,target=TARGET,improvement=kappa-TARGET,bit_saving=saving,
                next_bit_saving=Q(high,denominator),bit=bit,
                accepted_moment=accepted,rejected_moment=rejected,
                independent_bounds=independent,independent_next=independent_next,
                finite_bridge=bridge,assembly=assembled,
                coarse_grid_control=dict(bit_saving=coarse_saving,assembly=coarse),
                parent_profile_at_new_saving=parent_at_new)


def verify(record=False):
    digest = sources()
    axes,profiles = {},[]
    with tempfile.TemporaryDirectory(prefix='aligned-coordinate-edge-') as directory:
        work = Path(directory)
        exe = work/'profiles'
        subprocess.run([*shlex.split(os.environ.get('CXX','c++')),'-O3','-std=c++17',
            '-I',str(ROOT/'references/frame-compiler/pr48/scripts/partial_swap'),
            str(EXP/'binary_frame_profiles.cpp'),'-o',str(exe)],check=True)
        for h in (23,25):
            raw = regenerate(h)
            word = HERE/f'word-{h}.json.gz'
            receipt = replay(word)
            trans = work/f'{h}.bin'
            transitions = prepare(word,trans)
            subprocess.run([str(exe),str(trans)],check=True)
            profile = json.loads(Path(str(trans)+'.profiles.json').read_text())
            assert profile == json.loads((HERE/f'profiles-{h}.json').read_text())
            assert receipt['roles'] == profile['R'] == {23:26387,25:34772}[h]
            profiles.append(profile)
            axes[str(h)] = dict(permutation=permutation(h),word_sha256=sha256(raw).hexdigest(),
                gzip_sha256=sha256(word.read_bytes()).hexdigest(),profile=profile,
                replay=receipt,transitions=transitions)
            print(f'PASS h={h}: deterministic coordinate regeneration, full dirty replay, transitions and CRT profile',flush=True)
    result = score(profiles)
    assert result['kappa'] == EXPECTED > LATEST_TARGET > TARGET
    assert result['parent_profile_at_new_saving']['lower'] > 1
    assert result['coarse_grid_control']['assembly']['kappa'] > LATEST_TARGET
    previous_profiles = [json.loads((HERE/f'pr93-profiles-{h}.json').read_text()) for h in (23,25)]
    previous = score(previous_profiles)
    assert previous['kappa'] == LATEST_TARGET
    previous_rows = previous['bit']['child_multiplicities']
    previous_at_new = refine.exact_moment(previous['bit']['m'],previous['bit']['W'],previous_rows,result['bit_saving'])
    assert previous_at_new['lower'] > 1
    result['pr93_comparison'] = dict(kappa=LATEST_TARGET,improvement=result['kappa']-LATEST_TARGET,
        complete_profile_at_new_saving=previous_at_new,
        provenance=json.loads((HERE/'pr93-comparison.json').read_text()))
    result.update(status='Exact finite conditional coordinate witness; inherited all-size transfer assumptions remain',
        parent_commit='264f202b52edc04d0c72ca9cb3138282ca68b9ad',
        source_manifest_sha256=digest,axes=axes,
        proof_limits=['The PR91 producer and all-size compiler argument are inherited, not recompiled here.',
            'Only coordinate relabels are regenerated; all complete physical words and fixed-basis profiles are replayed.',
            'The PR91 Lean arithmetic module certifies the parent, not these new numbers.',
            'Analytic, routing, recovery, prime-selection and fixed-tape assumptions remain inherited.',
            'No global optimum, practical speedup or O(n sqrt(log n)) algorithm is established.'])
    payload = json.loads(json.dumps(arithmetic.js(result)))
    if record:
        save(HERE/'certificate.json',payload)
    else:
        assert payload == json.loads((HERE/'certificate.json').read_text()), 'Certificate changed'
    print('PASS kappa='+str(result['kappa'])+'; gain='+str(result['improvement'])+'; 47 constraints, 7 margins, independent bounds and next-grid rejection',flush=True)
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--record',action='store_true')
    verify(parser.parse_args().record)
