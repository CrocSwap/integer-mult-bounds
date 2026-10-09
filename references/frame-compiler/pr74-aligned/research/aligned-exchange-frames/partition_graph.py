#!/usr/bin/env python3
"""Frozen aligned split partitions on the archived weighted pair graph.

Prepared for Thomas DiFiore with substantial OpenAI Codex assistance.
Apache-2.0. Pair assembly: Avi Eisenberg PR62 and Dominik Scholz PR63;
interval graph/order: Rohan Arun PR65; split operation: Rohan Garg PR59;
anchored split composition: Chafik Boukhalfa PR71; balanced coarse sums:
eumemic PR69. Core renumbering is retained from our balanced-split-frames.
Original source files and notices remain in the contributor archives.
"""
import sys
if sys.flags.optimize:
    raise ValueError('Assertions must remain enabled')
sys.dont_write_bytecode = True

from hashlib import sha256
import importlib.util
from pathlib import Path
import types
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ARCHIVE = ROOT/'references/frame-compiler/pr71'
PROVIDER = ARCHIVE/'scripts/experiments/split_pair_graph.py'
PROVIDER_SHA256 = '9d4ee7179f880f9576e81c7ad3a5290fe61380a7531d559ef3cf0939bb30089c'
PAIR_GRAPH_SHA256 = '3d47e89d2649c90800a276bdd0480131def50e0bdf92c122a19494b55bf17420'
SPLITS = {23: 6, 25: 9}


assert sha256(PROVIDER.read_bytes()).hexdigest() == PROVIDER_SHA256
_spec = importlib.util.spec_from_file_location('aligned_archived_split_pair_graph', PROVIDER)
provider = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(provider)

BEFORE = '''            coarse = {(i, j): self.total([e(a, b) for a in groups[i] for b in groups[j]])
                      for i, j in combinations(range(ng), 2)}'''
AFTER = '''            def coarse_sum(i, j):
                mode = COARSE[level] if level<len(COARSE) else 'c'
                if mode=='c' or (mode=='h' and i+j<ng-1):
                    pieces = [self.total([e(a,b) for a in groups[i]]) for b in groups[j]]
                else:
                    pieces = [self.total([e(a,b) for b in groups[j]]) for a in groups[i]]
                return self.total(pieces)
            coarse = {(i,j):coarse_sum(i,j) for i,j in combinations(range(ng),2)}'''


def reorder(c):
    """Preserve source IDs and each frame's original internal node order."""
    groups = {}
    for node in sorted(c.active):
        if c.args[node]:
            groups.setdefault((c.core[node], c.union[node]), []).append(node)
    def key(item):
        (core, cover), nodes = item
        return cover.bit_count()-core.bit_count(), -core, cover, min(nodes)
    ids = list(range(len(c.inputs)+1)) + [node
        for _, nodes in sorted(groups.items(), key=key) for node in nodes]
    mapping = {node:i for i,node in enumerate(ids)}
    args, core, cover, provenance = c.args, c.core, c.union, c.provenance
    c.args = [tuple(mapping[x] for x in args[node]) if args[node] else None for node in ids]
    c.core = [core[node] for node in ids]
    c.union = [cover[node] for node in ids]
    c.provenance = [provenance[node] for node in ids]
    c.active = {mapping[node] for node in c.active}
    c.outputs = {target:mapping[node] for target,node in c.outputs.items()}
    c.support_in.cache_clear()
    c.verify()
    return c


def graph(h, ordered=True):
    """Return the frozen h=23 or h=25 graph, before or after renumbering."""
    if type(h) is not int or h not in SPLITS or type(ordered) is not bool:
        raise ValueError('Only frozen dimensions 23 and 25 are supported')
    config=json.loads((HERE/'selection.json').read_text())['axes'][str(h)]
    count = SPLITS[h]
    choices=config['groups'];coarse=config['coarse_word']
    assert choices[0]=='first'+str(count)
    assert coarse and set(coarse)<=set('crh')
    assert all((type(x) is int and 0<=x<=3) or (isinstance(x,str) and x.startswith('first') and x[5:].isdigit()) for x in choices)
    source_path = Path(provider._graph.__file__)
    source = source_path.read_text()
    assert sha256(source.encode()).hexdigest() == PAIR_GRAPH_SHA256
    assert source.count(BEFORE) == 1
    module = types.ModuleType('aligned_partition_private_graph')
    module.__file__ = str(source_path)
    module.COARSE = coarse
    exec(compile(source.replace(BEFORE, AFTER), str(source_path)+':aligned-partition', 'exec'), module.__dict__)
    original = module.circuit_class

    def selected_class(dimension):
        class Partition(original(dimension)):
            def grouping(self, points):
                groups = super().grouping(points)
                level, n = self._level, len(points)
                indices = []
                choice=choices[level] if level<len(choices) else 0
                if n > 3:
                    if choice in (1,2,3):
                        indices=[{1:0,2:(len(groups)-1)//2,3:len(groups)-1}[choice]]
                    elif isinstance(choice,str):
                        indices=list(range(min(int(choice[5:]),len(groups))))
                selected = [i for i in sorted(set(indices)) if len(groups[i]) == 2]
                # Each split adds one group. This cap leaves at least one pair.
                selected = selected[:max(0, n-len(groups)-1)]
                result = []
                for i, group in enumerate(groups):
                    result.extend([[point] for point in group] if i in selected else [group])
                assert all(len(group) in (1, 2) for group in result)
                assert len(result) < n
                assert [point for group in result for point in group] == list(points)
                return result
        return Partition

    module.circuit_class = selected_class
    original_points = module.alternating_points
    def anchored_points(dimension, common):
        order = original_points(dimension, common)
        pairs = [(a,a+1) for a in range(0, dimension-1, 2) if common not in (a,a+1)]
        head = [point for pair in pairs[:count] for point in pair]
        result = head + [point for point in order if point not in head]
        assert sorted(result) == [point for point in range(dimension) if point != common]
        return result
    module.alternating_points = anchored_points
    circuit = module.graph(h)
    if ordered:
        circuit = reorder(circuit)
        assert circuit.verify()['circuit_sha256'] == config['expected_scalar_sha256']
    else:
        circuit.verify()
    return circuit
