"""Staggered dual-paired positive-label bit producer at h=23.

Copyright 2026 Thomas Marchand, Apache-2.0. Prepared with Google Antigravity
assistance. Adapted from scripts/partial_swap/graph.py (Copyright 2026
icekylinx), using the credited PairedExclusionCircuit and SharedPointCircuit
modules.
"""
from pathlib import Path

from partial_swap.graph import export
from partial_swap.paired import PairedExclusionCircuit
from partial_swap.positive import run as positive_labels
from partial_swap.shared import SharedPointCircuit


def alternating_points(h, common):
    pairs = [(a, a + 1) for a in range(0, h - 1, 2) if common not in (a, a + 1)]
    if common % 2:
        pairs.reverse()
    head = [x for pair in pairs for x in pair]
    return head + [x for x in range(h) if x != common and x not in head]


class StaggeredDualPaired(PairedExclusionCircuit):
    """PairedExclusionCircuit with reverse-folded block totals and staggered dual-paired strips."""

    def total(self, values):
        values = [x for x in values if x]
        values.reverse()
        result = 0
        for node in values:
            result = self.add(result, node)
        return result

    def vector(self, values, two=True):
        if two:
            return super().vector(values, two=True)
        n = len(values)
        if n >= 3 and values[0] == 0:
            st, one_nz, _ = self.vector(values[1:], two=False)
            return st, [st] + one_nz, {}
        prefix = [0] * (n + 1)
        for i in range(n):
            if i % 2 == 0:
                prefix[i + 1] = self.add(prefix[i], values[i])
            else:
                p = self.add(values[i - 1], values[i])
                prefix[i + 1] = self.add(prefix[i - 1], p)
        suffix = [0] * (n + 1)
        for i in range(n - 1, -1, -1):
            if i % 2 == 1 and i + 1 < n:
                q = self.add(values[i], values[i + 1])
                suffix[i] = self.add(q, suffix[i + 2])
            else:
                suffix[i] = self.add(values[i], suffix[i + 1])
        return prefix[n], [self.add(prefix[i], suffix[i + 1]) for i in range(n)], {}


def build(h, dag_path):
    assert h == 23
    local = StaggeredDualPaired(h - 1)
    total = local.pair(list(range(h - 1)))[0]
    local.outputs[()] = total
    stack = [total]
    while stack:
        node = stack.pop()
        if not node or node in local.active:
            continue
        local.active.add(node)
        if local.args[node]:
            stack.extend(local.args[node])
    local.additions = sum(local.args[x] is not None for x in local.active)
    circuit = SharedPointCircuit(h, local, point_order=alternating_points)
    scalar = circuit.verify()
    frames = circuit.verify_frames()
    dag_path = Path(dag_path)
    export(circuit, dag_path)
    return dict(scalar=scalar, frames=frames)
