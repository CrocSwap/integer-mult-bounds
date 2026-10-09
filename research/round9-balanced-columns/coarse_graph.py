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

ROOT = Path(__file__).resolve().parent.parent/'round6-pr71/baseline/references/frame-compiler/pr65'
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


def graph(h, groups=(1, 1, 2), anchor='first', coarse='none'):
    if h not in (23, 25) or any(type(x) is not int or not 0 <= x <= 3 for x in groups):
        raise ValueError('Unsupported finite graph configuration')
    source = BASE.read_text()
    if coarse != 'none':
        assert source.count(BEFORE) == 1
        source = source.replace(BEFORE, {'columns': AFTER_COLUMNS, 'rows': AFTER_ROWS}[coarse])
    namespace = {'__file__': str(BASE), '__name__': 'next_use_graph_composition'}
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
    return result
