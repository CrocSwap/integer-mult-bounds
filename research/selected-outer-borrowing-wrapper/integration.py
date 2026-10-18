"""Unchanged PR2753 Node/Driver on the retained one-family GL2(F2) toy.

This is complete toy payload execution, not the selected odd-prime GL64
supplier. The stock and low-code vocabulary are the predecessor's toy input.
"""

from cardinal_counts import Count
from check_nested_model import Catalogue, Topology
from check_support import audit
from checks import case
from directory import Context
from model import Consumer, Incoming
from node import Node
from predecessor import require
from records import Tape
from words import Arena, Ring


def run_node():
    arena, indices = Arena(3), Arena(8)
    modulus = arena.input(2)
    ring = Ring(modulus)
    catalogue = Catalogue()
    context = Context(ring, catalogue.codes)
    size, depth = indices.input(2), indices.input(0)
    program = object()
    incoming = Incoming(context, indices, (1, 1))
    consumer = Consumer(context, indices, program, size, depth, catalogue, incoming)
    node = Node(
        context, indices, program, size, depth, Topology(catalogue), consumer, incoming
    )
    old, one, gap = Tape(), Count.literal(1), Count.literal(8)
    before = tuple(bytes(value.cells) for value in (size, depth, incoming.tape, old))

    def callee(source, rows):
        return node.run(source, old, one, rows, one, gap, one)

    try:
        result = case(q=2, n=2, k=3, stock_value=6, callee_factory=callee)
        after = tuple(bytes(value.cells) for value in (size, depth, incoming.tape, old))
        require(
            before == after, "frozen source metadata and generation depth unchanged"
        )
        require(
            all(value.head == 1 for value in (size, depth, incoming.tape, old)),
            "all frozen metadata heads restored",
        )
        require(consumer.calls == {"MOVE": 24}, "both full six-class two-MOVE calls")
        require(
            consumer.children == {"enter": 240, "return": 240},
            "all source children return before row restriction",
        )
        result.update(
            {
                "domain": "one-family GL2(F2) toy, not selected GL64",
                "residuals": dict(consumer.calls),
                "children": dict(consumer.children),
            }
        )
        return result
    finally:
        old.clear()
        one.close()
        gap.close()
        incoming.close()
        indices.free_many(size, depth)
        context.close()
        ring.close()
        arena.free(modulus)
        audit(arena)
        audit(indices)
