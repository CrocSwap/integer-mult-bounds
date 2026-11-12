"""Round 19 aggregate directed cross-chart transport and direct stock bound."""
from collections import Counter, defaultdict
from fractions import Fraction as Q
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from time import monotonic
import argparse
import json

PINS = {
    'round13/alternative/reprice.py': '97f4524d11a08cd3a09ceb9abc6b90f45ca579ac1c529a176b80a67201ecd90a',
    'round18/complex/stock_gate.py': '10bd50305623c1f4f276303c266f062d66136d510b4653b724b2dc7cf891352e',
    'round18/complex/STOCK.json': '9198aaa1e8f10ac0616f3810de013fc0cd86b72b7eb7dd23e7dc298c646baa74',
    'round18/complex/AUDIT.json': '40b437442d1a328f4e352cd67497a2a60ea938f4db75aa9cd4cd594d565c85b6',
    'round18/complex-free/FREE.json': '15b10a87d2861de84fca48efd62f499a7a3dd9824f10e11893a8488359a9df19',
    'round18/complex-free/AUDIT.json': '3784a06f0c6a62e083a3e67fcf8339ebeb29a68f446d76a2ebb93df835a27cc1',
}


def check(root, key):
    path = root / key
    data = path.read_bytes()
    if sha256(data).hexdigest() != PINS[key]:
        raise ValueError(f'SHA-256 mismatch: {key}')
    return path, data


def load(root, key):
    path, _ = check(root, key)
    spec = spec_from_file_location(path.stem, path)
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def binary_key(basis):
    """Unique reduced echelon tuple, with largest set bit as the pivot."""
    rows = {}
    for x in basis:
        for p, row in sorted(rows.items(), reverse=True):
            if x & (1 << p):
                x ^= row
        if not x:
            raise ValueError('dependent binary chart basis')
        p = x.bit_length() - 1
        for old, row in rows.items():
            if row & (1 << p):
                rows[old] = row ^ x
        rows[p] = x
    return tuple(row for _, row in sorted(rows.items()))


def bit_positions(bits):
    while bits:
        low = bits & -bits
        yield low.bit_length() - 1
        bits ^= low


def reachability(labels, ranks, events, down=True):
    """Forward time-expanded reachability with free holding/same-space switches."""
    masks = {f: 1 << f for f in labels}
    for _, _, f, g, _ in events:
        if down or ranks[f] < ranks[g]:
            masks[g] |= masks[f]
    return sorted((f, g) for g, mask in masks.items() for f in bit_positions(mask)
                  if f != g and ranks[f] == ranks[g])


def inventory(word, ranks, spaces):
    groups = defaultdict(list)
    direct = defaultdict(list)
    for f, basis in enumerate(word['frames']):
        groups[binary_key(basis)].append(f)
        direct[frozenset(spaces[f])].append(f)
    assert sorted(groups.values()) == sorted(direct.values())
    labels = {f: fs[0] for fs in groups.values() for f in fs}
    raw = [(t, j, f, g, owned) for t, (op, j, *a) in enumerate(word['program'])
           if op == 'MOVE' for f, g, owned in (a,)]
    events = [(t, j, labels[f], labels[g], owned) for t, j, f, g, owned in raw]
    down = [row for row in raw if ranks[row[2]] > ranks[row[3]]]
    assert all(owned and j >= word['public'] for _, j, _, _, owned in down)
    carrier = defaultdict(list)
    for row in events:
        carrier[row[1]].append(row)
    counts = Counter()
    same = []
    for j, itinerary in carrier.items():
        kind = 'owned' if j >= word['public'] else 'public'
        for i, (t, _, f, _, _) in enumerate(itinerary):
            for u, _, _, g, _ in itinerary[i:]:
                counts[kind] += 1
                if ranks[f] == ranks[g] and f != g:
                    same.append((j, t, u, f, g))
    assert not same
    public_only = reachability(set(labels.values()), ranks, [e for e in events if not e[-1]])
    no_down = reachability(set(labels.values()), ranks, events, down=False)
    all_old = reachability(set(labels.values()), ranks, events)
    literal = reachability(set(labels), ranks, raw)
    assert not public_only and not no_down
    report = dict(literal_charts=len(labels), canonical_spans=len(groups),
                  aliases=sorted(v for v in groups.values() if len(v) > 1),
                  old_paid_moves=len(raw), paid_carriers=len(carrier),
                  old_public_moves=sum(not e[-1] for e in raw),
                  old_owned_moves=sum(e[-1] for e in raw),
                  all_same_carrier_ordered_intervals=dict(counts),
                  rank_preserving_same_carrier_distinct_span=same,
                  public_only_distinct_equal_rank_pairs=public_only,
                  all_upward_distinct_equal_rank_pairs=no_down,
                  equal_rank_literal_endpoint_pairs_before_alias_merge=len(literal),
                  all_old_distinct_equal_rank_pairs=len(all_old),
                  all_old_pair_rank_histogram=dict(Counter(ranks[f] for f, _ in all_old)),
                  all_old_pairs=all_old,
                  owned_downward_moves=down,
                  copy_guards=[(t, j, *a) for t, (op, j, *a) in enumerate(word['program']) if op == 'COPY'])
    return labels, report


def observations(side, members, cut, reverse):
    return [(label, row) for f in members for label, row in side[f]
            if cut is None or label[0] == 'endpoint' or
            (label[0] >= cut if reverse else label[0] < cut)]


def stock_gate(inputs, deps, cap, seconds):
    assert __debug__
    began = monotonic()
    price = load(deps, 'round13/alternative/reprice.py')
    gate = load(deps, 'round18/complex/stock_gate.py')

    def clock():
        if monotonic() - began >= seconds:
            raise gate.TimeCap

    old = json.loads(check(deps, 'round18/complex/STOCK.json')[1])
    old_audit = json.loads(check(deps, 'round18/complex/AUDIT.json')[1])
    free = json.loads(check(deps, 'round18/complex-free/FREE.json')[1])
    free_audit = json.loads(check(deps, 'round18/complex-free/AUDIT.json')[1])
    assert old_audit['pins']['round18/complex/STOCK.json'] == PINS['round18/complex/STOCK.json']
    assert free_audit['pins']['round18/complex-free/FREE.json'] == PINS['round18/complex-free/FREE.json']
    word, result, caller = (price.authenticated(inputs, key) for key in price.PINS)
    targets, paid, _, _, stages, origins, visits, ranks, spaces = price.invoice(word, caller, result)
    assert stages == 17 and sum(paid.values()) == 110519 and sum(targets.values()) == 22427
    labels, geo = inventory(word, ranks, spaces)
    members = defaultdict(list)
    for f, rep in labels.items():
        members[rep].append(f)
    down = geo['owned_downward_moves']
    assert len(down) == 24 and len(geo['copy_guards']) == 1
    all_pair_from = defaultdict(set)
    for f, g in geo['all_old_pairs']:
        all_pair_from[f].add(g)
    stock = {}
    cross_shapes = {}
    for j, (a, b, r) in sorted(origins.items()):
        interior = [f for f in visits[j] if spaces[a] < spaces[f] < spaces[b]]
        stock[j] = sorted(interior)
        choices = [min(ranks[f] - ranks[a], ranks[b] - ranks[f]) for f in interior
                   if any(spaces[a] < spaces[g] < spaces[b] for g in all_pair_from[labels[f]])]
        if choices:
            cross_shapes[j] = (r, max(choices))
    group = {j for j, p in origins.items() if p == (3, 127, 9)}
    assert len(group) == 616 and len(origins) == 1099
    assert all(stock[j] == old['owner_paths'][str(j)] for j in group)
    inherited = set(free['prior_certified_zero_charts']) | {row['chart'] for row in free['tested']
                 if row['pair_rank'] == row['capacity'] == 0}
    assert inherited == {x['chart'] for x in old['tested']} | {x['chart'] for x in free['tested']}
    assert len(inherited) == 664 and len(free['pending']) == 176
    direct_owners = defaultdict(list)
    for j in sorted(group):
        for f in sorted({labels[f] for f in stock[j]}):
            direct_owners[f].append(j)
    direct_shapes = {f: min(ranks[f], 9 - ranks[f]) for f in direct_owners}
    pending = {f for f in direct_owners if len(members[f]) > 1 or f not in inherited}
    order = [f for f in pending if len(members[f]) > 1]
    order += [f for f in free['pending'] if f in pending and f not in order]
    assert set(order) == pending and len(order) == len(pending)
    capacity = {f: len(owners) if f in pending else 0 for f, owners in direct_owners.items()}

    def moment(h):
        return price.dot(h, lambda r: price.power(r, price.TARGET))

    def saving(r, d):
        h = Counter((d, r - d))
        h[r] -= 1
        return stages * moment(h)[1]

    h = Counter(targets)
    h.subtract(paid)
    baseline = moment(h)[1]
    small = sum(max((saving(r, ranks[f] - ranks[a]) for f in stock[j]), default=0)
                for j, (a, _, r) in origins.items() if j not in group)
    tariff = {0: Q(0), **{d: saving(9, d) for d in range(1, 5)}}
    assert all(tariff[d] > tariff[d - 1] for d in range(1, 5))
    # A random partition puts each cross lane across one directed class cut
    # with probability 1/4. Any such cut has capacity at most len(down).
    cross_cap = 4 * len(down)
    grants = sorted((saving(r, d), j) for j, (r, d) in cross_shapes.items())
    cross_upper = sum(s for s, _ in grants[-cross_cap:])
    shape_hist = Counter(f'{r}:{d}' for r, d in cross_shapes.values())
    assert all(cross_shapes[j][0] == 9 for j in cross_shapes if j in group)
    upward = {}
    for r in range(3, 10):
        a, b = (r - 1) // 2, r // 2
        assert a + b == r - 1
        h = Counter((a, b))
        h[r] -= 1
        upward[r] = stages * moment(h)[1]
        assert upward[r] < 0

    def upper():
        # A smaller owner is already granted its best literal midpoint,
        # including every equal-rank cross alternative for that owner.
        # Rank-nine owners compete for one shared cross cap or one direct chart.
        layers = {}
        for d in range(1, 5):
            cross = [j for j in sorted(group) if j in cross_shapes and cross_shapes[j][1] >= d]
            layers[d] = gate.layer_count({**direct_owners, -1: cross},
                                         {**capacity, -1: cross_cap},
                                         {**direct_shapes, -1: d}, d)
        gain = sum((tariff[d] - tariff[d - 1]) * count for d, count in layers.items())
        return dict(combined_rank9_layers=layers, combined_rank9_upper=str(gain),
                    raw_upper=str(baseline + small + gain))

    def pairing(prefix, suffix, fm, gm, t=None):
        left = observations(prefix, fm, t, False)
        right = observations(suffix, gm, None if t is None else t + 1, True)
        p, pr = gate.intersection(left, group, clock)
        s, sr = gate.intersection(right, group, clock)
        return dict(pair_rank=gate.rank_pair(p, s), prefix_generators=len(left),
                    suffix_generators=len(right), prefix_outside_rank=pr, suffix_outside_rank=sr,
                    prefix_group=gate.encode(p), suffix_group=gate.encode(s))

    directed = []
    checked = []
    initial = upper()
    marks = []
    reason = 'edge cap'
    try:
        need = {f for rep in order for f in members[rep]} | {f for _, _, a, b, _ in down for f in (a, b)}
        prefix = gate.scan(word, need, clock)
        suffix = gate.scan(word, need, clock, True)
        for t, j, f, g, _ in down[:cap]:
            record = pairing(prefix, suffix, [f], [g], t)
            directed.append(dict(event=t, carrier=j, source=f, target=g, **record))
        limit = max(0, cap - len(directed))
        for f in order[:limit]:
            fs = members[f]
            record = pairing(prefix, suffix, fs, fs)
            capacity[f] = min(capacity[f], record['pair_rank'])
            checked.append(dict(representative=f, members=fs, capacity=capacity[f], **record))
            if len(checked) % 8 == 0 or len(checked) == min(len(order), limit):
                status = upper()
                marks.append(dict(direct_checks=len(checked), **status))
                if Q(status['raw_upper']) < 0:
                    reason = 'negative combined directed upper'
                    break
    except gate.TimeCap:
        reason = 'time cap'
    final = upper()
    if Q(final['raw_upper']) < 0:
        reason = 'negative combined directed upper'
    elif len(checked) == len(order):
        reason = 'scoped stock exhausted'
    return dict(status='NEGATIVE_DIRECTED_COMBINED_STOCK_UPPER' if Q(final['raw_upper']) < 0 else 'INCOMPLETE_OR_NONNEGATIVE',
                reason=reason, source_head=old['source_head'], source_scientific_tree=old['source_scientific_tree'],
                pins={**PINS, **{f'public/{k}': v for k, v in price.PINS.items()}}, target=str(price.TARGET),
                stages=stages, paid_positions=sum(paid.values()), productive_targets=sum(targets.values()),
                caps=dict(edge_cases=cap, seconds=seconds), seed=None, site_tests=0, new_paid_positions=0,
                geometry=geo, cross_owner_count=len(cross_shapes), cross_stock_shapes=dict(shape_hist),
                cross_split_cap=cross_cap, cross_saving_upper=str(cross_upper),
                rank_up_split_margin_upper={r: str(v) for r, v in upward.items()},
                old_moment_upper=str(baseline), smaller_direct_ideal_upper=str(small), initial=initial, final=final,
                inherited_zero_literal_charts=sorted(inherited), direct_order=order, direct_checked=checked,
                direct_pending=order[len(checked):], downward_timed_checked=directed,
                downward_timed_pending=[e[0] for e in down[len(directed):]], checkpoints=marks,
                controls=gate.controls())


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('inputs', type=Path)
    parser.add_argument('deps', type=Path)
    parser.add_argument('--cap', type=int, choices=range(1, 257), default=256)
    parser.add_argument('--seconds', type=int, choices=range(1, 721), default=720)
    print(json.dumps(stock_gate(**vars(parser.parse_args())), indent=2, sort_keys=True))
