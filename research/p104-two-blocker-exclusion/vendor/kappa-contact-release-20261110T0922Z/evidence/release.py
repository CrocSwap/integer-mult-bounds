"""Price each scalar bridge release before imposing its replacement equality."""

from collections import Counter, defaultdict
from fractions import Fraction as Q
from functools import lru_cache
from hashlib import sha256
from math import prod
from pathlib import Path
import gzip
import json
import sys
import time

PRIOR = Path(__file__).resolve().parents[2] / 'kappa-coupled-boundaries-20261110T0908Z' / 'evidence'
sys.path.append(str(PRIOR))
from eliminate import chart, load, solve, subspace_count

WORD_SHA = 'cca66a7ec924bab47ccd1410968d16e071a01dc6110b5c08040bd207f753d066'
BRACKET = ('0.00363432724063755030618121129092973',
           '0.00363432724063755030618121129092974')
EMPTY = frozenset((0,))
FULL = frozenset(range(512))


@lru_cache(None)
def join(a, b):
    if a <= b:
        return b
    if b <= a:
        return a
    current = set(a)
    for v in sorted(b):
        if v not in current:
            current |= {x ^ v for x in current}
    return frozenset(current)


def bridge_forest(adj):
    index = [-1] * len(adj)
    end = [-1] * len(adj)
    low = [-1] * len(adj)
    children = {}
    cursor = 0

    def dfs(u, parent_edge):
        nonlocal cursor
        index[u] = low[u] = cursor
        cursor += 1
        for v, e in adj[u]:
            if e == parent_edge:
                continue
            if index[v] >= 0:
                low[u] = min(low[u], index[v])
            else:
                dfs(v, e)
                low[u] = min(low[u], low[v])
                if low[v] > index[u]:
                    children[e] = v
        end[u] = cursor

    for u in range(len(adj)):
        if index[u] < 0:
            dfs(u, -1)
    return index, end, children


def inventory(word, graph):
    groups, frames, _, paid_check, _ = graph.graph(word)
    raw = [v for group in groups for v in group]
    raw_id = {(r, e): i for i, (r, e, _) in enumerate(raw)}
    comp = [i for i, g in enumerate(groups) for _ in g]
    adj = [[] for _ in raw]
    public = word['public']
    roles = public + word['owned_fields']
    initial = [raw_id[r, -1] for r in range(roles)]
    active = initial.copy()
    main = set(word['live']) | {r + 112 for r in word['live']}
    main |= set(word['hosted']['X2']) | set(word['hosted']['Y2'])
    paid, scalar = [], {}
    for i, event in enumerate(word['program']):
        op, r = event[:2]
        if op in ('MOVE', 'INIT', 'CLEAR'):
            after = raw_id[r, i]
            if op == 'MOVE' and r < public:
                paid.append((i, active[r], after))
            active[r] = after
        elif op in ('ADD', 'COPY'):
            a, b = active[r], active[event[2]]
            assert comp[a] == comp[b] and raw[a][2] == raw[b][2] == event[-1]
            adj[a].append((b, i))
            adj[b].append((a, i))
            scalar[i] = (a, b)
    assert [(i, comp[a], comp[b]) for i, a, b in paid] == paid_check
    assert [raw[v][2] for v in active[:public]] == word['final']
    target = [(initial[r], active[r]) for r in range(public) if r not in main]
    fixed = {i for i, (r, _, _) in enumerate(raw) if r >= public}
    fixed.update(initial[r] for r in main)
    fixed.update(active[r] for r in main)
    space = [graph.span(word['frames'][f]) if f is not None else None for f in frames]
    sys.setrecursionlimit(30000)
    entry, finish, child = bridge_forest(adj)
    return raw, raw_id, comp, paid, target, fixed, scalar, space, entry, finish, child


def bounds(space, paid, frozen):
    parents, children = [set() for _ in space], [set() for _ in space]
    order = sorted(range(len(space)), key=lambda i: len(space[i]) if space[i] is not None else -1)
    for a, b in paid:
        assert space[a] < space[b]
        parents[b].add(a)
        children[a].add(b)
    lo, hi = [EMPTY] * len(space), [FULL] * len(space)
    for i in order:
        if i in frozen and space[i] is not None:
            lo[i] = space[i]
        for a in parents[i]:
            lo[i] = join(lo[i], lo[a])
    for i in reversed(order):
        if i in frozen and space[i] is not None:
            hi[i] = space[i]
        for b in children[i]:
            hi[i] &= hi[b]
    return lo, hi, [a | b for a, b in zip(parents, children)]


def changed_blocks(space, low, high, neighbors, target, affected):
    for a, b in target:
        neighbors[a].add(b)
        neighbors[b].add(a)
    variable = {i for i, s in enumerate(space) if s is not None and low[i] != high[i]}
    blocks = []
    while variable & affected:
        r = min(variable & affected)
        variable.remove(r)
        stack, block = [r], [r]
        while stack:
            u = stack.pop()
            for v in sorted(neighbors[u] & variable):
                variable.remove(v)
                stack.append(v)
                block.append(v)
        blocks.append(sorted(block))
    return blocks


def admissible_volume(block, low, high, neighbors, cap=250000):
    q = {i: len(high[i]).bit_length()-len(low[i]).bit_length() for i in block}
    if max(q.values()) > 5:
        return False
    sizes = {i: sum(subspace_count(d, r) for r in range(d+1)) for i, d in q.items()}
    pending = {i: neighbors[i] & sizes.keys() for i in block}
    total = 0
    while pending:
        work = {i: sizes[i] * prod(sizes[j] for j in ns) for i, ns in pending.items()}
        v = min(pending, key=lambda i: (work[i], i))
        ns = pending.pop(v)
        total += work[v]
        if total > cap:
            return False
        for n in ns:
            pending[n].remove(v)
            pending[n].update(ns - {n})
    return True


def screen(word, proposals, graph, price, journal, time_cap):
    raw, ids, comp, raw_paid, raw_target, raw_fixed, scalar, original, enter, end, child = inventory(word, graph)
    base = {i: chart(s) for i, s in enumerate(original) if s is not None}
    p0 = Counter((comp[a], comp[b]) for _, a, b in raw_paid)
    old_lo, old_hi, _ = bounds(original, p0, {comp[i] for i in raw_fixed})
    assert all(old_lo[i] <= s <= old_hi[i] for i, s in enumerate(original) if s is not None)
    left, right = map(Q, BRACKET)
    interval = {r: (price.raw_margin({r:1}, right)[0], price.raw_margin({r:1}, left)[1])
                for r in range(1, 10)}
    assert graph.margin({1: 1, 2: -2, 3: 1}, interval)[0] > 0
    by_edge = defaultdict(list)
    for row in proposals:
        by_edge[row['add']].append(row)
    assert len(by_edge) == 2024 and len(proposals) == 4094
    counts = Counter()
    all_hits = []
    todo = []
    started = time.monotonic()
    deadline = started + time_cap
    new_id = len(original)

    for e, rows in sorted(by_edge.items()):
        if time.monotonic() >= deadline:
            todo.append(e)
            continue
        a, b = scalar[e]
        old_id = comp[a]
        branch = child[e]
        assert comp[b] == comp[branch] == old_id
        enter_branch, end_branch = enter[branch], end[branch]

        def belong(i):
            return new_id if comp[i] == old_id and enter_branch <= enter[i] < end_branch else comp[i]

        assert belong(a) != belong(b)
        paid = Counter((belong(i), belong(j)) for _, i, j in raw_paid)
        target = Counter((belong(i), belong(j)) for i, j in raw_target)
        frozen = {belong(i) for i in raw_fixed}
        space = [*original, original[old_id]]
        low, high, neighbors = bounds(space, paid, frozen)
        possible = []
        for row in rows:
            u, v = [belong(ids[r, start-1]) for r, start, _ in row['new_visits']]
            if join(low[u], low[v]) <= high[u] & high[v]:
                possible.append((u, v, row))
            else:
                counts['new_equality_interval_impossible'] += 1
        record = {'add': e, 'old_component': old_id, 'split_component': new_id,
                  'proposals': len(rows), 'optimistically_feasible_cuts': len(possible)}
        if not possible:
            record['status'] = 'all new equality cuts impossible'
        else:
            changed = {i for i, (a, b) in enumerate(zip(low, high))
                       if i == new_id or (a,b) != (old_lo[i],old_hi[i])}
            changed.add(old_id)
            blocks = changed_blocks(space, low, high, neighbors, target, changed)
            old_state = base | {new_id: base[old_id]}
            records = []
            for block in blocks:
                active = any(paid[x] != target[x] for x in paid.keys() | target.keys()
                             if x[0] in block or x[1] in block)
                if active and not admissible_volume(block, low, high, neighbors):
                    records.append(dict(proof='deferred volume bound', vertices=block))
                else:
                    records.append(solve(block, old_state, low, high, paid, target, interval, graph))
            hits = [r for r in records if r['proof'] == 'strict positive candidate']
            waits = [r for r in records if r['proof'] in ('deferred volume bound', 'interval inconclusive')]
            record['released_components'] = len(blocks)
            if hits or waits:
                record.update(status='relaxed positive' if hits else 'deferred',
                              positive=hits, deferred=waits)
                replacements = {i: graph.span(basis) for r in hits for i, basis in r['changed_bases'].items()}
                matches = [row for u, v, row in possible if replacements.get(u, space[u]) ==
                           replacements.get(v, space[v])]
                record['best_assignment_valid_cuts'] = [row['cut'] for row in matches]
                record['possible_cuts'] = [dict(row, cut_components=[u, v]) for u, v, row in possible]
                record['split_raw_visits'] = [raw[i] for i in range(len(raw)) if belong(i) == new_id]
                all_hits.append(record)
            else:
                record['status'] = 'release upper bound zero'
        counts[record['status']] += 1
        counts['tested_cuts'] += len(rows)
        journal.write(json.dumps(record, separators=(',', ':')) + '\n')
        journal.flush()
        if sum(counts[k] for k in ('all new equality cuts impossible','relaxed positive','deferred','release upper bound zero')) % 100 == 0:
            print(f"progress at ADD {e}, {counts['tested_cuts']} cuts", file=sys.stderr, flush=True)
    return dict(word=WORD_SHA, counts=counts, remaining_adds=todo, hits=all_hits,
                seconds=time.monotonic()-started, cap_seconds=time_cap)


def main(word_path, proposals_path, graph_path, price_path, journal_path, cap):
    raw = gzip.decompress(Path(word_path).read_bytes())
    assert sha256(raw).hexdigest() == WORD_SHA
    proposals = json.loads(Path(proposals_path).read_bytes())
    assert proposals['word'] == WORD_SHA
    graph = load('chart_graph', Path(graph_path))
    price = load('directed_price', Path(price_path))
    with Path(journal_path).open('x') as journal:
        receipt = screen(json.loads(raw), proposals['surviving_pairs'], graph, price, journal, int(cap))
    print(json.dumps(receipt, indent=2))


if __name__ == '__main__':
    if not __debug__:
        raise RuntimeError('Assertions are proof checks')
    main(*sys.argv[1:])
