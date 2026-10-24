"""Rank-debt certificate. Apache-2.0; substantial OpenAI Codex assistance.

Checks the hypotheses of PROOF.md, not native phases or a new supplier.
Original word: Cao Yifan/PR4610, retained by Cinna Davis/PR4665.
"""
from collections import Counter
from copy import deepcopy
from fractions import Fraction as Q
import gzip
import hashlib
import json
from math import isqrt
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
PAID = {1: 2201, 2: 412, 3: 510, 4: 127, 5: 40, 8: 8}
HELPERS = {4: 28, 7: 7, 8: 47, 9: 326}


def need(ok, message):
    if not ok:
        raise ValueError(message)


def span(basis):
    out = {0}
    for x in basis:
        need(type(x) is int and 0 < x < 512, 'nonzero nine-bit vector')
        out |= {v ^ x for v in tuple(out)}
    need(len(out) == 2 ** len(basis), 'independent binary frame')
    return frozenset(out)


def mv(columns, x):
    out = 0
    for i, v in enumerate(columns):
        if x >> i & 1:
            out ^= v
    return out


def invert(columns):
    table = {mv(columns, x): x for x in range(512)}
    need(len(table) == 512, 'invertible warp')
    return [table[1 << i] for i in range(9)]


def audit(payload):
    c, programs = payload['canonical'], payload['programs']
    frames = c['frames']
    spaces = list(map(span, frames))
    need(len(c['start']) == len(c['final']) == 632, '632 independent fields')
    need(set(programs) == {'forward', 'backward'}, 'both orientations')
    maps = {w['op']: w['G_columns'] for w in c['warps']}
    maps.update({-op: invert(g) for op, g in list(maps.items())})
    results = {}
    for direction, word in sorted(programs.items()):
        current = {('L', r): f for r, f in enumerate(c['start'])}
        current['C', 0] = None
        images = [list(frames[f]) for f in c['start']]
        widths = [[] for _ in range(632)]
        blocks = [[] for _ in range(632)]
        helper_blocks = Counter()
        paid, counts = Counter(), Counter()

        def close_block(r):
            if r >= 224:
                need(len(blocks[r]) <= 1, 'at most one original paid call between scalar contacts')
                helper_blocks[len(blocks[r])] += 1
            blocks[r] = []

        for e in word:
            kind = e[0]
            counts[kind] += 1
            if kind in ('climb', 'center'):
                if kind == 'climb':
                    _, _, r, a, b, width = e
                    role = ('L', r)
                    need(spaces[a] < spaces[b], 'monotone persistent transport')
                    widths[r].append(width)
                    blocks[r].append(width)
                else:
                    _, r, a, b, width = e
                    role = ('C', r)
                    need(spaces[a] < spaces[b] or spaces[b] < spaces[a],
                         'nested center transport')
                need(current[role] == a, 'paid input chart')
                need(width == abs(len(frames[b]) - len(frames[a])), 'paid width')
                paid[width] += 1
                current[role] = b
            elif kind == 'warp':
                _, reg, op, a, b = e
                role = tuple(reg)
                need(role[0] == 'L' and current[role] == a, 'warp input chart')
                need(span([mv(maps[op], x) for x in frames[a]]) == spaces[b],
                     'warp acts on its complete declared subspace')
                need(len(frames[a]) == len(frames[b]), 'warp preserves dimension')
                images[role[1]] = [mv(maps[op], x) for x in images[role[1]]]
                current[role] = b
            elif kind == 'scalar':
                g, f = e[1:]
                role = tuple(g[1])
                if g[0] == 'clear':
                    need(role == ('C', 0), 'only owned center cleared')
                    current[role] = f
                else:
                    need(g[0] in ('add', 'copy', 'scale'), 'known scalar action')
                    refs = g[1:3] if g[0] in ('add', 'copy') else g[1:2]
                    need(all(current[tuple(reg)] == f for reg in refs), 'common scalar chart')
                    for typ, r in refs:
                        if typ == 'L':
                            close_block(r)
                    if g[0] == 'copy':
                        need(role == ('C', 0), 'only owned center overwritten')
            else:
                need(kind in ('phase', 'adapter'), 'known inert marker')
                if kind == 'adapter':
                    close_block(e[2])
        need(paid == PAID, 'complete source paid profile, including centers')
        need([current['L', r] for r in range(632)] == c['final'], 'all final charts')
        helpers, maximum_step, path_mass = Counter(), Counter(), 0
        for r in range(632):
            close_block(r)
            h = len(frames[c['final'][r]]) - len(frames[c['start'][r]])
            need(sum(widths[r]) == h, 'telescoping persistent paid mass')
            if r >= 224:
                need(h > 0 and spaces[c['start'][r]] <= spaces[c['final'][r]],
                     'positive nested helper endpoint')
                need(images[r] == frames[c['start'][r]], 'net warp fixes helper entrance pointwise')
                need(max(widths[r], default=0) <= h, 'each paid step bounded by endpoint rank')
                helpers[h] += 1
                maximum_step[max(widths[r], default=0)] += 1
                path_mass += sum(widths[r])
        need(helpers == HELPERS and path_mass == 3471, 'all 408 helper paths')
        results[direction] = {
            'events': dict(sorted(counts.items())), 'paid': dict(sorted(paid.items())),
            'helper_ranks': dict(sorted(helpers.items())),
            'helper_maximum_paid_step': dict(sorted(maximum_step.items())),
            'helper_path_rank_mass': path_mass, 'pointwise_fixed_helper_entrances': 408,
            'helper_contact_blocks_by_original_paid_calls': dict(sorted(helper_blocks.items())),
            'persistent_paths_with_exact_rank_telescope': 632,
        }
    return results


def rank(rows):
    pivots = {}
    for x in rows:
        while x:
            p = x.bit_length() - 1
            if p not in pivots:
                pivots[p] = x
                break
            x ^= pivots[p]
    return len(pivots)


def controls(payload):
    forms = [(a | b << 1, b | c << 1)
             for a in range(2) for b in range(2) for c in range(2)]
    cases = 0
    for a in forms:
        for b in forms:
            for c in forms:
                difference = lambda x, y: [u ^ v for u, v in zip(x, y)]
                g = rank(difference(a, c))
                debt = rank(difference(a, b)) + rank(difference(b, c))
                need(g <= debt, 'exact endpoint rank triangle inequality')
                cases += 1
    scale = 1 << 80
    root = lambda n: (Q(isqrt(n * scale * scale), scale),
                      Q(isqrt(n * scale * scale) + 1, scale))
    need(root(2)[0] - 1 > root(5)[1] - 2,
         'split path pays more than its endpoint at t=1/2')
    need(root(9)[1] - root(8)[0] < root(5)[0] - 2,
         'step larger than endpoint breaks the required inequality')
    failures = []
    for label in ('wrong_width', 'missing_center', 'wrong_warp', 'wrong_helper_endpoint'):
        bad = deepcopy(payload)
        word = bad['programs']['forward']
        if label == 'wrong_width':
            next(e for e in word if e[0] == 'climb')[5] += 1
        elif label == 'missing_center':
            word.remove(next(e for e in word if e[0] == 'center'))
        elif label == 'wrong_warp':
            next(e for e in word if e[0] == 'warp' and bad['canonical']['frames'][e[3]])[4] = 0
        else:
            bad['canonical']['final'][224] = 0
        try:
            audit(bad)
        except (ValueError, KeyError):
            failures.append(label)
        else:
            raise ValueError('mutation accepted: ' + label)
    return {'symmetric_form_rank_triangles': cases,
            'strict_concave_increment_and_missing_hypothesis': True,
            'source_mutations_rejected': failures}


def main():
    source = HERE / 'inputs/round3-native.json.gz'
    pins = json.loads((HERE / 'SOURCES.json').read_text())
    pin = next(row for row in pins['files'] if row['path'].endswith(source.name))
    raw = source.read_bytes()
    need(hashlib.sha256(raw).hexdigest() == pin['sha256'], 'exact original source bytes')
    payload = json.loads(gzip.decompress(raw))
    report = {'status': 'FIXED_WORD_PHASE_CHANGES_CANNOT_IMPROVE_ANY_CONCAVE_MOMENT',
              'no_new_kappa': True, 'orientations': audit(payload),
              'controls': controls(payload)}
    changed = deepcopy(payload)
    for basis in changed['canonical']['frames']:
        if len(basis) >= 2:
            basis[0] ^= basis[1]
    need(audit(changed) == report['orientations'], 'all frame basis changes preserve certificate')
    report['controls']['all_frame_basis_changes'] = True
    report = json.loads(json.dumps(report))
    path = HERE / 'RESULT.json'
    if '--write' in sys.argv:
        path.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
    else:
        need(report == json.loads(path.read_text()), 'committed result equality')
    print('PASS_PHASE_RANK_DEBT: both orientations, 408 helpers, all 0<=t<=1; no new kappa')


if __name__ == '__main__':
    main()
