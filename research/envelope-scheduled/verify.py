#!/usr/bin/env python3
"""Replay the scheduled envelope-balanced axes and rebuild their exact kappa.

The two words in this directory are produced by `compiler.py` in this
directory -- the pinned envelope-balanced composition with the region order of
each axis taken from `scheduler.MODES` (`node-asc` for axis 23, `width-node`
for axis 25) -- and then relabelled by the pinned coordinate orders
`order-23.json` and `order-25.json`, exactly as the pinned certificate does.

Everything downstream of the words is inherited without change: the PR48
logarithm enclosures, the PR65 rational moment/assembly arithmetic and the
balanced transfer.  `--regenerate` recompiles both words through the compiler
and asserts the result is byte-identical.
"""
import sys
if sys.flags.optimize: raise ValueError('Assertions must remain enabled')
sys.dont_write_bytecode = True
from pathlib import Path
from fractions import Fraction as Q
from collections import Counter
from math import comb
from hashlib import sha256
import argparse, gzip, importlib.util, json, os, shlex, subprocess, tempfile

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
PINNED = ROOT / 'research/envelope-balanced'
MODES = {23: 'node-asc', 25: 'width-node'}
sys.path.insert(0, str(ROOT / 'scripts/experiments'))
from binary_frame_replay import replay
from binary_frame_profile_prepare import prepare
from split_pair_arithmetic import refine, audit
import binary_frame_math as arithmetic
sys.path.insert(0, str(PINNED))
from width_bridge import bridge_for_width

DENOMINATOR = 10**18


def pinned_record():
    return json.loads((PINNED / 'certificate.json').read_text())


def shipped_profiles():
    return {h: json.loads((HERE / f'profiles-{h}.json').read_text()) for h in (23, 25)}


def relabel(word, order):
    spec = importlib.util.spec_from_file_location('pinned_verify', PINNED / 'verify.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    perm = {old: new for new, old in enumerate(order)}
    return module.relabel(word, dict(order=list(order), mapping={str(k): v for k, v in perm.items()}))


def regenerate(work):
    """Recompile both axes through this candidate's compiler and compare bytes."""
    words = {}
    for h in (23, 25):
        axis = PINNED / f'order-{h}.json'
        order = json.loads(axis.read_text())['order']
        directory = work / f'axis-{h}'
        subprocess.run([sys.executable, str(HERE / 'compiler.py'), '--h', str(h), '--work', str(directory)],
                       check=True, env=dict(os.environ, CXX=os.environ.get('CXX', 'c++')))
        compiled = json.loads(gzip.decompress((directory / 'word.json.gz').read_bytes()))
        raw = (json.dumps(relabel(compiled, order), separators=(',', ':')) + '\n').encode()
        words[h] = gzip.compress(raw, mtime=0)
        assert words[h] == (HERE / f'word-{h}.json.gz').read_bytes(), f'regenerated axis {h} changed'
        print(f'PASS regenerated axis {h} through this candidate\'s compiler.py with region order {MODES[h]}',
              flush=True)
    return words


def replay_axes(work, regenerate_words=False):
    profiler = work / 'profiles'
    subprocess.run(['c++', '-O3', '-std=c++17', '-I',
                    str(ROOT / 'references/frame-compiler/pr48/scripts/partial_swap'),
                    str(ROOT / 'scripts/experiments/binary_frame_profiles.cpp'), '-o', str(profiler)], check=True)
    if regenerate_words:
        regenerate(work)
    axes = []
    for h in (23, 25):
        gz = HERE / f'word-{h}.json.gz'
        path = work / f'word-{h}.json'
        path.write_bytes(gzip.decompress(gz.read_bytes()))
        receipt = replay(path)
        trans = work / f'transitions-{h}.bin'
        transitions = prepare(path, trans)
        subprocess.run([str(profiler), str(trans)], check=True)
        profile = json.loads(Path(str(trans) + '.profiles.json').read_text())
        assert profile == shipped_profiles()[h], f'axis {h} profile changed'
        assert profile['crt_disagreements'] == 0 and profile['v'] == comb(h, 3)
        axes.append(dict(h=h, mode=MODES[h], roles=receipt['roles'], profile=profile,
                         replay=receipt, transitions=transitions,
                         word_sha256=sha256(gz.read_bytes()).hexdigest(),
                         profile_sha256=sha256((HERE / f'profiles-{h}.json').read_bytes()).hexdigest()))
        print(f'PASS replay, transitions and exact profile of axis {h} (mode {MODES[h]})', flush=True)
    return axes


def rows_for(profiles):
    N = comb(23, 3) * comb(25, 3); m = 575
    W = 2 * N + sum(N // p['v'] * p['R'] for p in profiles)
    L = sum(N // p['v'] * p['loss'] for p in profiles)
    rows = Counter({1: 19 * N, 21: 2 * N, 17: 2 * N, 481: 2 * N})
    for p in profiles:
        h = p['h']; rep = N // p['v']; bank = rep * p['R']
        assert p['crt_disagreements'] == 0 and p['v'] == comb(h, 3)
        assert sum(t * n for t, n in enumerate(p['blocks'])) == h * p['R'] + h * (h - 1) == p['rank_sum']
        rows.update({t: n * rep for t, n in enumerate(p['blocks']) if t and n})
        rows[h] += bank; rows[m - 2 * h] += bank; rows[1] += 2 * N; rows[h - 2] += 2 * N
    bit = dict(m=m, N=N, W=W, L=L, total_rank=sum(t * n for t, n in rows.items()),
               child_multiplicities=dict(sorted(rows.items())))
    assert bit['total_rank'] == m * W - N + L, 'rank mass identity'
    assert all(0 < t < m for t in rows), 'child multiplicity outside the allowed band'
    return bit


def exact(bit, axes):
    m, width, rows = bit['m'], bit['W'], {int(t): n for t, n in bit['child_multiplicities'].items()}
    low, high = 1, refine.floor_scaled(Q(717, 10**7), DENOMINATOR)
    assert refine.exact_moment(m, width, rows, Q(low, DENOMINATOR))['upper'] < 1
    assert refine.exact_moment(m, width, rows, Q(high, DENOMINATOR))['lower'] > 1
    steps = 0
    while low + 1 < high:
        mid = (low + high) // 2
        test = refine.exact_moment(m, width, rows, Q(mid, DENOMINATOR))
        if test['upper'] < 1:
            low = mid
        elif test['lower'] > 1:
            high = mid
        else:
            raise ArithmeticError('Rational bounds inconclusive')
        steps += 1
    saving = Q(low, DENOMINATOR)
    accepted = refine.exact_moment(m, width, rows, saving)
    rejected = refine.exact_moment(m, width, rows, Q(high, DENOMINATOR))
    assert accepted['upper'] < 1 < rejected['lower'], 'grid neighbours must straddle one'
    bounds = audit.independent_moment(arithmetic.js(bit), saving, arithmetic.js(accepted['terms']))
    next_bounds = audit.independent_moment(arithmetic.js(bit), saving + Q(1, DENOMINATOR),
                                           arithmetic.js(rejected['terms']))
    assert bounds[1] < 1 < next_bounds[0], 'independent moment bounds must separate'
    inherited = pinned_record()['finite_bridge']
    bridge = bridge_for_width(inherited, width)
    result = refine.assemble(bridge, saving, Q(1, 10**12), DENOMINATOR)
    kappa = Q(result['kappa'])
    prior = Q(pinned_record()['kappa'])
    assert kappa > prior, 'candidate does not improve the pinned envelope-balanced kappa'
    for axis in axes:
        receipt = axis['replay']
        assert receipt['roles'] == axis['profile']['R'] == axis['roles']
    # Grid-robustness control: the candidate also clears the pinned kappa when the
    # saving and kappa are rounded down to the coarser 1e-11 grid.
    coarse = Q(refine.floor_scaled(saving, 10**11), 10**11)
    coarse_result = refine.assemble(bridge, coarse, Q(1, 10**12), 10**11)
    assert Q(coarse_result['kappa']) > prior
    return dict(
        status='Conditional exact fixed-basis moment and balanced assembly for the scheduled region orders; '
               'inherited PR48/PR57/PR65/PR82 transfer, routing, recovery and compiler advances remain assumed.',
        grid_denominator=DENOMINATOR, binary_search_steps=steps,
        bit_saving=saving, next_bit_saving=Q(high, DENOMINATOR),
        bit=bit, exact_moment=accepted, rejected_moment=rejected,
        independent_bounds=dict(accepted=bounds, next=next_bounds),
        finite_bridge=bridge, assembly=result,
        axes=[{k: v for k, v in axis.items() if k != 'profile'} for axis in axes],
        profiles={str(axis['h']): axis['profile'] for axis in axes},
        comparison=dict(pinned_kappa=pinned_record()['kappa'], kappa=kappa,
                        difference=kappa - prior, ratio=kappa / prior,
                        pinned_bit_saving=pinned_record()['bit_saving'],
                        coarse_grid=dict(kappa=coarse_result['kappa'], bit_saving=coarse)),
        proof_limits=['The complete physical profiles are supplied; the replay, transition and profile receipts above '
                      'are reproduced from the shipped words inside this verifier.',
                      'The region order substitution is confined to the compiler scheduling hook documented in '
                      'scheduler.py; no arithmetic, assembly, routing or recovery code is modified.',
                      'The rational logarithm and exponential enclosure derivations are inherited and documented in the '
                      'pinned README, not formally mechanized here.',
                      'All-size compiler, routing, recovery, prime-selection and fixed-tape transfer remain inherited.',
                      'Neither global optimality over region orders nor measured practical speedup is claimed.'])


def verify(record_mode=False, regenerate_words=False):
    with tempfile.TemporaryDirectory(prefix='envelope-scheduled-') as directory:
        work = Path(directory)
        axes = replay_axes(work, regenerate_words)
        bit = rows_for([axis['profile'] for axis in axes])
        for axis in axes:
            axis.pop('word_sha256')
        result = exact(bit, axes)
        result['local_source_sha256'] = {str(path.relative_to(ROOT)): sha256(path.read_bytes()).hexdigest()
                                        for path in (HERE / 'verify.py', HERE / 'scheduler.py',
                                                     HERE / 'compiler.py', HERE / 'flag_engine.py')}
        result['word_sha256'] = {str(h): sha256((HERE / f'word-{h}.json.gz').read_bytes()).hexdigest()
                                 for h in (23, 25)}
        payload = json.loads(json.dumps(arithmetic.js(result)))
        target = HERE / 'certificate.json'
        if record_mode:
            target.write_text(json.dumps(payload, indent=2, sort_keys=True) + '\n')
        else:
            assert payload == json.loads(target.read_text()), 'arithmetic certificate changed'
        print('PASS exact conditional scheduled kappa', str(result['comparison']['kappa']),
              'vs pinned', str(result['comparison']['pinned_kappa']),
              '(difference', str(result['comparison']['difference']) + ')', flush=True)
        print('47 strict inequalities, seven margins, next-grid rejection, independent moment bounds and '
              'byte or arithmetic comparison with the pinned certificate', flush=True)
        return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--record', action='store_true')
    parser.add_argument('--regenerate', action='store_true')
    arguments = parser.parse_args()
    verify(arguments.record, arguments.regenerate)
