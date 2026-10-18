"""A C1 primitive invokes a fitted toy B1 while C0 retains both A0 bindings."""
from pathlib import Path
import json
import sys
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import stage_sources
stage_sources.activate()
from cardinal_counts import Count
from check_engine import fixture_engine, toy_plan
from check_support import no_decode
from compile_routes import Registry
from physical_words import PhysicalArena, PhysicalWord
from provenance import Provenance
from records import Tape
import routes
from scratch_pool import ScratchPool
from stage import Adapter, StagePool
import stream_runner
from words import BLANK, Ring, Word, need


def body(tape):
    return bytes(tape.cells[1:]).rstrip(bytes([BLANK]))


def run():
    native = fixture_engine()
    entered = []
    class FittedFixture:
        def __getattr__(self, name):
            return getattr(native, name)
        def run(self, payload, original, prefixes, gap, suffix):
            need(adapter.in_base and stream_runner.atom_swap is scope.original_swap and
                 routes.route_cube is scope.original_cube, "both preceding bindings at native entry")
            entered.append("base-entry")
            return native.execute_plan(payload, original, prefixes, gap, suffix, toy_plan)
    pool = ScratchPool(260)
    adapter = Adapter(FittedFixture(), Registry(2), capacity=64)
    scope = StagePool(pool, adapter)
    bank = PhysicalArena(64)
    maximum, one = Count.literal(32), Count.literal(1)
    bank.prepare(maximum)
    modulus = bank.load(maximum)
    ring = Ring(modulus)
    source = Tape()
    for address in range(1024):
        source.append((address*13 ^ address//7 ^ 5) & 1)
    source.rewind()
    initial = body(source)
    observer = Provenance(1024)
    observer.mark(source)
    saved = {slot: (word, bytes(word.cells), word.head) for slot, word in enumerate(bank.words) if slot in bank.live}
    def native_observe(stage, _payload, _returned):
        need(stream_runner.atom_swap is scope.original_swap and routes.route_cube is scope.original_cube,
             "C0 roots cannot see successor primitive hooks")
        entered.append(stage)
    native.observe = native_observe
    def forbidden(*_args, **_kwargs):
        raise ValueError("fixture-only numerical operation during handoff")
    with no_decode(), observer.installed(), patch.object(Word, "__init__", forbidden), \
            patch.object(PhysicalWord, "inspect", forbidden), scope.install():
        operands = [one.marginal() for _ in range(3)]
        try:
            output = stream_runner.atom_swap(source, ring, 2, *operands)
        finally:
            for value in operands:
                value.close()
        expected, masks = bytearray(1024), [0]*1024
        for address, bit in enumerate(initial):
            first, second = divmod(address, 32)
            expected[second*32+first], masks[second*32+first] = bit, 1 << address
        need(bytes(output.physical.cells[1:]).rstrip(bytes([BLANK])) == expected and
             observer.masks(output.physical, 1024) == tuple(masks), "complete fitted nested interchange")
        need(saved == {slot: (word, bytes(word.cells), word.head) for slot, word in enumerate(bank.words) if slot in bank.live},
             "nested preceding stage preserves live parent numerical objects")
        need(body(source) == initial and source.head == 1, "nested preceding stage preserves source")
        output.clear()
        pool.empty()
        adapter.in_base = True
        for function in (lambda: adapter.swap(None, None, 2, None, None, None),
                         lambda: adapter.route_cube(None, None, None, None)):
            try:
                function()
            except ValueError:
                pass
            else:
                raise ValueError("preceding stage re-entered successor")
        adapter.in_base = False
    adapter.close()
    need(entered == ["base-entry", "before", "after", "before", "after"],
         "two actual fitted roots under the preceding bindings")
    result = dict(columns=1024, stage_trace=entered, reentry_rejections=2,
                  parent_peak=pool.peak, preceding_roots=native.runtime.completed_roots,
                  calls=adapter.calls)
    ring.close()
    bank.free(modulus)
    bank.erase_owned()
    source.clear()
    maximum.close()
    one.close()
    return result


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
    print("PASS_NONCIRCULAR_FITTED_HANDOFF")
