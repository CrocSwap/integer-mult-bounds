"""Two literal padded physical calls and ordinary return at the new contract.

Follows PR2899's source fixture, with Q=2, S=12, R=16, R'=24, all 4096
independent columns. Manual fitted plan: distinct from full selected setup.
"""
from hashlib import sha256
from unittest.mock import patch

from cardinal_counts import Count
from check_support import no_decode
import check_nested_model as model
from directory import Context
from macro_binding import ToyBinding
from macro_code import compile_node
from ordinary import Ordinary
from physical_words import PhysicalWord
from provenance import Provenance
from records import Tape
import scheduler
from words import Arena, BLANK, Ring, Word, need


def body(tape):
    return bytes(tape.cells[1:]).rstrip(bytes([BLANK]))


class Binding(ToyBinding):
    stock_multiple = 2

    def __init__(self, catalogue, plans):
        super().__init__(catalogue, plans)
        self.observations = 0

    def check_stock(self, runtime):
        expected = Count.literal(4)
        try:
            need(expected.equals(runtime.count("unused")), "padded wrapper U=4")
            self.observations += 1
        finally:
            expected.close()


def run():
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
    engine = Ordinary(2, binding, topology, (program,), capacity=128, fixture_index_floor=64)
    payload = Tape()
    volume = 4096
    for i in range(volume):
        payload.append(((i * 17) ^ (i >> 3) ^ (i >> 8) ^ 0x73) & 1)
    payload.rewind()
    original = body(payload)
    width, one = Count.literal(6), Count.literal(1)
    provenance = Provenance(volume)
    provenance.mark(payload)
    pending, completed = [], []

    def observe(stage, padded, returned):
        if stage == "before":
            need(not pending, "one padded root in flight")
            saved = body(padded)
            pending.append((saved, provenance.masks(padded, len(saved))))
            return
        saved, masks = pending.pop()
        expected, expected_masks = bytearray(len(saved)), [0] * len(saved)
        # [row][Hbody:4][Dhi:16][Dbody:4], preserving row and Dhi.
        for a, bit in enumerate(saved):
            r, rest = divmod(a, 256)
            left, rest = divmod(rest, 64)
            dhi, right = divmod(rest, 4)
            rev_left = ((left & 1) << 1) | (left >> 1)
            rev_right = ((right & 1) << 1) | (right >> 1)
            target = ((r * 4 + rev_right) * 16 + dhi) * 4 + rev_left
            expected[target], expected_masks[target] = bit, masks[a]
        need(body(returned) == expected and
             provenance.masks(returned, len(saved)) == tuple(expected_masks),
             "every independent column at each padded endpoint")
        need(body(padded) == saved and padded.head == returned.head == 1,
             "borrowed padded packet preserved")
        need(len(saved) == 6144, "each root has 24 complete rows")
        completed.append(len(saved))

    engine.observe = observe
    def plan():
        values = dict(width=1, depth=1, stock=12, rows=16, borrowed=4, body=2, remainder=0)
        return dict(fits=True, **{k: Count.literal(v) for k, v in values.items()})
    def forbidden(*_args, **_kwargs):
        raise ValueError("fixture decoding or allocation inside ordinary call")
    with no_decode(), provenance.installed(), patch.object(Word, "__init__", forbidden), \
            patch.object(PhysicalWord, "inspect", forbidden), \
            patch.object(scheduler.Invocation, "__init__", forbidden):
        output = engine.execute_plan(payload, width, one, one, one, plan)
        expected, expected_masks = bytearray(volume), [0] * volume
        for address, bit in enumerate(original):
            h, d = divmod(address, 64)
            target = d * 64 + h
            expected[target], expected_masks[target] = bit, 1 << address
        need(body(output) == expected and provenance.masks(output, volume) == tuple(expected_masks),
             "full independent-column ordinary permutation")
        need(body(payload) == original and payload.head == output.head == 1 and output is not payload,
             "borrowed source, distinct owned output, canonical heads")
        need(not pending and completed == [6144, 6144] and engine.runtime.completed_roots == 2,
             "two completed padded calls before return")
        need(engine.closed and engine.runtime.closed and engine.last_fitted and binding.observations == 24,
             "complete fitted return and stock checks")
        work = [*engine.pool.tapes, *engine.runtime.pool.tapes, *engine.runtime.roles.values(),
                *engine.runtime.handoff.values(), engine.runtime.output]
        for bank in (*engine.banks, engine.runtime.arena, engine.runtime.indices):
            need(not bank.live and not bank.initialized, "closed physical banks")
            work.extend(word.tape for word in (*bank.words, bank.template))
        need(all(all(x == BLANK for x in t.cells) for t in work), "erase complete owned work")
        need(engine.runtime.numerical.machine.tapes == [{}, {}], "erase parking work")
        output.clear()
    payload.clear()
    width.close()
    one.close()
    return dict(independent_columns=volume, input_sha256=sha256(original).hexdigest(),
                compatibility=2, stock=12, genuine_rows=16, padded_rows=24,
                padded_return_sizes=completed, stock_observations=binding.observations,
                outer_peak=engine.pool.peak, inner_peak=engine.runtime.pool.peak,
                complete_ownership_cleanup=True,
                domain="manual fitted q2 dimension2 body2; no recursive child in these roots")
