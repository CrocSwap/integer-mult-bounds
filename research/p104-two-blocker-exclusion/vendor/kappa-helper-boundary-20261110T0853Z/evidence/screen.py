"""One-dimensional closure search with variable productive helper endpoints."""

from collections import Counter, defaultdict
from fractions import Fraction as Q
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import gzip
import json
import sys

WORD_SHA = 'e2db4293ac41720af326d3acddabb580c1781c781b18d50dc81cfc8739f0cc38'
BRACKET = ('0.00363214407269170173702203666413962',
           '0.00363214407269170173702203666413963')


def load(name, path):
    spec = spec_from_file_location(name, path)
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def boundaries(word, groups):
    main = set(word['live']) | {i + 112 for i in word['live']}
    main |= set(word['hosted']['X2']) | set(word['hosted']['Y2'])
    visits = defaultdict(list)
    for a, group in enumerate(groups):
        for r, event, _ in group:
            visits[r].append((event, a))
    helper_pairs = []
    frozen = set()
    for r, history in sorted(visits.items()):
        first, last = min(history)[1], max(history)[1]
        if r >= word['public']:
            frozen.update(a for _, a in history)
        elif r in main:
            frozen.update((first, last))
        else:
            helper_pairs.append((r, first, last))
    return frozen, helper_pairs


def edit_span(space, mode, vector):
    if mode == 'up':
        return space | {v ^ vector for v in space}
    return frozenset(v for v in space if not (v & vector).bit_count() % 2)


def basis(space):
    generated = {0}
    result = []
    for v in sorted(space):
        if v not in generated:
            result.append(v)
            generated |= {w ^ v for w in generated}
    assert generated == space
    return result


def screen(word, graph, price):
    groups, frames, old_frozen, moves, scalars = graph.graph(word)
    fixed, helpers = boundaries(word, groups)
    assert fixed < old_frozen
    assert len(helpers) == word['public'] - 208 - 192
    spaces = [graph.span(word['frames'][f]) if f is not None else None for f in frames]
    dims = [len(word['frames'][f]) if f is not None else -1 for f in frames]
    masks = [sum(1 << v for v in s) if s is not None else 0 for s in spaces]
    order = sorted(range(len(groups)), key=dims.__getitem__)
    frozen_mask = sum(1 << i for i in fixed)
    old_frozen_mask = sum(1 << i for i in old_frozen)
    parents = [set() for _ in groups]
    children = [set() for _ in groups]
    paid_at = [[] for _ in groups]
    helper_at = [[] for _ in groups]
    for j, (_, a, b) in enumerate(moves):
        assert spaces[a] < spaces[b]
        parents[b].add(a)
        children[a].add(b)
        paid_at[a].append(j)
        paid_at[b].append(j)
    for j, (_, a, b) in enumerate(helpers):
        assert spaces[a] < spaces[b]
        helper_at[a].append(j)
        helper_at[b].append(j)
    assert old_frozen - fixed <= {a for _, u, v in helpers for a in (u, v)}

    lower, upper = map(Q, BRACKET)
    power = {r: (price.raw_margin({r: 1}, upper)[0], price.raw_margin({r: 1}, lower)[1])
             for r in range(1, 10)}
    assert graph.margin({1: 1, 2: -2, 3: 1}, power)[0] > 0
    assert graph.margin({1: -1, 2: 2, 3: -1}, power)[1] < 0
    stats = {}
    hits = []
    prices = {}
    for mode in ('up', 'down'):
        counts = Counter()
        seen = set()
        up = mode == 'up'
        inward = children if up else parents
        visits = order[::-1] if up else order
        step = 1 if up else -1
        for v in range(1, 512):
            bad = 1 << v if up else sum(1 << x for x in range(512) if (x & v).bit_count() % 2)
            active = [bool(mask & bad) != up and dim >= 0 for mask, dim in zip(masks, dims)]
            closures = [0] * len(groups)
            for a in visits:
                if not active[a]:
                    continue
                closure = 1 << a
                for b in inward[a]:
                    closure |= closures[b]
                closures[a] = closure
                if not closure & old_frozen_mask:
                    continue
                if closure & frozen_mask:
                    counts['blocked'] += 1
                    continue
                if closure in seen:
                    continue
                seen.add(closure)
                counts['distinct_eligible_closures'] += 1
                changed = list(graph.bits(closure))
                paid_delta = Counter()
                target_delta = Counter()
                helper_changes = []
                zero_moves = []
                for j in sorted({j for i in changed for j in helper_at[i]}):
                    r, u, w = helpers[j]
                    old = dims[w] - dims[u]
                    new = old + step * (bool(closure & (1 << w)) - bool(closure & (1 << u)))
                    if new != old:
                        helper_changes.append((r, u, w, old, new))
                        target_delta[old] -= 1
                        target_delta[new] += 1
                if target_delta[0]:
                    counts['zero_target_rejected'] += 1
                    continue
                for j in sorted({j for i in changed for j in paid_at[i]}):
                    event, u, w = moves[j]
                    old = dims[w] - dims[u]
                    new = old + step * (bool(closure & (1 << w)) - bool(closure & (1 << u)))
                    assert new >= 0
                    if new != old:
                        paid_delta[old] -= 1
                        if new:
                            paid_delta[new] += 1
                        else:
                            zero_moves.append(event)
                delta = paid_delta.copy()
                delta.subtract(target_delta)
                assert sum(r*n for r, n in delta.items()) == 0
                signature = tuple((r, n) for r, n in sorted(delta.items()) if n)
                if not signature:
                    counts['exact_ties'] += 1
                    continue
                if signature not in prices:
                    prices[signature] = graph.margin(dict(signature), power)
                lo, hi = prices[signature]
                if hi < 0:
                    counts['directed_losses'] += 1
                    continue
                counts['positive_or_unresolved'] += 1
                replacements = {i: edit_span(spaces[i], mode, v) for i in changed}
                for _, u, w in moves:
                    if u in replacements or w in replacements:
                        assert replacements.get(u, spaces[u]) <= replacements.get(w, spaces[w])
                for _, u, w in helpers:
                    if u in replacements or w in replacements:
                        assert replacements.get(u, spaces[u]) < replacements.get(w, spaces[w])
                hits.append({
                    'mode': mode, 'vector': v, 'seed_component': a,
                    'changed_bases': {i: basis(s) for i, s in replacements.items()},
                    'visit_count': sum(len(groups[i]) for i in changed),
                    'target_delta': {r: n for r, n in sorted(target_delta.items()) if n},
                    'paid_delta': {r: n for r, n in sorted(paid_delta.items()) if n},
                    'zero_moves': zero_moves,
                    'helper_rank_changes': helper_changes,
                    'gain_bounds': [str(lo), str(hi)],
                })
        stats[mode] = dict(counts)
    hits.sort(key=lambda h: (Q(h['gain_bounds'][0]), -h['visit_count']), reverse=True)
    return dict(scope='single direction single-seed nested chart closure; main boundary and all owned visits fixed; productive helper endpoints relaxed',
                original_frozen=len(old_frozen), retained_frozen=len(fixed), helpers=len(helpers),
                stats=stats, count=len(hits), best=hits[:20])


def main(word_path, graph_path, price_path):
    raw = gzip.decompress(word_path.read_bytes())
    assert sha256(raw).hexdigest() == WORD_SHA
    word = json.loads(raw)
    result = screen(word, load('chart_graph', graph_path), load('directed_price', price_path))
    print(json.dumps(dict(word=WORD_SHA, crossing_bracket=BRACKET, **result), indent=2))


if __name__ == '__main__':
    if not __debug__:
        raise RuntimeError('Assertions are proof checks')
    main(*(Path(p) for p in sys.argv[1:]))
