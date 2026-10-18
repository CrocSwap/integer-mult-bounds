"""Complete reduced two-level return with Q*b^2, not (Q*b)^2.

The fixture grammar and controller checks follow Jose Manuel's PR2809
macro_checks and David Arias's PR2753 nested model; neither source is changed.
New premise: Q=2 at EVERY NODE, R=72, whereas the repeated-factor reserve is144.
"""
from hashlib import sha256
from unittest.mock import patch

from cardinal_counts import Count
from check_support import no_decode
import check_nested_model as model
from directory import Context
from macro_binding import ToyBinding
from macro_code import compile_node
from macro_machine import Machine
from records import Tape
import scheduler
from words import Arena, BLANK, Ring, need


def body(tape):
    return bytes(tape.cells[1:]).rstrip(bytes([BLANK]))


def destination(address, rows):
    row, rem = divmod(address, 256)
    left, right = divmod(rem, 16)
    if row >= rows:
        raise ValueError("row outside fixture")
    def reverse4(v):
        return int(f"{v:04b}"[::-1], 2)
    return row * 256 + reverse4(right) * 16 + reverse4(left)


class GuardBinding(ToyBinding):
    stock_multiple = 2

    def __init__(self, catalogue, plans):
        super().__init__(catalogue, plans)
        self.guards = {"root": 0, "child": 0}

    def check_stock(self, runtime):
        # Fixture observation, additional to the unchanged actual NODE's
        # stock_multiple guard. It must not change the runtime decision.
        expected = Count.literal(12 if runtime.root else 2)
        try:
            need(expected.equals(runtime.count("unused")), "one-factor child stock")
            self.guards["root" if runtime.root else "child"] += 1
        finally:
            expected.close()


def run():
    catalogue = model.Catalogue()
    topology = model.Topology(catalogue)
    source_arena, source_indices = Arena(3), Arena(8)
    modulus = source_arena.input(2)
    ring = Ring(modulus)
    context = Context(ring, catalogue.codes)
    plans = model.compile_coefficients(catalogue, context, source_indices, model.UnitIncoming(context))
    binding = GuardBinding(catalogue, plans)
    programs = tuple(compile_node(topology, binding, mode) for mode in (0, 1))
    context.close()
    ring.close()
    size, depth = source_indices.input(4), source_indices.input(0)
    source, directory, program = Tape(), Tape(), Tape()
    rows_value = 72
    volume = rows_value * 256
    for i in range(volume):
        # New row-sensitive input, not a replicated old 36-row payload.
        source.append(((i * 29) ^ (i >> 2) ^ (i >> 8) ^ (i >> 10) ^ 0xA7) & 1)
    source.rewind()
    original = body(source)
    old_count, rows, before, gap, suffix = (Count.literal(v) for v in (1, rows_value, 1, 1, 1))
    runtime = Machine(binding, topology, programs, Arena(3, 512), Arena(8, 512))
    def forbidden(*_args, **_kwargs):
        raise ValueError("logical scheduler entered physical controller")
    with no_decode(), patch.object(scheduler.Invocation, "__init__", forbidden):
        output = runtime.run(source, directory, program, modulus, size, depth,
                             old_count, rows, before, gap, suffix, mode=1)
    actual = body(output)
    expected = bytearray(volume)
    for address in range(volume):
        expected[destination(address, rows_value)] = original[address]
    need(actual == expected, "complete two-level one-factor payload")
    need(body(source) == original and not body(directory) and not body(program)
         and source.head == directory.head == program.head == output.head == 1,
         "borrowed root streams and canonical heads")
    need(output is not source, "owned output is distinct")
    need(runtime.counts["calls"] == runtime.counts["returns"] == 12
         and runtime.counts["residuals"] == 156, "complete recursive census")
    need(binding.guards == {"root": 12, "child": 144}, "every residual stock boundary")
    need(runtime.closed and not runtime.arena.live and not runtime.indices.live
         and not runtime.pool.live and runtime.numerical.machine.tapes == [{}, {}],
         "empty numerical, scratch and parking state")
    work = (*runtime.roles.values(), *runtime.handoff.values(), *runtime.pool.tapes)
    need(all(all(x == BLANK for x in t.cells) for t in work), "erased role bodies and markers")
    need(all(all(x == BLANK for x in word.cells)
             for bank in (runtime.arena, runtime.indices)
             for word in (*bank.words, bank.template)), "erased word banks and templates")
    result = dict(domain="q2 GL2 reduced grammar; w1; root coordinate projectors",
                  compatibility=2, depth=2, base_factor=6, fresh_rows=72,
                  repeated_factor_rows=144, payload_bits=volume,
                  input_sha256=sha256(original).hexdigest(), output_sha256=sha256(actual).hexdigest(),
                  counts=runtime.counts, stock_observations=binding.guards,
                  scratch_peak=runtime.pool.peak, complete_return=True)
    for tape in (source, directory, program, output):
        tape.clear()
    for count in (old_count, rows, before, gap, suffix):
        count.close()
    source_arena.free(modulus)
    source_indices.free_many(size, depth)
    return result
