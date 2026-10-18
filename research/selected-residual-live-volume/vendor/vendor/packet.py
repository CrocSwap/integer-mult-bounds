"""One shared trace across a sequential directory of complete raw prefixes.

Each primitive traverses the whole packet before the next trace event. Child
entry/return occur once for the packet, never once per sampled high header.
"""
from bitstream import copy_bits
from cardinality import Natural, multiply_atom_power
from records import RECORD_END, Tape
from stream import Counter, positive_extent
from stream_runner import Layout, action
from trace import execute
from words import BLANK, need


def read_prefix(directory, field_count):
    out, remaining = Tape(), Counter(field_count)
    while not remaining.finished:
        while directory.read() != RECORD_END:
            symbol = directory.read()
            need(symbol != BLANK, "complete raw-prefix directory")
            out.append(symbol)
            directory.step(1)
        out.append(RECORD_END)
        directory.step(1)
        remaining.decrement()
    remaining.close()
    out.rewind()
    return out


def copy_prefix(source, output, before, body):
    count = Counter(before)
    while not count.finished:
        copy_bits(source, output, body)
        count.decrement()
    count.close()


def run(source, geometry, parent_size, ring, q, before, suffix, prefix_count,
        field_count, directory, coefficient, payload_factory=Tape, boundary_observer=None):
    positive_extent(prefix_count)
    expected_fields = geometry.plus(geometry.depth, geometry.one)
    matches = geometry.raw.compare(field_count, expected_fields) == 0
    geometry.index.free(expected_fields)
    need(matches, "original frozen/current field count")
    layout = Layout(geometry, parent_size, ring, q, before, suffix)
    body = Natural(suffix)
    multiply_atom_power(body, layout.total, ring, q)
    current, active = source, None
    try:
        for event in execute(geometry):
            if event.kind == "enter":
                need(active is None and event.parent_identity is geometry.parent_identity,
                     "one whole-packet child invocation")
                active = event
                if boundary_observer is not None:
                    boundary_observer(event.kind)
                continue
            if event.kind == "return":
                need(active is not None and active.parent_identity is event.parent_identity and
                     (active.child_kind, active.field, active.reverse, active.half, active.source_code) ==
                     (event.child_kind, event.field, event.reverse, event.half, event.source_code),
                     "whole-packet symbolic return")
                for a, b in ((active.first, event.first), (active.second, event.second),
                             (active.width, event.width), (active.depth, event.depth)):
                    need(geometry.raw.compare(a, b) == 0, "whole-packet encoded child return")
                active = None
                if boundary_observer is not None:
                    boundary_observer(event.kind)
                continue
            output, prefixes = payload_factory(), Counter(prefix_count)
            directory.rewind()
            while not prefixes.finished:
                fields = read_prefix(directory, field_count)
                local = payload_factory()
                copy_prefix(current, local, before, body)
                local.rewind()
                changed = action(local, event, layout, lambda request: coefficient(fields, request), payload_factory)
                copy_prefix(changed, output, before, body)
                need(changed.read() == BLANK, "complete returned prefix fibre")
                changed.clear()
                local.clear()
                fields.clear()
                prefixes.decrement()
            prefixes.close()
            need(current.read() == directory.read() == BLANK, "complete shared high packet")
            current.rewind()
            directory.rewind()
            if current is not source:
                current.clear()
            output.rewind()
            current = output
        need(active is None, "whole-packet child return")
        return current
    finally:
        layout.close()
        body.close()
