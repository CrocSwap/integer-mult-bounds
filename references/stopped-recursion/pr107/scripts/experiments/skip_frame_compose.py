"""Exact conditional assembly of the PR53 skip producer and frame compiler.

Uses the unchanged fixed-I+J profiles and balanced assembly interfaces from
PR48. All auxiliary counts come from complete serialized new physical words.
The fixed rational witness is independent of discovery or floating arithmetic.
"""
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
PR53 = ROOT / 'references/frame-compiler/pr53'
AB = Q(116741511, 2500000000000)
KAPPA = Q(4669442391, 10**14)
EXCLUDED_ABOVE = Q(466966047, 10**13)
PR53_KAPPA = Q(4498144, 10**11)
PR54_CLAIMED_KAPPA = Q(4529040672, 10**14)

spec = importlib.util.spec_from_file_location('skip_frame_balanced_assembly', OLD / 'balanced_assembly.py')
balanced = importlib.util.module_from_spec(spec)
spec.loader.exec_module(balanced)


def check_sources():
    manifests = []
    for directory in (INHERITED, PR53):
        path = directory / 'SOURCE.json'
        document = json.loads(path.read_text())
        for name, digest in document['files'].items():
            assert sha256((directory / name).read_bytes()).hexdigest() == digest, name
        if 'shared_dependency_manifest' in document:
            dependency = directory / document['shared_dependency_manifest']
            assert sha256(dependency.read_bytes()).hexdigest() == document['shared_dependency_manifest_sha256']
        manifests.append(document)
    return manifests


def profile():
    a, b = 23, 25
    m, N = a*b, comb(a, 3)*comb(b, 3)
    profiles = [json.loads((OUT / f'skip-frame-profiles-{h}.json').read_text()) for h in (a, b)]
    words = json.loads((OUT / 'skip-frame-compiler.json').read_text())
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
        receipt = json.loads((OUT / f'skip-frame-transitions-{h}.json').read_text())
        for key in ('h', 'v', 'R'):
            assert f[key] == receipt[key]
        assert f['R'] == replay['roles']
        assert f['v'] == comb(h, 3) and f['loss'] == h*(h-1)
        assert f['crt_disagreements'] == 0 and f['field_prime'] == 2**61-1
        assert sum(t*n for t, n in enumerate(f['blocks'])) == h*f['R']+f['loss'] == f['rank_sum'] == receipt['rank_mass'] == replay['rank_mass']
        assert f['blocks'][h] == 0  # Copied centers already included.
        assert receipt['transition_events_equal_independent_xor_word_reconstruction']
        packed = (OUT / f'skip-frame-word-{h}.json.gz').read_bytes()
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
    assert (W, mass, m*W-mass) == (153481944, 88250270900, 1846900)
    return dict(m=m, N=N, W=W, L=L, total_rank=mass, deficit=m*W-mass,
                maxchild=max(rows), child_multiplicities=dict(sorted(rows.items())),
                parts=parts, axes=profiles, words=receipts)


def compose():
    sources = check_sources()
    compiler_record = json.loads((OUT / 'skip-frame-compiler.json').read_text())
    assert compiler_record['source'] == sources[1]
    p = profile()
    exact = arithmetic.moment(p['m'], p['W'], p['child_multiplicities'], AB)
    excluded = arithmetic.moment(p['m'], p['W'], p['child_multiplicities'], EXCLUDED_ABOVE)
    assert exact['strict_gap'] > 0 and excluded['lower'] > 1
    prior = json.loads((OLD / 'certificate.json').read_text())
    bridge = prior['finite_bridge']
    bridge['bit']['W'] = p['W']
    assert p['W'].bit_length() == bridge['bit']['wire_bits']
    assembled = balanced.assembly(bridge, AB, KAPPA, a_complex=Q(717, 10**7))
    assert len(assembled['constraints']) == 47 and len(assembled['margins']) == 7
    local_sources = [HERE / name for name in (
        'skip_frame_compiler.py', 'skip_frame_compose.py', 'verify_skip_frame.py',
        'binary_frame_compiler.py', 'binary_frame_math.py', 'binary_frame_replay.py',
        'binary_frame_profile_prepare.py', 'binary_frame_profiles.cpp')]
    result = dict(
        status='Conditional exact fixed-basis moment and balanced assembly; inherited transfer hypotheses remain assumed',
        kappa=KAPPA, bit_saving=AB, bit_saving_excluded_above=EXCLUDED_ABOVE,
        bit=dict(p, moment=exact, excluded_above_lower=excluded['lower']),
        assembly=assembled, eventual_bounds=balanced.cutoffs(bridge, assembled), finite_bridge=bridge,
        comparison=dict(pr48_kappa=Q(prior['kappa']), pr53_kappa=PR53_KAPPA,
                        ratio_pr53=KAPPA/PR53_KAPPA, pr54_claimed_kappa=PR54_CLAIMED_KAPPA,
                        ratio_pr54=KAPPA/PR54_CLAIMED_KAPPA,
                        next_dyadic_reached=KAPPA > Q(1, 2**14)),
        exactness=[arithmetic.exactness(h) for h in (23, 25)], sources=sources,
        local_source_sha256={str(p.relative_to(ROOT)): sha256(p.read_bytes()).hexdigest() for p in local_sources},
        dependencies=dict(
            data_profile='Unchanged inherited all-pairs data profile: 9 singletons +21+17+481; ten exact rational recoveries',
            producer='PR53 skip graph with exact original-envelope block compilation; complete serialized physical words',
            geometry='Unchanged fixed-I+J original-envelope projector and CRT formulas',
            proof_scope='Ordered affine residual compiler, fixed-tape recursion, finite scalar overhead, balanced transfer, analytic/routing/recovery interfaces remain inherited.'))
    (OUT / 'skip-frame-kappa.json').write_text(json.dumps(arithmetic.js(result), indent=2, sort_keys=True)+'\n')
    print('PASS conditional kappa='+str(KAPPA)+'; bit saving='+str(AB), flush=True)
    return result


if __name__ == '__main__':
    compose()
