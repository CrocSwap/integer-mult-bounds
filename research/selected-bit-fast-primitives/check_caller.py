"""Complete generated C1 node through both substituted primitive interfaces."""
from pathlib import Path
from time import monotonic
import json
import sys
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import stage_sources
stage_sources.activate()
from cardinal_counts import Count
from check_engine import fixture_engine
from check_join import Binding
from check_runtime import destination
from check_support import no_decode
import check_nested_model as model
from compile_routes import Registry
from directory import Context
from macro_code import compile_node
from ordinary import unit_program
from physical_words import PhysicalArena, PhysicalWord
from provenance import Provenance
from records import Tape
import scheduler
from stage import successor_session
from words import Arena, BLANK, Ring, Word, need


def body(tape):
    return bytes(tape.cells[1:]).rstrip(bytes([BLANK]))


def run():
    started = monotonic()
    catalogue = model.Catalogue()
    topology = model.Topology(catalogue)
    compile_arena, compile_indices = Arena(3), Arena(8)
    compile_modulus = compile_arena.input(2)
    compile_ring = Ring(compile_modulus)
    context = Context(compile_ring, catalogue.codes)
    plans = model.compile_coefficients(catalogue, context, compile_indices, model.UnitIncoming(context))
    binding = Binding(catalogue, plans)
    code = compile_node(topology, binding, 0)
    context.close()
    compile_ring.close()
    compile_arena.free(compile_modulus)
    native = fixture_engine()
    runtime = successor_session(binding, topology, (code,), PhysicalArena(64), PhysicalArena(64),
                                native, Registry(2))
    arena, indices = PhysicalArena(64), PhysicalArena(64)
    modulus_count, index_maximum, size_count = Count.literal(2), Count.literal(64), Count.literal(2)
    for bank in (arena, runtime.arena):
        bank.prepare(modulus_count)
    for bank in (indices, runtime.indices):
        bank.prepare(index_maximum)
    modulus, size, depth = arena.load(modulus_count), indices.load(size_count), indices.zero()
    ring = Ring(modulus)
    program = unit_program(indices, ring, size, depth, catalogue.codes.bits)
    source, directory = Tape(), Tape()
    length = 192
    for address in range(length):
        source.append((address*13 ^ address//3 ^ 5) & 1)
    source.rewind()
    initial = body(source)
    observer = Provenance(length)
    observer.mark(source)
    prefixes, rows, one = Count.literal(1), Count.literal(12), Count.literal(1)
    def forbidden(*_args, **_kwargs):
        raise ValueError("fixture-only operation in complete successor node")
    with no_decode(), observer.installed(), patch.object(Word, "__init__", forbidden), \
            patch.object(PhysicalWord, "inspect", forbidden), \
            patch.object(scheduler.Invocation, "__init__", forbidden):
        output = runtime.run(source, directory, program.tape, modulus, size, depth,
                             prefixes, rows, one, one, one)
        expected, masks = bytearray(length), [0]*length
        for address, bit in enumerate(initial):
            target = destination(address, 2, 2, (1,1))
            expected[target], masks[target] = bit, 1 << address
        need(body(output) == expected and observer.masks(output, length) == tuple(masks),
             "complete C1 endpoint for every independent input column")
        need(body(source) == initial and source.head == output.head == 1,
             "complete successor preserves borrowed root input")
        output.clear()
        runtime.finish(1)
    adapter = runtime.pool.adapter
    work = [*runtime.roles.values(), *runtime.handoff.values(), *runtime.pool.tapes, runtime.output,
            *native.pool.tapes, *native.runtime.roles.values(), *native.runtime.handoff.values(),
            *native.runtime.pool.tapes, native.runtime.output, native.output]
    for bank in (runtime.arena, runtime.indices, adapter.high_bank,
                 *native.banks, native.runtime.arena, native.runtime.indices):
        need(not bank.live and not bank.initialized, "closed successor numerical contexts")
        work.extend(word.tape for word in (*bank.words, bank.template))
    need(all(all(bit == BLANK for bit in tape.cells) for tape in work),
         "complete successor and preceding-stage physical erasure")
    need(adapter.calls["swaps"] > 0 and adapter.calls["cubes"] == 12,
         "both reached successor primitive bindings")
    result = dict(columns=length, counts=runtime.counts, primitive_calls=adapter.calls,
                  parent_capacity=len(runtime.pool.tapes), parent_peak=runtime.pool.peak,
                  scope="q2 dimension2 one-family complete node; preceding ordinary calls use their elementary branch")
    for tape in (source, directory, program.tape):
        tape.clear()
    ring.close()
    arena.free(modulus)
    indices.free_many(size, depth)
    arena.erase_owned()
    indices.erase_owned()
    for value in (modulus_count, index_maximum, size_count, prefixes, rows, one):
        value.close()
    print("complete successor node seconds", round(monotonic()-started, 2), flush=True)
    return result


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
    print("PASS_COMPLETE_SUCCESSOR_CALLER")
