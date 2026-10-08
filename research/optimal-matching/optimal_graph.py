"""RaD / hipotures PR #41 alternating producer with descending summand order at both h.

Identical to research/copied-fixed/changed_graph.py (PR #43) except that the
descending (support size, support bitmask) summand sort is applied at h=25 as
well as h=23. At h=23 the exported DAG is byte-identical to PR #43's.
"""
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'scripts'))
from partial_swap.paired import PairedExclusionCircuit
from partial_swap.shared import SharedPointCircuit
import importlib.util
_spec = importlib.util.spec_from_file_location('pr43_changed_graph', ROOT/'research/copied-fixed/changed_graph.py')
_pr43 = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(_pr43)
alternating_points = _pr43.alternating_points  # PR #43 / RaD point order


def graph(h):
    assert h in (23, 25)
    class Changed(PairedExclusionCircuit):
        base_threshold = 2
        def total(self, values):
            values = [x for x in values if x]
            values.sort(key=lambda node: (self.support[node].bit_count(), self.support[node]), reverse=True)
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
    return SharedPointCircuit(h, local, point_order=alternating_points)
