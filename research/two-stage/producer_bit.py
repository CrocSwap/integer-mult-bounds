"""Ordinary-base retained triples for the endpoint-gauge construction.

Copyright 2026 icekylinx, Apache-2.0. AI-assisted integration of the research
handoff; paired circuit by the credited PR7 contributors. The ordinary base
threshold is four, distinct from the preceding partial-swap base-two choice.
"""
from paired_exclusion_circuit import PairedExclusionCircuit
from partial_swap.graph import aligned_points, export
from partial_swap.shared import SharedPointCircuit


def graph(h):
    local = PairedExclusionCircuit(h-1)
    total = local.pair(list(range(h-1)))[0]
    local.outputs[()] = total
    stack = [total]
    while stack:
        node = stack.pop()
        if node in local.active:
            continue
        local.active.add(node)
        if local.args[node]:
            stack.extend(local.args[node])
    local.additions = sum(local.args[x] is not None for x in local.active)
    return SharedPointCircuit(h, local, point_order=aligned_points)
