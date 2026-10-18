"""Selected grammar through the new fixed-role CALL/RETURN boundary.

The controlled 23-bit child body checks the protocol, not a GL64 payload.
"""
from pathlib import Path
from dataclasses import replace
import sys
from types import SimpleNamespace
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import loader
loader.activate()
from cardinal_counts import Count
from catalogue import Catalogue, Specifications
from check_support import inspect_count, no_decode
from directory import append_tape
from frame_checks import restored, snapshot
from macro_binding import SelectedBinding, view
from macro_code import Code
from macro_machine import Machine
import macro_machine
import oracle
from packet import read_prefix
from plan import Request
from records import Fields, Program, Tape
from words import Arena, BLANK, need


def body(tape):
    return bytes(tape.cells[1:]).rstrip(bytes([BLANK]))


def run():
    catalogue = Catalogue(3)
    specifications = Specifications(catalogue)
    binding = SelectedBinding(specifications)
    identifier = next(i for i, request in enumerate(catalogue.requests)
                      if request.kind == "IDLE" and request.base.rank == 42)
    template = catalogue.template_for(identifier, False)
    low = tuple(map(tuple, oracle.inverse(oracle.reduce_rational(template.preparation, 3), 3)))
    definition = binding.residual(identifier, False, low, 0)
    need(definition.plan.good, "selected native good source")
    arena, indices = Arena(3), Arena(10)
    modulus, size, depth = arena.input(3), indices.input(256), indices.input(0)
    program = Program.fixture(indices, arena, 256, 2, (), catalogue.codes.bits)
    field = Fields.fixture(indices, arena, [(definition.code, [[0] * 64 for _ in range(64)])], catalogue.codes.bits)
    directory, old_directory, source = Tape(), Tape(), Tape()
    for _ in range(2):
        append_tape(field.tape, directory)
    directory.rewind()
    initial = bytes((i * 7 ^ i // 3) & 1 for i in range(23))
    for bit in initial:
        source.append(bit)
    source.rewind()
    saved_directory, saved_program = body(directory), body(program.tape)
    borrowed_words = snapshot(arena), snapshot(indices)
    old_count, stock, before, gap, suffix = [Count.literal(value) for value in (2, 11, 2, 5, 3)]
    topology = SimpleNamespace(families=1)
    code = Code((("block", definition, ("good", 1, 0)), ("return",)), 0)
    machine = Machine(binding, topology, (code,), Arena(3, 65536), Arena(10, 512))
    with machine.pool.install():
        machine.load_root(source, old_directory, program.tape, modulus, size, depth,
                          old_count, stock, before, gap, suffix)
        machine.commit(source, "current")
        machine.commit(directory, "directory")
        machine.commit(old_count.tape, "prefixes")
        machine.commit(stock.tape, "unused")
        machine.save_count(Count.product(stock, before), "leading")
        field_count, coordinate = machine.indices.literal(1), machine.indices.zero()
        first = read_prefix(machine.tape("directory"), field_count)
        machine.tape("directory").rewind()
        try:
            requests = (Request("adapter", coordinate, definition.plan.commands[0].reference),
                        Request("child", coordinate, child_kind="good"))
            for request, expected_value in zip(requests, (0, 2)):
                with no_decode():
                    coefficient = binding.coefficient(machine, definition, first, request)
                expected = machine.arena.literal(expected_value)
                need(machine.context.raw.compare(coefficient, expected) == 0,
                     "selected identity-projector adapter and generated child coefficients")
                machine.arena.free_many(coefficient, expected)
        finally:
            first.clear()
            machine.indices.free_many(field_count, coordinate)
        machine.boundary()
        parent_words = snapshot(machine.arena), snapshot(machine.indices)
        parent_roles = {label: body(tape) for label, tape in machine.roles.items()}
        rejected = []
        original_events = macro_machine.block_events
        for label, changes in (("wrong_parent", {"parent_identity": None}),
                               ("foreign_program", {"parent_identity": view(Program, machine, machine.program.tape)}),
                               ("wrong_source", {"source_code": definition.code + 1})):
            def malformed(page, block):
                iterator = original_events(page, block)
                try:
                    for event in iterator:
                        yield replace(event, **changes) if event.kind == "enter" else event
                finally:
                    iterator.close()
            try:
                with patch.object(macro_machine, "block_events", malformed):
                    machine.block(definition, ("good", 1, 0))
            except ValueError as error:
                need(str(error) == "recursive gate belongs to the current program and source",
                     "malformed gate rejects at its binding check")
                rejected.append(label)
            else:
                raise ValueError("malformed selected gate accepted")
            finally:
                machine.close_geometry()
            machine.boundary()
            restored(machine.arena, parent_words[0])
            restored(machine.indices, parent_words[1])
            need(all(body(tape) == parent_roles[name] for name, tape in machine.roles.items()) and
                 all(not body(tape) for tape in machine.handoff.values()) and machine.counts["calls"] == 0,
                 "reject before changing the parent or preparing a child capsule")
        with no_decode():
            need(machine.block(definition, ("good", 1, 0)), "internal selected child gate")
        machine.boundary()
        need(not machine.root and machine.pc == 0, "child enters its finite node label")
        need((inspect_count(machine.size), inspect_count(machine.depth)) == (168, 1),
             "selected width and generation grants")
        need(tuple(inspect_count(machine.count(label)) for label in ("old_count", "rows", "before", "gap", "suffix"))
             == (2, 11, 2, 5 * 3 ** 176, 3), "complete selected child capsule extents")
        root_size, root_unit, root_depth = machine.program.root()
        need(tuple(inspect_count(word) for word in (root_size, root_unit, root_depth)) == (256, 2, 1),
             "real selected extended root program")
        machine.indices.free_many(root_size, root_depth)
        machine.arena.free(root_unit)
        level = machine.indices.literal(1)
        metadata, parent_size, child_size = machine.program.step(level)
        need(metadata == (0, definition.code, 42, 0, 0, 0) and
             (inspect_count(parent_size), inspect_count(child_size)) == (256, 168),
             "real selected appended descriptor")
        machine.indices.free_many(level, parent_size, child_size)
        changed = bytes(1 - bit for bit in reversed(initial))
        for bit in changed:
            machine.output.append(bit)
        machine.output.rewind()
        with no_decode():
            need(not machine.complete_return(), "one parent restoration")
        need(machine.root and machine.pc == 1, "resume the serialized successor without replay")
        machine.boundary()
        restored(machine.arena, parent_words[0])
        restored(machine.indices, parent_words[1])
        for label, tape in machine.roles.items():
            need(body(tape) == (changed if label == "current" else parent_roles[label]),
                 "exact parent stream restoration and protected result commit")
        need(not body(machine.output), "consume protected child return port")
        machine.close_frame()
        machine.erase_work()
    need(body(source) == initial and body(directory) == saved_directory and
         body(program.tape) == saved_program and not body(old_directory) and
         source.head == directory.head == old_directory.head == program.tape.head == 1,
         "controlled borrowed streams and heads preserved")
    restored(arena, borrowed_words[0])
    restored(indices, borrowed_words[1])
    result = dict(source_request=identifier, child_width=168, depth=1,
                  parent_successor_pc=1, source_bits=23, peak_scratch_leases=machine.pool.peak,
                  selected_coefficients=[0, 2],
                  rejected_gates=rejected,
                  counts=machine.counts, parking_charge=machine.numerical.machine.counts,
                  scope="Actual selected grammar, fixed-role CALL/RETURN; controlled child body and unused stock 11")
    field.tape.clear()
    program.tape.clear()
    source.clear()
    directory.clear()
    old_directory.clear()
    for value in (old_count, stock, before, gap, suffix):
        value.close()
    arena.free(modulus)
    indices.free_many(size, depth)
    need(not arena.live and not indices.live, "closed selected fixture")
    return result


if __name__ == "__main__":
    import json
    print(json.dumps(run(), indent=2, sort_keys=True))
