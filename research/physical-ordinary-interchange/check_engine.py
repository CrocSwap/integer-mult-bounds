"""Encoded word banks, two padded roots, reuse and the elementary fallback."""
from pathlib import Path
import json
import sys
from time import monotonic
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import source
source.activate()
from cardinal_counts import Count
from check_support import no_decode
import check_nested_model as model
from check_join import Binding, body
from directory import Context
from macro_code import compile_node
from ordinary import Ordinary
from physical_words import PhysicalWord
from provenance import Provenance
from records import Tape
import scheduler
from words import Arena, BLANK, Ring, Word, need


def fixture_engine():
    catalogue = model.Catalogue()
    topology = model.Topology(catalogue)
    arena, indices = Arena(3), Arena(8)
    modulus = arena.input(2)
    ring = Ring(modulus)
    context = Context(ring, catalogue.codes)
    plans = model.compile_coefficients(catalogue, context, indices, model.UnitIncoming(context))
    binding = Binding(catalogue, plans)
    program = compile_node(topology, binding, 0)
    context.close()
    ring.close()
    arena.free(modulus)
    return Ordinary(2, binding, topology, (program,), capacity=128, fixture_index_floor=64)


def toy_plan():
    values = dict(width=1, depth=1, stock=6, rows=8, borrowed=3, body=2, remainder=0)
    return dict(fits=True, **{name: Count.literal(value) for name, value in values.items()})


def check_case(engine, width, prefix, gap, suffix, fitted):
    extent = 2**width
    volume = prefix*extent*gap*extent*suffix
    payload = Tape()
    for address in range(volume):
        payload.append(((address * 13) ^ (address >> 3) ^ (address >> 7) ^ 0x53) & 1)
    payload.rewind()
    initial = body(payload)
    original, prefixes, middle, tail = (Count.literal(value) for value in (width, prefix, gap, suffix))
    provenance = Provenance(volume)
    provenance.mark(payload)
    pending = []
    completed = []
    def observe(stage, padded, returned):
        if stage == "before":
            need(not pending, "one observed root at a time")
            pending.append((body(padded), provenance.masks(padded, len(body(padded)))))
            return
        saved, saved_masks = pending.pop()
        expected_f, expected_masks = bytearray(len(saved)), [0]*len(saved)
        for address, bit in enumerate(saved):
            row, rest = divmod(address, 128)
            first, rest = divmod(rest, 32)
            middle_field, second = divmod(rest, 4)
            first_reversed = ((first & 1) << 1) | (first >> 1)
            second_reversed = ((second & 1) << 1) | (second >> 1)
            target = ((row*4+second_reversed)*8+middle_field)*4+first_reversed
            expected_f[target], expected_masks[target] = bit, saved_masks[address]
        need(body(returned) == expected_f and
             provenance.masks(returned, len(saved)) == tuple(expected_masks),
             "each encoded-bank padded F_I preserves every input column")
        need(body(padded) == saved and padded.head == returned.head == 1,
             "each padded input survives its completed root")
        completed.append(len(saved))
    engine.observe = observe
    def forbidden(*_args, **_kwargs):
        raise ValueError("fixture-only construction or decoding during execution")
    with no_decode(), provenance.installed(), patch.object(Word, "__init__", forbidden), \
            patch.object(PhysicalWord, "inspect", forbidden), \
            patch.object(scheduler.Invocation, "__init__", forbidden):
        output = (engine.execute_plan(payload, original, prefixes, middle, tail, toy_plan)
                  if fitted else engine.run(payload, original, prefixes, middle, tail))
        expected, masks = bytearray(volume), [0]*volume
        for address, bit in enumerate(initial):
            quotient, last = divmod(address, suffix)
            quotient, second = divmod(quotient, extent)
            quotient, between = divmod(quotient, gap)
            first_prefix, first = divmod(quotient, extent)
            target = ((((first_prefix*extent+second)*gap+between)*extent+first)*suffix+last)
            expected[target], masks[target] = bit, 1 << address
        need(body(output) == expected and provenance.masks(output, volume) == tuple(masks),
             "complete independent-column ordinary endpoint")
        need(body(payload) == initial and payload.head == output.head == 1,
             "borrowed source and output boundary")
        need(engine.closed and engine.runtime.closed and engine.last_fitted == fitted,
             "closed ordinary invocation with the expected branch")
        need(not pending and len(completed) == (2 if fitted else 0),
             "both independent padded returns precede wrapper cancellation")
        work = [*engine.pool.tapes, *engine.runtime.pool.tapes, *engine.runtime.roles.values(),
                *engine.runtime.handoff.values(), engine.runtime.output]
        for bank in (*engine.banks, engine.runtime.arena, engine.runtime.indices):
            need(not bank.live and not bank.initialized, "closed encoded word banks")
            work.extend(word.tape for word in (*bank.words, bank.template))
        need(all(all(bit == BLANK for bit in tape.cells) for tape in work),
             "erase owned bodies, markers and templates after ordinary return")
        need(engine.runtime.numerical.machine.tapes == [{}, {}], "erase owned parking workspace")
        output.clear()
    result = dict(width=width, shape=[prefix, gap, suffix], independent_columns=volume,
                  fitted=fitted, roots=engine.runtime.completed_roots,
                  padded_returns=completed, outer_peak=engine.pool.peak, inner_peak=engine.runtime.pool.peak)
    payload.clear()
    for value in (original, prefixes, middle, tail):
        value.close()
    return result


def run():
    started = monotonic()
    engine = fixture_engine()
    result = [check_case(engine, 5, 1, 1, 1, True),
              check_case(engine, 2, 2, 3, 2, False),
              check_case(engine, 5, 1, 1, 1, True),
              binary_fitted(engine)]
    print("completed encoded physical ordinary engine in", round(monotonic()-started, 2), "seconds", flush=True)
    return result


def binary_fitted(engine):
    """The binary scope, ordinary scope and C0 pool all execute in one call."""
    from binary import Binary
    class NativeFixture:
        q = 2
        output = engine.output
        @property
        def closed(self):
            return engine.closed
        def run(self, payload, original, prefixes, gap, suffix):
            return engine.execute_plan(payload, original, prefixes, gap, suffix, toy_plan)
        def finish(self, fitted):
            engine.finish(fitted)
    engine.observe = None
    binary = Binary(NativeFixture())
    payload = Tape()
    for address in range(1024):
        payload.append(((address * 13) ^ (address >> 3) ^ (address >> 7) ^ 0x53) & 1)
    payload.rewind()
    initial = body(payload)
    width, one = Count.literal(5), Count.literal(1)
    provenance = Provenance(1024)
    provenance.mark(payload)
    def forbidden(*_args, **_kwargs):
        raise ValueError("fixture-only operation in binary fitted composition")
    with no_decode(), provenance.installed(), patch.object(Word, "__init__", forbidden), \
            patch.object(PhysicalWord, "inspect", forbidden), \
            patch.object(scheduler.Invocation, "__init__", forbidden):
        output = binary.run(payload, width, one, one, one)
        expected, masks = bytearray(1024), [0]*1024
        for address, bit in enumerate(initial):
            first, second = divmod(address, 32)
            expected[second*32+first], masks[second*32+first] = bit, 1 << address
        need(body(output) == expected and provenance.masks(output, 1024) == tuple(masks),
             "complete binary-to-fitted-native independent columns")
        need(body(payload) == initial and payload.head == output.head == 1,
             "binary fitted composition preserves borrowed input")
        work = [*binary.pool.tapes, *engine.pool.tapes, *engine.runtime.pool.tapes,
                *engine.runtime.roles.values(), *engine.runtime.handoff.values(),
                engine.runtime.output, engine.output]
        for bank in (*engine.banks, engine.runtime.arena, engine.runtime.indices):
            work.extend(word.tape for word in (*bank.words, bank.template))
        need(all(all(bit == BLANK for bit in tape.cells) for tape in work),
             "binary and fitted native work both erase on return")
        output.clear()
    payload.clear()
    width.close()
    one.close()
    return dict(binary_fitted_columns=1024, native_roots=engine.runtime.completed_roots,
                binary_peak=binary.pool.peak, outer_peak=engine.pool.peak)


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
    print("PASS_PHYSICAL_ORDINARY_ENGINE")
