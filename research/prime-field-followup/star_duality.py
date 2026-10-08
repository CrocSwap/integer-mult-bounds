"""Explore exact transpose circuits for the four-point stars in PR #7.

This is a scalar circuit experiment, not a new multiplication theorem.
Input demands come from Zhihao Chen's pinned PR #7 producer; see provenance
recorded by the driver. Every generated addition has disjoint input supports.
"""
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path
import argparse
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
REFERENCE = Path(__file__).resolve().parent
sys.path[:0] = [str(REFERENCE / 'vendor'), str(ROOT / 'scripts')]
from prime_field_circuit import canonical, optimize
from paired_triple_circuit import PairedTriple


class AlignedTriple(PairedTriple):
    """Keep complete index pairs together in the contracted weighted circuits."""
    def grouping(self, points):
        present = set(points)
        intact = [(x, x ^ 1) for x in sorted(points)
                  if not x & 1 and x ^ 1 in present]
        used = {x for pair in intact for x in pair}
        tail = [x for x in sorted(points) if x not in used]
        return [list(pair) for pair in intact] + [tail[i:i+2] for i in range(0, len(tail), 2)]

    def block(self, points, edges, weights):
        total, single, pair = super().block(points, edges, weights)
        return total, single, {tuple(sorted(key)): value for key, value in pair.items()}


class Sums:
    def __init__(self, width):
        self.width = width
        self.gates = []
        self.computed = {1 << i for i in range(width)}

    def add(self, a, b):
        if not a:
            return b
        if not b:
            return a
        assert not a & b
        value = a | b
        if value not in self.computed:
            assert a in self.computed and b in self.computed
            self.gates.append((a, b))
            self.computed.add(value)
        return value

    def total(self, terms):
        if not terms:
            return 0
        if len(terms) == 1:
            return terms[0]
        middle = len(terms) // 2
        return self.add(self.total(terms[:middle]), self.total(terms[middle:]))

    def prune(self, outputs):
        parents = {a | b: (a, b) for a, b in self.gates}
        needed = set()
        pending = list(outputs)
        while pending:
            value = pending.pop()
            if value in needed:
                continue
            needed.add(value)
            pending.extend(parents.get(value, ()))
        self.gates = [(a, b) for a, b in self.gates if a | b in needed]
        return self.gates


def check(masks, gates):
    computed = {1 << i for i in range(max(masks).bit_length())}
    for a, b in gates:
        assert a and b and not a & b
        assert a in computed and b in computed
        assert a | b not in computed
        computed.add(a | b)
    assert all(mask in computed for mask in masks)


def transpose(masks):
    """Synthesize the dual incidence matrix, then transpose its addition DAG."""
    width = max(masks).bit_length()
    dual = [sum(1 << j for j, mask in enumerate(masks) if mask >> i & 1)
            for i in range(width)]
    assert all(dual)
    gates = optimize(dual)
    adjoints = defaultdict(list)
    for i, root in enumerate(dual):
        adjoints[root].append(1 << i)
    circuit = Sums(width)
    for a, b in reversed(gates):
        value = circuit.total(adjoints[a | b])
        assert value
        adjoints[a].append(value)
        adjoints[b].append(value)
    outputs = [circuit.total(adjoints[1 << j]) for j in range(len(masks))]
    assert outputs == masks
    result = circuit.prune(outputs)
    check(masks, result)
    return result


def dyadic(masks, order=None):
    width = max(masks).bit_length()
    order = list(range(width)) if order is None else order
    circuit = Sums(width)
    cache = {}

    def build(mask, points):
        if not mask:
            return 0
        if mask in circuit.computed:
            return mask
        if mask in cache:
            return cache[mask]
        middle = len(points) // 2
        left = sum(1 << i for i in points[:middle])
        value = circuit.add(build(mask & left, points[:middle]),
                            build(mask & ~left, points[middle:]))
        cache[mask] = value
        return value

    outputs = [build(mask, order) for mask in masks]
    assert outputs == masks
    result = circuit.prune(outputs)
    check(masks, result)
    return result


def bundles(masks):
    """Factor repeated multi-term intersections, rather than one pair at a time."""
    width = max(masks).bit_length()
    circuit = Sums(width)
    terms = [{1 << i for i in range(width) if mask >> i & 1} for mask in masks]
    while any(len(t) > 1 for t in terms):
        candidates = set()
        for a, b in combinations(terms, 2):
            common = frozenset(a & b)
            if len(common) > 1:
                candidates.add(common)
        if not candidates:
            for t in terms:
                if len(t) > 1:
                    candidates.add(frozenset(t))
        def score(bundle):
            count = sum(bundle <= t for t in terms)
            value = sum(bundle)
            cost = 0 if value in circuit.computed else len(bundle)-1
            return (count*(len(bundle)-1)-cost, count, len(bundle), -value)
        chosen = max(candidates, key=score)
        value = circuit.total(sorted(chosen))
        for t in terms:
            contained = {x for x in t if not x & ~value}
            if len(contained) > 1 and sum(contained) == value:
                t.difference_update(contained)
                t.add(value)
    outputs = [next(iter(t)) for t in terms]
    assert outputs == masks
    result = circuit.prune(outputs)
    check(masks, result)
    return result


def alternative_greedy(masks, large=False, reverse=False):
    width = max(masks).bit_length()
    circuit = Sums(width)
    terms = [{1 << i for i in range(width) if mask >> i & 1} for mask in masks]
    while any(len(t) > 1 for t in terms):
        frequency = Counter(pair for t in terms for pair in combinations(sorted(t), 2))
        def priority(pair):
            value = pair[0] | pair[1]
            return (-frequency[pair], (-1 if large else 1)*value.bit_count(),
                    (-1 if reverse else 1)*value, pair)
        a, b = min(frequency, key=priority)
        value = circuit.add(a, b)
        for t in terms:
            contained = {x for x in t if not x & ~value}
            if len(contained) > 1 and sum(contained) == value:
                t.difference_update(contained)
                t.add(value)
    outputs = [next(iter(t)) for t in terms]
    assert outputs == masks
    result = circuit.prune(outputs)
    check(masks, result)
    return result


def templates(path):
    counts = Counter()
    for line in path.read_text().splitlines():
        core, old, *masks = map(int, line.split())
        counts[canonical(core, masks)] += 1
    return counts


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--limit', type=int, default=10)
    args = parser.parse_args()
    counts = templates(ROOT / 'build/references/pr7/run/demands.txt')
    for targets, multiplicity in counts.most_common(args.limit):
        candidates = {'published_greedy': optimize(list(targets)),
                      'transposed_greedy': transpose(list(targets)),
                      'dyadic': dyadic(list(targets)),
                      'bundles': bundles(list(targets)),
                      'large_greedy': alternative_greedy(list(targets), large=True),
                      'reverse_greedy': alternative_greedy(list(targets), reverse=True)}
        lengths = {name: len(gates) for name, gates in candidates.items()}
        print(json.dumps(dict(multiplicity=multiplicity,outputs=len(targets),
                              additions=lengths,
                              weighted_saving=multiplicity*(lengths['published_greedy']-min(lengths.values())))), flush=True)
