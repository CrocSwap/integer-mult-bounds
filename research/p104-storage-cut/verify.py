#!/usr/bin/env python3
"""Exact frame-cut certificate; no predecessor executable or network imports."""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict, deque
from copy import deepcopy
from fractions import Fraction
import hashlib
import importlib.util
import json
from pathlib import Path

P = Path(__file__).resolve().parent
ROOT = P.parents[1]
WITNESS = 'research/p104-native-channel/inputs/LOWRANK-WITNESS.json'
CUT = (2463, 2472, 2479, 2487, 2495, 2503, 2510, 2518)


def need(ok, message):
    if not ok:
        raise ValueError(message)


def basis(vectors):
    """Unique reduced basis using high-bit pivots, independent of presentation."""
    need(isinstance(vectors, (list, tuple)), 'basis list')
    rows = {}
    for value in vectors:
        need(type(value) is int and 0 <= value < 512, 'nine-bit generator')
        x = value
        while x:
            p = x.bit_length() - 1
            if p in rows:
                x ^= rows[p]
            else:
                rows[p] = x
                break
    for p in sorted(rows):
        for q in sorted(rows):
            if q > p and (rows[q] >> p) & 1:
                rows[q] ^= rows[p]
    return tuple(rows[p] for p in sorted(rows, reverse=True))


def contains(a, b):
    return basis(a + b) == a


def span(a):
    out = [0]
    for x in a:
        out += [v ^ x for v in out]
    return tuple(sorted(out))


def parse(w):
    need(set(w) == {'initial_frames', 'final_frames', 'program'}, 'witness keys')
    roles = {f'{s}{i}' for s, n in [('X', 104), ('Y', 104), ('Q', 8), ('G', 32), ('D', 32)] for i in range(n)}
    need(set(w['initial_frames']) == roles == set(w['final_frames']), 'persistent inventory')
    live = {r: basis(v) for r, v in w['initial_frames'].items()}
    initial = dict(live)
    final = {r: basis(v) for r, v in w['final_frames'].items()}
    need(len({initial[f'X{i}'] for i in range(104)}) == 104, 'distinct entrances')
    need(all(len(initial[f'X{i}']) == 1 for i in range(104)), 'source line dimensions')
    need(all(not initial[r] for r in roles if not r.startswith('X')), 'other entrances')
    need(len({final[f'Y{i}'] for i in range(104)}) == 104, 'distinct target exits')
    need(all(len(final[f'Y{i}']) == 8 for i in range(104)), 'target dimensions')
    frames = set(live.values()) | set(final.values())
    arrows = []
    counts = Counter()
    for i, e in enumerate(w['program']):
        need(isinstance(e, list) and bool(e), 'event list')
        op = e[0]
        counts[op] += 1
        if op == 'transport':
            need(len(e) == 5, 'transport arity')
            _, r, a, b, cost = e
            a, b = basis(a), basis(b)
            need(r in live and live[r] == a, 'transport source frame')
            need(a != b and (contains(a, b) or contains(b, a)), 'strict nested transport')
            need(type(cost) is int and cost == abs(len(a)-len(b)), 'native rank declaration')
            arrows.append((i, a, b, cost, r))
            live[r] = b
            frames |= {a, b}
        elif op == 'zero':
            need(len(e) == 3 and e[1] == 'C' and 'C' not in live, 'private allocation')
            live['C'] = basis(e[2]); frames.add(live['C'])
        elif op == 'erase':
            need(len(e) == 3 and e[1] == 'C' and 'C' in live, 'private disposal')
            need(live['C'] == basis(e[2]), 'disposal frame')
            del live['C']
        elif op == 'copy':
            need(len(e) == 4, 'copy arity')
            _, t, s, f = e
            need(t == 'C' and s in live and t in live, 'copy roles')
            need(live[t] == live[s] == basis(f), 'copy common frame')
        elif op == 'add':
            need(len(e) == 5, 'addition arity')
            _, t, s, c, f = e
            need(t in live and s in live and t != s, 'addition roles')
            need(live[t] == live[s] == basis(f), 'addition common frame')
            Fraction(c)
        else:
            raise ValueError('unknown event')
    need(live == final, 'final frames and lifetimes')
    return frames, arrows, {initial[f'X{i}'] for i in range(104)}, {final[f'Y{i}'] for i in range(104)}, dict(counts)


def reachable(starts, arrows, reverse=False):
    graph = defaultdict(set)
    for _, a, b, *_ in arrows:
        graph[b if reverse else a].add(a if reverse else b)
    seen = set(starts); todo = deque(starts)
    while todo:
        for b in graph[todo.popleft()]:
            if b not in seen:
                seen.add(b); todo.append(b)
    return seen


def require_cut(starts, targets, arrows):
    r = reachable(starts, arrows)
    need(not r & targets, 'static source-target cut failed')
    return r


def reject(call, text):
    try:
        call()
    except ValueError as e:
        need(text in str(e), 'wrong rejecting guard: ' + str(e))
        return
    raise RuntimeError('negative control unexpectedly accepted: ' + text)


def analyze(w):
    frames, edges, starts, targets, counts = parse(w)
    omitted = [e for e in edges if e[0] in CUT]
    need(tuple(e[0] for e in omitted) == CUT, 'eight fixed descent occurrences')
    need(all(e[3:] == (7, 'C') and len(e[1]) == 8 and len(e[2]) == 1 for e in omitted), 'descent signature')
    kept = [e for e in edges if e[0] not in CUT]
    r = require_cut(starts, targets, kept)
    t = reachable(targets, kept, reverse=True)
    need(not r & t and r | t == frames, 'complete unique partition')
    need(all(e[1] in r and e[2] in t for e in omitted), 'all omitted edges cross cut')
    transition_counts = Counter(('R' if a in r else 'T') + ('R' if b in r else 'T') for _, a, b, *_ in kept)
    restored = [len(reachable(starts, kept + [e]) & targets) for e in omitted]
    # A valid new monotone helper path crosses the cut, yet all its rank is
    # endpoint progress. This is a control against a false excess-cost claim.
    full = basis([1 << i for i in range(9)])
    pair = next((a, b) for a in sorted(starts) for b in sorted(targets) if contains(b, a))
    a, b = pair
    need(() in t and full in r and a in r and b in t, 'productive crossing endpoints')
    need(1 + (len(b)-len(a)) + (9-len(b)) == 9, 'productive helper progress')
    mass = sum(e[3] for e in edges)
    boundary = sum(len(basis(w['final_frames'][role])) - len(basis(f)) for role, f in w['initial_frames'].items())
    need(mass == 2368 and boundary == 2312, 'inherited rank and endpoint mass')
    idle = 72*832 - 9*boundary
    paid = 9*(mass+96)+idle
    need(idle == 39096 and paid == 61272, 'conditional invoice arithmetic')
    return {
        'events': len(w['program']), 'event_counts': counts,
        'frames': len(frames), 'transport_occurrences': len(edges),
        'retained_occurrences': len(kept),
        'retained_distinct_arrows': len({(e[1], e[2]) for e in kept}),
        'source_frames': len(starts), 'target_frames': len(targets),
        'reachable_bases': [list(x) for x in sorted(r)],
        'target_ancestor_bases': [list(x) for x in sorted(t)],
        'reachable_dimensions': dict(sorted(Counter(map(len, r)).items())),
        'target_ancestor_dimensions': dict(sorted(Counter(map(len, t)).items())),
        'retained_partition_arrows': dict(sorted(transition_counts.items())),
        'cut_event_indices': list(CUT), 'cut_native_ranks': [e[3] for e in omitted],
        'reachable_targets_without_cut': len(r & targets),
        'targets_after_each_single_restore': restored,
        'targets_after_all_restores': len(reachable(starts, edges) & targets),
        'added_whole_array_transport_floor': len(targets)-len(omitted),
        'inherited_local_profile': dict(sorted(Counter(e[3] for e in edges).items())),
        'inherited_rank_mass': mass, 'persistent_endpoint_progress': boundary,
        'conditional_no_new_progress_invoice': {
            'assumptions': 'm=73 W=832 N=9; unchanged old idle requirement; added transports earn no new coverage credit',
            'old_idle_mass': idle, 'completed_mass_lower': paid, 'capacity': 73*832,
            'zero_saving_moment_lower': str(Fraction(paid, 73*832)),
            'scope': 'Conditional comparison only; does not apply automatically to new monotone helper inventories.'
        },
        'productive_path_counterexample': {
            'source_role': next(k for k, v in w['initial_frames'].items() if k.startswith('X') and basis(v) == a),
            'target_role': next(k for k, v in w['final_frames'].items() if k.startswith('Y') and basis(v) == b),
            'frames': [[], list(a), list(b), list(full)],
            'native_ranks': [1, 7, 1], 'rank_mass': 9, 'endpoint_progress': 9,
            'scope': 'Legal nested frame path only; not a complete dirty-restored identity supplier.'
        },
    }


def controls(w):
    frames, edges, starts, targets, _ = parse(w)
    kept = [e for e in edges if e[0] not in CUT]
    # Actual separation guard, beyond a source hash/schema check.
    for e in [x for x in edges if x[0] in CUT]:
        reject(lambda e=e: require_cut(starts, targets, kept+[e]), 'static source-target cut failed')
    full = basis([1 << i for i in range(9)])
    bypass = (99999, full, sorted(targets)[0], 1, 'new')
    reject(lambda: require_cut(starts, targets, kept+[bypass]), 'static source-target cut failed')
    bad = deepcopy(w); bad['program'][2463][2] = []
    reject(lambda: parse(bad), 'transport source frame')
    bad = deepcopy(w); bad['program'][2463][4] = 1
    reject(lambda: parse(bad), 'native rank declaration')
    bad = deepcopy(w); bad['program'][0][-1] = [1]
    reject(lambda: parse(bad), 'addition common frame')
    bad = deepcopy(w); bad['program'][0][0] = 'free_cross_chart'
    reject(lambda: parse(bad), 'unknown event')
    equivalent = deepcopy(w)
    for field in ['initial_frames', 'final_frames']:
        for k, v in equivalent[field].items():
            equivalent[field][k] = list(reversed(v)) + [0] + v[:1]
    for e in equivalent['program']:
        indices = {'transport': (2, 3), 'zero': (2,), 'erase': (2,), 'copy': (3,), 'add': (4,)}[e[0]]
        for i in indices:
            v=e[i]; e[i]=list(reversed(v))+[0]+v[:1]
    need(analyze(equivalent) == analyze(w), 'equivalent basis presentation')
    return {'restored_descent_rejections': 8, 'new_full_to_target_bypass_rejected': True,
            'bad_source_frame_rejected': True, 'bad_native_rank_rejected': True,
            'bad_common_frame_rejected': True, 'unknown_operation_rejected': True,
            'redundant_permuted_basis_accepted': True}


def load_sources():
    sources = json.loads((P/'SOURCES.json').read_text())
    for item in sources['files']:
        if item['usage'] == 'input':
            data=(ROOT/item['path']).read_bytes()
            need(hashlib.sha256(data).hexdigest() == item['sha256'], 'source pin: '+item['path'])
    return json.loads((ROOT/WITNESS).read_text())


def compare_oracle(w, result, independent):
    def digest(x):
        return hashlib.sha256(json.dumps(x, separators=(',', ':'), sort_keys=True).encode('ascii')).hexdigest()
    forward = [list(x) for x in sorted(span(tuple(b)) for b in result['reachable_bases'])]
    backward = [list(x) for x in sorted(span(tuple(b)) for b in result['target_ancestor_bases'])]
    need(independent['reachable_frames'] == forward, 'independent source partition')
    need(independent['coreachable_frames'] == backward == independent['unreachable_frames'], 'independent target partition')
    need(independent['partition_complete'] and independent['unclassified_count'] == 0, 'independent coverage')
    _, arrows, _, _, _ = parse(w)
    signatures = [[i, role, cost, list(span(a)), list(span(b))] for i, a, b, cost, role in arrows]
    need(independent['transport_event_signatures_sha256'] == digest(signatures), 'independent every-transport signature')
    pairs = [('vertex_count', 'frames'), ('transport_occurrences', 'transport_occurrences'),
             ('source_frame_count', 'source_frames'), ('target_frame_count', 'target_frames'),
             ('retained_transport_occurrences', 'retained_occurrences'),
             ('distinct_retained_arrows', 'retained_distinct_arrows'),
             ('reachable_target_count', 'reachable_targets_without_cut'),
             ('retained_arrow_directions', 'retained_partition_arrows'),
             ('all_restored_target_count', 'targets_after_all_restores')]
    for a, b in pairs:
        need(independent[a] == result[b], 'independent count: '+a)
    need([independent['edge_restoration_target_counts'][str(i)] for i in CUT] == result['targets_after_each_single_restore'], 'independent restoration controls')
    need(independent['reachable_frames_sha256'] == digest(forward), 'independent forward digest')
    need(independent['coreachable_frames_sha256'] == digest(backward), 'independent backward digest')
    return {k: independent[k] for k in ['transport_event_signatures_sha256', 'reachable_frames_sha256',
            'coreachable_frames_sha256', 'distinct_retained_arrow_directions', 'partition_complete']}


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--write', type=Path); args=ap.parse_args()
    w=load_sources(); result=analyze(w)
    spec=importlib.util.spec_from_file_location('p104_storage_oracle', P/'oracle.py')
    oracle=importlib.util.module_from_spec(spec); spec.loader.exec_module(oracle)
    independent=oracle.analyze(w)
    result['independent_oracle'] = compare_oracle(w, result, independent)
    result['controls']=controls(w)
    result['status']='PASS_P104_STORAGE_CUT_no_new_kappa'
    rendered=json.dumps(result, indent=2, sort_keys=True)+'\n'
    if args.write:
        with args.write.open('x') as f: f.write(rendered)
    else:
        need(json.loads((P/'RESULT.json').read_text()) == json.loads(rendered), 'fixed receipt mismatch')
    print(result['status'], '444 frames; 222/222 partition; >=96 added array transports; no automatic excess-cost claim')


if __name__ == '__main__':
    main()
