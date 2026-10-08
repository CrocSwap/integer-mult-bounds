#!/usr/bin/env python3
"""Exact arithmetic witness for paid original-envelope clones on PR53 skip-prefix graphs.

Avi Eisenberg/Anthropic Claude PR53 supplies the skip-prefix base; RaD / hipotures
with OpenAI Codex assistance PR51 supplies paid whole-chain source partitions.
Chafik Boukhalfa/OpenAI Codex PR43/46/48 supplies the original-envelope finite
checkers, exact data recovery and arithmetic; Rohan Arun/Anthropic Claude PR44
supplies weighted-matching discovery. All retained notices and source pins apply.
Prepared with OpenAI Codex assistance. Apache-2.0; general transfer proofs remain
inherited dependencies.
"""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from math import comb
from pathlib import Path
import argparse
import importlib.util
import json
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PR43 = ROOT/'research/copied-fixed'
sys.path.insert(0, str(ROOT/'scripts'))
sys.path.insert(0, str(PR43))
sys.path.insert(0, str(HERE))
from clone_io import read, require, integer, check_sources, CERTIFICATE_INPUTS
from cloned_graph import graph

_spec = importlib.util.spec_from_file_location('skip_clones53_pr43_verify', PR43/'verify.py')
base = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(base)
_spec = importlib.util.spec_from_file_location('skip_clones53_balanced_assembly', PR43/'balanced_assembly.py')
balanced = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(balanced)
moment, js = base.moment, base.js
assembly, cutoffs = balanced.assembly, balanced.cutoffs
AC = base.AC
PR53_KAPPA = Q(4498144, 10**11)
PR48_KAPPA = Q(411862541, 10**13)


def rational_pair(value, name):
    require(type(value) is list and len(value) == 2, 'Expected rational pair: '+name)
    return Q(integer(value[0], name+' numerator', 1), integer(value[1], name+' denominator', 1))


def parameters():
    values = read(HERE/'parameters.json')
    require(set(values) == {'bit_saving', 'kappa', 'grid_denominator'}, 'Unexpected parameter keys')
    ab = rational_pair(values['bit_saving'], 'bit_saving')
    kappa = rational_pair(values['kappa'], 'kappa')
    grid = Q(1, integer(values['grid_denominator'], 'grid_denominator', 1))
    require(PR53_KAPPA < kappa < ab < 1, 'Savings do not improve PR53')
    require((ab/grid).denominator == (kappa/grid).denominator == 1, 'Savings must lie on declared grid')
    return ab, kappa, grid


def counts(row, names):
    for name in names:
        integer(row[name], name)


def histogram(value, length, name):
    require(type(value) is list and len(value) == length, 'Wrong histogram length: '+name)
    for item in value:
        integer(item, name)
    return value


def profile():
    a, b = 23, 25
    m, N = a*b, comb(a, 3)*comb(b, 3)
    rows = [read(HERE/f'original-{h}.json') for h in (a, b)]
    for h, row in zip((a, b), rows):
        counts(row, ('h', 'v', 'R', 'c', 'q', 'matched', 'loss', 'rank_sum', 'baseline_R', 'orientation_changes'))
        require(row['h'] == h and row['v'] == comb(h, 3), 'Wrong local dimension or source count')
        require(row['baseline_R'] == row['c']+row['q'], 'Wrong unmatched role count')
        require(row['R'] == row['baseline_R']-row['matched'], 'Wrong matched role count')
        require(row['loss'] == h*(h-1), 'Wrong retained center loss')
        hist = histogram(row['histogram'], h+1, 'rank histogram')
        require(sum(t*n for t, n in enumerate(hist)) == row['rank_sum'] == h*row['R']+2*row['loss'],
                'Original rank mass')
    W = 2*N+sum(N//row['v']*row['R'] for row in rows)
    L = sum(N//row['v']*row['loss'] for row in rows)
    data = base.data_corners()
    good, bad = data['good'], data['fallback']
    require(good+bad == N, 'Wrong data-pair denominator')
    parts = {'data': Counter({1: 2*(9*good+47*bad), 21: 2*good, 17: 2*good, 481: 2*N}),
             'paid_endpoint_copy': Counter({1: N})}
    for row in rows:
        h = row['h']
        f = read(HERE/f'profiles-{h}.json')
        counts(f, ('h', 'v', 'R', 'loss', 'rank_sum', 'crt_disagreements',
                   'field_prime', 'frames', 'distinct_matrices', 'crt_matrices'))
        for key in ('h', 'v', 'R', 'loss', 'rank_sum'):
            require(f[key] == row[key], 'Fixed/original mismatch: '+key)
        require(f['crt_disagreements'] == 0 and f['field_prime'] == 2**61-1, 'Invalid CRT profile')
        blocks = histogram(f['blocks'], h+1, 'fixed blocks')[:]
        require(blocks[0] == 0 and blocks[h] == h, 'Expected zero null blocks and h full center cleanups')
        require(sum(t*n for t, n in enumerate(blocks)) == f['rank_sum'], 'Fixed profile mass')
        blocks[h] -= h
        blocks[1] += h
        require(sum(t*n for t, n in enumerate(blocks)) == h*row['R']+row['loss'], 'Copied profile mass')
        scalar = read(HERE/f'scalar-{h}.json')
        counts(scalar, ('h', 'inputs', 'additions', 'merged_additions', 'partial_outputs', 'roles'))
        require(all(scalar[key] is True for key in ('all_additions_disjoint', 'all_partial_outputs_exact',
                                                  'every_node_has_common_point')), 'Scalar replay flags')
        require(scalar['h'] == h and scalar['inputs'] == row['v'] and scalar['additions'] == row['c'],
                'Scalar dimensions differ')
        timeline = read(HERE/f'timeline-{h}.json')
        counts(timeline, ('h', 'v', 'roles', 'retained_links', 'additions', 'center_rank',
                          'center_terminal_count', 'copied_rank_sum', 'designated_outputs',
                          'full_output_coefficients', 'native_zero_rank_bookkeeping',
                          'physical_frame_transitions', 'rational_frame_classes',
                          'reverse_complement_frame_incidences'))
        histogram(timeline['copied_histogram'], h+1, 'timeline histogram')
        require(timeline['copied_histogram'][1:] == [row['histogram'][t]+(h if t == 1 else -h if t == h else 0)
                                                    for t in range(1, h+1)], 'Timeline histogram differs')
        require(timeline['h'] == h and timeline['roles'] == row['R'] and timeline['retained_links'] == row['matched'],
                'Physical timeline differs')
        require(timeline['copied_rank_sum'] == h*row['R']+row['loss'], 'Physical copied mass')
        dirty = timeline['complete_dirty_basis']
        counts(dirty, ('auxiliary_basis_vectors', 'total_basis_vectors', 'elementary_word_length',
                       'inputs', 'targets'))
        require(dirty['all_dirty_restore'] is True and dirty['auxiliary_basis_vectors'] == row['R'] and
                dirty['total_basis_vectors'] == 2*row['v']+row['R'] and
                dirty['orientations'] == ['forward', 'reverse-complement'], 'Incomplete dirty-basis replay')
        rep, bank = N//row['v'], N//row['v']*row['R']
        parts[f'internal_{h}'] = Counter({t: n*rep for t, n in enumerate(blocks) if t and n})
        parts[f'exterior_{h}'] = Counter({h: bank, m-2*h: bank})
        parts[f'data_growth_{h}'] = Counter({1: 2*N, h-2: 2*N})
    hist = sum(parts.values(), Counter())
    total_rank = sum(t*n for t, n in hist.items())
    require(total_rank == W*m-N+L, 'Complete rank mass')
    require((m, N, L) == (575, 4073300, 2226400) and W < 160799739, 'Physical constants or PR53 width')
    require(max(hist) == 529 and all(type(t) is int and 0 < t < m and type(n) is int and n > 0
                                   for t, n in hist.items()), 'Improper children')
    return dict(m=m, N=N, W=W, L=L, total_rank=total_rank, deficit=W*m-total_rank,
                maxchild=max(hist), child_multiplicities=dict(sorted(hist.items())), parts=parts)


def excluded(path, ab):
    c = read(path)
    counts(c, ('m', 'W'))
    children = {}
    for key, multiplicity in c['child_multiplicities'].items():
        require(key.isdecimal() and str(int(key)) == key, 'Invalid child width key')
        width = int(key)
        require(0 < width < c['m'], 'Comparison child does not contract')
        children[width] = integer(multiplicity, 'comparison multiplicity', 1)
    rank_mass = sum(t*n for t, n in children.items())
    require(0 < rank_mass < c['m']*c['W'], 'Comparison rank deficit')
    # The pinned PR40 fixture predates the redundant total_rank metadata.
    if 'total_rank' in c:
        require(rank_mass == integer(c['total_rank'], 'comparison rank mass'), 'Comparison rank mass')
    lower = moment(c['m'], c['W'], children, ab)['lower']
    require(lower > 1, path.name+' network not excluded at new saving')
    return lower


def run():
    require(not sys.flags.optimize, 'Assertions must remain enabled')
    check_sources(CERTIFICATE_INPUTS)
    base.check_sources()
    for h in (23, 25):
        rebuilt = graph(h).verify()
        require(rebuilt == read(HERE/f'scalar-{h}.json'), 'Cloned scalar record differs from exact graph replay')
    ab, kappa, grid = parameters()
    p = profile()
    exact = moment(p['m'], p['W'], p['child_multiplicities'], ab)
    require(exact['upper'] < 1, 'Bit characteristic failed')
    nxt = moment(p['m'], p['W'], p['child_multiplicities'], ab+grid)
    require(nxt['lower'] > 1, 'Next bit grid point unexpectedly certified')
    prior = base.baseline.certificate()
    phase = prior['complex']['counts']
    phase_row = read(ROOT/'certificates/copied-centers-complex-input.json')
    bridge = base.baseline.finite_bridge(p, phase, [phase_row, phase_row])
    final = assembly(bridge, ab, kappa, a_complex=AC)
    require(len(final['constraints']) == 47 and len(final['margins']) == 7, 'Changed assembly interface')
    require(all(value > 0 for value in final['constraints'].values()), 'Nonpositive assembly constraint')
    eventual = cutoffs(bridge, final)
    try:
        assembly(bridge, ab, kappa+grid, a_complex=AC)
    except (AssertionError, ValueError):
        pass
    else:
        raise ValueError('Next kappa grid point unexpectedly accepted')
    controls = {path.name: excluded(path, ab) for path in sorted(HERE.glob('comparison-pr*.json'))}
    controls['comparison-pr48.json'] = excluded(ROOT/'research/skip-strips/comparison-pr48.json', ab)
    controls.update({name: excluded(PR43/name, ab) for name in
                     ('comparison-pr40.json', 'comparison-pr41.json', 'comparison-pr42.json',
                      'comparison-pr43.json', 'comparison-pr44.json', 'comparison-pr46.json', 'comparison-pr47.json')})
    comparisons = {'PR53': PR53_KAPPA, 'PR48': PR48_KAPPA}
    for path in sorted(HERE.glob('comparison-pr*.json')):
        row = read(path)
        if 'kappa' in row:
            previous = rational_pair(row['kappa'], path.name+' kappa')
            require(kappa > previous, 'Kappa does not improve '+path.name)
            comparisons['PR'+str(row['PR'])] = previous
    require(Q(1, 2**15) < kappa < Q(1, 2**14), 'Unexpected dyadic bracket')
    local = sorted(path for path in HERE.iterdir() if path.suffix in ('.py', '.cpp', '.uses', '.json', '.md')
                   and path.name not in ('certificate.json', 'validation.json', 'producer-receipt.json'))
    return dict(status='Conditional exact arithmetic witness; general transfer proofs are inherited dependencies',
                kappa=kappa, bit=dict(counts=p, **exact), next_bit_grid_lower=nxt['lower'],
                complex=prior['complex'], finite_bridge=bridge, assembly=final, eventual_bounds=eventual,
                comparison=dict(prior_savings=comparisons, ratio_PR53=kappa/PR53_KAPPA,
                                dyadic_corollary='2^-15', next_dyadic_not_reached='2^-14'),
                exclusion_lower_moments=controls,
                local_sha256={str(path.relative_to(ROOT)): sha256(path.read_bytes()).hexdigest() for path in local},
                scope='Pinned paid whole-chain clones on the PR53 skip-prefix graph family; '
                      'fixed I+J profiles, exact data recovery, copied centers and paid endpoint corrections. '
                      'Fresh finite replay is required; no exact matching optimality or global search optimality claim.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    result = run()
    if args.output:
        args.output.write_text(json.dumps(js(result), indent=2, sort_keys=True)+'\n')
    print('PASS conditional kappa='+str(result['kappa'])+'; 47 strict inequalities and seven margins')
