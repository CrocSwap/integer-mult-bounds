"""Exact conditional assembly of the balanced coarse-sum composition.

Uses the unchanged fixed-I+J profiles and balanced assembly interfaces from
PR48. All auxiliary counts come from complete serialized new physical words.
The fixed rational witness is independent of discovery or floating arithmetic.
Four-edge coarse sums use two two-edge column sums and then their sum.
The inherited interval graph, frame compiler and rank priority are retained.
"""
import sys
sys.dont_write_bytecode = True
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
PRODUCER = ROOT / 'references/frame-compiler/balanced-coarse'
AB = Q(513710137, 10**13)
KAPPA = Q(1284209371, 25000000000000)
EXCLUDED_ABOVE = Q(25685507, 500000000000)
PR63_REPORTED_KAPPA = Q(5102757, 10**11)
PR64_REPORTED_KAPPA = Q(20411033624901463, 400000000000000000000)

spec = importlib.util.spec_from_file_location('balanced_coarse_balanced_assembly', OLD / 'balanced_assembly.py')
balanced = importlib.util.module_from_spec(spec)
spec.loader.exec_module(balanced)


def check_sources():
    manifests = []
    pending = [INHERITED, PRODUCER]
    seen = set()
    while pending:
        directory = pending.pop(0).resolve()
        if directory in seen:
            continue
        seen.add(directory)
        path = directory / 'SOURCE.json'
        document = json.loads(path.read_text())
        for name, digest in document['files'].items():
            assert sha256((directory / name).read_bytes()).hexdigest() == digest, name
        if 'shared_dependency_manifest' in document:
            dependency = directory / document['shared_dependency_manifest']
            assert sha256(dependency.read_bytes()).hexdigest() == document['shared_dependency_manifest_sha256']
            pending.append(dependency.resolve().parent)
        manifests.append(document)
    return manifests


def profile():
    a, b = 23, 25
    m, N = a*b, comb(a, 3)*comb(b, 3)
    profiles = [json.loads((OUT / f'balanced-coarse-profiles-{h}.json').read_text()) for h in (a, b)]
    words = json.loads((OUT / 'balanced-coarse-compiler.json').read_text())
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
        receipt = json.loads((OUT / f'balanced-coarse-transitions-{h}.json').read_text())
        for key in ('h', 'v', 'R'):
            assert f[key] == receipt[key]
        assert f['R'] == replay['roles'] == {23: 27698, 25: 36300}[h]
        assert recorded['compiled']['roles'] == f['R']
        assert recorded['compiled']['complete_dirty_basis_both_orientations']
        assert recorded['compiled']['all_physical_frame_inclusions']
        assert f['v'] == comb(h, 3) and f['loss'] == h*(h-1)
        assert f['crt_disagreements'] == 0 and f['field_prime'] == 2**61-1
        assert sum(t*n for t, n in enumerate(f['blocks'])) == h*f['R']+f['loss'] == f['rank_sum'] == receipt['rank_mass'] == replay['rank_mass']
        assert f['blocks'][h] == 0  # Copied centers already included.
        assert receipt['transition_events_equal_independent_xor_word_reconstruction']
        packed = (OUT / f'balanced-coarse-word-{h}.json.gz').read_bytes()
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
    assert (W, mass, m*W-mass) == (136139300, 78278250600, 1846900)
    return dict(m=m, N=N, W=W, L=L, total_rank=mass, deficit=m*W-mass,
                maxchild=max(rows), child_multiplicities=dict(sorted(rows.items())),
                parts=parts, axes=profiles, words=receipts)


def compose():
    assert all(type(x) is Q for x in (AB, KAPPA, EXCLUDED_ABOVE)), 'Final exact witness not pinned'
    sources = check_sources()
    compiler_record = json.loads((OUT / 'balanced-coarse-compiler.json').read_text())
    assert compiler_record['source'] == sources[1]
    predecessor = json.loads((OUT / 'ranked-interval-kappa.json').read_text())
    p = profile()
    exact = arithmetic.moment(p['m'], p['W'], p['child_multiplicities'], AB)
    excluded = arithmetic.moment(p['m'], p['W'], p['child_multiplicities'], EXCLUDED_ABOVE)
    assert exact['strict_gap'] > 0 and excluded['lower'] > 1
    previous_bit = predecessor['bit']
    previous_moment = arithmetic.moment(
        previous_bit['m'], previous_bit['W'],
        {int(t): n for t, n in previous_bit['child_multiplicities'].items()}, AB)
    assert previous_moment['lower'] > 1
    prior = json.loads((OLD / 'certificate.json').read_text())
    bridge = prior['finite_bridge']
    bridge['bit']['W'] = p['W']
    assert p['W'].bit_length() == bridge['bit']['wire_bits']
    assembled = balanced.assembly(bridge, AB, KAPPA, a_complex=Q(717, 10**7))
    assert len(assembled['constraints']) == 47 and len(assembled['margins']) == 7
    local_sources = [HERE / name for name in (
        'balanced_coarse_compiler.py', 'balanced_coarse_compose.py', 'verify_balanced_coarse.py',
        'binary_frame_compiler.py', 'binary_frame_math.py', 'binary_frame_replay.py',
        'binary_frame_profile_prepare.py', 'binary_frame_profiles.cpp')]
    result = dict(
        status='Conditional exact fixed-basis moment and balanced assembly; inherited transfer hypotheses remain assumed',
        kappa=KAPPA, bit_saving=AB, bit_saving_excluded_above=EXCLUDED_ABOVE,
        bit=dict(p, moment=exact, excluded_above_lower=excluded['lower']),
        controls=dict(ranked_interval_at_new_bit_saving=dict(
            moment=previous_moment,
            strict_exclusion_gap=previous_moment['lower']-1,
            scope='The complete hash-pinned predecessor child network fails the exact lower moment test at the new bit saving.')),
        assembly=assembled, eventual_bounds=balanced.cutoffs(bridge, assembled), finite_bridge=bridge,
        comparison=dict(pr48_kappa=Q(prior['kappa']),
                        ranked_interval_kappa=Q(predecessor['kappa']),
                        ratio_ranked_interval=KAPPA/Q(predecessor['kappa']),
                        pr63_reported_kappa=PR63_REPORTED_KAPPA,
                        ratio_pr63_reported=KAPPA/PR63_REPORTED_KAPPA,
                        pr63_comparison_scope='Reported PR63 value for the interval graph, joint frame compiler and descending-rank priority; the complete PR63 source witness was not independently replayed here. The separately pinned ranked-interval certificate independently reproduces this composition with finer rounding.',
                        pr64_reported_kappa=PR64_REPORTED_KAPPA,
                        ratio_pr64_reported=KAPPA/PR64_REPORTED_KAPPA,
                        pr64_comparison_scope='Reported PR64 arithmetic refinement for the same physical words as PR63; its complete source witness was not independently replayed here.',
                        next_dyadic_reached=KAPPA > Q(1, 2**14)),
        exactness=[arithmetic.exactness(h) for h in (23, 25)], sources=sources,
        local_source_sha256={str(p.relative_to(ROOT)): sha256(p.read_bytes()).hexdigest() for p in local_sources},
        dependencies=dict(
            data_profile='Unchanged inherited all-pairs data profile: 9 singletons +21+17+481; ten exact rational recoveries',
            producer='Balanced column-pair factorization of each four-edge coarse sum, prepared with OpenAI Codex assistance. Based on PR62 cyclic interval graph (Avi Eisenberg / ikeboy with Anthropic Claude assistance), PR57 joint frame compiler (eumemic with OpenAI Codex assistance), and PR60 descending-rank reclamation priority (Chafik Boukhalfa with OpenAI Codex assistance); complete serialized physical words',
            geometry='Unchanged fixed-I+J original-envelope projector and CRT formulas',
            proof_scope='Ordered affine residual compiler, fixed-tape recursion, finite scalar overhead, balanced transfer, analytic/routing/recovery interfaces remain inherited.'))
    (OUT / 'balanced-coarse-kappa.json').write_text(json.dumps(arithmetic.js(result), indent=2, sort_keys=True)+'\n')
    print('PASS conditional kappa='+str(KAPPA)+'; bit saving='+str(AB), flush=True)
    return result


if __name__ == '__main__':
    compose()
