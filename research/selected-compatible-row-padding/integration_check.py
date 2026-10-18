"""Unchanged recursive-caller Node on a one-family two-MOVE GL2(F3) fixture.

The source Node, Driver, model normal forms and one-family topology execute
unchanged. Source tables, modulus, weights and provenance are fixture inputs.
This is neither the four-family source model nor selected GL64 execution.
"""

from hashlib import sha256

import model
import padding
from cardinal_counts import Count
from check_nested_model import Topology
from check_runtime import Tracker
from check_support import audit, no_decode
from directory import Context
from low_codes import LowCodes
from node import Node
from records import Tape
from source import require
from words import Arena, Ring


def destination(address):
    """Independent width-two, radix-three weighted reversal at gap=suffix=1."""
    row, body = divmod(address, 81)
    head, tail = divmod(body, 9)
    h0, h1 = divmod(head, 3)
    t0, t1 = divmod(tail, 3)
    return row * 81 + ((2 * t1 % 3) * 3 + t0) * 9 + h1 * 3 + 2 * h0 % 3


def check_endpoint(source, result, saved, old, tracker, consumer):
    for address in range(49 * 81):
        target = destination(address)
        require(
            result.origins.get(target + 1) == 1 << address
            and result.cells[target + 1] == saved[address + 1],
            "all genuine Boolean columns and values after actual source Node",
        )
    require(
        bytes(source.cells) == saved and source.head == result.head == old.head == 1,
        "input, directory and heads preserved",
    )
    require(tracker.live == {source, result}, "all tracked caller/wrapper work erased")
    require(
        consumer.children["enter"] == consumer.children["return"] > 0,
        "all completed source child returns",
    )


def receipt(consumer, result):
    return {
        "domain": "one-family GL2(F3) two-MOVE model, not selected GL64",
        "genuine_rows": 49,
        "stock_divisor": 48,
        "compatible_rows": 96,
        "genuine_columns": 49 * 81,
        "added_zero_columns": 47 * 81,
        "children": dict(sorted(consumer.children.items())),
        "residuals": dict(sorted(consumer.calls.items())),
        "output_sha256": sha256(bytes(result.cells)).hexdigest(),
    }


def run_node():
    catalogue = model.Catalogue()
    # Finite fixture source: two complementary rank-one MOVE requests.
    # The one-family Topology is retained unchanged from the nested model.
    catalogue.requests = (model.Request("MOVE", 0, 0), model.Request("MOVE", 1, 0))
    catalogue.codes = LowCodes(3, 2, 2)
    topology = Topology(catalogue)
    arena, indices = Arena(3), Arena(8)
    modulus = arena.input(3)
    ring = Ring(modulus)
    context = Context(ring, catalogue.codes)
    size, depth = indices.input(2), indices.input(0)
    program = object()
    incoming = model.Incoming(context, indices, (2, 1))
    consumer = model.Consumer(
        context, indices, program, size, depth, catalogue, incoming
    )
    node = Node(context, indices, program, size, depth, topology, consumer, incoming)
    tracker = Tracker()
    source = tracker.source(49 * 81)
    saved = bytes(source.cells)
    old = Tape()
    old_count, before, gap, suffix = (Count.literal(1) for _ in range(4))
    prefixes, rows, stock, body = (Count.literal(v) for v in (1, 49, 48, 81))
    original_tape, original_scan = padding.Tape, padding.scan_rows
    padding.Tape = tracker.payload

    def annotated_scan(source, output, count, width, mode):
        if mode == "zero":
            tracker.last = (
                0  # Checker provenance of a literal zero, not a runtime gate.
            )
        return original_scan(source, output, count, width, mode)

    padding.scan_rows = annotated_scan

    def callee(padded, row_count):
        require(bytes(padded.cells[1:]).count(4) == 0, "complete padded payload")
        return node.run(padded, old, old_count, row_count, before, gap, suffix)

    result = None
    try:
        with tracker.install(), no_decode():
            result = padding.complete(source, prefixes, rows, stock, body, callee)
        check_endpoint(source, result, saved, old, tracker, consumer)
        return receipt(consumer, result)
    finally:
        padding.Tape, padding.scan_rows = original_tape, original_scan
        if result is not None:
            result.clear()
        source.clear()
        old.clear()
        for count in (old_count, before, gap, suffix, prefixes, rows, stock, body):
            count.close()
        incoming.close()
        indices.free_many(size, depth)
        context.close()
        ring.close()
        arena.free(modulus)
        audit(indices)
        audit(arena)
