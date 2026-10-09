"""Retained-total triples, aligned global pairs, weighted base threshold two.

Copyright 2026 icekylinx. Apache-2.0; adapted with AI assistance from
triple_graph.py in the partial-swap handoff, using the PR7 circuit modules.
"""
import array
import struct

from .binary import write_array
from .paired import PairedExclusionCircuit
from .shared import SharedPointCircuit


def aligned_points(h, common):
    head = [j for a in range(0, h-1, 2) if common not in (a, a+1)
            for j in (a, a+1)]
    return head + [j for j in range(h) if j != common and j not in head]


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


def export(circuit, path):
    roots = list(circuit.outputs.values())
    kinds = [int(len(target) == 1) for _, target in circuit.outputs]
    with open(path, 'wb') as stream:
        stream.write(struct.pack('<4I', circuit.h, len(circuit.inputs),
                                 len(circuit.args), len(roots)))
        write_array(stream, array.array('I', (y for args in circuit.args
                                              for y in (args or (0, 0)))))
        for values in (circuit.core, circuit.union):
            write_array(stream, array.array('Q', values))
        for values in (roots, kinds):
            write_array(stream, array.array('I', values))
        stream.write(bytes(int(x in circuit.active) for x in range(len(circuit.args))))
