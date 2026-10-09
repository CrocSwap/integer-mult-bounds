"""Exact conditional assembly of the rank-priority interval composition.

Uses the unchanged fixed-I+J profiles and balanced assembly interfaces from
PR48. All auxiliary counts come from complete serialized new physical words.
The fixed rational witness is independent of discovery or floating arithmetic.
This independently reproduces the composition also submitted as PR63; the
slightly larger rational witness is finer rounding, not a new mechanism.
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
PRODUCER = ROOT / 'references/frame-compiler/pr62'
AB = Q(255150939, 5000000000000)
KAPPA = Q(318922399, 6250000000000)
EXCLUDED_ABOVE = Q(510301881, 10**13)
PR61_REPORTED_KAPPA = Q(25508460085039, 5*10**17)
PR63_REPORTED_KAPPA = Q(5102757, 10**11)

spec = importlib.util.spec_from_file_location('ranked_interval_balanced_assembly', OLD / 'balanced_assembly.py')
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
    profiles = [json.loads((OUT / f'ranked-interval-profiles-{h}.json').read_text()) for h in (a, b)]
    words = json.loads((OUT / 'ranked-interval-compiler.json').read_text())
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
        receipt = json.loads((OUT / f'ranked-interval-transitions-{h}.json').read_text())
        for key in ('h', 'v', 'R'):
            assert f[key] == receipt[key]
        assert f['R'] == replay['roles'] == {23: 27918, 25: 36586}[h]
        assert recorded['compiled']['roles'] == f['R']
        assert recorded['compiled']['complete_dirty_basis_both_orientations']
        assert recorded['compiled']['all_physical_frame_inclusions']
        assert f['v'] == comb(h, 3) and f['loss'] == h*(h-1)
        assert f['crt_disagreements'] == 0 and f['field_prime'] == 2**61-1
        assert sum(t*n for t, n in enumerate(f['blocks'])) == h*f['R']+f['loss'] == f['rank_sum'] == receipt['rank_mass'] == replay['rank_mass']
        assert f['blocks'][h] == 0  # Copied centers already included.
        assert receipt['transition_events_equal_independent_xor_word_reconstruction']
        packed = (OUT / f'ranked-interval-word-{h}.json.gz').read_bytes()
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
    assert (W, mass, m*W-mass) == (137151806, 78860441550, 1846900)
    return dict(m=m, N=N, W=W, L=L, total_rank=mass, deficit=m*W-mass,
                maxchild=max(rows), child_multiplicities=dict(sorted(rows.items())),
                parts=parts, axes=profiles, words=receipts)


def compose():
    assert all(type(x) is Q for x in (AB, KAPPA, EXCLUDED_ABOVE)), 'Final exact witness not pinned'
    sources = check_sources()
    compiler_record = json.loads((OUT / 'ranked-interval-compiler.json').read_text())
    assert compiler_record['source'] == sources[1]
    pr62 = json.loads((PRODUCER / 'comparison-pr62.json').read_text())
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
        'ranked_interval_compiler.py', 'ranked_interval_compose.py', 'verify_ranked_interval.py',
        'binary_frame_compiler.py', 'binary_frame_math.py', 'binary_frame_replay.py',
        'binary_frame_profile_prepare.py', 'binary_frame_profiles.cpp')]
    result = dict(
        status='Conditional exact fixed-basis moment and balanced assembly; inherited transfer hypotheses remain assumed',
        kappa=KAPPA, bit_saving=AB, bit_saving_excluded_above=EXCLUDED_ABOVE,
        bit=dict(p, moment=exact, excluded_above_lower=excluded['lower']),
        assembly=assembled, eventual_bounds=balanced.cutoffs(bridge, assembled), finite_bridge=bridge,
        comparison=dict(pr48_kappa=Q(prior['kappa']),
                        pr62_stacked_kappa=Q(pr62['kappa']),
                        ratio_pr62_stacked=KAPPA/Q(pr62['kappa']),
                        pr61_reported_kappa=PR61_REPORTED_KAPPA,
                        ratio_pr61_reported=KAPPA/PR61_REPORTED_KAPPA,
                        pr61_comparison_scope='Reported PR61 value; its complete source witness was not independently replayed here',
                        pr63_reported_kappa=PR63_REPORTED_KAPPA,
                        ratio_pr63_reported=KAPPA/PR63_REPORTED_KAPPA,
                        pr63_comparison_scope='Contemporaneous PR63 by Dominik Scholz reports the same graph/compiler/priority composition. This local witness uses finer exact rounding and does not claim a new mechanism; PR63 source was not independently replayed here.',
                        next_dyadic_reached=KAPPA > Q(1, 2**14)),
        exactness=[arithmetic.exactness(h) for h in (23, 25)], sources=sources,
        local_source_sha256={str(p.relative_to(ROOT)): sha256(p.read_bytes()).hexdigest() for p in local_sources},
        dependencies=dict(
            data_profile='Unchanged inherited all-pairs data profile: 9 singletons +21+17+481; ten exact rational recoveries',
            producer='PR62 cyclic interval graph (Avi Eisenberg / ikeboy with Anthropic Claude assistance), PR57 joint frame compiler (eumemic with OpenAI Codex assistance), and PR60 descending-rank reclamation priority (Chafik Boukhalfa with OpenAI Codex assistance); complete serialized physical words',
            geometry='Unchanged fixed-I+J original-envelope projector and CRT formulas',
            proof_scope='Ordered affine residual compiler, fixed-tape recursion, finite scalar overhead, balanced transfer, analytic/routing/recovery interfaces remain inherited.'))
    (OUT / 'ranked-interval-kappa.json').write_text(json.dumps(arithmetic.js(result), indent=2, sort_keys=True)+'\n')
    print('PASS conditional kappa='+str(KAPPA)+'; bit saving='+str(AB), flush=True)
    return result


if __name__ == '__main__':
    compose()
