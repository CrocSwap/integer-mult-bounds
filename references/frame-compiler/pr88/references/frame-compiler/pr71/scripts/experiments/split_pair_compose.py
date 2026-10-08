"""Complete paid split/pair profile and PR65's exact refined balanced assembly.

The unchanged full physical words determine every auxiliary multiplicity.
Only fixed-basis finite claims are certified; all-size transfer remains inherited.
Prepared by Chafik Boukhalfa with OpenAI Codex assistance. Apache-2.0.
"""
import sys
if sys.flags.optimize:
    raise ValueError('Assertions must remain enabled')
sys.dont_write_bytecode = True

from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from math import comb
from pathlib import Path
import gzip
import json

import binary_frame_math as arithmetic
from split_pair_arithmetic import refine, audit
from split_pair_graph import checked_manifest
from split_pair_compiler import source_record
from pin_split_pair_sources import required_paths

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUT = ROOT / 'certificates'
INHERITED = ROOT / 'references/frame-compiler/pr48'
OLD = INHERITED / 'research/copied-fixed'
BASELINE = ROOT / 'references/frame-compiler/pr65'
BASELINE_CASE = BASELINE / 'research/reordered-rank-pair'
PROFILE_BASELINE = ROOT / 'references/frame-compiler/pr67/research/slot-cost-rank-pair'


def check_sources():
    sources = source_record()
    operation = ROOT / 'references/frame-compiler/pr59-split-operation'
    checked_manifest(operation)
    local = json.loads((ROOT/'research/split-pair/SOURCE.json').read_text())
    assert required_paths() <= set(local['files']), 'Incomplete source/finite-input closure'
    for name, digest in local['files'].items():
        assert sha256((ROOT/name).read_bytes()).hexdigest() == digest, name
    engine = ROOT / 'scripts/experiments/joint_dual_reclaim_compiler.py'
    assert engine.read_bytes() == (BASELINE/'scripts/experiments/rank_pair_compiler.py').read_bytes()
    provenance = json.loads((ROOT/'research/split-pair/engine-provenance.json').read_text())
    assert sha256((HERE/'split_pair_engine.py').read_bytes()).hexdigest() == provenance['portable_engine_sha256']
    for name in ('binary_frame_math.py', 'binary_frame_replay.py',
                 'binary_frame_profile_prepare.py', 'binary_frame_profiles.cpp'):
        assert (HERE/name).read_bytes() == (BASELINE/'scripts/experiments'/name).read_bytes()
    return dict(sources, split_operation=checked_manifest(operation))


def profile():
    parameters = json.loads((ROOT/'research/split-pair/parameters.json').read_text())
    a, b = 23, 25
    m, N = a*b, comb(a, 3)*comb(b, 3)
    profiles = [json.loads((OUT / f'split-pair-profiles-{h}.json').read_text()) for h in (a, b)]
    words = json.loads((OUT / 'split-pair-compiler.json').read_text())
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
        receipt = json.loads((OUT / f'split-pair-transitions-{h}.json').read_text())
        for key in ('h', 'v', 'R'):
            assert f[key] == receipt[key]
        assert f['R'] == replay['roles'] == recorded['compiled']['roles'] == parameters['roles'][str(h)]
        assert f['v'] == comb(h, 3) and f['loss'] == h*(h-1)
        assert f['crt_disagreements'] == 0 and f['field_prime'] == 2**61-1
        assert sum(t*n for t, n in enumerate(f['blocks'])) == h*f['R']+f['loss'] == f['rank_sum'] == receipt['rank_mass'] == replay['rank_mass']
        assert f['blocks'][0] == 0 and f['blocks'][h] == 0  # Positive children; copied centers already included.
        assert receipt['transition_events_equal_independent_xor_word_reconstruction']
        packed = (OUT / f'split-pair-word-{h}.json.gz').read_bytes()
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
    assert (W, mass, m*W-mass) == (parameters['W'], parameters['total_rank'], 1846900)
    return dict(m=m, N=N, W=W, L=L, total_rank=mass, deficit=m*W-mass,
                maxchild=max(rows), child_multiplicities=dict(sorted(rows.items())),
                parts=parts, axes=profiles, words=receipts)


def compose():
    sources = check_sources()
    parameters = json.loads((ROOT/'research/split-pair/parameters.json').read_text())
    bit_saving, kappa = Q(parameters['bit_saving']), Q(parameters['kappa'])
    denominator = parameters['grid_denominator']
    assert type(denominator) is int and denominator == 10**18
    grid = Q(1, denominator)
    assert json.loads((OUT/'split-pair-compiler.json').read_text())['source'] == source_record()
    p = profile()
    exact = refine.exact_moment(p['m'], p['W'], p['child_multiplicities'], bit_saving)
    excluded = refine.exact_moment(p['m'], p['W'], p['child_multiplicities'], bit_saving+grid)
    assert exact['upper'] < 1 < excluded['lower']
    independent = audit.independent_moment(arithmetic.js(p), bit_saving, arithmetic.js(exact['terms']))
    independent_rejected = audit.independent_moment(arithmetic.js(p), bit_saving+grid, arithmetic.js(exact['terms']))
    assert independent[1] < 1 < independent_rejected[0]
    prior65 = json.loads((PROFILE_BASELINE/'arithmetic/certificate.json').read_text())
    oldprofile = json.loads((PROFILE_BASELINE/'paired-candidate.json').read_text())
    oldbit = oldprofile['bit']
    previous_kappa = Q(prior65['preferred']['kappa'])
    previous_rows = {int(t): n for t,n in oldbit['child_multiplicities'].items()}
    prior65_lower = refine.exact_moment(oldbit['m'], oldbit['W'], previous_rows, bit_saving)['lower']
    assert prior65_lower > 1 and kappa > previous_kappa
    bridge = json.loads((OLD/'certificate.json').read_text())['finite_bridge']
    bridge['bit']['W'] = p['W']
    assert p['W'].bit_length() == bridge['bit']['wire_bits']
    assembled = refine.assemble(bridge, bit_saving, Q(1, 10**12), denominator)
    assert assembled['kappa'] == kappa
    assert all(value > 0 for value in assembled['assembly']['constraints'].values())
    assert all(value > kappa for value in assembled['assembly']['margins'].values())
    coarse_denominator = 10**11
    coarse_bit = Q(refine.floor_scaled(bit_saving, coarse_denominator), coarse_denominator)
    coarse = refine.assemble(bridge, coarse_bit, Q(1, 10**12), coarse_denominator)
    assert arithmetic.moment(p['m'], p['W'], p['child_multiplicities'], coarse_bit)['upper'] < 1
    result = dict(
        status='Finite conditional physical witness and exact balanced assembly; inherited transfer hypotheses remain assumed',
        source_manifest_sha256=sha256((ROOT/'research/split-pair/SOURCE.json').read_bytes()).hexdigest(),
        kappa=kappa, bit_saving=bit_saving, bit_saving_excluded_above=bit_saving+grid,
        grid_denominator=denominator, bit=dict(p, moment=exact, excluded_moment=excluded),
        independent_enclosures=dict(accepted_lower=independent[0], accepted_upper=independent[1],
                                    rejected_lower=independent_rejected[0], rejected_upper=independent_rejected[1]),
        assembly=assembled['assembly'], eventual_bounds=assembled['eventual_bounds'], finite_bridge=bridge,
        next_kappa=assembled['next_kappa'], next_kappa_rejection=assembled['next_kappa_rejection'],
        coarse_grid_control=dict(bit_saving=coarse_bit, **coarse),
        comparison=dict(pr67_commit='b3745601e947a94316bf25c2c6263d93c06e3364',
                        pr67_kappa=previous_kappa, ratio_pr67=kappa/previous_kappa,
                        absolute_gain_pr67=kappa-previous_kappa,
                        pr67_complete_profile_exclusion_lower=prior65_lower,
                        full_pr67_child_list_excluded_at_new_bit_saving=True),
        exactness=[arithmetic.exactness(h) for h in (23,25)], sources=sources,
        dependencies=dict(
            data_profile='Unchanged inherited all-pairs data profile: 9 singletons +21+17+481; ten exact rational recoveries',
            producer='PR62/63 interval pair assembly, selected split-pair partition and point permutation, PR65 schedules, PR67 profile-cost reclamation, PR68 pending live controls and selected next-use scoring; complete literal words',
            geometry='Unchanged fixed-I+J original-envelope projector and CRT formulas',
            proof_scope='Ordered affine residual compiler, all-size recursion, finite scalar overhead, routing, prime selection, exact recovery and fixed-tape/analytic transfer remain inherited. Arithmetic cutoffs are not full operational thresholds.'))
    (OUT/'split-pair-kappa.json').write_text(json.dumps(arithmetic.js(result), indent=2, sort_keys=True)+'\n')
    print('PASS finite conditional kappa='+str(kappa)+'; bit saving='+str(bit_saving), flush=True)
    return result


if __name__ == '__main__':
    compose()
