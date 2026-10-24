#!/usr/bin/env python3
"""Exact batching for the fixed #4436 direct flow; no native admission.

Independent multiplicative-polynomial implementation of the flow's counts.
The chronological/Pascal construction is due to Sussman and zxv.
Mihir Srivastava, with substantial OpenAI Codex assistance. Apache-2.0.
"""
from collections import Counter
from math import gcd, lcm


def require(condition, message):
    if not condition:
        raise ValueError(message)


def validate(targets, paid, n):
    for histogram in (targets, paid):
        require(bool(histogram), 'nonempty histogram')
        require(all(type(k) is int and type(v) is int and k > 0 and v > 0
                    for k, v in histogram.items()), 'positive integer histogram')
    require(type(n) is int and 2 <= min(targets) <= max(targets) <= n
            and max(paid) < max(targets), 'strict rank contract')


def polynomial_layers(targets, cap, height):
    """Coefficient of each product in an ordered target word of length h."""
    layers = [{1: 1}]
    for _ in range(height):
        following = Counter()
        for c, count in layers[-1].items():
            for k, multiplicity in targets.items():
                if c*k <= cap:
                    following[c*k] += count*multiplicity
        layers.append(dict(following))
    return layers


def direct_flow(targets, paid, n):
    validate(targets, paid, n)
    m, kmin = max(targets), min(targets)
    cap, height, least = n//m, 0, 1
    while least*kmin <= cap:
        height += 1
        least *= kmin
    layers = polynomial_layers(targets, cap, height)

    def units(depth, rho):
        return {c: q for c, q in layers[height-depth].items() if rho*c <= cap}

    def demand(depth, rho):
        result = Counter()
        for c, q in units(depth, rho).items():
            for k, w in targets.items():
                result[c*k] += w*q
        return result

    sources = Counter(demand(0, 1))
    exits, boundary = Counter(), Counter()
    cuts = []
    paths = {1: 1}
    unit_count = column_mass = matched = 0
    for depth in range(height+1):
        next_paths = Counter()
        for rho, path_count in sorted(paths.items()):
            supply = units(depth, rho)
            unit_count += path_count*sum(supply.values())
            column_mass += path_count*sum(rho*c*q for c, q in supply.items())
            for r, occurrences in sorted(paid.items()):
                child_rho = rho*r
                copies = path_count*occurrences
                if depth == height:
                    local = Counter({child_rho: supply.get(1, 0)})
                else:
                    child = demand(depth+1, child_rho)
                    local = Counter()
                    for c in supply.keys() | child.keys():
                        have, want = supply.get(c, 0), child.get(c, 0)
                        if have:
                            require(want <= have, 'Pascal containment')
                        matched += copies*min(have, want)
                        if have > want:
                            local[child_rho*c] += have-want
                            boundary[child_rho*c] += copies*(have-want)
                        elif want > have:
                            sources[child_rho*c] += copies*(want-have)
                    if child_rho <= cap:
                        next_paths[child_rho] += copies
                for e, q in sorted(local.items()):
                    if q:
                        # copies counts separate chronological calls. It MUST
                        # NOT multiply q in the divisibility constraint.
                        cuts.append({'depth': depth, 'rho': rho, 'paid_rank': r,
                                     'rank': e, 'count': q, 'copies': copies})
                        exits[e] += copies*q
        paths = next_paths
    sources, exits, boundary = +sources, +exits, +boundary
    require(sources and all(n < m*s <= m*n for s in sources), 'source bounds')
    require(all(0 < e < n for e in exits), 'strict exit descent')
    mass = lambda h: sum(k*q for k, q in h.items())
    require(mass(sources)-mass(exits) == (mass(targets)-mass(paid))*column_mass,
            'rank-one conservation')
    return {'sources': sources, 'exits': exits, 'boundary_exits': boundary,
            'cuts': cuts, 'height': height, 'units': unit_count,
            'column_mass': column_mass, 'matched_jobs': matched}


def requirements(flow, n, pooled_exits=False):
    """Rank/count batches: all complements first, then one exit per cut."""
    rows = [(n-s, count) for s, count in flow['sources'].items()]
    if pooled_exits:
        rows += list(flow['exits'].items())
    else:
        rows += [(c['rank'], c['count']) for c in flow['cuts']]
    return rows


def multiplier(widths, rows):
    result = 1
    for rank, count in rows:
        require(type(rank) is int and 0 <= rank < len(widths), 'smaller rank')
        require(type(count) is int and count > 0, 'positive batch count')
        width = widths[rank]
        require(type(width) is int and width > 0, 'positive supplier width')
        result = lcm(result, width//gcd(width, count))
    return result


def check_batches(widths, rows, replication):
    require(type(replication) is int and replication > 0, 'positive replication')
    require(all(replication*q % widths[r] == 0 for r, q in rows),
            'whole chronological batch')


def compile_widths(targets, paid, maximum):
    """Compare least cut-feasible widths with #4436's nested construction."""
    m = max(targets)
    widths, nested = [1]*m, [1]*m
    leaves, old_leaves = list(range(m)), list(range(m))
    counters = {'compiled_ranks': 0, 'batch_constraints': 0, 'strict_width_gains': 0}
    first_pooled_failure = None
    rows_out = []
    prior_cap, flow = None, None
    for n in range(m, maximum+1):
        if n//m != prior_cap:
            flow = direct_flow(targets, paid, n)
            prior_cap = n//m
        rows = requirements(flow, n)
        a = multiplier(widths, rows)
        check_batches(widths, rows, a)
        source_count = sum(flow['sources'].values())
        width, old_width = a*source_count, nested[-1]*source_count
        require(old_width % width == 0, 'new width divides old nested width')
        # The exact same cut constraints are enforced for the old construction.
        check_batches(nested, rows, nested[-1])
        # rows contains one representative of each repeated exit cut; leaf
        # accounting must retain all of those repetitions.
        total = sum(a*q//widths[n-s]*leaves[n-s] for s, q in flow['sources'].items())
        total += sum(a*c['count']//widths[c['rank']]*leaves[c['rank']]*c['copies']
                     for c in flow['cuts'])
        old_a = nested[-1]
        old_total = sum(old_a*q//nested[n-s]*old_leaves[n-s]
                        for s, q in flow['sources'].items())
        old_total += sum(old_a*c['count']//nested[c['rank']]*old_leaves[c['rank']]*c['copies']
                         for c in flow['cuts'])
        require(total*old_width == old_total*width, 'unchanged normalized leaf cost')
        pooled_a = multiplier(widths, requirements(flow, n, pooled_exits=True))
        if pooled_a < a and first_pooled_failure is None:
            bad = next(c for c in flow['cuts'] if pooled_a*c['count'] % widths[c['rank']])
            first_pooled_failure = {'n': n, 'pooled_multiplier': pooled_a,
                                    'chronological_multiplier': a,
                                    'cut': bad, 'child_width': widths[bad['rank']]}
        widths.append(width); nested.append(old_width)
        leaves.append(total); old_leaves.append(old_total)
        counters['compiled_ranks'] += 1
        counters['batch_constraints'] += len(rows)
        counters['strict_width_gains'] += width < old_width
        rows_out.append((n, a, width, total))
    return {'widths': widths, 'nested_widths': nested, 'leaves': leaves,
            'nested_leaves': old_leaves, 'counters': counters,
            'first_pooled_failure': first_pooled_failure, 'rows': rows_out}
