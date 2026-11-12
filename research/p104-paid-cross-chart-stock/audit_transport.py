"""Independent every-contact, reverse reachability and directed price audit."""
from collections import Counter, defaultdict
from fractions import Fraction as Q
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import argparse
import gzip
import json
from itertools import permutations


PINS = {
    'public/native/WORD.json.gz': 'c1caec11ca3ee264ef03018dd91037eac10c3e28950c4c525ee1b4bf5ee210e2',
    'public/native/RESULT.json': '59080d75e7281b1a8c1353930917fd15869ad747ff4200948898f78f11c14089',
    'public/caller/CALLER.json': '255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc',
    'round18/complex/audit_stock.py': 'e942cbf0e3844e2180827a1598c31bb54f31b87d8b2dbcc52ca315f1b81c5c80',
    'round11/frontier/independent_adapter_price.py': '2a46157d156bdfc0e892289005fd3fb7c23708de48c9abd90c1914b0372bc726',
}


def checked(root, key):
    path = root / key.removeprefix('public/')
    data = path.read_bytes()
    if sha256(data).hexdigest() != PINS[key]:
        raise ValueError(f'SHA-256 mismatch: {key}')
    return path, data


def load(root, key):
    path, _ = checked(root, key)
    spec = spec_from_file_location(path.stem, path)
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def every_contact(word, selected, reverse):
    events = word['program']
    p = word['public']
    start = word['final' if reverse else 'initial']
    at = [*start, *([None] * word['owned_fields'])]
    rows = [{i: Q(1)} for i in range(p)] + [{} for _ in range(word['owned_fields'])]
    saved = defaultdict(list)

    def record(j, cut):
        if at[j] in selected and rows[j]:
            saved[at[j]].append((cut, rows[j]))

    def add(j, s, c):
        a, b = rows[j], rows[s]
        rows[j] = {k: v for k in a.keys() | b.keys() if (v := a.get(k, 0) + c * b.get(k, 0))}

    for j in range(p):
        record(j, len(events) if reverse else 0)
    for i in reversed(range(len(events))) if reverse else range(len(events)):
        op, j, *a = events[i]
        touched = (j, a[0]) if op in ('ADD', 'COPY') else (j,)
        for role in touched:
            record(role, i + reverse)
        if op == 'MOVE':
            f, g = a[:2]
            if reverse:
                f, g = g, f
            assert at[j] == f
            at[j] = g
        elif op == 'SCALE':
            assert at[j] == a[-1]
            rows[j] = {k: Q(a[0]) * v for k, v in rows[j].items()}
        elif op == 'ADD':
            s = a[0]
            assert at[j] == at[s] == a[-1]
            add(s, j, Q(a[1])) if reverse else add(j, s, Q(a[1]))
        elif op == 'COPY':
            s = a[0]
            assert at[j] == at[s] == a[-1]
            if reverse:
                add(s, j, Q(a[1]))
                rows[j] = {p + i: Q(1)}
            else:
                rows[j] = {k: Q(a[1]) * v for k, v in rows[s].items()}
        else:
            assert op in ('INIT', 'CLEAR')
            create = (op == 'INIT') != reverse
            assert at[j] == (None if create else a[0])
            at[j] = a[0] if create else None
            rows[j] = {}
        for role in touched:
            record(role, i + (not reverse))
    assert at == [*word['initial' if reverse else 'final'], *([None] * word['owned_fields'])]
    return saved


def ordered_cut_controls():
    """Corroborate the chart-order argument, including parallel payloads."""
    charts = range(3)
    possible = [(a, b) for a in charts for b in charts if a != b]

    def check(arcs, order):
        position = {chart: index for index, chart in enumerate(order)}
        forward = sorted(((a, b) for a, b in arcs if position[a] < position[b]),
                         key=lambda edge: position[edge[0]])
        reverse_count = sum(position[a] > position[b] for a, b in arcs)
        assert len(forward) + reverse_count == len(arcs)
        assert 2 * max(len(forward), reverse_count) >= len(arcs)
        for row, (_, destination) in enumerate(forward):
            for col, (source, _) in enumerate(forward):
                if source == destination:
                    assert col > row
        return len(forward)

    for mask in range(1 << len(possible)):
        arcs = [edge for index, edge in enumerate(possible) if mask & (1 << index)]
        for order in permutations(charts):
            check(arcs, order)
    assert check([(0, 1), (0, 1), (1, 2), (2, 0)], charts) == 3
    # A same-chart lane could contribute its own diagonal in the cut network.
    try:
        check([(1, 1)], charts)
    except AssertionError:
        pass
    else:
        raise AssertionError('same-chart loop must fail the transport-only control')
    return {'simple_graphs': 64, 'orders': 6, 'parallel_lane_control': True,
            'same_chart_loop_rejected': True}


def run(inputs, deps, receipt, ordered_cut=False):
    data = receipt.read_bytes()
    r = json.loads(data)
    w = json.loads(gzip.decompress(checked(inputs, 'public/native/WORD.json.gz')[1]))
    result = json.loads(checked(inputs, 'public/native/RESULT.json')[1])
    caller = json.loads(checked(inputs, 'public/caller/CALLER.json')[1])
    ap = load(deps, 'round11/frontier/independent_adapter_price.py')
    alg = load(deps, 'round18/complex/audit_stock.py')
    spans = [frozenset(ap.chart_span(frame)) for frame in w['frames']]
    rank = [len(f) for f in w['frames']]
    first = {space: f for f, space in reversed(list(enumerate(spans)))}
    alias = [f for f, space in enumerate(spans) if first[space] != f]
    assert [[first[spans[f]], f] for f in alias] == r['geometry']['aliases']
    reps = sorted(first.values())
    reverse_reach = {f: {f} for f in reps}
    down = []
    movement = Counter()
    carrier_moves = Counter()
    for i in reversed(range(len(w['program']))):
        op, j, *a = w['program'][i]
        if op != 'MOVE':
            continue
        f, g, owned = a
        assert (spans[f] > spans[g] and owned) or spans[f] < spans[g]
        reverse_reach[first[spans[f]]].update(reverse_reach[first[spans[g]]])
        if rank[f] > rank[g]:
            down.append([i, j, f, g, owned])
        movement[abs(rank[f] - rank[g])] += 1
        carrier_moves[j] += 1
    actual_pairs = {(f, g) for f, gs in reverse_reach.items() for g in gs if f != g and rank[f] == rank[g]}
    assert actual_pairs == {tuple(row) for row in r['geometry']['all_old_pairs']}
    assert down[::-1] == r['geometry']['owned_downward_moves']
    assert len(down) * 4 == r['cross_split_cap']
    capacity = len(down) * (2 if ordered_cut else 4)
    assert sum(movement.values()) == r['geometry']['old_paid_moves']
    intervals = {kind: sum(n * (n + 1) // 2 for j, n in carrier_moves.items()
                           if (j >= w['public']) == (kind == 'owned')) for kind in ('public', 'owned')}
    assert intervals == r['geometry']['all_same_carrier_ordered_intervals']
    main = set(w['live']) | {j + 112 for j in w['live']} | set(w['hosted']['X2']) | set(w['hosted']['Y2'])
    origins = {j: (a, b) for j, (a, b) in enumerate(zip(w['initial'], w['final'], strict=True)) if j not in main}
    group = {j for j, ab in origins.items() if ab == (3, 127)}
    interior = defaultdict(set)
    for op, j, *a in w['program']:
        if op == 'MOVE' and j in origins:
            entrance, terminal = origins[j]
            g = a[1]
            if spans[entrance] < spans[g] < spans[terminal]:
                interior[j].add(g)
    pending = set(r['direct_pending'])
    assert len(pending) + len(r['direct_checked']) == len(r['direct_order'])
    assert all(x['capacity'] == x['pair_rank'] == 0 for x in r['direct_checked'])
    pair_tests = [((x['source'],), (x['target'],), x['event'], x) for x in r['downward_timed_checked']]
    pair_tests += [(tuple(x['members']), tuple(x['members']), None, x) for x in r['direct_checked']]
    selected = {f for fs, gs, _, _ in pair_tests for f in fs + gs}
    [(copy_cut, _, _, _, copy_chart)] = r['geometry']['copy_guards']
    selected.add(copy_chart)
    prefix = every_contact(w, selected, False)
    suffix = every_contact(w, selected, True)
    guard_coord = w['public'] + copy_cut
    assert any(cut == copy_cut and row == {guard_coord: Q(1)} for cut, row in suffix[copy_chart])
    windows_with_copy_guard = 0
    for fs, gs, t, primary in pair_tests:
        left = [row for f in fs for clock, row in prefix[f] if t is None or clock <= t]
        right = [row for g in gs for clock, row in suffix[g] if t is None or clock >= t + 1]
        windows_with_copy_guard += any(guard_coord in row for row in right)
        a, outside_a = alg.outside_image(left, group)
        b, outside_b = alg.outside_image(right, group)
        assert (outside_a, outside_b) == (primary['prefix_outside_rank'], primary['suffix_outside_rank'])
        for expected, basis in ((primary['prefix_group'], a), (primary['suffix_group'], b)):
            assert len(expected) == len(basis)
            assert all(alg.insertion({int(k): Q(v) for k, v in row.items()}, basis, None) == {} for row in expected)
        assert primary['pair_rank'] == 0
        assert all(not sum(x * v.get(j, 0) for j, x in u.items()) for u in a.values() for v in b.values())

    stages = 0
    paid = Counter()
    for e in caller['events']:
        if e[0] == 'J':
            stages += 1
            paid.update(movement)
        elif e[1] == 'QUERY':
            paid[1] += len(caller['types'][e[0]]['ports'])
        elif e[1] in ('IDLE_ONE', 'IDLE_ODD'):
            paid[8 * len(e[3]) + (e[1] == 'IDLE_ODD')] += len(caller['types'][e[0]]['ports'])
    targets = Counter(rank[b] - rank[a] for a, b in origins.values())
    targets = Counter({k: v * stages for k, v in targets.items()})
    for spec in caller['types'].values():
        for _, _, *body in spec['diagonal']:
            targets[1 + 8 * sum(body)] += len(spec['ports'])
    assert {str(k): n for k, n in targets.items()} == result['price']['after']['T']
    assert {str(k): n for k, n in paid.items()} == result['price']['after']['P']

    def dot(h):
        lo = hi = Q()
        for rank, count in h.items():
            a, b = ap.price(rank)
            lo += count * (a if count >= 0 else b)
            hi += count * (b if count >= 0 else a)
        return lo, hi

    def split(r, d):
        h = Counter((d, r - d))
        h[r] -= 1
        return tuple(stages * v for v in dot(h))

    h = targets.copy()
    h.subtract(paid)
    old = dot(h)
    small = [Q(), Q()]
    possible = {}
    coframed = {}
    for j, (a, b) in origins.items():
        d = {f: min(rank[f] - rank[a], rank[b] - rank[f]) for f in interior[j]}
        if j not in group and d:
            for i, q in enumerate(split(rank[b] - rank[a], max(d.values()))):
                small[i] += q
        cross = [v for f, v in d.items() if any(g != first[spans[f]] and rank[f] == rank[g]
                 and spans[a] < spans[g] < spans[b] for g in reverse_reach[first[spans[f]]])]
        if cross:
            possible[j] = max(cross)
        if j in group:
            coframed[j] = max((v for f, v in d.items() if first[spans[f]] in pending), default=0)
    assert len(possible) == r['cross_owner_count']
    layers = {}
    for d in range(1, 5):
        direct = {j for j in group if coframed[j] >= d}
        routed = {j for j in group if possible.get(j, 0) >= d}
        layers[d] = len(direct) + min(capacity, len(routed - direct))
    prior_layers = {int(k): v for k, v in r['final']['combined_rank9_layers'].items()}
    if ordered_cut:
        assert all(layers[d] <= prior_layers[d] for d in layers)
    else:
        assert layers == prior_layers
    weights = [None] + [layers[d] - layers.get(d + 1, 0) for d in range(1, 5)]
    bounds = tuple(old[i] + small[i] + sum(weights[d] * split(9, d)[i] for d in range(1, 5)) for i in range(2))
    assert bounds[1] <= Q(r['final']['raw_upper']) < 0
    order_evidence = {}
    if ordered_cut:
        assert bounds[1] < Q(r['final']['raw_upper'])
        saving = tuple(bounds[i] - old[i] for i in range(2))
        order_evidence = dict(ordered_cut_capacity=capacity,
                              ordered_cut_controls=ordered_cut_controls(),
                              optimistic_saving_interval=ap.encode(saving),
                              benchmark_moment_interval=ap.encode(old),
                              rounded_directed_upper=ap.encode(bounds)[1])
    return dict(status='PASS_EVERY_CONTACT_REVERSE_REACHABILITY_INVOICE_AND_OWNER_PRICE',
                **order_evidence,
                pins={**PINS, 'round19/complex/TRANSPORT.json': sha256(data).hexdigest()},
                productive_targets=sum(targets.values()), paid_total=sum(paid.values()), stages=stages,
                reverse_reach_endpoint_pairs=len(actual_pairs), down_edges=len(down),
                independently_tested_pairs=len(pair_tests), pairings_containing_copy_guard=windows_with_copy_guard,
                copy_guard_seen_at_literal_cut=copy_cut,
                independent_combined_rank9_layers=layers, independently_bounded_raw_margin=ap.encode(bounds),
                pending_priced_at_ideal=len(pending))


if __name__ == '__main__':
    assert __debug__
    p = argparse.ArgumentParser(description=__doc__)
    for name in ('inputs', 'deps', 'receipt'):
        p.add_argument(name, type=Path)
    p.add_argument('--ordered-cut', action='store_true')
    print(json.dumps(run(**vars(p.parse_args())), indent=2, sort_keys=True))
