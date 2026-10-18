"""Complete small ordinary exchange through the generated two-root session."""
from hashlib import sha256
import json
from pathlib import Path
import sys
from time import monotonic
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import source
loader, padding, outer = source.activate()
from cardinal_counts import Count
from check_support import no_decode
import check_nested_model as model
from directory import Context
from macro_binding import ToyBinding
from macro_code import compile_node
from provenance import Provenance
from records import Tape
import scheduler
from scratch_pool import ScratchPool
from session import OuterScope, RootSession, borrowed_count, borrowed_tape, sealed_constructors
from words import Arena, BLANK, Ring, need


def body(tape):
    return bytes(tape.cells[1:]).rstrip(bytes([BLANK]))


class Binding(ToyBinding):
    def check_stock(self, runtime):
        expected = Count.literal(2 if runtime.root else 1)
        try:
            need(expected.equals(runtime.count("unused")), "outer toy compatible stock")
        finally:
            expected.close()


def run():
    started = monotonic()
    catalogue = model.Catalogue()
    topology = model.Topology(catalogue)
    arena, high_arena, indices = Arena(3, 512), Arena(5, 512), Arena(8, 512)
    modulus, high_modulus = arena.input(2), high_arena.input(8)
    ring, high_ring = Ring(modulus), Ring(high_modulus)
    context = Context(ring, catalogue.codes)
    plans = model.compile_coefficients(catalogue, context, indices, model.UnitIncoming(context))
    context.close()
    binding = Binding(catalogue, plans)
    program = compile_node(topology, binding, 0)
    runtime = RootSession(binding, topology, (program,), Arena(3, 512), Arena(8, 512))
    pool = ScratchPool(260)
    scope = OuterScope(pool)
    size, depth = indices.input(2), indices.input(0)
    original, directory, coefficient_program = Tape(), Tape(), Tape()
    for address in range(1024):
        original.append(((address * 13) ^ (address >> 3) ^ (address >> 7) ^ 0x53) & 1)
    original.rewind()
    initial = body(original)
    provenance = Provenance(len(initial))
    provenance.mark(original)
    prefixes, gap, suffix, stock, one, actual_gap = (
        Count.literal(value) for value in (1, 1, 1, 6, 1, 8))
    calls = []

    def callee(payload, padded_rows):
        retained = {slot: (lease, body(lease.physical), lease.head)
                    for slot, lease in pool.live.items()}
        input_bytes = body(borrowed_tape(payload))
        input_masks = provenance.masks(borrowed_tape(payload), len(input_bytes))
        with scope.suspended():
            returned = runtime.run(borrowed_tape(payload), directory, coefficient_program,
                                   modulus, size, depth, borrowed_count(prefixes),
                                   borrowed_count(padded_rows), borrowed_count(one),
                                   borrowed_count(actual_gap), borrowed_count(suffix))
        need(retained == {slot: (lease, body(lease.physical), lease.head)
                          for slot, lease in pool.live.items()},
             "root return preserves all outer-owned leases and their contents")
        expected_f = bytearray(len(input_bytes))
        expected_masks = [0] * len(input_bytes)
        for address, bit in enumerate(input_bytes):
            row, tail = divmod(address, 128)
            first, tail = divmod(tail, 32)
            middle, second = divmod(tail, 4)
            reverse_first = ((first & 1) << 1) | (first >> 1)
            reverse_second = ((second & 1) << 1) | (second >> 1)
            target = ((row * 4 + reverse_second) * 8 + middle) * 4 + reverse_first
            expected_f[target] = bit
            expected_masks[target] = input_masks[address]
        need(body(returned) == expected_f, "each complete padded F_I endpoint")
        need(provenance.masks(returned, len(expected_f)) == tuple(expected_masks),
             "every independent input column at each padded F_I return")
        calls.append(dict(volume=len(body(returned)), roots=runtime.completed_roots))
        return returned

    def forbidden_invocation(*_args, **_kwargs):
        raise ValueError("logical scheduler reached the physical ordinary wrapper")

    with no_decode(), patch.object(scheduler.Invocation, "__init__", forbidden_invocation), provenance.installed():
        with sealed_constructors(), scope.installed():
            result = outer.interchange(original, size, ring, high_ring, 2,
                                       prefixes, gap, suffix, stock, callee)
            output = body(result.physical)
            expected = bytearray(1024)
            expected_masks = [0] * 1024
            for address, bit in enumerate(initial):
                first, second = divmod(address, 32)
                expected[second * 32 + first] = bit
                expected_masks[second * 32 + first] = 1 << address
            need(output == expected, "complete ordinary chunk endpoint")
            need(provenance.masks(result.physical, 1024) == tuple(expected_masks),
                 "all independent Boolean columns of the complete ordinary endpoint")
            need(body(original) == initial and original.head == 1,
                 "ordinary wrapper preserves its borrowed source")
            result.clear()
            runtime.finish()
            pool.empty()
    receipt = dict(payload_bits=1024, independent_columns=1024, calls=calls, macros=runtime.counts,
                   output_sha256=sha256(output).hexdigest(),
                   outer_capacity=len(pool.tapes), outer_peak=pool.peak,
                   inner_capacity=len(runtime.pool.tapes), inner_peak=runtime.pool.peak,
                   completed_roots=runtime.completed_roots)
    for value in (prefixes, gap, suffix, stock, one, actual_gap):
        value.close()
    for tape in (original, directory, coefficient_program):
        tape.clear()
    ring.close()
    high_ring.close()
    arena.free(modulus)
    high_arena.free(high_modulus)
    indices.free_many(size, depth)
    need(not arena.live and not high_arena.live and not indices.live, "closed outer fixture words")
    print("completed physical ordinary fixture in", round(monotonic() - started, 2), "seconds", flush=True)
    return receipt


if __name__ == "__main__":
    print(json.dumps(run(), sort_keys=True, indent=2))
