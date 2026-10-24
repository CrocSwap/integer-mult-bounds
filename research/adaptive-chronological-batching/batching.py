#!/usr/bin/env python3
"""Per-cut census and least batch widths for arbitrary-height forests.

Multiplicative-polynomial implementation of the capped overlapping-rank flow
of zxv's PR #4436 at an explicit integer height G (the arbitrary-height forest
of PR #4483), with the cut-aware batching policy of PR #4507. The integer
Pascal compiler is Jacob Alan Sussman's. This module imports no predecessor
code and no ordered-word enumeration: the checker supplies those oracles.
Prepared with substantial AI assistance. Apache-2.0.
"""
from collections import Counter
from math import gcd, lcm

# Verification-only fault switches. Production callers pass none. Each models a
# plausible arbitrary-height shortcut that the verifier must reject.
CENSUS_FAULTS = frozenset({
    'drop-empty-parent',       # stop a path whose own class holds no unit
    'drop-boundary',           # discard premature exits above the leaf depth
    'drop-leaf',               # discard exits at the final depth
    'ignore-path-multiplier',  # child eligibility without the paid prefix
    'split-collisions',        # keep target-product collisions in separate cuts
})
POLICIES = ('per-cut', 'aggregate', 'occurrences', 'leaf-pooled')


def require(condition, message):
    if not condition:
        raise ValueError(message)


def is_count(value):
    return type(value) is int and value > 0


def validate(targets, paid, n):
    for histogram in (targets, paid):
        require(isinstance(histogram, dict) and bool(histogram), 'nonempty histogram')
        require(all(is_count(k) and is_count(v) for k, v in histogram.items()),
                'positive integer histogram')
    require(type(n) is int and 2 <= min(targets) <= max(targets) <= n
            and max(paid) < max(targets), 'strict rank contract')


def floor_log(value, base):
    require(is_count(value) and type(base) is int and base >= 2, 'integer logarithm')
    result = 0
    while value >= base:
        value //= base
        result += 1
    return result


def height(rule, targets, n):
    """Integer height: ('default',), ('adaptive', M, a, b) or ('fixed', G)."""
    cap = n//max(targets)
    kind = rule[0]
    if kind == 'default':
        return floor_log(cap, min(targets))
    if kind == 'adaptive':
        _, base, a, b = rule
        require(is_count(a) and is_count(b), 'positive adaptive multipliers')
        return (a+b)*floor_log(cap, base)
    require(kind == 'fixed' and type(rule[1]) is int and rule[1] >= 0, 'height rule')
    return rule[1]


def target_layers(targets, cap, depth, split=False):
    """F_h: ordered target words of length h by product (or product and letters).

    Distinguishable copies of one rank carry weight W_k. Products above cap are
    dropped: all target ranks are at least two, so they never recover.
    """
    layers = [{(1, ()): 1}]
    for _ in range(depth):
        following = Counter()
        for (c, tag), count in layers[-1].items():
            for k, copies in targets.items():
                if c*k <= cap:
                    following[(c*k, tuple(sorted(tag+(k,))) if split else ())] += count*copies
        layers.append(dict(following))
    return layers


def census(targets, paid, cap, G, faults=frozenset()):
    """Every chronological cut of the height-G forest at integer cutoff ``cap``.

    A class is (depth d, path multiplier rho). Its present units are ordered
    target words of length G-d with rho*c <= cap. Each unit demands one job per
    target letter; the child at paid rank r (multiplier rr=rho*r) accepts those
    demands whose tail fits rr. Present parents cover child demand; the excess
    leaves as exits of that one cut. Demand with no present parent is a fresh
    source. A class keeps spawning children while rr <= cap, even if empty.
    """
    require(is_count(cap) and type(G) is int and G >= 0, 'cap and height')
    require(faults <= CENSUS_FAULTS, 'known fault switch')
    split = 'split-collisions' in faults
    layers = target_layers(targets, cap, G, split)
    one = (1, ())

    def supply(depth, rho):
        return {key: q for key, q in layers[G-depth].items() if rho*key[0] <= cap}

    def demand(depth, rho):
        result = Counter()
        for (c, tag), q in supply(depth, rho).items():
            for k, copies in targets.items():
                result[(c*k, tuple(sorted(tag+(k,))) if split else ())] += copies*q
        return result

    roots, inner = Counter(), Counter()
    for (c, _), q in demand(0, 1).items():
        roots[c] += q
    boundary, leaves, columns = Counter(), Counter(), Counter()
    cuts, units, matched, empty_feeds = [], 0, 0, 0
    paths = {1: 1}
    for depth in range(G+1):
        following = Counter()
        for rho, occurrences in sorted(paths.items()):
            here = supply(depth, rho)
            units += occurrences*sum(here.values())
            for (c, _), q in here.items():
                columns[rho*c] += occurrences*q
            for r, repeats in sorted(paid.items()):
                rr, copies = rho*r, occurrences*repeats
                local = Counter()
                if depth == G:
                    if here.get(one, 0):
                        local[(rr, ())] = here[one]
                else:
                    below = demand(depth+1, rho if 'ignore-path-multiplier' in faults else rr)
                    for key in here.keys() | below.keys():
                        have, want = here.get(key, 0), below.get(key, 0)
                        require(have == 0 or want <= have, 'present parent covers demand')
                        matched += copies*min(have, want)
                        if have > want:
                            local[(rr*key[0], key[1])] = have-want
                        elif want > have:
                            inner[rr*key[0]] += copies*(want-have)
                    if rr <= cap and not ('drop-empty-parent' in faults and not here):
                        following[rr] += copies
                    if not here and rr <= cap and supply(depth+1, rr):
                        empty_feeds += copies
                for (e, tag), q in sorted(local.items()):
                    if ('drop-leaf' in faults and depth == G) \
                            or ('drop-boundary' in faults and depth < G):
                        continue
                    cuts.append((depth, rho, r, e, q, copies))
                    (leaves if depth == G else boundary)[e] += copies*q
        paths = following
    roots, inner, boundary, leaves = (+x for x in (roots, inner, boundary, leaves))
    return {'cap': cap, 'height': G, 'roots': roots, 'inner': inner,
            'sources': roots+inner, 'boundary': boundary, 'leaves': leaves,
            'exits': boundary+leaves, 'cuts': cuts, 'columns': +columns,
            'units': units, 'column_mass': sum(z*q for z, q in columns.items()),
            'matched': matched, 'empty_parent_feeds': empty_feeds}


def compressed_cuts(flow):
    """Occurrences of each (depth, rho, paid rank, exit rank, batch size)."""
    result = Counter()
    for depth, rho, r, e, count, copies in flow['cuts']:
        result[(depth, rho, r, e, count)] += copies
    return result


def rank_invoice(flow, targets, paid):
    """Sources minus exits minus unit targets plus unit paid jobs, by rank."""
    invoice = Counter(flow['sources'])
    invoice.subtract(flow['exits'])
    for z, count in flow['columns'].items():
        for k, w in targets.items():
            invoice[k*z] -= count*w
        for r, w in paid.items():
            invoice[r*z] += count*w
    return {rank: v for rank, v in invoice.items() if v}


def check_ledger(flow, targets, paid, n):
    """Structural obligations of one arbitrary-height flow at ambient rank n."""
    validate(targets, paid, n)
    m, rmax = max(targets), max(paid)
    require(flow['cap'] == n//m, 'cutoff is floor(n/m)')
    for name in ('roots', 'inner', 'sources', 'boundary', 'leaves', 'exits', 'columns'):
        require(all(is_count(k) and is_count(v) for k, v in flow[name].items()),
                'positive integer inventory '+name)
    require(bool(flow['sources']) and bool(flow['columns']), 'nonempty arbitrary-height flow')
    require(flow['sources'] == flow['roots']+flow['inner'], 'root/inner source partition')
    require(flow['exits'] == flow['boundary']+flow['leaves'], 'boundary/leaf exit partition')
    require(all(1 <= s <= n for s in flow['sources']), 'sources fit the ambient rank')
    require(all(m*s > n for s in flow['inner']), 'inner source lower bound')
    require(all(1 <= e < n and m*e <= rmax*n for e in flow['exits']), 'strict exit descent')
    require(all(m*z <= n for z in flow['columns']), 'unit columns fit cutoff')
    require(sum(flow['columns'].values()) == flow['units'], 'unit column count')
    cut_exits = Counter()
    for _, _, _, e, q, copies in flow['cuts']:
        require(is_count(q) and is_count(copies), 'positive cut size and occurrences')
        cut_exits[e] += q*copies
    require(cut_exits == flow['exits'], 'cut inventory equals exit inventory')
    require(not rank_invoice(flow, targets, paid), 'formal rank-invoice cancellation')
    return True


def batch_rows(flow, n, policy='per-cut'):
    """(rank, array count) batches that one unreplicated pass must complete."""
    require(policy in POLICIES, 'known batching policy')
    rows = [(n-s, q) for s, q in sorted(flow['sources'].items())]
    cuts = flow['cuts']
    if policy == 'per-cut':
        rows += [(e, q) for _, _, _, e, q, _ in cuts]
    elif policy == 'aggregate':
        rows += sorted(flow['exits'].items())
    elif policy == 'occurrences':
        rows += [(e, q*copies) for _, _, _, e, q, copies in cuts]
    else:
        rows += [(e, q) for depth, _, _, e, q, _ in cuts if depth < flow['height']]
        rows += sorted(flow['leaves'].items())
    return rows


def multiplier(widths, rows):
    result = 1
    for rank, count in sorted(set(rows)):
        require(type(rank) is int and 0 <= rank < len(widths), 'smaller rank')
        require(is_count(count), 'positive batch count')
        width = widths[rank]
        require(is_count(width), 'positive supplier width')
        result = lcm(result, width//gcd(width, count))
    return result


def check_rows(widths, rows, replication):
    require(is_count(replication), 'positive replication')
    for rank, count in rows:
        if replication*count % widths[rank]:
            raise ValueError('whole chronological batch')


def leaf_total(flow, n, widths, leaves, replication, occurrences=True):
    """Rank-one leaves of the replicated recursive calls (rank 0 costs 0)."""
    total = sum(replication*q//widths[n-s]*leaves[n-s] for s, q in flow['sources'].items())
    for _, _, _, e, q, copies in flow['cuts']:
        total += replication*q//widths[e]*leaves[e]*(copies if occurrences else 1)
    return total


def compile_widths(targets, paid, maximum, rule, occurrence_cost=True):
    """Least cut-feasible widths and the nested #4436 widths for one height rule."""
    m = max(targets)
    widths, nested = [1]*m, [1]*m
    leaves, nested_leaves = list(range(m)), list(range(m))
    records, flows = [], {}
    gaps = {p: {'ranks_with_gap': 0, 'ranks_underpaying': 0, 'first': None}
            for p in POLICIES if p != 'per-cut'}
    for n in range(m, maximum+1):
        G = height(rule, targets, n)
        if (n//m, G) not in flows:
            flows[(n//m, G)] = census(targets, paid, n//m, G)
        flow = flows[(n//m, G)]
        check_ledger(flow, targets, paid, n)
        rows = batch_rows(flow, n)
        a = multiplier(widths, rows)
        check_rows(widths, rows, a)
        count = sum(flow['sources'].values())
        width, old_width = a*count, nested[-1]*count
        require(old_width % width == 0, 'least width divides nested width')
        check_rows(nested, rows, nested[-1])
        total = leaf_total(flow, n, widths, leaves, a, occurrence_cost)
        old_total = leaf_total(flow, n, nested, nested_leaves, nested[-1])
        for policy in gaps:
            pooled_rows = batch_rows(flow, n, policy)
            pooled = multiplier(widths, pooled_rows)
            gaps[policy]['ranks_with_gap'] += pooled != a
            # The relaxed policy always satisfies its own rows; the question
            # is whether its multiplier also completes every actual cut.
            check_rows(widths, pooled_rows, pooled)
            failing = [(e, q) for e, q in rows if pooled*q % widths[e]]
            if failing:
                gaps[policy]['ranks_underpaying'] += 1
                if gaps[policy]['first'] is None:
                    rank, size = failing[0]
                    cut = next(c for c in flow['cuts'] if c[3] == rank and c[4] == size)
                    gaps[policy]['first'] = {
                        'n': n, 'height': G, 'pooled_multiplier': pooled,
                        'cut_multiplier': a, 'cut': list(cut), 'width': widths[rank],
                        'pooled_remainder': pooled*size % widths[rank],
                        'failing_cuts': len(failing)}
        widths.append(width)
        nested.append(old_width)
        leaves.append(total)
        nested_leaves.append(old_total)
        records.append({'n': n, 'height': G, 'multiplier': a, 'sources': count,
                        'batches': len(rows), 'cuts': len(flow['cuts']),
                        'width': width, 'nested_width': old_width, 'leaves': total,
                        'nested_leaves': old_total})
    return {'widths': widths, 'nested': nested, 'leaves': leaves,
            'nested_leaves': nested_leaves, 'records': records, 'gaps': gaps,
            'flows': flows}
