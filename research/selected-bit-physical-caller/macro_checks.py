"""Complete reduced-source payload through the generated fixed-role caller."""
from hashlib import sha256
import json
from pathlib import Path
import sys
from time import monotonic
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import loader
loader.activate()
from cardinal_counts import Count
from check_support import no_decode
from check_runtime import destination
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


def run():
    started = monotonic()
    catalogue = model.Catalogue()
    topology = model.Topology(catalogue)
    source_arena, source_indices = Arena(3), Arena(8)
    modulus = source_arena.input(2)
    ring = Ring(modulus)
    context = Context(ring, catalogue.codes)
    plans = model.compile_coefficients(catalogue, context, source_indices, model.UnitIncoming(context))
    binding = ToyBinding(catalogue, plans)
    programs = (compile_node(topology, binding, 0), compile_node(topology, binding, 1))
    context.close()
    ring.close()
    size, depth = source_indices.input(4), source_indices.input(0)
    source, directory, program = Tape(), Tape(), Tape()
    for index in range(9216):
        source.append(((index * 13) ^ (index >> 3) ^ (index >> 7) ^ 0x53) & 1)
    source.rewind()
    original = body(source)
    old_count, rows, before, gap, suffix = (Count.literal(value) for value in (1, 36, 1, 1, 1))
    runtime = Machine(binding, topology, programs, Arena(3, 512), Arena(8, 512))
    print("compiled", [len(p.operations) for p in programs], "instructions", flush=True, file=sys.stderr)
    def reject_invocation(*_args, **_kwargs):
        raise ValueError("source recursive Invocation reached the physical controller")
    with no_decode(), patch.object(scheduler.Invocation, "__init__", reject_invocation):
        output = runtime.run(source, directory, program, modulus, size, depth,
                             old_count, rows, before, gap, suffix, mode=1)
    actual = body(output)
    expected = bytearray(9216)
    for address in range(9216):
        expected[destination(address, 4, 2, (1, 1, 1, 1))] = original[address]
    need(actual == expected, "complete generated-controller Boolean endpoint")
    need(sha256(bytes([2]) + actual).hexdigest() ==
         "68477c468bd70d3488f9e1afbfa576aab2fa9db44949874ab873d64c22853b46",
         "same complete payload as the pinned logical replay, including LEFT")
    need(body(source) == original and not body(directory) and not body(program) and
         source.head == directory.head == program.head == output.head == 1,
         "generated caller preserves borrowed root streams and heads")
    need(runtime.counts["calls"] == runtime.counts["returns"] == 12 and
         runtime.counts["residuals"] == 156, "complete model recursive census")
    need(not runtime.arena.live and not runtime.indices.live and
         all(not body(tape) and tape.head == 1 for tape in runtime.roles.values()) and
         all(not body(tape) and tape.head == 1 for tape in runtime.handoff.values()),
         "complete generated caller clears working frames and handoff ports")
    need(runtime.closed and runtime.numerical.machine.tapes == [{}, {}] and
         all(all(symbol == BLANK for symbol in tape.cells)
             for tape in (*runtime.roles.values(), *runtime.handoff.values(), *runtime.pool.tapes)) and
         all(all(symbol == BLANK for symbol in word.cells)
             for bank in (runtime.arena, runtime.indices) for word in (*bank.words, bank.template)),
         "final root return erases physical work markers and templates")
    result = dict(domain="q2 dimension2 cutoff2 one-family model; root coordinate projectors",
                  instructions=[len(p.operations) for p in programs], counts=runtime.counts,
                  payload_sha256=sha256(actual).hexdigest(), physical_stream_roles=len(runtime.roles),
                  handoff_ports=len(runtime.handoff), scratch_capacity=len(runtime.pool.tapes),
                  peak_scratch_leases=runtime.pool.peak, scratch_allocations=runtime.pool.allocations,
                  numerical_slots=[len(runtime.arena.words), len(runtime.indices.words)],
                  parking_charge=runtime.numerical.machine.counts,
                  codec_charge=runtime.numerical.codec_counts)
    source.clear()
    directory.clear()
    program.clear()
    output.clear()
    for value in (old_count, rows, before, gap, suffix):
        value.close()
    source_arena.free(modulus)
    source_indices.free_many(size, depth)
    need(not source_arena.live and not source_indices.live, "closed source fixture banks")
    print("generated controller completed in", round(monotonic() - started, 2), "seconds", file=sys.stderr)
    return result


if __name__ == "__main__":
    print(json.dumps(run(), sort_keys=True, indent=2))
