#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Replay one exact four-bin relay from the pinned PR3010 k940 allocation.

Ross Richardson, with substantial OpenAI GPT-6.1 Sol assistance. Source words
and actual provider inventory: Marius-Paul Dumitrean / PR2979. Chronological
owner method: Yiyang Lu / PR2857, Mason Hale / PR2917 and retained predecessors.
The event replay follows the contract documented and checked in PR3010.
No solver, external checkout module, floating arithmetic or search is needed.
"""
import argparse
from collections import Counter, defaultdict
from copy import deepcopy
import gzip
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
WIDTHS = (4, 5, 6, 7, 8, 9)
PROFILE = {1: 822840, 2: 235098, 3: 79734, 4: 35964,
           5: 6858, 8: 2664, 48: 14095}
BINS = {'C': (23, 16, 0), 'D': (17, 14, 0),
        'R7': (16, 17, 111), 'R9': (21, 15, 111)}
STAGES = [
    ('same_width_7', [((224, 337), 'R7'), ((271, 342), 'D')]),
    ('same_width_9', [((259, 166), 'R9'), ((266, 64), 'D')]),
    ('inverse_face_swap', [((268, 399), 'D'), ((269, 87), 'D'),
                           ((271, 342), 'C'), ((266, 64), 'C')]),
]


def need(ok, message):
    if not ok:
        raise ValueError(message)


def read(path):
    data = Path(path).read_bytes()
    return json.loads(gzip.decompress(data) if data[:2] == b'\x1f\x8b' else data)


def save(path, obj):
    data = json.dumps(obj, sort_keys=True, separators=(',', ':')).encode()
    if str(path).endswith('.gz'):
        data = bytearray(gzip.compress(data, mtime=0))
        data[9] = 255
        data = bytes(data)
    Path(path).write_bytes(data)


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def windows(order, template, plan):
    """Source events give open lower and closed upper integral call times."""
    ranks = {}
    for item in template['idle_children']:
        c = item['child']
        need(c not in ranks or ranks[c] == item['rank'], 'source rank consistency')
        ranks[c] = item['rank']
    active = {e['stage']: e['pair'] for e in template['recipe'] if e['kind'] == 'local'}
    blocks, stage = {}, None
    for event in template['execution_schedule']:
        kind = event['kind']
        if kind in ('bank_padding_cover_sweep', 'translate_every_live_family'):
            continue
        if kind == 'local_cover_sweep':
            stage = event['stage']
            blocks[stage] = []
        need(stage is not None, 'event before stage')
        blocks[stage].append(event)
    touch, result = {}, {}
    progress = [0] * 37
    for t, (s, r) in enumerate(order):
        need(progress[r] == s, 'replica internal order')
        progress[r] += 1
        for event in blocks[s]:
            kind = event['kind']
            if kind == 'local_cover_sweep':
                touch[r, active[s]] = t
            elif kind == 'bridge':
                touch[r, event['src']] = touch[r, event['dst']] = t
            elif kind == 'idle_cover_sweep':
                lower = touch.get((r, event['pair']), -1)
                for c in event['child_indices']:
                    if c in ranks:
                        need((r, c) not in result, 'unique pending child')
                        need(plan['pairs'][str(c)] == event['pair'], 'source pair')
                        result[r, c] = (ranks[c], lower, t)
            else:
                need(kind in ('terminal_Y_translations', 'terminal'), 'known event')
    need(progress == [9] * 37 and len(result) == 666, 'all source windows')
    return result, active


def geometry(rows, order, dispatch, providers, plan, win, active):
    """Generator checks; independent verifiers must check the literal again."""
    bybin = defaultdict(list)
    roles = [set() for _ in order]
    families = [set() for _ in order]
    for row in rows:
        t, h, o, c, p, z = row
        cap, lower, upper = win[o, c]
        need(lower < t <= upper, 'strict source window')
        need(h not in roles[t] and 0 <= h < 408, 'helper identity')
        roles[t].add(h)
        s, r = order[t]
        pair, side = plan['pairs'][str(c)], plan['sides'][str(c)]
        family = (o, pair, side, p)
        need(not (o == r and pair == active[s]), 'active family exclusion')
        need(family not in families[t], 'per-call family exclusion')
        families[t].add(family)
        w = providers[dispatch[s, r]]['widths'][h]
        need(0 <= p < 112 and 0 <= z and z + w <= cap, 'mask bounds')
        bybin[o, c, p].append((z, w, t, h))
    need(len(rows) == 135864 and all(len(s) == 408 for s in roles), 'complete roles')
    patterns, idle = Counter(), Counter()
    for (o, c), (cap, lower, upper) in win.items():
        for p in range(112):
            end, q = 0, Counter()
            for z, w, t, h in sorted(bybin.get((o, c, p), [])):
                need(z == end, 'compact disjoint prefix')
                end += w
                q[w] += 1
            patterns[cap, tuple(q[w] for w in WIDTHS)] += 1
            if end < cap:
                idle[cap - end] += 1
    profile = Counter(idle)
    for s, r in order:
        profile.update({int(k): n for k, n in providers[dispatch[s, r]]['actual_paid_profile'].items()})
    need(dict(profile) == PROFILE, 'complete paid child profile')
    need(sum(r * n for r, n in profile.items()) == 2408256, 'rank mass')
    return patterns, idle, dict(sorted(profile.items()))


def construct(out):
    manifest = read(ROOT / 'SOURCES.json')
    for path, item in manifest['exports'].items():
        need(digest(ROOT / path) == item['sha256'], 'pinned source bytes: ' + path)
    start = read(ROOT / 'start/FILL.json.gz')
    rows = deepcopy(start['rows'])
    before = deepcopy(rows)
    order = read(ROOT / 'start/ORDER.json')
    dispatch_rows = read(ROOT / 'start/DISPATCH.json')
    dispatch = {(s, r): p for s, r, p in dispatch_rows}
    providers = read(ROOT / 'sources/allocation/PROVIDERS.json')
    for provider in providers.values():
        need(len(provider['widths']) == 408 and Counter(provider['widths']) ==
             Counter({4: 26, 5: 2, 6: 16, 7: 52, 8: 99, 9: 213}), 'actual provider registry')
    template = read(ROOT / 'sources/allocation/vendor/TEMPLATE.json.gz')
    plan = read(ROOT / 'sources/allocation/vendor/PLAN.json.gz')
    win, active = windows(order, template, plan)
    start_patterns, _, _ = geometry(rows, order, dispatch, providers, plan, win, active)
    byrole = {(row[0], row[1]): i for i, row in enumerate(rows)}
    need(len(byrole) == len(rows), 'unique actual helper identities')
    width = [providers[dispatch[tuple(order[t])]]['widths'][h] for t, h, *_ in rows]
    stage_records = []
    for name, transfers in STAGES:
        previous = deepcopy(rows)
        affected = set()
        for role, dest in transfers:
            i = byrole[role]
            affected.add(tuple(rows[i][2:5]))
            affected.add(BINS[dest])
            rows[i][2:5] = BINS[dest]
        need(affected <= set(BINS.values()), 'only declared four bins')
        for b in sorted(affected):
            ids = [i for i, row in enumerate(rows) if tuple(row[2:5]) == b]
            z = 0
            for i in sorted(ids, key=lambda j: (rows[j][0], rows[j][1])):
                rows[i][5] = z
                z += width[i]
        patterns, idle, profile = geometry(rows, order, dispatch, providers, plan, win, active)
        stage_records.append({
            'name': name,
            'transfers': [{'role': list(role), 'width': width[byrole[role]],
                           'before': previous[byrole[role]], 'after': list(rows[byrole[role]])}
                          for role, dest in transfers],
            'repacked_stationary': [{'role': [row[0], row[1]], 'before': old, 'after': list(row)}
                                    for old, row in zip(previous, rows)
                                    if old != row and old[2:5] == row[2:5]],
        })
    target = Counter({(cap, tuple(q)): n for cap, q, n in
                      read(ROOT / 'sources/construction/allocation/T37-FACE-MIX.json')['target']})
    target[16, (0, 0, 0, 0, 2, 0)] = 1262
    target[16, (0, 0, 0, 1, 0, 1)] = 15314
    target[32, (0, 0, 0, 1, 2, 1)] = 124
    target[32, (0, 0, 0, 2, 0, 2)] = 939
    need(patterns == target, 'exact k939 face mix')
    delta = patterns - start_patterns
    minus = start_patterns - patterns
    need(sum(delta.values()) == sum(minus.values()) == 2, 'one inverse face swap')
    need(all(old == row for old, row in zip(before, rows)
             if tuple(old[2:5]) not in set(BINS.values())), 'all other bins unchanged')
    owner_moves = [{'role': [row[0], row[1]], 'width': width[i], 'before': old,
                    'after': list(row), 'before_bin': old[2:5], 'after_bin': row[2:5]}
                   for i, (old, row) in enumerate(zip(before, rows)) if old[2:5] != row[2:5]]
    stationary = [{'role': [row[0], row[1]], 'before': old, 'after': list(row)}
                  for old, row in zip(before, rows) if old != row and old[2:5] == row[2:5]]
    need(len(owner_moves) == 6, 'six distinct final owner moves')
    need(sum(len(s['transfers']) for s in stage_records) == 8, 'eight staged transfers')
    states = []
    for name, b in BINS.items():
        cap, lower, upper = win[b[:2]]
        states.append({'name': name, 'bin': list(b), 'capacity': cap,
                       'window': {'lower_open': lower, 'upper_closed': upper},
                       'before': [r for r in before if tuple(r[2:5]) == b],
                       'after': [r for r in rows if tuple(r[2:5]) == b]})
    fill = {'columns': start['columns'], 'dispatch_overrides': [],
            'method': 'Three exact staged exchanges on four bins from pinned PR3010 k940; GPT-6.1 Sol assisted',
            'rows': rows}
    journal = {'schema_version': 1, 'start_k': 940, 'end_k': 939,
               'columns': start['columns'], 'moves': owner_moves,
               'repacked_stationary': stationary, 'stages': stage_records, 'bin_states': states}
    meta = {'schema_version': 1, 'T': 37, 'k': 939, 'mode': 'four-bin same-width relay and inverse face swap',
            'moves': 6, 'staged_transfers': 8, 'changed_bins': 4, 'capacity48_bins_changed': 0,
            'start_reference': {'commit': manifest['predecessor_commit'], 'path': 'start/FILL.json.gz',
                                'sha256': digest(ROOT / 'start/FILL.json.gz'), 'k': 940},
            'source_commit': manifest['source_commit'], 'base_commit': manifest['base_commit'],
            'proof_level': 'Finite exact construction with generator checks; independent literal check required',
            'profile': profile, 'idle_profile': dict(sorted(idle.items())), 'rank_mass': 2408256,
            'conditional_stock': 33661, 'private_buffers': 91,
            'cost_delta_for_every_rank_tariff': 0, 'no_new_kappa': True,
            'search': 'One bounded standard-library vacancy-path attempt; first trial gave this witness; replay has no search dependency'}
    out.mkdir(parents=True, exist_ok=False)
    for name, obj in [('ORDER.json', order), ('DISPATCH.json', dispatch_rows), ('FILL.json.gz', fill),
                      ('PROFILE.json', profile), ('JOURNAL.json', journal), ('META.json', meta),
                      ('PATTERNS.json', {'T': 37, 'k': 939, 'widths': WIDTHS,
                                         'target': [[cap, q, n] for (cap, q), n in sorted(patterns.items())]})]:
        save(out / name, obj)
    print(json.dumps({'status': 'PASS_CONSTRUCTION_GENERATOR', 'candidate': str(out), 'k': 939,
                      'owner_moves': 6, 'staged_transfers': 8, 'changed_bins': 4}, sort_keys=True))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--out', type=Path, default=ROOT / 'candidate')
    args = ap.parse_args()
    construct(args.out)


if __name__ == '__main__':
    main()
