"""Actual compact TARGET114 at the physical bank and CALL/RETURN boundary.

Adapted from Jose Manuel's macro_selected_checks.py (Apache-2.0). The changed
source, full compact role inventory, threshold and complete backing checks are
by JoyboyBrian with substantial OpenAI Codex assistance. This is a protocol
calibration with an explicit controlled child body, not a GL64 payload proof.
"""
import ast
from pathlib import Path
from hashlib import sha256
from dataclasses import replace
from unittest.mock import patch
from cardinal_counts import Count
from catalogue import Specifications
from check_support import inspect_count, no_decode
from directory import append_tape
from frame_checks import restored, snapshot
from macro_binding import SelectedBinding, view
from macro_code import Code
import macro_code
from macro_machine import Machine
import macro_machine
import oracle
from packet import read_prefix
from plan import Request
from records import Fields, Program, Tape
from words import Arena, BLANK, need

def body(tape):
    return bytes(tape.cells[1:]).rstrip(bytes([BLANK]))


def generated_region(binding, low):
    """Execute the actual, unmodified nested compiler residual emitter.

    Only its finite lexical environment is supplied. No opcode body or source
    constant is rewritten. This is one actual residual region, not GL64 word
    enumeration and not a replacement payload implementation.
    """
    tree = ast.parse(Path(macro_code.__file__).read_bytes())
    compiler = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == 'compile_node')
    emitters = [node for node in compiler.body if isinstance(node, ast.FunctionDef) and node.name == 'residual']
    need(len(emitters) == 1, 'unique actual compiler residual emitter')
    emitter = emitters[0]
    operations = []
    namespace = dict(binding=binding, mode=0, operations=operations, Cursor=macro_code.Cursor)
    exec(compile(ast.Module(body=[emitter], type_ignores=[]), str(macro_code.__file__), 'exec',
                 dont_inherit=True, optimize=0), namespace)
    namespace['residual'](('stage', 114), 1933, True, low)
    need([operation[0] for operation in operations] ==
         ['residual_begin', 'block', 'block', 'block', 'residual_end'], 'actual generated region')
    need([operation[2] for operation in operations if operation[0] == 'block'] ==
         [('forward', 0, 0), ('good', 1, 0), ('backward', 2, 0)], 'exact generated child successor')
    return Code(tuple(operations) + (('return',),), 659), sha256(ast.dump(emitter).encode()).hexdigest()


def run(catalogue):
    specifications = Specifications(catalogue)
    binding = SelectedBinding(specifications)
    identifier = 1933
    template = catalogue.template_for(identifier, True)
    low = tuple(map(tuple, oracle.inverse(oracle.reduce_rational(template.preparation, 3), 3)))
    definition = binding.residual(identifier, True, low, 0)
    need(definition.plan.good, "selected native good source")
    arena, indices = Arena(3), Arena(11)
    modulus, size, depth = arena.input(3), indices.input(640), indices.input(0)
    program = Program.fixture(indices, arena, 640, 2, (), catalogue.codes.bits)
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
    borrowed_tapes = (source, directory, old_directory, program.tape,
                      *(value.tape for value in (old_count, stock, before, gap, suffix)))
    protected_tapes = [(tape, bytes(tape.cells), tape.head) for tape in borrowed_tapes]
    topology = catalogue._recursive_caller_topology
    code, emitter_sha = generated_region(binding, low)
    definition = code.operations[0][2]
    operation = code.operations[2]
    need(operation[1] is definition, 'generated source identity at child opcode')
    machine = Machine(binding, topology, (code,), Arena(3, 65536), Arena(11, 512))
    with machine.pool.install():
        machine.load_root(source, old_directory, program.tape, modulus, size, depth,
                          old_count, stock, before, gap, suffix)
        machine.commit(source, "current")
        machine.commit(source, ("stage", 114))
        # Enter the actual emitted CHILD opcode after its complete forward block.
        # The fixture supplies its prepared packet explicitly; no full adapter
        # or GL64 payload execution is claimed.
        machine.pc = 2
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
        # Distinct nontrivial parked parent roles, including the last ordinary
        # stage and last family; the private role stays empty at this MOVE.
        for label in (("stage", 0), ("stage", 657), ("family", 0), ("family", 28415)):
            for bit in (1, 0, 1, 1):
                machine.tape(label).append(bit)
            machine.tape(label).rewind()
        machine.boundary()
        parent_words = snapshot(machine.arena), snapshot(machine.indices)
        parent_roles = {label: body(tape) for label, tape in machine.roles.items()}
        rejected = []
        original_events = macro_machine.block_events
        for label, changes in (("wrong_parent", {"parent_identity": None}),
                               ("foreign_program", {"parent_identity": view(Program, machine, machine.program.tape)}),
                               ("wrong_source", {"source_code": definition.code + 1}),
                               ("noncontracting_width", {"width": machine.size})):
            def malformed(page, block):
                iterator = original_events(page, block)
                try:
                    for event in iterator:
                        yield replace(event, **changes) if event.kind == "enter" else event
                finally:
                    iterator.close()
            try:
                with patch.object(macro_machine, "block_events", malformed):
                    machine.dispatch(operation)
            except ValueError as error:
                need(str(error) == ("strict child contraction" if label == "noncontracting_width" else
                                    "recursive gate belongs to the current program and source"),
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
            need(machine.dispatch(operation) == "jump", "actual generated internal child opcode")
        machine.boundary()
        need(not machine.root and machine.pc == 0, "child enters its finite node label")
        need((inspect_count(machine.size), inspect_count(machine.depth)) == (70, 1),
             "selected width and generation grants")
        need(tuple(inspect_count(machine.count(label)) for label in ("old_count", "rows", "before", "gap", "suffix"))
             == (2, 11, 2, 5 * 3 ** 1140, 3), "complete selected child capsule extents")
        root_size, root_unit, root_depth = machine.program.root()
        need(tuple(inspect_count(word) for word in (root_size, root_unit, root_depth)) == (640, 2, 1),
             "real selected extended root program")
        machine.indices.free_many(root_size, root_depth)
        machine.arena.free(root_unit)
        level = machine.indices.literal(1)
        metadata, parent_size, child_size = machine.program.step(level)
        need(metadata == (0, definition.code, 7, 0, 0, 0) and
             (inspect_count(parent_size), inspect_count(child_size)) == (640, 70),
             "real selected appended descriptor")
        machine.indices.free_many(level, parent_size, child_size)
        changed = bytes(1 - bit for bit in reversed(initial))
        for bit in changed:
            machine.output.append(bit)
        machine.output.rewind()
        with no_decode():
            need(not machine.complete_return(), "one parent restoration")
        need(machine.root and machine.pc == 3, "resume the serialized successor without replay")
        machine.boundary()
        restored(machine.arena, parent_words[0])
        restored(machine.indices, parent_words[1])
        for label, tape in machine.roles.items():
            need(body(tape) == (changed if label == "current" else parent_roles[label]),
                 "exact parent stream restoration and protected result commit")
        need(not body(machine.output), "consume protected child return port")
        machine.close_frame()
        machine.erase_work()
        owned = (*machine.roles.values(), *machine.handoff.values(), *machine.pool.tapes)
        need(all(t.head == 1 and all(symbol == BLANK for symbol in t.cells) for t in owned),
             "all owned visited stream backing and markers erased")
        need(machine.numerical.machine.tapes == [{}, {}], "both parking tapes including origin erased")
        need(all(not any(symbol != BLANK for symbol in w.cells)
                 for a in (machine.arena, machine.indices) for w in (*a.words, a.template)),
             "all numerical backing and templates erased")
    need(body(source) == initial and body(directory) == saved_directory and
         body(program.tape) == saved_program and not body(old_directory) and
         source.head == directory.head == old_directory.head == program.tape.head == 1,
         "controlled borrowed streams and heads preserved")
    need(all(bytes(tape.cells) == raw and tape.head == head == 1 for tape, raw, head in protected_tapes),
         "every borrowed stream/count body, backing and head preserved")
    restored(arena, borrowed_words[0])
    restored(indices, borrowed_words[1])
    result = dict(source_request=identifier, child_width=70, depth=1,
                  parent_successor_pc=3, source_bits=23, peak_scratch_leases=machine.pool.peak,
                  selected_coefficients=[0, 2],
                  rejected_gates=rejected,
                  counts=machine.counts, parking_charge=machine.numerical.machine.counts,
                  generated_region_operations=len(code.operations), generated_child_pc=2,
                  generated_successor_block=code.operations[3][2][0], emitter_ast_sha256=emitter_sha,
                  permanent_roles=len(machine.roles), staged_roles=code.staged_roles,
                  scratch_capacity=len(machine.pool.tapes), bank_capacities=[machine.arena.capacity, machine.indices.capacity],
                  numerical_codec=machine.numerical.codec_counts,
                  all_owned_backing_erased=True,
                  scope="Actual compact TARGET114, all permanent roles and physical banks/CALL/RETURN; controlled 23-bit child body, stock11, not a complete GL64 payload")
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

