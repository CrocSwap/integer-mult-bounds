#!/usr/bin/env python3
"""Test the physical hole condition at the retained transfer cuts."""

from collections import Counter, defaultdict, deque
import gzip
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
LANES = HERE.parent.parent
PAYLOAD = LANES / 'history-encoding/independent-skeleton-20261018/INDEPENDENT-SKELETON-PROGRAMS.json.gz'
COMPILER = LANES / 'new-native-recipes-20261017/sources/vendor/clifford/clifford_exact.py'
PINS = {
    'payload_decompressed': '8fe1147e5cb80d9f1d9ef309b0ee6f42b1a64cc5ebabd19b818623c246c9fd64',
    'compiler': '2982ead07721e83358dc67c6f49c2b4c16a236a6bebdfd72f58221be1f5d0962',
}


def need(value, message):
    if not value:
        raise AssertionError(message)


def matmul(a, b, ce):
    bt = ce.transpose(b, 9)
    return tuple(sum(ce.parity(row & col) << j for j, col in enumerate(bt)) for row in a)


def maximum_matching(edges):
    adjacency = defaultdict(list)
    for s, t in sorted(edges):
        adjacency[s].append(t)
    left, right = {}, {}
    for start in range(112):
        queue, seen, pred, end = deque([start]), {start}, {}, None
        while queue and end is None:
            s = queue.popleft()
            for t in adjacency[s]:
                if t in pred:
                    continue
                pred[t] = s
                if t not in right:
                    end = t
                    break
                if right[t] not in seen:
                    seen.add(right[t])
                    queue.append(right[t])
        if end is None:
            continue
        while True:
            s, t = pred[end], end
            old = left.get(s)
            left[s], right[t] = t, s
            if old is None:
                break
            end = old
    return left


def check_provider(provider, ce):
    canonical = provider['canonical']
    ports = canonical['ports']
    need(len(ports) == 112, 'Port count')
    frames = list(canonical['start'])
    history = [[] for _ in frames]
    identity = tuple(1 << j for j in range(9))
    warp_rows = {row['op']: ce.transpose(tuple(row['G_columns']), 9) for row in canonical['warps']}
    warp_rows.update({-symbol: ce.inv(g, 9) for symbol, g in list(warp_rows.items())})
    prefixes = [identity for _ in frames]
    factors = [ce.transpose(ce.basis_extend(basis, 9), 9) for basis in canonical['frames']]
    factor_inverse = [ce.inv(g, 9) for g in factors]
    active = False
    graph, boundary_graph, pairs_seen = {}, {}, set()
    flag_checks = Counter()
    stats = Counter()
    cache = {}
    events = provider['programs']['forward']
    for index, event in enumerate(events):
        tag = event[0]
        # Remove only the emitted transfer. The retained native path stays fixed.
        if tag == 'monomial_view' or (tag == 'scalar' and event[1][0] == 'add'):
            continue
        if event[:2] == ['phase', 'A']:
            active = True
        elif event[:2] == ['phase', 'exit_adapters']:
            active = False
        if tag == 'climb':
            target, old, new = event[2:5]
            need(frames[target] == old, 'Climb frame')
            frames[target] = new
        elif tag == 'warp':
            token, symbol, old, new = event[1:5]
            need(token[0] == 'L', 'Live warp')
            target = token[1]
            need(frames[target] == old, 'Warp frame')
            frames[target] = new
            prefixes[target] = matmul(warp_rows[symbol], prefixes[target], ce)
            if history[target] and history[target][-1] == -symbol:
                history[target].pop()
            else:
                history[target].append(symbol)
        if not active or tag not in ('phase', 'climb', 'warp'):
            continue
        targets = defaultdict(list)
        for t in range(112):
            target = 112 + t
            rank = len(canonical['frames'][frames[target]])
            if 1 <= rank <= 8:
                targets[rank].append(t)
        for s in range(112):
            u = frames[s]
            rank = len(canonical['frames'][u])
            if not 1 <= rank <= 8:
                continue
            if not history[s]:
                flag_checks['source_tests'] += 1
                need(ce.rank(canonical['frames'][u] + [ports[s]]) == rank, 'Source line in frame')
            for t in targets[rank]:
                target, v = 112 + t, frames[112 + t]
                if not history[target]:
                    flag_checks['target_tests'] += 1
                    need(all(ce.parity(w & ports[t]) == 0 for w in canonical['frames'][v]), 'Target frame in hole')
                key = (s, t, u, v, prefixes[s], prefixes[target])
                if key in pairs_seen:
                    continue
                pairs_seen.add(key)
                stats['cut_frame_prefix_cases'] += 1
                record = {'source': s, 'target': t, 'cut': index, 'rank': rank,
                          'source_frame': u, 'target_frame': v,
                          'source_warps': list(history[s]), 'target_warps': list(history[target])}
                graph.setdefault((s, t), record)
                # G_E = W_t^-1 G_v G_u^-1 W_s, in mathematical order.
                pkey = (u, v, prefixes[s], prefixes[target])
                if pkey not in cache:
                    g = matmul(factor_inverse[u], prefixes[s], ce)
                    g = matmul(factors[v], g, ce)
                    g = matmul(ce.inv(prefixes[target], 9), g, ce)
                    cache[pkey] = ce.transpose(g, 9)
                need(ce.parity(ports[s] & ports[s]) == 1 and ce.parity(ports[t] & ports[t]) == 1, 'Odd lines')
                if ce.mv(cache[pkey], ports[t]) == ports[s]:
                    boundary_graph.setdefault((s, t), record)
    need(frames == canonical['final'], 'Final frames')
    need(all(not w for w in history), 'All logical warp histories close')
    need(all(g == identity for g in prefixes), 'All binary prefix maps close')
    matching = maximum_matching(boundary_graph)
    return {
        'all_equal_rank_edges': len(graph), 'hole_compatible_edges': len(boundary_graph),
        'hole_compatible_matching_size': len(matching), 'stats': dict(stats),
        'empty_history_flag_checks': dict(flag_checks),
        'matching': [boundary_graph[s, t] for s, t in sorted(matching.items())],
        'hole_compatible_edge_records': list(boundary_graph.values()),
    }


def main():
    raw = gzip.decompress(PAYLOAD.read_bytes())
    need(sha256(raw).hexdigest() == PINS['payload_decompressed'], 'Payload pin')
    need(sha256(COMPILER.read_bytes()).hexdigest() == PINS['compiler'], 'Compiler pin')
    spec = importlib.util.spec_from_file_location('monomial_compiler_exact', COMPILER)
    ce = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = ce
    spec.loader.exec_module(ce)
    data = json.loads(raw)
    result = {'pins': PINS, 'providers': {name: check_provider(p, ce) for name, p in data['providers'].items()}}
    result['checker_sha256'] = sha256(Path(__file__).read_bytes()).hexdigest()
    result['scope'] = 'Canonical equal-rank K_v K_u^-1 transfers with all actual signed prefix warp histories. A binary boundary screen, not a new native word.'
    (HERE / 'WARPED-MATCHING.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    for name, r in result['providers'].items():
        print(name, r['all_equal_rank_edges'], r['hole_compatible_edges'], r['hole_compatible_matching_size'], r['stats'])


if __name__ == '__main__':
    main()
