"""Actual selected descriptors through literal Machine CALL/RETURN.

Fixtures use arbitrary 23-bit protected results, not full GL64 payloads. The
fallback tests lower only the dispatch cutoff to 2 to reach both half cuts at
manageable n=257. The good test retains the production cutoff 64. This extends
Jose Manuel's macro_selected_checks fixture to actual fallback flags and
nonzero remainder geometry; it does not certify a child implementation.
"""

from types import SimpleNamespace

import specification as spec


def body(tape):
    from words import BLANK

    return bytes(tape.cells[1:]).rstrip(bytes([BLANK]))


def source_definitions():
    import oracle
    from catalogue import Catalogue, Specifications
    from macro_binding import SelectedBinding

    catalogue = Catalogue(3)
    binding = SelectedBinding(Specifications(catalogue))
    identifier = next(
        i
        for i, item in enumerate(catalogue.requests)
        if item.kind == "IDLE" and item.base.rank == 42
    )
    template = catalogue.template_for(identifier, False)
    low = oracle.inverse(oracle.reduce_rational(template.preparation, 3), 3)
    good = binding.residual(identifier, False, tuple(map(tuple, low)), 0)
    low[0], low[63] = low[63], low[0]
    fallback = binding.residual(identifier, False, tuple(map(tuple, low)), 0)
    spec.need(
        good.plan.good and not fallback.plan.good, "two real selected low classes"
    )
    spec.need(
        len(fallback.plan.commands) <= 32894, "bounded 128-field compiler grammar"
    )
    return binding, good, fallback


def setup(binding, definition, block):
    from cardinal_counts import Count
    from directory import append_tape
    from macro_code import Code
    from macro_machine import Machine
    from records import Fields, Program, Tape
    from words import Arena

    arena, indices = Arena(3), Arena(10)
    modulus, size, depth = arena.input(3), indices.input(257), indices.input(0)
    program = Program.fixture(indices, arena, 257, 2, (), binding.codes.bits)
    field = Fields.fixture(
        indices,
        arena,
        [(definition.code, [[0] * 64 for _ in range(64)])],
        binding.codes.bits,
    )
    directory, old_directory, source = Tape(), Tape(), Tape()
    for _ in range(2):
        append_tape(field.tape, directory)
    directory.rewind()
    for bit in bytes((i * 7 ^ i // 3) & 1 for i in range(23)):
        source.append(bit)
    source.rewind()
    counts = [Count.literal(value) for value in (2, 11, 2, 5, 3)]
    code = Code((("block", definition, block), ("return",)), 0)
    machine = Machine(
        binding, SimpleNamespace(families=1), (code,), Arena(3, 65536), Arena(10, 512)
    )
    machine.load_root(
        source, old_directory, program.tape, modulus, size, depth, *counts
    )
    machine.commit(source, "current")
    machine.commit(directory, "directory")
    machine.commit(counts[0].tape, "prefixes")
    machine.commit(counts[1].tape, "unused")
    machine.save_count(Count.product(counts[1], counts[2]), "leading")
    external = (
        arena,
        indices,
        modulus,
        size,
        depth,
        program,
        field,
        directory,
        old_directory,
        source,
        counts,
    )
    return machine, external


def capsule_expectation(definition, block):
    from specification import spectator_extents

    kind, position, stage = block
    if kind == "good":
        first, second, width = (
            0,
            (128 - definition.plan.rank) * 4,
            definition.plan.rank * 4,
        )
        flags = (0, definition.code, definition.plan.rank, 0, 0, 0)
    else:
        command = definition.plan.commands[position]
        i, k = command.target, command.source
        if stage != 1:
            first, second, width = k * 4, (k + 1) * 4 - 2, 2
            flags = (2, definition.code, 42, 0, 0, 1)
        else:
            first, second, width = i * 4, k * 4, 4
            pair = command.reference.kind == "pair"
            flags = (
                1 if pair else 2,
                definition.code,
                42,
                i if pair else 0,
                int(i >= 64) if pair else 0,
                0,
            )
    # The actual n=257 has two unused body atoms between the compact banks.
    a, b = first + (2 if first >= 256 else 0), second + (2 if second >= 256 else 0)
    extents, region = spectator_extents(257, 2, 5, 3, a, b, width)
    return width, flags, tuple(c * 3**e for c, e in extents), region


def inspect_child(machine, definition, block, parent_roles):
    from check_support import inspect_count

    width, flags, extents, region = capsule_expectation(definition, block)
    spec.need(
        body(machine.tape("source")) == parent_roles["current"],
        "whole child source copied",
    )
    spec.need(
        body(machine.tape("old_directory")) == parent_roles["directory"],
        "whole child directory copied",
    )
    actual = tuple(
        inspect_count(machine.count(label))
        for label in ("old_count", "rows", "before", "gap", "suffix")
    )
    spec.need(
        actual == (2, 11, *extents), "complete child capsule without duplicated U"
    )
    spec.need(
        (inspect_count(machine.size), inspect_count(machine.depth)) == (width, 1),
        "child numeric grants",
    )
    root_size, root_unit, root_depth = machine.program.root()
    try:
        spec.need(
            tuple(inspect_count(x) for x in (root_size, root_unit, root_depth))
            == (257, 2, 1),
            "unchanged root and incremented depth",
        )
    finally:
        machine.indices.free_many(root_size, root_depth)
        machine.arena.free(root_unit)
    level = machine.indices.literal(1)
    try:
        metadata, parent_size, child_size = machine.program.step(level)
        try:
            spec.need(metadata == flags, "real appended child metadata")
            spec.need(
                (inspect_count(parent_size), inspect_count(child_size)) == (257, width),
                "descriptor width agrees with grants",
            )
        finally:
            machine.indices.free_many(parent_size, child_size)
    finally:
        machine.indices.free(level)
    return {
        "width": width,
        "kind": flags[0],
        "field": flags[3],
        "reverse": flags[4],
        "half": flags[5],
        "gap_region": region,
    }


def close_external(external):
    (
        arena,
        indices,
        modulus,
        size,
        depth,
        program,
        field,
        directory,
        old_directory,
        source,
        counts,
    ) = external
    for tape in (program.tape, field.tape, directory, old_directory, source):
        tape.clear()
    for value in counts:
        value.close()
    arena.free(modulus)
    indices.free_many(size, depth)
    spec.need(not arena.live and not indices.live, "external fixture cleanup")


def capsule_controls(machine, definition, block, parent_roles):
    """Reject loss of either complete handoff tape, then restore the fixture."""
    for label, message in (
        ("source", "whole child source copied"),
        ("old_directory", "whole child directory copied"),
    ):
        tape = machine.tape(label)
        saved = body(tape)
        tape.clear()
        try:
            try:
                inspect_child(machine, definition, block, parent_roles)
            except ValueError as error:
                spec.need(
                    str(error) == message, "capsule control reaches byte relation"
                )
            else:
                raise ValueError("truncated handoff accepted: " + label)
        finally:
            for symbol in saved:
                tape.append(symbol)
            tape.rewind()


def one(binding, definition, cutoff, block, corrupt=None):
    from check_support import no_decode
    from frame_checks import restored, snapshot

    binding.cutoff = cutoff
    machine, external = setup(binding, definition, block)
    parent_roles = {label: body(tape) for label, tape in machine.roles.items()}
    parent_words = snapshot(machine.arena), snapshot(machine.indices)
    borrowed = tuple(
        body(tape) for tape in (external[5].tape, external[7], external[9])
    )
    closed = False
    try:
        with machine.pool.install(), no_decode():
            spec.need(machine.block(definition, block), "real internal block dispatch")
            machine.boundary()
            observed = inspect_child(machine, definition, block, parent_roles)
            if block[0] == "good":
                capsule_controls(machine, definition, block, parent_roles)
            changed = bytes(1 - bit for bit in reversed(parent_roles["current"]))
            for bit in changed:
                machine.output.append(bit)
            machine.output.rewind()
            spec.need(not machine.complete_return(), "one successful parent return")
            if corrupt == "pc":
                machine.pc -= 1
            spec.need(machine.root and machine.pc == 1, "resume successor exactly once")
            machine.boundary()
            restored(machine.arena, parent_words[0])
            restored(machine.indices, parent_words[1])
            for label, tape in machine.roles.items():
                spec.need(
                    body(tape)
                    == (changed if label == "current" else parent_roles[label]),
                    "contextual parent stream restoration",
                )
            spec.need(not body(machine.output), "protected result consumed")
            spec.need(
                tuple(
                    body(tape) for tape in (external[5].tape, external[7], external[9])
                )
                == borrowed,
                "borrowed source streams preserved",
            )
            machine.close_frame()
            machine.erase_work()
            closed = True
        return observed
    finally:
        if not closed:
            machine.close_frame()
            machine.erase_work()
        close_external(external)


def run():
    binding, good, fallback = source_definitions()
    entries = [(good, 64, ("good", 1, 0))]
    # Choose actual selected commands, not a synthetic fallback plan.
    for bank in (False, True):
        position = next(
            j
            for j, c in enumerate(fallback.plan.commands)
            if c.kind == "child"
            and c.reference.kind == ("pair" if bank else "unit")
            and (c.target >= 64) == bank
            and (c.source >= 64) == bank
        )
        entries.extend((fallback, 2, ("pair", position, stage)) for stage in range(3))
    cross = next(
        j
        for j, c in enumerate(fallback.plan.commands)
        if c.kind == "child"
        and c.reference.kind == "unit"
        and c.target < 64 <= c.source
    )
    entries.append((fallback, 2, ("pair", cross, 1)))
    result = [
        one(binding, definition, cutoff, block) for definition, cutoff, block in entries
    ]
    # Controls after successful return can cleanly close the parent. The source
    # and directory controls exercise inspect_child directly on the live child.
    try:
        one(binding, good, 64, ("good", 1, 0), corrupt="pc")
    except ValueError as error:
        spec.need(str(error) == "resume successor exactly once", "wrong-PC contract")
    else:
        raise ValueError("wrong-PC control accepted")
    return {
        "calls": result,
        "wrong_pc_rejected": True,
        "truncated_source_and_directory_rejected": True,
        "source_request": good.identifier,
        "fallback_commands": len(fallback.plan.commands),
        "scope": "23-bit opaque child result; fallback dispatch cutoff 2; good cutoff 64; n=257",
    }
