"""Impose each actual replacement equality on the optimistic release graph."""

from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import gzip
import json
import sys

from release import BRACKET, WORD_SHA, admissible_volume, bounds, changed_blocks, inventory, join
from eliminate import basis, bits, chart, domain, elimination, load

GRID = 10**45
IMPOSSIBLE = -10**100


def solve_equal(block, base, low, high, paid, target, equal, weights, ranks_only):
    return solve_equalities(block, base, low, high, paid, target, (equal,), weights, ranks_only)


def solve_equalities(block, base, low, high, paid, target, equalities, weights, ranks_only, overrides=None):
    variables = set(block)
    edges = sorted({(a, b) for a, b in paid.keys() | target.keys() if a in variables or b in variables})
    mass = sum(abs(target[a,b]-paid[a,b]) for a, b in edges)
    stride_base = max(3, 2*mass+1)
    stride = stride_base**9
    mid = {r: int(GRID*(lo+hi)/2) for r, (lo, hi) in weights.items()}
    score = {r: n*stride + stride_base**(r-1) for r, n in mid.items()} | {0: 0}
    uncertainty = max(max(abs(Q(mid[r], GRID)-a), abs(Q(mid[r], GRID)-b))
                      for r, (a, b) in weights.items())
    assert 2*mass*max(score.values()) < -IMPOSSIBLE//4
    all_nodes = {i for edge in (*edges,*equalities) for i in edge}
    states = {i: (base[i],) for i in all_nodes if i not in variables}
    for i in block:
        if ranks_only:
            lo, hi = len(low[i]).bit_length()-1, len(high[i]).bit_length()-1
            states[i] = tuple((None, rank) for rank in range(lo, hi+1))
        elif overrides is not None:
            states[i] = overrides[i]
        else:
            states[i] = domain(low[i], high[i])
    if any(not states[i] for i in variables):
        return {'infeasible': True}

    factors = []
    edge_specs = [(a,b,False) for a,b in edges]
    edge_specs.extend((a,b,True) for a,b in equalities if a != b and variables & {a,b})
    for a, b, equality in edge_specs:
        scope = tuple(sorted({a, b} & variables))
        table = {}
        old_rank = base[b][1]-base[a][1]
        for j, (am, ad) in enumerate(states[a]):
            for k, (bm, bd) in enumerate(states[b]):
                if equality:
                    valid = ad == bd if ranks_only else am == bm
                    value = 0
                else:
                    valid = ad <= bd if ranks_only else not am & ~bm
                    valid &= not target[a,b] or ad < bd
                    value = (target[a,b]-paid[a,b])*(score[bd-ad]-score[old_rank]) if valid else 0
                table[tuple(j if i == a else k for i in scope)] = (value if valid else IMPOSSIBLE, None)
        assert table and scope
        factors.append((scope, table))
    best, second, assignment, stats = elimination(factors, {i:len(states[i]) for i in block})
    if best < IMPOSSIBLE//2:
        return {'infeasible': True, 'stats': stats, 'ranks_only': ranks_only}
    selected = base | {i: states[i][j] for i,j in assignment.items()}
    profile = Counter()
    for a,b in edges:
        old_rank = base[b][1]-base[a][1]
        new_rank = selected[b][1]-selected[a][1]
        c = target[a,b]-paid[a,b]
        profile[old_rank] -= c
        if new_rank:
            profile[new_rank] += c
    profile = {r:n for r,n in sorted(profile.items()) if n}
    assert sum(r*n for r,n in profile.items()) == 0 and sum(score[r]*n for r,n in profile.items()) == best
    gain_lo = sum(n*weights[r][n<0] for r,n in profile.items())
    gain_hi = sum(n*weights[r][n>0] for r,n in profile.items())
    if second is not None and second > IMPOSSIBLE//2:
        center = Q((second+stride//2)//stride, GRID)
        gain_hi = max(gain_hi, center+2*mass*uncertainty)
    result = dict(ranks_only=ranks_only, profile=profile,
                  lower=str(gain_lo), upper=str(gain_hi), stats=stats)
    if not ranks_only:
        result['changed_bases'] = {i:basis(frozenset(bits(selected[i][0])))
                                   for i in sorted(block) if selected[i] != base[i]}
    elif overrides is not None:
        result['selected_ranks'] = {i:selected[i][1] for i in sorted(block)}
    return result


def screen(word, previous, graph, price):
    raw, ids, comp, raw_paid, raw_target, fixed, scalar, original, entry, end, child = inventory(word, graph)
    base = {i:chart(s) for i,s in enumerate(original) if s is not None}
    old_lo, old_hi, _ = bounds(original, Counter((comp[a],comp[b]) for _,a,b in raw_paid), {comp[i] for i in fixed})
    left, right = map(Q, BRACKET)
    weights = {r:(price.raw_margin({r:1},right)[0],price.raw_margin({r:1},left)[1])
               for r in range(1,10)}
    counts = Counter()
    results = []
    for row in previous['hits']:
        e = row['add']
        old_id = comp[scalar[e][0]]
        branch = child[e]
        new_id = len(original)

        def belong(i):
            return new_id if comp[i] == old_id and entry[branch] <= entry[i] < end[branch] else comp[i]

        assert [raw[i] for i in range(len(raw)) if belong(i)==new_id] == [tuple(x) for x in row['split_raw_visits']]
        space = [*original, original[old_id]]
        paid = Counter((belong(a),belong(b)) for _,a,b in raw_paid)
        target = Counter((belong(a),belong(b)) for a,b in raw_target)
        low, high, adjacency = bounds(space, paid, {belong(i) for i in fixed})
        changed = {i for i, (a,b) in enumerate(zip(low, high))
                   if i == new_id or (a,b) != (old_lo[i],old_hi[i])} | {old_id}
        states = base | {new_id:base[old_id]}
        for proposal in row['possible_cuts']:
            u,v = [belong(ids[r,start-1]) for r,start,_ in proposal['new_visits']]
            assert [u,v] == proposal['cut_components']
            lower, upper = low.copy(), high.copy()
            lower[u] = lower[v] = join(low[u],low[v])
            upper[u] = upper[v] = high[u]&high[v]
            assert lower[u] <= upper[u]
            neighbors = [s.copy() for s in adjacency]
            if u != v:
                neighbors[u].add(v)
                neighbors[v].add(u)
            # Preserve the released graph's variable list even when the new
            # constraint reduces one of its domains to a forced new chart.
            blocks = changed_blocks(space, low, high, neighbors, target, changed|{u,v})
            entries = []
            for block in blocks:
                ranks_only = not admissible_volume(block, lower, upper, neighbors)
                entries.append(solve_equal(block, states, lower, upper, paid, target, (u,v), weights, ranks_only))
            hit = dict(add=e, cut=proposal['cut'], proposal=proposal, split_raw_visits=row['split_raw_visits'],
                       old_component=old_id, split_component=new_id, blocks=entries)
            if any(x.get('infeasible') for x in entries):
                status = 'no feasible chart assignment'
            else:
                lower_gain = sum(Q(x['lower']) for x in entries)
                upper_gain = sum(Q(x['upper']) for x in entries)
                hit.update(gain=[str(lower_gain),str(upper_gain)])
                if upper_gain <= 0:
                    status = 'nonpositive'
                elif lower_gain > 0 and not any(x['ranks_only'] for x in entries):
                    status = 'strict literal chart nominee'
                else:
                    status = 'unresolved upper bound'
            hit['status'] = status
            counts[status] += 1
            results.append(hit)
    return dict(word=WORD_SHA, bracket=BRACKET, counts=counts, cases=results)


def main(word_path, release_path, graph_path, price_path):
    raw = gzip.decompress(word_path.read_bytes())
    previous = json.loads(release_path.read_bytes())
    assert sha256(raw).hexdigest() == WORD_SHA == previous['word']
    assert not previous['remaining_adds']
    print(json.dumps(screen(json.loads(raw), previous, load('chart_graph',graph_path),
                            load('directed_price',price_path)), indent=2))


if __name__ == '__main__':
    if not __debug__:
        raise RuntimeError('Assertions are proof checks')
    main(*(Path(p) for p in sys.argv[1:]))
