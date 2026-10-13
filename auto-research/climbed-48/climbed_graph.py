"""PR #48 exclusion graphs with hill-climbed summand and leave-one-out orders.

Base orders are exactly PR #48's research/copied-fixed/changed_graph.py:
- total(): reverse input order at h=23, descending (support size, bitmask) at h=25
- vector(two=False): ascending support size, ties by ascending (h=23) or
  descending (h=25) support, with the original output indexing restored
After each base ordering, adjacent pairs are swapped where the next pinned bit
is 1 (tbits for total() calls, vbits for vector() calls, each consumed in call
order). All bits zero reproduces PR #48 exactly.
Prepared by Rohan Arun with Anthropic Claude assistance. Apache-2.0.
"""
import json
import sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
from partial_swap.paired import PairedExclusionCircuit
from partial_swap.shared import SharedPointCircuit
import importlib.util
_spec = importlib.util.spec_from_file_location('pr48_changed_graph', ROOT/'research/copied-fixed/changed_graph.py')
_pr48 = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(_pr48)
alternating_points = _pr48.alternating_points


def bits(h):
    d = json.loads((HERE/f'bits-{h}.json').read_text())
    assert d['h'] == h and all(b in (0, 1) for b in d['tbits']+d['vbits'])
    return d['tbits'], d['vbits']


def _swap(values, b, pos):
    for i in range(len(values)-1):
        k = pos[0]; pos[0] += 1
        if k < len(b) and b[k]:
            values[i], values[i+1] = values[i+1], values[i]


def graph(h, tbits=None, vbits=None):
    assert h in (23, 25)
    if tbits is None:
        tbits, vbits = bits(h)
    tp, vp = [0], [0]
    class Changed(PairedExclusionCircuit):
        base_threshold = 2
        def total(self, values):
            values = [x for x in values if x]
            if h == 23:
                values.reverse()
            else:
                values.sort(key=lambda n: (self.support[n].bit_count(), self.support[n]), reverse=True)
            _swap(values, tbits, tp)
            result = 0
            for node in values:
                result = self.add(result, node)
            return result
        def vector(self, values, two=True):
            if two:
                return super().vector(values, two)
            sign = 1 if h == 23 else -1
            order = sorted(range(len(values)), key=lambda i: (self.support[values[i]].bit_count(), sign*self.support[values[i]]))
            _swap(order, vbits, vp)
            total, one, _ = super().vector([values[i] for i in order], False)
            restored = [0]*len(values)
            for position, original in enumerate(order):
                restored[original] = one[position]
            return total, restored, {}
    local = Changed(h-1)
    total = local.pair(list(range(h-1)))[0]
    local.outputs[()] = total
    stack = [total]
    while stack:
        node = stack.pop()
        if not node or node in local.active:
            continue
        local.active.add(node)
        if local.args[node]:
            stack.extend(local.args[node])
    local.additions = sum(local.args[node] is not None for node in local.active)
    assert tp[0] == len(tbits) and vp[0] == len(vbits), 'Swap decision count mismatch'
    return SharedPointCircuit(h, local, point_order=alternating_points)
