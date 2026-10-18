"""Scratch ownership controls and a complete nonzero remainder-peel block."""
from hashlib import sha256
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import loader
loader.activate()
from cardinal_counts import Count
from bitstream import atom_swap
from check_runtime import destination
from check_support import no_decode
from directory import Context
from frame_checks import restored, snapshot
import model
import peel
from records import Tape
from scratch_pool import ScratchPool
from stream import Counter
from words import Arena, BLANK, Ring, need


def body(tape):
    return bytes(tape.cells[1:]).rstrip(bytes([BLANK]))


def ownership():
    pool = ScratchPool(2)
    first = pool.acquire()
    first.append(0)
    first.clear()
    second = pool.acquire()
    second.append(1)
    second.rewind()
    need(first.slot == second.slot, "reuse a physical scratch role")
    first.clear()
    need(second.read() == 1, "stale cleanup preserves the new borrower's data")
    rejected = []
    try:
        first.read()
    except ValueError:
        rejected.append("stale_read")
    literal = Count.literal(1)
    with pool.install():
        counter = Counter(literal)
        for label, operation in (("exhaustion", pool.acquire),
                                 ("physical_tape", Tape), ("numerical_arena", lambda: Arena(3))):
            try:
                operation()
            except ValueError:
                rejected.append(label)
        counter.decrement()
        counter.close()
        second.clear()
        pool.empty()
    literal.close()
    need(rejected == ["stale_read", "exhaustion", "physical_tape", "numerical_arena"],
         "scratch ownership and fixed-inventory controls reject")
    return dict(rejected=rejected, peak=pool.peak, stale_cleanup_preserves_new_owner=True)


def lease_traffic():
    for length in (0, 1, 3, 17):
        pool = ScratchPool(1)
        lease, reference = pool.acquire(), Tape()
        for tape in (lease, reference):
            for i in range(length):
                tape.append(i & 1)
            tape.rewind()
            tape.step(1)
            tape.read()
            tape.rewind()
            tape.clear()
        need(lease.meter.record() == reference.meter.record(),
             "delegated lease loops retain the literal tape API invoice")
        pool.empty()
    return dict(extents=[0, 1, 3, 17], exact_api_traffic=True)


def remainder():
    catalogue = model.Catalogue()
    arena, indices = Arena(3, 512), Arena(8, 512)
    modulus = arena.input(3)
    ring = Ring(modulus)
    context = Context(ring, catalogue.codes)
    incoming = model.Incoming(context, indices, (2, 1, 2))
    size, depth = indices.input(3), indices.zero()
    source, directory = Tape(), Tape()
    for address in range(1458):
        source.append(((address * 7) ^ (address >> 3) ^ 0x57) & 1)
    source.rewind()
    original = body(source)
    counts = [Count.literal(value) for value in (1, 1, 1, 2, 1)]
    before = snapshot(arena), snapshot(indices)
    pool = ScratchPool(3 ** 2 + 128)
    with pool.install(), no_decode():
        output = peel.run(source, context, indices, size, depth, object(), directory, *counts, incoming)
        actual = body(output.physical)
        expected = bytearray(1458)
        for address in range(1458):
            expected[destination(address, 3, 3, (2, 1, 2), 2, active=(2,))] = original[address]
        need(actual == expected and body(source) == original and not body(directory),
             "complete nonzero remainder peel preserves other atoms and the external gap")
        output.clear()
        pool.empty()
    restored(arena, before[0])
    restored(indices, before[1])
    result = dict(addresses=1458, remainder_atoms=1, gap=2, peak_scratch_leases=pool.peak,
                  payload_sha256=sha256(actual).hexdigest())
    source.clear()
    directory.clear()
    incoming.close()
    for value in counts:
        value.close()
    context.close()
    ring.close()
    arena.free(modulus)
    indices.free_many(size, depth)
    need(not arena.live and not indices.live, "closed remainder fixture")
    return result


def run():
    return dict(ownership=ownership(), remainder=remainder(), two_digit=two_digit(), traffic=lease_traffic())


def two_digit():
    arena = Arena(5, 512)
    modulus = arena.input(9)
    ring = Ring(modulus)
    parameters = []
    for value in (2, 5, 3):
        count = Count.literal(value)
        parameters.append(count.marginal())
        count.close()
    source = Tape()
    for address in range(2430):
        source.append(((address * 11) ^ (address >> 2) ^ (address >> 5)) & 1)
    source.rewind()
    original = body(source)
    saved = snapshot(arena)
    pool = ScratchPool(137)
    with pool.install(), no_decode():
        output = atom_swap(source, ring, 3, *parameters)
        actual = body(output.physical)
        expected = bytearray(2430)
        for address in range(2430):
            rest, suffix = divmod(address, 3)
            rest, second = divmod(rest, 9)
            rest, middle = divmod(rest, 5)
            outer, first = divmod(rest, 9)
            target = ((((outer * 9 + second) * 5 + middle) * 9 + first) * 3 + suffix)
            expected[target] = original[address]
        need(actual == expected and body(source) == original and source.head == output.head == 1,
             "complete two-digit swap preserves all spectator coordinates")
        output.clear()
        pool.empty()
    restored(arena, saved)
    result = dict(modulus=9, digits=2, addresses=2430, peak_scratch_leases=pool.peak,
                  payload_sha256=sha256(actual).hexdigest())
    source.clear()
    for parameter in parameters:
        parameter.close()
    ring.close()
    arena.free(modulus)
    need(not arena.live, "closed two-digit fixture")
    return result


if __name__ == "__main__":
    import json
    print(json.dumps(run(), indent=2, sort_keys=True))
