"""RaD / hipotures PR #41 alternating producer with hill-climbed summand orders.

Each total() call sorts its summands by descending (support size, support
bitmask) as in PR #44's optimal_graph.py, then walks adjacent pairs in order
and swaps a pair when the next pinned bit in bits-{h}.json is 1. Bits are
consumed globally in total() call order; missing bits mean no swap. With all
bits zero this is exactly PR #44's graph. Found by greedy bit-flip hill
climbing with optimal carrier matching in the loop.
Prepared by Rohan Arun with Anthropic Claude assistance. Apache-2.0.
"""
import importlib.util
import json
import sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
from partial_swap.paired import PairedExclusionCircuit
from partial_swap.shared import SharedPointCircuit
_spec = importlib.util.spec_from_file_location('pr43_changed_graph', ROOT/'research/copied-fixed/changed_graph.py')
_pr43 = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(_pr43)
alternating_points = _pr43.alternating_points  # RaD point order


def bits(h):
    d = json.loads((HERE/f'bits-{h}.json').read_text())
    assert d['h'] == h and all(b in (0, 1) for b in d['bits'])
    return d['bits']


def graph(h, swap_bits=None):
    assert h in (23, 25)
    b = bits(h) if swap_bits is None else swap_bits
    pos = [0]
    class Changed(PairedExclusionCircuit):
        base_threshold = 2
        def total(self, values):
            values = [x for x in values if x]
            values.sort(key=lambda node: (self.support[node].bit_count(), self.support[node]), reverse=True)
            for i in range(len(values)-1):
                k = pos[0]; pos[0] += 1
                if k < len(b) and b[k]:
                    values[i], values[i+1] = values[i+1], values[i]
            result = 0
            for node in values:
                result = self.add(result, node)
            return result
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
    assert pos[0] == len(b), 'Swap decision count mismatch'
    return SharedPointCircuit(h, local, point_order=alternating_points)
