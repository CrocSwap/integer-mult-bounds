#!/usr/bin/env python3
"""Compose the PR79 balanced-split witness with merged auxiliary exteriors.

Each selected role loses its entrance (0 -> first frame) or final cleanup
(last frame -> I_h) local transition and its exterior [h, m-2h], and gains one
exactly profiled merged edge. The removed transitions are profiled by the
unchanged inherited profiler. Words, data, endpoint copies and the complex
layer are PR79's. The finite bridge is recomputed for the new largest child.
"""
import sys
if sys.flags.optimize:
    raise ValueError('Assertions must remain enabled')
sys.dont_write_bytecode = True

from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import json, struct, subprocess, tempfile

import binary_frame_math as arithmetic
import balanced_split_compose as base
from split_pair_arithmetic import refine, audit
from merged_exterior import A_, B_, M_, OUT, ROOT, HERE, load_word

ROW_DEGREE = 2200          # product row stock p^2200 (PROOF.md, section 4)


def removed_transitions(h, chosen):
    d, first, last, outputs, digest = load_word(h)
    assert digest == chosen['word_sha256'] and d['R'] == chosen['R']
    assert not set(chosen['entrance']) & set(chosen['exit']) and not set(chosen['exit']) & outputs
    frames = [(0, 0, 0), (0, 0, h)] + [(c, u, 1 if c == u else u.bit_count() - c.bit_count()) for c, u in d['frames']]
    removed = Counter()
    for s in chosen['entrance']:
        removed[0, first[s] + 2] += 1
    for s in chosen['exit']:
        removed[last[s] + 2, 1] += 1
    mass = sum((frames[b][2] - frames[a][2]) * n for (a, b), n in removed.items())
    edges = Counter([f'entrance:{first[s]}' for s in chosen['entrance']] + [f'exit:{last[s]}' for s in chosen['exit']])
    return frames, removed, mass, d['v'], edges


def profile_removed(h, frames, removed, mass, v):
    """Unchanged inherited profiler on the removed transitions only."""
    with tempfile.TemporaryDirectory(prefix='merged-exterior-') as tmp:
        tmp = Path(tmp)
        binary = tmp / 'profiles'
        subprocess.run(['c++', '-O2', '-std=c++17', '-I', str(ROOT / 'references/frame-compiler/pr48/scripts/partial_swap'),
                        str(HERE / 'binary_frame_profiles.cpp'), '-o', str(binary)], check=True)
        path = tmp / f'removed{h}.bin'
        with path.open('wb') as f:
            # R=0 and loss=mass satisfy the inherited header check sum == h*R + loss.
            f.write(struct.pack('<6I2Q', h, v, 0, len(frames), len(removed), 0, mass, mass))
            for c, u, r in frames:
                f.write(struct.pack('<2QI', c, u, r))
            for (a, b), n in sorted(removed.items()):
                f.write(struct.pack('<2Iq', a, b, n))
        subprocess.run([str(binary), str(path)], check=True, capture_output=True, text=True)
        prof = json.loads(Path(str(path) + '.profiles.json').read_text())
    assert prof['crt_disagreements'] == 0 and prof['rank_sum'] == mass
    return prof['blocks']


def profile(selection):
    p = base.profile()                      # PR79 complete profile and all of its checks
    m, N, W, L = p['m'], p['N'], p['W'], p['L']
    parts = {name: Counter(rows) for name, rows in p['parts'].items()}
    axes = {}
    for f in p['axes']:
        h = f['h']
        chosen = selection[str(h)]
        frames, removed, mass, v, edges = removed_transitions(h, chosen)
        assert v == f['v']
        blocks = profile_removed(h, frames, removed, mass, v)
        rep = N // v
        internal = Counter({t: n for t, n in enumerate(f['blocks']) if n})
        internal.subtract(Counter({t: n for t, n in enumerate(blocks) if n}))
        assert min(internal.values()) >= 0, 'removed more than present'
        merged = Counter()
        for key, count in edges.items():
            e = chosen['merged_edges'][key]
            assert sum(e['runs']) == e['rank'] and len(e['runs']) and max(e['runs']) < m
            for t in e['runs']:
                merged[t] += count
        assert set(chosen['merged_edges']) == set(edges)
        roles = len(chosen['entrance']) + len(chosen['exit'])
        # Each merged role trades its removed local edge and one exterior (rank m-h) for one edge.
        assert sum(t * n for t, n in merged.items()) == mass + roles * (m - h)
        bank = rep * (f['R'] - roles)
        parts[f'internal_{h}'] = Counter({t: n * rep for t, n in internal.items() if n})
        parts[f'merged_{h}'] = Counter({t: n * rep for t, n in merged.items()})
        parts[f'exterior_{h}'] = Counter({h: bank, m - 2 * h: bank})
        axes[str(h)] = dict(R=f['R'], entrance_roles=len(chosen['entrance']), exit_roles=len(chosen['exit']),
                            merged_edges=len(edges), removed_rank_mass=mass, removed_blocks=blocks,
                            word_sha256=chosen['word_sha256'])
    rows = sum(parts.values(), Counter())
    total = sum(t * n for t, n in rows.items())
    assert total == m * W - N + L == p['total_rank'] and all(0 < t < m for t in rows)
    return dict(m=m, N=N, W=W, L=L, total_rank=total, deficit=m * W - total, maxchild=max(rows),
                child_multiplicities=dict(sorted(rows.items())), parts=parts, axes=axes)


def finite_bridge(width, maxchild):
    """PR79 bridge with the bit layer's largest child, halving degree and row stock updated."""
    bridge = base.finite_bridge(width)
    bridge['bit']['maxchild'] = maxchild
    bridge['bit']['halving_degree'] = refine.balanced.halving_degree(bridge['bit']['m'], maxchild)
    coefficient = sum(bridge[k]['halving_degree'] * bridge[k]['wire_bits'] for k in ('bit', 'complex'))
    bridge['rows'].update(coefficient=coefficient, degree=ROW_DEGREE,
                          degree_gap=ROW_DEGREE - Q(51, 25) * coefficient, suffix_slope=4 * ROW_DEGREE)
    refine.balanced.validate_bridge(bridge)
    return bridge


def best_saving(p, denominator):
    """Largest grid saving whose exact upper moment is below one."""
    lo, hi = 1, denominator // 10**4
    assert refine.exact_moment(p['m'], p['W'], p['child_multiplicities'], Q(hi, denominator))['lower'] > 1
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if refine.exact_moment(p['m'], p['W'], p['child_multiplicities'], Q(mid, denominator))['upper'] < 1:
            lo = mid
        else:
            hi = mid
    return Q(lo, denominator)


def compose(selection):
    denominator = 10**18
    grid = Q(1, denominator)
    p = profile(selection)
    bit = best_saving(p, denominator)
    exact = refine.exact_moment(p['m'], p['W'], p['child_multiplicities'], bit)
    excluded = refine.exact_moment(p['m'], p['W'], p['child_multiplicities'], bit + grid)
    assert exact['upper'] < 1 < excluded['lower']
    js = arithmetic.js(dict(p, parts={}))
    independent = audit.independent_moment(js, bit, arithmetic.js(exact['terms']))
    rejected = audit.independent_moment(js, bit + grid, arithmetic.js(exact['terms']))
    assert independent[1] < 1 < rejected[0]
    bridge = finite_bridge(p['W'], p['maxchild'])
    assembled = refine.assemble(bridge, bit, Q(1, 10**12), denominator)
    kappa = assembled['kappa']
    assert all(value > 0 for value in assembled['assembly']['constraints'].values())
    assert all(value > kappa for value in assembled['assembly']['margins'].values())
    pr79 = json.loads((OUT / 'balanced-split-kappa.json').read_text())
    previous = Q(pr79['kappa'])
    old = {int(t): n for t, n in pr79['bit']['child_multiplicities'].items()}
    pr79_lower = refine.exact_moment(pr79['bit']['m'], pr79['bit']['W'], old, bit)['lower']
    assert pr79_lower > 1 and kappa > previous
    return dict(
        status='Finite conditional physical witness and exact balanced assembly; inherited transfer hypotheses remain assumed',
        kappa=kappa, bit_saving=bit, bit_saving_excluded_above=bit + grid, grid_denominator=denominator,
        bit=dict(p, moment=exact, excluded_moment=excluded),
        independent_enclosures=dict(accepted_lower=independent[0], accepted_upper=independent[1],
                                    rejected_lower=rejected[0], rejected_upper=rejected[1]),
        assembly=assembled['assembly'], eventual_bounds=assembled['eventual_bounds'], finite_bridge=bridge,
        next_kappa=assembled['next_kappa'], next_kappa_rejection=assembled['next_kappa_rejection'],
        comparison=dict(pr79_commit='9a58e62cf9e8954a4dde3c9b1372d733c276a6d1', pr79_kappa=previous,
                        ratio_pr79=kappa / previous, pr79_complete_profile_exclusion_lower=pr79_lower),
        selection_sha256=sha256(json.dumps(selection, sort_keys=True, separators=(',', ':')).encode()).hexdigest())


if __name__ == '__main__':
    outdir = Path(sys.argv[1])
    selection = json.loads((outdir / 'merged-exterior-selection.json').read_text())
    result = compose(selection)
    (outdir / 'merged-exterior-kappa.json').write_text(json.dumps(arithmetic.js(result), indent=1, sort_keys=True) + '\n')
    print(f'kappa {result["kappa"]} = {float(result["kappa"]):.12e}; bit saving {float(result["bit_saving"]):.12e}; '
          f'maxchild {result["bit"]["maxchild"]}; ratio to PR79 {float(result["comparison"]["ratio_pr79"]):.5f}', flush=True)
