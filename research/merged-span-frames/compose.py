#!/usr/bin/env python3
"""Complete paid composition of PR96 endpoint profiles and our verified axes.

Endpoint replacement ledger and bridge adaptation derive from eumemic's
PR96 merged_exterior_compose.py, pinned unchanged under references/frame-compiler/pr96/; Anthropic
Claude assistance, Apache-2.0. Existing axis/arithmetic attributions remain.
This research wrapper makes no claim to regenerate PR96's own parent words.
"""
import sys
if sys.flags.optimize:
    raise ValueError('Assertions must remain enabled')
sys.dont_write_bytecode = True
from pathlib import Path
import argparse
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
import json
import struct
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DEP = ROOT / 'references/frame-compiler/pr71'
sys.path.insert(0, str(DEP / 'scripts/experiments'))
from split_pair_arithmetic import refine, audit
import binary_frame_math as arithmetic
from endpoints import load_word


def load(path):
    return json.loads(path.read_text())

def compose(directory, words, profiler):
    selected = {str(h): load(directory / f'selection-{h}.json') for h in (23, 25)}
    profiles = [load(words / f'profile-{h}.json') for h in (23, 25)]
    m, N = 575, 4073300
    width = 2*N + sum(N//f['v']*f['R'] for f in profiles)
    parts = {'data': Counter({1:18*N, 21:2*N, 17:2*N, 481:2*N}), 'endpoint_copy': Counter({1:N})}
    for f in profiles:
        h, rep = f['h'], N//f['v']
        assert f['crt_disagreements'] == 0 and f['loss'] == h*(h-1)
        assert f['rank_sum'] == h*f['R']+f['loss'] == sum(t*n for t,n in enumerate(f['blocks']))
        parts[f'growth_{h}'] = Counter({1:2*N, h-2:2*N})
    axes = {}
    for f in profiles:
        h = f['h']
        d, first, last, outputs, digest = load_word(h, words)
        chosen = selected[str(h)]
        assert digest == chosen['word_sha256'] and d['R'] == chosen['R'] == f['R']
        assert not set(chosen['entrance']) & set(chosen['exit'])
        assert not set(chosen['exit']) & outputs
        frames = [(0, 0, 0), (0, 0, h)] + [(c, u, 1 if c == u else u.bit_count() - c.bit_count()) for c, u in d['frames']]
        removed = Counter()
        edges = Counter()
        for s in chosen['entrance']:
            removed[0, first[s] + 2] += 1
            edges[f'entrance:{first[s]}'] += 1
        for s in chosen['exit']:
            removed[last[s] + 2, 1] += 1
            edges[f'exit:{last[s]}'] += 1
        mass = sum((frames[b][2] - frames[a][2]) * n for (a, b), n in removed.items())
        path = directory / f'removed-{h}.bin'
        with path.open('wb') as out:
            out.write(struct.pack('<6I2Q', h, f['v'], 0, len(frames), len(removed), 0, mass, mass))
            for c, u, rank in frames:
                out.write(struct.pack('<2QI', c, u, rank))
            for (a, b), n in sorted(removed.items()):
                out.write(struct.pack('<2Iq', a, b, n))
        with (directory / f'removed-{h}.log').open('w') as log:
            subprocess.run([str(profiler), str(path)], check=True, stdout=log, stderr=subprocess.STDOUT)
        removed_profile = load(Path(str(path) + '.profiles.json'))
        assert removed_profile['crt_disagreements'] == 0 and removed_profile['rank_sum'] == mass
        internal = Counter({t: n for t, n in enumerate(f['blocks']) if n})
        internal.subtract({t: n for t, n in enumerate(removed_profile['blocks']) if n})
        assert all(n >= 0 for n in internal.values())
        merged = Counter()
        assert set(chosen['merged_edges']) == set(edges)
        for key, n in edges.items():
            edge = chosen['merged_edges'][key]
            assert sum(edge['runs']) == edge['rank'] and 0 < min(edge['runs']) <= max(edge['runs']) < m
            merged.update({t: count * n for t, count in Counter(edge['runs']).items()})
        roles = len(chosen['entrance']) + len(chosen['exit'])
        assert sum(t * n for t, n in merged.items()) == mass + roles * (m - h)
        rep = N // f['v']
        bank = rep * (f['R'] - roles)
        parts[f'internal_{h}'] = Counter({t: n * rep for t, n in internal.items() if n})
        parts[f'merged_{h}'] = Counter({t: n * rep for t, n in merged.items()})
        parts[f'exterior_{h}'] = Counter({h: bank, m - 2 * h: bank})
        axes[str(h)] = dict(R=f['R'], entrance_roles=len(chosen['entrance']), exit_roles=len(chosen['exit']),
                           merged_edges=len(edges), removed_rank_mass=mass, removed_blocks=removed_profile['blocks'],
                           word_sha256=digest, selection_sha256=sha256((directory / f'selection-{h}.json').read_bytes()).hexdigest(),
                           removed_crt_matrices=removed_profile['crt_matrices'])
    rows = sum(parts.values(), Counter())
    total = sum(t * n for t, n in rows.items())
    assert total == m * width - 1846900 and all(0 < t < m for t in rows)
    bit_profile = dict(m=m, N=N, W=width, L=N-1846900, total_rank=total, deficit=1846900,
                       maxchild=max(rows), child_multiplicities=dict(sorted(rows.items())), parts=parts, axes=axes)
    grid = 10**18
    lo, hi = 1, grid // 10000
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if refine.exact_moment(m, width, rows, Q(mid, grid))['upper'] < 1:
            lo = mid
        else:
            hi = mid
    saving = Q(lo, grid)
    accepted = refine.exact_moment(m, width, rows, saving)
    rejected = refine.exact_moment(m, width, rows, saving + Q(1, grid))
    assert accepted['upper'] < 1 < rejected['lower']
    independent = audit.independent_moment(arithmetic.js(bit_profile), saving, arithmetic.js(accepted['terms']))
    independent_rejected = audit.independent_moment(arithmetic.js(bit_profile), saving + Q(1, grid), arithmetic.js(accepted['terms']))
    assert independent[1] < 1 < independent_rejected[0]
    bridge = load(DEP / 'references/frame-compiler/pr48/research/copied-fixed/certificate.json')['finite_bridge']
    bridge['bit']['W'] = width
    bridge['bit']['wire_bits'] = width.bit_length()
    bridge['bit']['maxchild'] = max(rows)
    bridge['bit']['halving_degree'] = refine.balanced.halving_degree(m, max(rows))
    coefficient = sum(bridge[k]['halving_degree'] * bridge[k]['wire_bits'] for k in ('bit', 'complex'))
    minimum_degree = Q(51, 25) * coefficient
    row_degree = max(2000, 100 * (minimum_degree // 100 + 1))
    bridge['rows'].update(coefficient=coefficient, degree=row_degree, degree_gap=row_degree-minimum_degree, suffix_slope=4*row_degree)
    refine.balanced.validate_bridge(bridge)
    assembled = refine.assemble(bridge, saving, Q(1, 10**12), grid)
    kappa = assembled['kappa']
    assert all(v > 0 for v in assembled['assembly']['constraints'].values())
    assert all(v > kappa for v in assembled['assembly']['margins'].values())
    result = dict(status='Finite conditional witness; multiplicative endpoint gauge and independent audits checked separately; inherited all-size transfer remains assumed',
                  bit_saving=saving, bit_saving_excluded_above=saving+Q(1, grid),
                  bit=dict(bit_profile, moment=accepted, excluded_moment=rejected),
                  independent_enclosures=dict(accepted=independent, rejected=independent_rejected),
                  finite_bridge=bridge, **assembled)
    (directory / 'certificate.json').write_text(json.dumps(arithmetic.js(result), indent=2, sort_keys=True) + '\n')
    print('EXACT', float(kappa), str(kappa), 'maxchild', max(rows), 'width', width, flush=True)
    return result

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory', type=Path)
    parser.add_argument('--words', type=Path, default=HERE)
    parser.add_argument('--profiler', type=Path, required=True)
    args = parser.parse_args()
    compose(args.directory.resolve(), args.words.resolve(), args.profiler.resolve())
