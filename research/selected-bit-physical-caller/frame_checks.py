"""Selected descriptor/Frame checks with explicit controlled child consumers."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
import loader
loader.activate()

from hashlib import sha256
import json
from types import SimpleNamespace
from unittest.mock import patch
from cardinal_counts import Count
from catalogue import Catalogue, Specifications
from check_support import audit, bits, inspect_count, no_decode
from directory import Context, append_tape
from layout import Layout
import node
from numerical_frame import Session
from numeric import Geometry
import oracle
from packet import read_prefix
from records import Fields, Program, Tape
from recursive_call import child_call
from scheduler import complete
from trace import Event
from words import Arena, BLANK, Ring, need


def snapshot(arena):
    return {slot: (arena.words[slot], bytes(arena.words[slot].cells)) for slot in arena.live}


def restored(arena, expected):
    need(arena.live == set(expected), "same protected numerical roles after return")
    for slot, (word, value) in expected.items():
        need(arena.words[slot] is word and bytes(word.cells) == value and word.head == 1,
             "same parent Word alias, bits and head after return")


def selected_handoff(catalogue, mode="normal"):
    specifications = Specifications(catalogue)
    identifier = next(i for i, request in enumerate(catalogue.requests)
                      if request.kind == "IDLE" and request.base.rank == 42)
    template = catalogue.template_for(identifier, False)
    low = tuple(map(tuple, oracle.inverse(oracle.reduce_rational(template.preparation, 3), 3)))
    spec = specifications.bind(identifier, False, low)
    need(spec.good, "selected native rank-42 source class")
    indices, arena = Arena(10), Arena(3)
    modulus = arena.input(3)
    ring = Ring(modulus)
    context = Context(ring, catalogue.codes)
    size, depth, fields = (indices.input(value) for value in (256, 0, 1))
    program = Program.fixture(indices, arena, 256, 2, (), catalogue.codes.bits)
    root = node.SelectedNode(context, indices, program, size, depth, catalogue, specifications)
    high = [[0]*64 for _ in range(64)]
    field = Fields.fixture(indices, arena, [(spec.code, high)], catalogue.codes.bits)
    directory = Tape()
    for _ in range(2):
        append_tape(field.tape, directory)
    directory.rewind()
    field.tape.clear()
    counts = [Count.literal(value) for value in (2, 11, 2, 5, 3)]
    prefixes, stock, before, gap, suffix = counts
    source = Tape()
    initial = bytes((index*7 ^ index//3) & 1 for index in range(23))
    for bit in initial:
        source.append(bit)
    source.rewind()
    initial_program, initial_directory = bytes(program.tape.cells), bytes(directory.cells)
    protected = snapshot(arena), snapshot(indices)
    transitions, handoffs, returns, outputs = [], [], [], []
    labels = {}
    observed_frames = []

    def observe(kind, frame):
        if kind == "enter":
            level = inspect_count(frame.depth)
            labels[id(frame)] = level
            observed_frames.append(frame)
            need(frame.arena is arena and frame.indices is indices, "same numerical banks in the real Frame")
        transitions.append((kind, labels[id(frame)]))

    session = Session(arena, indices, observe=observe)

    def invoke(owner, current, old, count, field_count, unused, b, g, s):
        f = inspect_count(owner.parent_size)//64  # Checker-only fixture construction.
        columns = indices.input(f)
        geometry = Geometry(SimpleNamespace(dimension=64), indices, columns, owner.depth, spec.code, owner.program)
        leading = Count.product(unused, b)
        layout = Layout(geometry, owner.parent_size, owner.context.ring, 3, leading, g, s)
        operands = [indices.input(value) for value in (0, 86*f, 42*f, inspect_count(owner.depth)+1)]
        event = Event("invoke", operands[0], operands[1], width=operands[2], depth=operands[3],
                      child_kind="good", source_code=spec.code, parent_identity=owner.program)
        saved = snapshot(arena), snapshot(indices)
        old_payload, old_fields = bytes(current.cells), bytes(old.cells)
        try:
            output = yield from child_call(owner, current, event, layout, old, count, field_count, unused, b)
            restored(arena, saved[0])
            restored(indices, saved[1])
            need(bytes(current.cells) == old_payload and bytes(old.cells) == old_fields,
                 "real call preserves complete supplied source and frozen directory")
            return output
        finally:
            layout.close()
            geometry.close()
            leading.close()
            indices.free_many(columns, *operands)

    def controlled_run(self, current, old, count, unused, b, g, s, observe=None):
        level, width = inspect_count(self.depth), inspect_count(self.parent_size)
        need(self.indices is indices and self.context.arena is arena, "child executes in the shared banks")
        need((level, width) in ((1, 168), (2, 84)), "actual selected generated child widths")
        need(unused is stock and inspect_count(count) == 2 and inspect_count(unused) == 11,
             "separate repeated-prefix count and unused stock")
        need(tuple(inspect_count(x) for x in (b, g, s)) == (2, 5*3**(176 if level == 1 else 344), 3),
             "actual ordered child gap survives both frames")
        root_size, root_unit, root_depth = self.program.root()
        need(tuple(inspect_count(x) for x in (root_size, root_unit, root_depth)) == (256, 2, level),
             "child program retains original root and current generation")
        indices.free_many(root_size, root_depth)
        arena.free(root_unit)
        old.rewind()
        for _ in range(2):
            saved = read_prefix(old, self.depth)
            need(bits(saved) == bits(directory)[:len(bits(directory))//2]*level,
                 "ordered repeated physical prefixes remain independent")
            saved.clear()
        need(old.read() == BLANK, "exact old-prefix directory extent")
        old.rewind()
        handoffs.append({"depth": level, "width": width, "old_prefixes": 2, "fresh_rows": 11})
        if mode == "child_failure" and level == 2:
            # A failed child leaves a valid local Word. Cleanup must remove it
            # while the parent is still parked, then allow outer LIFO cleanup.
            arena.input(2)
            raise ValueError("injected deepest child failure")
        if level == 1:
            new_directory = Tape()
            new_field = Fields.fixture(indices, arena, [(spec.code, high)], catalogue.codes.bits)
            for _ in range(2):
                prefix = read_prefix(old, self.depth)
                append_tape(prefix, new_directory)
                append_tape(new_field.tape, new_directory)
                prefix.clear()
            old.rewind()
            new_directory.rewind()
            new_field.tape.clear()
            child_fields = indices.input(2)
            extents = [Count(value) for value in (b, g, s)]
            try:
                transformed = yield from invoke(self.consumer, current, new_directory, count,
                                                child_fields, unused, *extents)
                output = Tape()
                outputs.append(output)
                transformed.rewind()
                while transformed.read() in (0, 1):
                    output.append(1-transformed.read())
                    transformed.step(1)
                transformed.rewind()
                transformed.clear()
                output.rewind()
            finally:
                indices.free(child_fields)
                new_directory.clear()
                for value in extents:
                    value.close()
        else:
            output = Tape()
            outputs.append(output)
            for bit in reversed(bits(current)):
                output.append(bit)
            output.rewind()
        returns.append(level)
        return output

    original_node = node.SelectedNode
    def constructor_failure(*args, **kwargs):
        arena.input(2)
        raise ValueError("injected child constructor failure")
    error = None
    output = None
    try:
        with patch.object(original_node, "run_generator", controlled_run), session.install(), no_decode():
            if mode == "constructor_failure":
                with patch.object(node, "SelectedNode", constructor_failure):
                    output = complete(invoke(root.consumer, source, directory, prefixes, fields, stock, before, gap, suffix))
            else:
                output = complete(invoke(root.consumer, source, directory, prefixes, fields, stock, before, gap, suffix))
        need(mode == "normal", "injected lifecycle failure must propagate")
        need(bits(output) == bytes(1-bit for bit in reversed(initial)), "controlled nested endpoint")
        need(returns == [2, 1] and transitions == [("enter", 1), ("enter", 2), ("return", 2), ("return", 1)],
             "actual LIFO shared-frame return")
    except ValueError as failure:
        need(mode != "normal", "normal shared Frame failed: " + str(failure))
        error = str(failure)
        expected = "injected child constructor failure" if mode == "constructor_failure" else "injected deepest child failure"
        need(error == expected, "cleanup preserves the initiating failure")
    finally:
        restored(arena, protected[0])
        restored(indices, protected[1])
        need(bytes(source.cells)[1:] == initial and bytes(program.tape.cells) == initial_program and
             bytes(directory.cells) == initial_directory, "root borrowed inputs preserved")
        need(session.codec.machine.tapes == [{}, {0: "^"}] and session.codec.machine.heads == [0, 1],
             "shared numerical parking stack is empty after the complete source call")
        need(all(frame.closed for frame in observed_frames), "completed or aborted frames close")
        for item in outputs:
            item.clear()
        if output is not None:
            output.clear()
        source.clear()
        directory.clear()
        program.tape.clear()
        for value in counts:
            value.close()
        indices.free_many(size, depth, fields)
        context.close()
        ring.close()
        arena.free(modulus)
    audit(indices)
    audit(arena)
    return {"mode": mode, "source_request": identifier, "handoffs": handoffs,
            "transitions": transitions, "return_order": returns, "failure": error,
            "scope": "Actual selected descriptors, constructors and child_call; controlled 23-bit child bodies, not selected GL64 payload",
            "table_charge": dict(session.codec.machine.counts)}


def run():
    catalogue = Catalogue(3)
    return [selected_handoff(catalogue, mode) for mode in ("normal", "constructor_failure", "child_failure")]


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
