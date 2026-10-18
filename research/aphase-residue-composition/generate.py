#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Reproduce the four-move P53 width7 relay using only the standard library.

A-phase words: Philippe Van Velzen, PR2853; Jeremy Kothe, PR2833 predecessor.
Replica/owner lineage: Marius-Paul Dumitrean, Yiyang Lu, Tekalign, Dugongue
and retained source notices. This relay was developed with OpenAI Codex.
No solver, producer receipt, stored candidate or validation output is input.
"""
from collections import Counter, defaultdict
from pathlib import Path
import argparse
import gzip
import hashlib
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
HEAD = 'd01045dfb67428679618027dff552f1d032fa999'
PINS = {'DISPATCH.json': '2d178ebfbf3147d1f844897c779d151e04a0b9f480cbf57b76add4a24b8858ee',
 'GLOBAL-TEMPLATE.json.gz': '1d31424c4e27e26a35a9932ca778e43f1f3577589275422cc642aa68b31112db',
 'MANIFEST.json': '44ed6a457e1d1ba24726f35db86dc9e551072dd9331a8fed3ad3f0efa33ff0be',
 'ORDER.json': '30856f042860e5b5c613357b236ff643f107d7d70e2c64eb5fcaaa09bf81a90d',
 'PLAN.json': 'fafce692c9aee7fbabf1e194dcffeeb14a0a67eda22583057718831c63f35ef2',
 'PROFILE.json': '5ee33d3f641a9d3f0b643001ca506ae26defdfed3e823897abb7bd6f3b4011ea',
 'new/BORROW-PROVIDERS.json': 'd4b8c2ecd493a35b99c6c97cd2dfc4131859cce21e98527f45d9fd183c650f7b',
 'new/borrow-fill/FILL.json.gz': '36ab8173de9cc5558eb6f6407c97aa015e92b949d30de6b042db4d8427d6600b',
 'outer/OUTER-CLAIM.json': 'eb3260be191774b931cff6e562978a2af27bbc6ff666ca8c1d387a2b18dc86fa'}
BINS = [(0, 0, 2), (0, 0, 3), (7, 4, 34), (62, 10, 94), (66, 10, 90)]
PREIMAGE = [[1, 2, 0, 0, 2, 0],
 [1, 3, 0, 0, 3, 0],
 [0, 228, 66, 10, 90, 0],
 [432, 256, 66, 10, 90, 7],
 [433, 238, 66, 10, 90, 23],
 [434, 238, 66, 10, 90, 31],
 [435, 254, 66, 10, 90, 15],
 [438, 316, 66, 10, 90, 39],
 [26, 243, 7, 4, 34, 0],
 [28, 108, 7, 4, 34, 9],
 [29, 327, 7, 4, 34, 18],
 [30, 360, 7, 4, 34, 25],
 [0, 227, 62, 10, 94, 0],
 [372, 17, 62, 10, 94, 7],
 [376, 254, 62, 10, 94, 16],
 [377, 256, 62, 10, 94, 24],
 [378, 256, 62, 10, 94, 32],
 [379, 256, 62, 10, 94, 40]]
MOVES = {(29, 327): (66, 10, 90), (0, 228): (0, 0, 2), (30, 360): (62, 10, 94), (0, 227): (0, 0, 3)}


def need(condition, message):
    if not condition:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if raw[:2] == b'\x1f\x8b' else raw)


def authenticate(source):
    need(source.is_dir() and not source.is_symlink(), 'real immutable source directory')
    for name, pin in PINS.items():
        need(sha(source/name) == pin, 'exact P53 source SHA256: ' + name)
    manifest = read(source/'MANIFEST.json')
    need(len(manifest) == 549, 'complete 549-file P53 source')
    actual = {}
    for path in sorted(source.rglob('*')):
        need(not path.is_symlink(), 'source symlink')
        relative = path.relative_to(source).as_posix()
        need('__pycache__' not in path.parts and path.suffix != '.pyc', 'source bytecode')
        if path.is_file() and relative != 'MANIFEST.json':
            actual[relative] = sha(path)
    need(actual == manifest, 'complete exact P53 source inventory')
    return actual


def windows(template, order):
    ranks = {row['child']: row['rank'] for row in template['idle_children']}
    pairs = {row['stage']: row['pair'] for row in template['recipe'] if row['kind'] == 'local'}
    blocks, stage = {}, None
    for event in template['execution_schedule']:
        if event['kind'] in ('bank_padding_cover_sweep', 'translate_every_live_family'):
            continue
        if event['kind'] == 'local_cover_sweep':
            stage = event['stage']
            blocks[stage] = []
        need(stage is not None, 'source event before a call')
        blocks[stage].append(event)
    need(set(blocks) == set(range(9)), 'nine exact source stages')
    last, result, progress = {}, {}, [0]*74
    for time, (stage, replica) in enumerate(order):
        need(0 <= replica < 74 and stage == progress[replica], 'source call chronology')
        progress[replica] += 1
        for event in blocks[stage]:
            if event['kind'] == 'local_cover_sweep':
                last[replica, pairs[stage]] = time
            elif event['kind'] == 'bridge':
                last[replica, event['src']] = last[replica, event['dst']] = time
            elif event['kind'] == 'idle_cover_sweep':
                for child in event['child_indices']:
                    if child in ranks:
                        result[replica, child] = (ranks[child], last.get((replica, event['pair']), -1), time)
            else:
                need(event['kind'] in ('terminal_Y_translations', 'terminal'), 'known source event')
    need(progress == [9]*74, 'complete source projection')
    return result


def build(source):
    before = authenticate(source)
    fill = read(source/'new/borrow-fill/FILL.json.gz')
    order = read(source/'ORDER.json')
    dispatch = read(source/'DISPATCH.json')
    providers = read(source/'new/BORROW-PROVIDERS.json')
    plan = read(source/'PLAN.json')
    win = windows(read(source/'GLOBAL-TEMPLATE.json.gz'), order)
    widths = providers['gauge44']['widths']
    need(widths == providers['extra']['widths'] and len(widths) == 408, 'both exact width arrays')
    need(all(widths[helper] == 7 for time, helper in MOVES), 'four actual width7 roles')
    need(len(order) == len(dispatch) == 666 and len(fill['rows']) == 271728, 'exact T74 coverage')
    rows = fill['rows']
    changed = {i: list(row) for i, row in enumerate(rows) if tuple(row[2:5]) in BINS}
    need(list(changed.values()) == PREIMAGE, 'exact affected-bin row preimages')
    family = lambda row: row[2]*896+(2*plan['pairs'][str(row[3])]+plan['sides'][str(row[3])])*112+row[4]
    active = defaultdict(set)
    for row in rows:
        active[row[0]].add(family(row))
    found = set()
    for i, old in changed.items():
        identity = tuple(old[:2])
        if identity not in MOVES:
            continue
        destination = MOVES[identity]
        row = rows[i]
        row[2:5] = destination
        cap, lo, hi = win[destination[:2]]
        need(lo < row[0] <= hi, 'relay destination source window')
        need(family(row) not in active[row[0]], 'relay destination family initially free')
        found.add(identity)
    need(found == set(MOVES), 'exact four whole-helper moves')
    by_bin = defaultdict(list)
    for i in changed:
        by_bin[tuple(rows[i][2:5])].append(i)
    for b in BINS:
        cap, lo, hi = win[b[:2]]
        offset = 0
        for i in sorted(by_bin[b], key=lambda i: tuple(rows[i][:2])):
            row = rows[i]
            need(lo < row[0] <= hi, 'every changed-bin role source window')
            row[5] = offset
            offset += widths[row[1]]
        need(offset <= cap, 'changed-bin capacity')
    seen = defaultdict(set)
    changed_times = {row[0] for row in changed.values()}
    for row in rows:
        if row[0] in changed_times:
            f = family(row)
            need(f not in seen[row[0]], 'complete changed-call family collision')
            seen[row[0]].add(f)
    old_idle, new_idle = Counter(), Counter()
    for b in BINS:
        cap = win[b[:2]][0]
        old_rank = cap-sum(widths[row[1]] for row in changed.values() if tuple(row[2:5]) == b)
        new_rank = cap-sum(widths[rows[i][1]] for i in by_bin[b])
        need(old_rank >= 0 and new_rank >= 0, 'actual residual ranks')
        if old_rank:
            old_idle[old_rank] += 1
        if new_rank:
            new_idle[new_rank] += 1
    need(old_idle == Counter({7: 2}) and new_idle == Counter({14: 1}), 'exact residue coalescence')
    delta = new_idle.copy()
    delta.subtract(old_idle)
    need(sum(r*n for r, n in delta.items()) == 0, 'rank-neutral paid delta')
    profile = Counter({int(r): n for r, n in read(source/'PROFILE.json').items()})
    profile.update(delta)
    need(all(n >= 0 for n in profile.values()), 'nonnegative full paid profile')
    profile = +profile
    need(sum(r*n for r, n in profile.items()) == 65088*74, 'complete rank mass')
    edits = [dict(before=old, after=rows[i]) for i, old in changed.items() if old != rows[i]]
    need(len(edits) == 9, 'exact nine changed row records')
    need(authenticate(source) == before, 'immutable P53 source drift')
    return {'ORDER.json': order, 'FILL.json.gz': fill, 'DISPATCH.json': dispatch,
            'PROFILE.json': dict(profile)}, edits


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--source', type=Path, default=HERE.parent/'gmx-t74-borrow43-handoff')
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    need(not args.source.is_symlink(), 'source symlink')
    source, out = args.source.resolve(), args.out.resolve()
    need(not out.exists() and not out.is_relative_to(ROOT) and not out.is_relative_to(source),
         'fresh output outside checkout and source required')
    artifacts, edits = build(source)
    out.mkdir(parents=True)
    for name, value in artifacts.items():
        raw = json.dumps(value, sort_keys=True, separators=(',', ':')).encode()
        if name.endswith('.gz'):
            raw = bytearray(gzip.compress(raw, mtime=0))
            # Retain the frozen source run's header byte; compare decompressed
            # JSON across different compression-library implementations.
            raw[9] = 3
            raw = bytes(raw)
        (out/name).write_bytes(raw)
    print(json.dumps({'status': 'PASS_DETERMINISTIC_P53_WIDTH7_RELAY', 'source_head': HEAD,
                      'roles': 271728, 'moved_roles': 4, 'changed_rows': len(edits)}, sort_keys=True))


if __name__ == '__main__':
    main()
