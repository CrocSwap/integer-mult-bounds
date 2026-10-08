"""Exact conditional assembly of split-pair recursion and dual-suffix strips.

Uses the unchanged fixed-I+J profiles and balanced assembly interfaces from
PR48. All auxiliary counts come from complete serialized new physical words.
The fixed rational witness is independent of discovery or floating arithmetic.
"""
import sys
if sys.flags.optimize:
    raise ValueError('Assertions must remain enabled')

from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from math import comb
from pathlib import Path
import gzip
import importlib.util
import json

import binary_frame_math as arithmetic

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUT = ROOT / 'certificates'
INHERITED = ROOT / 'references/frame-compiler/pr48'
OLD = INHERITED / 'research/copied-fixed'
PRODUCER = ROOT / 'references/frame-compiler/pr59'
SUFFIX = ROOT / 'references/frame-compiler/pr55'
BASELINE = ROOT / 'references/frame-compiler/pr60'
AB = Q(2415663683, 50000000000000)
KAPPA = Q(120777349, 2500000000000)
GRID = Q(1, 10**14)
EXCLUDED_ABOVE = AB + GRID
PR60_KAPPA = Q(4764513337, 10**14)

spec = importlib.util.spec_from_file_location('split_dual_balanced_assembly', OLD / 'balanced_assembly.py')
balanced = importlib.util.module_from_spec(spec)
spec.loader.exec_module(balanced)


def check_sources():
    manifests = []
    for directory in (INHERITED, PRODUCER, SUFFIX, BASELINE):
        path = directory / 'SOURCE.json'
        document = json.loads(path.read_text())
        for name, digest in document['files'].items():
            assert sha256((directory / name).read_bytes()).hexdigest() == digest, name
        if 'shared_dependency_manifest' in document:
            dependency = directory / document['shared_dependency_manifest']
            assert sha256(dependency.read_bytes()).hexdigest() == document['shared_dependency_manifest_sha256']
        manifests.append(document)
    local = json.loads((ROOT/'research/split-dual/SOURCE.json').read_text())
    required = {'scripts/experiments/'+name for name in (
        'split_dual_graph.py', 'split_dual_compiler.py', 'split_dual_compose.py',
        'verify_split_dual.py', 'pin_split_dual_sources.py',
        'joint_dual_reclaim_compiler.py', 'binary_frame_math.py',
        'binary_frame_replay.py', 'binary_frame_profile_prepare.py', 'binary_frame_profiles.cpp')}
    required.update(('research/split-dual/PROOF.md', 'research/split-dual/README.md',
                     'tests/test_split_dual.py', 'Makefile', 'README.md', 'NOTICE',
                     'certificates/split-dual-compiler.json'))
    for h in (23,25):
        required.add(f'research/split-dual/config-{h}.json')
        required.update(f'certificates/split-dual-{kind}-{h}.{extension}'
                        for kind,extension in (('word','json.gz'),('profiles','json'),('transitions','json')))
    for prior in (48,55,59,60):
        relative = Path(f'references/frame-compiler/pr{prior}')
        required.add(str(relative/'SOURCE.json'))
        required.update(str(relative/name) for name in json.loads((ROOT/relative/'SOURCE.json').read_text())['files'])
    assert required <= set(local['files']), 'Incomplete local source/finite-input closure'
    for name, digest in local['files'].items():
        assert sha256((ROOT/name).read_bytes()).hexdigest() == digest, name
    original = json.loads((BASELINE/'research/joint-dual/SOURCE.json').read_text())
    engine = 'scripts/experiments/joint_dual_reclaim_compiler.py'
    assert sha256((ROOT/engine).read_bytes()).hexdigest() == original['files'][engine], 'PR60 compiler changed'
    return manifests


def profile():
    a, b = 23, 25
    m, N = a*b, comb(a, 3)*comb(b, 3)
    profiles = [json.loads((OUT / f'split-dual-profiles-{h}.json').read_text()) for h in (a, b)]
    words = json.loads((OUT / 'split-dual-compiler.json').read_text())
    W = 2*N + sum(N//f['v']*f['R'] for f in profiles)
    L = sum(N//f['v']*f['loss'] for f in profiles)
    parts = {'data': Counter({1: 18*N, 21: 2*N, 17: 2*N, 481: 2*N}),
             'paid_endpoint_copy': Counter({1: N})}
    receipts = []
    for f in profiles:
        h = f['h']
        rep, bank = N//f['v'], N//f['v']*f['R']
        recorded = words['axes'][str(h)]
        replay = recorded['replay']
        receipt = json.loads((OUT / f'split-dual-transitions-{h}.json').read_text())
        for key in ('h', 'v', 'R'):
            assert f[key] == receipt[key]
        assert f['R'] == replay['roles'] == recorded['compiled']['roles'] == {23: 30118, 25: 39663}[h]
        assert f['v'] == comb(h, 3) and f['loss'] == h*(h-1)
        assert f['crt_disagreements'] == 0 and f['field_prime'] == 2**61-1
        assert sum(t*n for t, n in enumerate(f['blocks'])) == h*f['R']+f['loss'] == f['rank_sum'] == receipt['rank_mass'] == replay['rank_mass']
        assert f['blocks'][0] == 0 and f['blocks'][h] == 0  # Positive children; copied centers already included.
        assert receipt['transition_events_equal_independent_xor_word_reconstruction']
        packed = (OUT / f'split-dual-word-{h}.json.gz').read_bytes()
        assert sha256(packed).hexdigest() == recorded['gzip_sha256']
        assert sha256(gzip.decompress(packed)).hexdigest() == recorded['word_sha256'] == receipt['word_sha256']
        histogram = {str(k): v for k, v in replay['histogram'].items() if int(k)}
        side = replay['output_roles']-h
        histogram['2'] -= side
        histogram['1'] += 2*side
        assert histogram == receipt['rank_histogram_with_side_growth_split_into_singletons']
        arithmetic.exactness(h)
        parts[f'internal_{h}'] = Counter({t: n*rep for t, n in enumerate(f['blocks']) if t and n})
        parts[f'exterior_{h}'] = Counter({h: bank, m-2*h: bank})
        parts[f'data_growth_{h}'] = Counter({1: 2*N, h-2: 2*N})
        receipts.append(receipt)
    rows = sum(parts.values(), Counter())
    mass = sum(t*n for t, n in rows.items())
    assert mass == m*W-N+L and max(rows) == 529 and all(0 < t < m for t in rows)
    assert (W, mass, m*W-mass) == (147661173, 84903327575, 1846900)
    return dict(m=m, N=N, W=W, L=L, total_rank=mass, deficit=m*W-mass,
                maxchild=max(rows), child_multiplicities=dict(sorted(rows.items())),
                parts=parts, axes=profiles, words=receipts)


def compose():
    import sys
    arithmetic.require(not sys.flags.optimize, 'Assertions must remain enabled')
    sources = check_sources()
    compiler_record = json.loads((OUT / 'split-dual-compiler.json').read_text())
    assert compiler_record['source'] == dict(split=sources[1], suffix=sources[2], ranked=sources[3])
    p = profile()
    exact = arithmetic.moment(p['m'], p['W'], p['child_multiplicities'], AB)
    excluded = arithmetic.moment(p['m'], p['W'], p['child_multiplicities'], EXCLUDED_ABOVE)
    assert exact['strict_gap'] > 0 and excluded['lower'] > 1
    previous60 = json.loads((BASELINE/'certificates/joint-dual-kappa.json').read_text())
    assert Q(previous60['kappa']) == PR60_KAPPA
    previous60_rows = {int(t): n for t,n in previous60['bit']['child_multiplicities'].items()}
    prior60_lower = arithmetic.moment(previous60['bit']['m'], previous60['bit']['W'], previous60_rows, AB)['lower']
    assert prior60_lower > 1 and KAPPA > PR60_KAPPA
    prior = json.loads((OLD / 'certificate.json').read_text())
    bridge = prior['finite_bridge']
    bridge['bit']['W'] = p['W']
    assert p['W'].bit_length() == bridge['bit']['wire_bits']
    assembled = balanced.assembly(bridge, AB, KAPPA, a_complex=Q(717, 10**7))
    assert len(assembled['constraints']) == 47 and len(assembled['margins']) == 7
    assert all(value > 0 for value in assembled['constraints'].values())
    assert all(value > KAPPA for value in assembled['margins'].values())
    try:
        balanced.assembly(bridge, AB, KAPPA+GRID, a_complex=Q(717, 10**7))
    except (AssertionError, ValueError):
        pass
    else:
        raise ValueError('Next kappa grid point unexpectedly accepted')
    local_sources = [HERE / name for name in (
        'split_dual_graph.py', 'split_dual_compiler.py', 'split_dual_compose.py',
        'verify_split_dual.py', 'pin_split_dual_sources.py', 'joint_dual_reclaim_compiler.py',
        'binary_frame_math.py', 'binary_frame_replay.py',
        'binary_frame_profile_prepare.py', 'binary_frame_profiles.cpp')]
    result = dict(
        status='Conditional exact fixed-basis moment and balanced assembly; inherited transfer hypotheses remain assumed',
        source_manifest_sha256=sha256((ROOT/'research/split-dual/SOURCE.json').read_bytes()).hexdigest(),
        kappa=KAPPA, bit_saving=AB, bit_saving_excluded_above=EXCLUDED_ABOVE,
        bit=dict(p, moment=exact, excluded_above_lower=excluded['lower']),
        assembly=assembled, eventual_bounds=balanced.cutoffs(bridge, assembled), finite_bridge=bridge,
        comparison=dict(pr60_kappa=PR60_KAPPA, ratio_pr60=KAPPA/PR60_KAPPA,
                        absolute_gain_pr60=KAPPA-PR60_KAPPA, pr60_exclusion_lower=prior60_lower,
                        pr60_commit='21a121960644b8c6fdf9c06fe39dea1944dd2231',
                        full_pr60_child_list_excluded_at_new_bit_saving=True,
                        next_kappa_grid_rejected=True, pr48_kappa=Q(prior['kappa']),
                        next_dyadic_reached=KAPPA > Q(1, 2**14)),
        exactness=[arithmetic.exactness(h) for h in (23, 25)], sources=sources,
        local_source_sha256={str(p.relative_to(ROOT)): sha256(p.read_bytes()).hexdigest() for p in local_sources},
        dependencies=dict(
            data_profile='Unchanged inherited all-pairs data profile: 9 singletons +21+17+481; ten exact rational recoveries',
            producer='PR59 split-pair groups with PR55 suffix-native layouts and unchanged PR60 ranked compiler; no paid clones or pinned permutation overrides; complete serialized physical words',
            geometry='Unchanged fixed-I+J original-envelope projector and CRT formulas',
            proof_scope='Ordered affine residual compiler, fixed-tape recursion, finite scalar overhead, balanced transfer, analytic/routing/recovery interfaces remain inherited.'))
    (OUT / 'split-dual-kappa.json').write_text(json.dumps(arithmetic.js(result), indent=2, sort_keys=True)+'\n')
    print('PASS conditional kappa='+str(KAPPA)+'; bit saving='+str(AB), flush=True)
    return result


if __name__ == '__main__':
    compose()
