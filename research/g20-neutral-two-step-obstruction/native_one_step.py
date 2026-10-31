#!/usr/bin/env python3
"""Exhaustive one-conjugation all-native-route floor certificate.

Prepared for @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
Credits: Ali Romman (#5616/#5708), unpaidmoon (#6290), Nick Petalas (#6305).
"""
import argparse
from collections import Counter, defaultdict
import gzip
from hashlib import sha256
import json
from pathlib import Path
from types import ModuleType
_native_path = Path(__file__).resolve().parent / 'native_floor.py'
_native_raw = _native_path.read_bytes()
if sha256(_native_raw).hexdigest() != '2a9b4cc47ce8ad3a4ab1a0467dda2737202ef9f982da564bd64fe0d3fb9cb5d3':
    raise ValueError('native implementation bytes')
N = ModuleType('frozen_native_floor')
N.__file__ = str(_native_path)
exec(compile(_native_raw, str(_native_path), 'exec'), N.__dict__)

WORD_SHA = '8dd441fdb9c8923df06eb5ebfda37d03e4539f2305763e688d8c7025d196c4b1'
PATHS_SHA = 'f4dd58b78121040b1f054c0f7a626b25f6ef8d39f3de044d3456ea7dea8a6a5e'


def inspect_interval(records, left, right):
    a, b = records[left][1:3]
    N.need(records[left][:3] == records[right][:3], 'equal outer gates')
    corrections = {}
    for index in range(left + 1, right):
        event = records[index]
        if event[0] in ('INIT', 'ERASE'):
            if event[1] in (a, b):
                return None, 'barrier'
        else:
            N.need(event[0] == 'ADD', 'scalar alphabet')
            destination, source, frame = event[1:]
            if destination == b and source == a:
                return None, 'reversed'
            if destination == b:
                corrections[index] = ('ADD', a, source, frame)
            elif source == a:
                corrections[index] = ('ADD', destination, b, frame)
    return corrections, None


def rewrite(records, left, right, corrections):
    out = []
    for index, event in enumerate(records):
        if index in (left, right):
            continue
        out.append(event)
        if index in corrections:
            out.append(corrections[index])
    return out


def endpoint(records, width, owned):
    rows = [1 << index for index in range(width)]
    for event in records:
        op, destination = event[:2]
        if op == 'ADD':
            N.need(destination != event[2], 'distinct ADD roles')
            rows[destination] ^= rows[event[2]]
        else:
            N.need(op in ('INIT', 'ERASE') and destination in owned, 'owned scalar event')
            N.need(op != 'INIT' or not rows[destination], 'whole-zero initialization')
            rows[destination] = 0
    return rows


def census(word, paths, frames):
    edges, dims = N.native_graph(frames)
    N.need(len(dims) == 645 and len(edges) == 52624, 'complete native graph')
    direct = {}
    for key, route in paths.items():
        N.need(len(route) == 1 and len(route[0]) == 3, 'retained singleton edge')
        a, b, rank = route[0]
        N.need(key == f'{a}:{b}' and edges[a, b] == rank, 'retained native admission')
        direct[a, b] = rank
    N.need(len(direct) == 2369, 'retained edge inventory')
    distances = N.metric(edges, dims)
    scalars = [tuple(event) for event in word['records'] if event[0] not in ('Q', 'ZERO_Q')]
    width, owned = len(word['start']), set(word['owned'])
    N.need(width == 685 and len(scalars) == 11930, 'frozen scalar shape')
    expected = [0 if i in owned else (1 << i) ^ ((1 << (i - 111)) if 111 <= i < 222 else 0)
                for i in range(width)]
    N.need(endpoint(scalars, width, owned) == expected, 'source all-column endpoint')
    base = Counter(event[4] for event in word['records'] if event[0] == 'Q')
    baseline, _, new_paid = N.invoice(scalars, word['start'], word['final'], owned, distances, direct)
    N.need(base == baseline and not new_paid, 'source paid invoice exact attainer')
    groups = defaultdict(list)
    for index, event in enumerate(scalars):
        if event[0] == 'ADD':
            groups[event[1:3]].append(index)
    outcomes, counts, shapes, neutral = [], Counter(), Counter(), []
    for gate, positions in sorted(groups.items()):
        for offset, left in enumerate(positions):
            for right in positions[offset + 1:]:
                counts['equal_pairs'] += 1
                corrections, rejection = inspect_interval(scalars, left, right)
                if rejection:
                    counts[rejection] += 1
                    continue
                counts['eligible'] += 1
                changed = rewrite(scalars, left, right, corrections)
                N.need(endpoint(changed, width, owned) == expected, 'rewritten all-column endpoint')
                histogram, requests, new_paid = N.invoice(changed, word['start'], word['final'], owned, distances, direct)
                delta = N.signed_delta(histogram, base)
                certificate = N.partition(delta)
                sign = N.check_partition(delta, certificate)
                counts[sign] += 1
                shapes[tuple(map(tuple, delta))] += 1
                row = {'first': left, 'last': right, 'gate': list(gate), 'contacts': len(corrections),
                       'delta': delta, 'sign': sign}
                if sign == 'zero':
                    N.need(not new_paid, 'original direct paid routes attain zero floor')
                    neutral.append({key: row[key] for key in ('first', 'last', 'gate', 'contacts')})
                outcomes.append(row)
    N.need(dict(counts) == {'equal_pairs': 2787, 'eligible': 2270, 'strict_loss': 2248, 'reversed': 517, 'zero': 22},
           'complete source-bound counts: ' + str(dict(counts)))
    N.need(len(shapes) == 211, 'all signed delta shapes')
    return {'schema': 'g20-native-all-path-one-step-v1',
            'source_sha256': {'word': WORD_SHA, 'paths': PATHS_SHA, 'frames_decoded': N.FRAME_SHA},
            'graph': {'frames': len(dims), 'directed_edges': len(edges),
                      'reachable_distinct_pairs': len(dims) * (len(dims) - 1),
                      'maximum_rank_distance': max(max(row.values()) for row in distances.values()),
                      'metric_sha256': N.metric_digest(distances),
                      'edge_rank_counts': {str(r): c for r, c in sorted(Counter(edges.values()).items())}},
            'counts': dict(sorted(counts.items())), 'base_paid': {str(r): c for r, c in sorted(base.items())},
            'neutral_first': neutral,
            'shapes': [{'delta': list(map(list, delta)), 'count': count, 'partition': N.partition(delta)}
                       for delta, count in sorted(shapes.items())], 'outcomes': outcomes}


def controls():
    accepted = []
    def reject(name, operation):
        try:
            operation()
        except (ValueError, KeyError):
            accepted.append(name)
        else:
            raise ValueError('accepted mutant: ' + name)
    distances = {0: {0: 0, 1: 1, 2: 3}, 1: {0: 1, 1: 0, 2: 2}, 2: {0: 3, 1: 2, 2: 0}}
    direct = {(0, 1): 1, (1, 2): 2}
    bill, _, new_paid = N.invoice([], [0], [2], set(), distances, direct)
    N.need(bill == {3: 1} and new_paid == {(0, 2)}, 'final public return charged')
    accepted.append('final_return_charged')
    bill, _, _ = N.invoice([('ERASE', 1, 0), ('ADD', 0, 1, 2)], [0, 0], [0, None], {1}, distances, direct)
    N.need(not bill, 'zero source omits both routes')
    accepted.append('zero_source_omission')
    bill, _, _ = N.invoice([('ERASE', 0, 0), ('ADD', 0, 1, 2), ('ERASE', 0, None)], [0, 0], [None, 2], {0}, distances, direct)
    N.need(bill == {3: 1}, 'zero destination route is free; source paid')
    accepted.append('zero_destination_free')
    reject('public_none_rejected', lambda: N.invoice([], [None], [2], set(), distances, direct))
    reject('dirty_owned_init_rejected', lambda: N.invoice([('INIT', 0, 1)], [0], [1], {0}, distances, direct))
    reject('dirty_owned_final_rejected', lambda: N.invoice([], [0], [None], {0}, distances, direct))
    reject('rank_zero_edge_rejected', lambda: N.metric({(0, 1): 0, (1, 0): 0}, {0, 1}))
    reject('rank_eight_edge_rejected', lambda: N.metric({(0, 1): 8, (1, 0): 8}, {0, 1}))
    valid = [[1, 2], [2, -1]]
    N.need(N.check_partition(valid, N.partition(valid)) == 'strict_loss', 'strict subadditivity control')
    reject('uncovered_negative_rejected', lambda: N.check_partition(valid, {'groups': [], 'left': [1, 1]}))
    reject('reused_positive_rejected', lambda: N.check_partition(valid, {'groups': [[2, [1, 1]]], 'left': [1]}))
    reject('underweight_group_rejected', lambda: N.check_partition([[1, 1], [2, -1]], {'groups': [[2, [1]]], 'left': []}))
    reject('boolean_rank_rejected', lambda: N.check_partition(valid, {'groups': [[2, [True, 1]]], 'left': []}))
    N.need(N.check_partition([], N.partition([])) == 'zero', 'zero attainer sign')
    accepted.append('zero_sign')
    return accepted


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--word', type=Path, required=True)
    parser.add_argument('--paths', type=Path, required=True)
    parser.add_argument('--frames', type=Path, required=True)
    parser.add_argument('--certificate', type=Path, required=True)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    word_bytes, paths_bytes = args.word.read_bytes(), args.paths.read_bytes()
    frames_bytes = gzip.decompress(args.frames.read_bytes())
    N.need(sha256(word_bytes).hexdigest() == WORD_SHA, 'pinned source word')
    N.need(sha256(paths_bytes).hexdigest() == PATHS_SHA, 'pinned retained paths')
    N.need(sha256(frames_bytes).hexdigest() == N.FRAME_SHA, 'pinned catalogue')
    result = census(json.loads(gzip.decompress(word_bytes)), json.loads(paths_bytes), json.loads(frames_bytes)['frames'])
    result['controls'] = controls()
    if args.write:
        raw = (json.dumps(result, sort_keys=True, indent=2) + '\n').encode()
        args.certificate.write_bytes(gzip.compress(raw, mtime=0) if args.certificate.suffix == '.gz' else raw)
    else:
        raw = args.certificate.read_bytes()
        expected = json.loads(gzip.decompress(raw) if args.certificate.suffix == '.gz' else raw)
        N.need(canonical(result) == canonical(expected), 'exact typed complete receipt')
    print(json.dumps({'status': 'PASS_G20_NATIVE_ONE_STEP_FLOOR', 'graph': result['graph'],
                      'counts': result['counts'], 'controls': result['controls']}, sort_keys=True))


if __name__ == '__main__':
    main()
