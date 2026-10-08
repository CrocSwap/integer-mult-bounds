"""Controlled combinations of the PR62, PR69 and PR71 scalar graphs.

PR62 graph: Avi Eisenberg with Claude assistance. PR59 split operation:
Rohan Garg. PR69 balanced coarse columns: eumemic with Codex assistance.
PR71 anchored split vector: Chafik Boukhalfa with Codex assistance.
This configurable composition/search adapter: huxint with Codex assistance.
Apache-2.0 and all inherited notices apply. No global search claim.
"""
import sys
if sys.flags.optimize:
    raise ValueError('Assertions must remain enabled')
from hashlib import sha256
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT/'research/pair-assembly/pair_graph.py'
BEFORE = '''            coarse = {(i, j): self.total([e(a, b) for a in groups[i] for b in groups[j]])
                      for i, j in combinations(range(ng), 2)}'''
AFTER_COLUMNS = '''            def coarse_sum(i, j):
                columns = [self.total([e(a,b) for a in groups[i]]) for b in groups[j]]
                return self.total(columns)
            coarse = {(i,j):coarse_sum(i,j) for i,j in combinations(range(ng),2)}'''
AFTER_ROWS = '''            def coarse_sum(i, j):
                rows = [self.total([e(a,b) for b in groups[j]]) for a in groups[i]]
                return self.total(rows)
            coarse = {(i,j):coarse_sum(i,j) for i,j in combinations(range(ng),2)}'''
AFTER_HALF = '''            def coarse_sum(i, j):
                if i+j < ng-1+COARSE_SHIFT:
                    pieces = [self.total([e(a,b) for a in groups[i]]) for b in groups[j]]
                else:
                    pieces = [self.total([e(a,b) for b in groups[j]]) for a in groups[i]]
                return self.total(pieces)
            coarse = {(i,j):coarse_sum(i,j) for i,j in combinations(range(ng),2)}'''


def reorder_envelopes(c):
    """Thomas DiFiore's PR74 scalar-envelope order, also used by PR76."""
    regions = {}
    for node in sorted(c.active):
        if c.args[node]:
            regions.setdefault((c.core[node], c.union[node]), []).append(node)
    def key(item):
        (core, union), nodes = item
        return union.bit_count()-core.bit_count(), -core, union, min(nodes)
    variables = len(c.inputs)
    ids = list(range(variables+1))+[x for _, nodes in sorted(regions.items(), key=key) for x in nodes]
    mapping = {x: i for i, x in enumerate(ids)}
    args, core, union, provenance = c.args, c.core, c.union, c.provenance
    c.args = [tuple(mapping[y] for y in args[x]) if args[x] else None for x in ids]
    c.core = [core[x] for x in ids]
    c.union = [union[x] for x in ids]
    c.provenance = [provenance[x] for x in ids]
    c.active = {mapping[x] for x in c.active}
    c.outputs = {k: mapping[v] for k, v in c.outputs.items()}
    # The pre-reorder audit populated keys (self,node,common). Their node
    # numbers now have different meanings; invalidate that derived cache.
    c.support_in.cache_clear()
    c.verify()
    return c


def graph(h, groups=(1, 1, 2), anchor='first', coarse='none', node_order='original', coarse_shift=0):
    if h not in (23, 25) or any(type(x) is not int or not 0 <= x <= 3 for x in groups):
        raise ValueError('Unsupported finite graph configuration')
    source = BASE.read_text()
    if coarse != 'none':
        assert source.count(BEFORE) == 1
        source = source.replace(BEFORE, {'columns': AFTER_COLUMNS, 'rows': AFTER_ROWS, 'half': AFTER_HALF}[coarse])
    namespace = {'__file__': str(BASE), '__name__': 'next_use_graph_composition', 'COARSE_SHIFT':coarse_shift}
    exec(compile(source, str(BASE)+':next_use_composition', 'exec'), namespace)
    original_class = namespace['circuit_class']

    def circuit_class(dimension):
        class SplitPair(original_class(dimension)):
            def grouping(self, points):
                partition = super().grouping(points)
                choice = groups[self._level] if self._level < len(groups) else 0
                if len(points) > 3 and choice:
                    index = {1: 0, 2: (len(partition)-1)//2, 3: len(partition)-1}[choice]
                    if len(partition[index]) == 2:
                        partition[index:index+1] = [[x] for x in partition[index]]
                assert all(len(g) in (1, 2) for g in partition)
                assert len(partition) < len(points)
                assert sorted(x for g in partition for x in g) == sorted(points)
                return partition
        return SplitPair

    namespace['circuit_class'] = circuit_class
    original_points = namespace['alternating_points']
    if anchor != 'none':
        def points(dimension, common):
            old = original_points(dimension, common)
            pairs = [(a, a+1) for a in range(0, dimension-1, 2) if common not in (a, a+1)]
            chosen = {'first': pairs[0], 'second': pairs[min(1, len(pairs)-1)], 'last': pairs[-1]}[anchor]
            result = list(chosen)+[x for x in old if x not in chosen]
            assert sorted(result) == [x for x in range(dimension) if x != common]
            return result
        namespace['alternating_points'] = points
    result = namespace['graph'](h)
    result.verify()
    if node_order == 'envelope':
        result = reorder_envelopes(result)
    elif node_order != 'original':
        raise ValueError(node_order)
    return result
