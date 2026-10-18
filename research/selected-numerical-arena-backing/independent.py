#!/usr/bin/env python3
"""Independent, bounded corroboration of the Arena backing proof.

Imports only the pinned runtime, never this package's primary verifier.
The mathematical all-parameter argument is in INDEPENDENT.md.
New work: Ross Richardson with substantial OpenAI Codex assistance, Apache-2.0.
"""

from hashlib import sha256
from itertools import permutations
import json
from pathlib import Path
from types import ModuleType


HERE = Path(__file__).resolve().parent
RUNTIME_SHA256 = "5c37f57708ba3131bdcb03139f9dbc29886bee44569c09cbba51b68f75acd7f9"


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def load_runtime():
    source = (HERE / "vendor" / "words.py").read_bytes()
    require(sha256(source).hexdigest() == RUNTIME_SHA256, "runtime source pin")
    module = ModuleType("independent_pinned_words")
    exec(compile(source, str(HERE / "vendor" / "words.py"), "exec"), module.__dict__)
    return module


W = load_runtime()
OBSERVERS = {}
COUNTS = {"histories": 0, "operations": 0, "samples": 0, "pending_samples": 0}
original_init = W.Word.__init__
original_write = W.Word.write


def watched_init(word, arena, slot):
    original_init(word, arena, slot)
    observer = OBSERVERS.get(id(arena))
    if observer is not None and slot >= 0:
        observer.pending = word
        observer.sample("constructed-before-append")


def watched_write(word, symbol):
    original_write(word, symbol)
    observer = OBSERVERS.get(id(word.arena))
    if observer is not None:
        observer.sample("cell-write")


W.Word.__init__ = watched_init
W.Word.write = watched_write


class WatchedSlots(list):
    def __init__(self, values, observer):
        super().__init__(values)
        self.observer = observer

    def append(self, value):
        super().append(value)
        self.observer.sample("appended-before-live-add")


class WatchedLive(set):
    def __init__(self, values, observer):
        super().__init__(values)
        self.observer = observer

    def add(self, value):
        super().add(value)
        self.observer.sample("live-add")

    def remove(self, value):
        super().remove(value)
        self.observer.sample("live-remove")


class Observer:
    def __init__(self, arena):
        self.arena = arena
        self.initial_backing = len(arena.words)
        self.high_live = len(arena.live)
        self.pending = None
        self.saw_uncorrected_failure = False
        arena.words = WatchedSlots(arena.words, self)
        arena.live = WatchedLive(arena.live, self)
        OBSERVERS[id(arena)] = self
        self.sample("entry")

    def sample(self, site):
        arena = self.arena
        live = len(arena.live)
        self.high_live = max(self.high_live, live)
        arrays = {id(word.cells): word.cells for word in arena.words}
        if self.pending is not None:
            arrays[id(self.pending.cells)] = self.pending.cells
        pending_unregistered = int(
            self.pending is not None and self.pending.slot not in arena.live
        )
        backing = len(arrays)
        corrected = max(self.initial_backing, self.high_live, live + pending_unregistered)
        require(backing == corrected, (site, "microstate recurrence"))
        if pending_unregistered:
            COUNTS["pending_samples"] += 1
            self.saw_uncorrected_failure |= backing != max(self.initial_backing, self.high_live)
        all_arrays = [*arrays.values(), arena.template.cells]
        require(all(len(cells) == arena.bits + 2 for cells in all_arrays), "fixed cell extent")
        require(all(cells[0] == W.LEFT for cells in all_arrays), "per-array LEFT")
        total = sum(map(len, all_arrays))
        require(total == (backing + 1) * (arena.bits + 2), "exact retained cell count")
        occupied = sum(
            symbol not in (W.BLANK, W.LEFT)
            for cells in all_arrays for symbol in cells
        )
        require(occupied <= (live + 1) * (arena.bits + 1), "intermediate occupied content")
        COUNTS["samples"] += 1

    def boundary(self, model, high_live):
        self.pending = None
        self.sample("boundary")
        arena = self.arena
        backing, live, available = model
        require(len(arena.words) == backing, "model backing")
        require(set(arena.live) == set(live), "model live identities")
        require(tuple(arena.available) == available, "model free stack")
        require(self.high_live == high_live, "live history")
        require(backing == max(self.initial_backing, high_live), "boundary recurrence")
        require(len(available) + len(live) == backing, "partition cardinality")
        require(set(available).isdisjoint(live), "partition disjointness")
        require(set(available) | set(live) == set(range(backing)), "partition coverage")
        require(len(set(available)) == len(available), "no duplicate available slots")
        for slot, word in enumerate(arena.words):
            require(word.slot == slot and word.arena is arena, "word ownership")
            require(word.head == 1, "restored head")
            if slot in live:
                require(all(x in (W.ZERO, W.ONE) for x in word.cells[1:-1]), "complete digits")
                require(word.cells[-1] == W.RIGHT, "complete RIGHT")
            else:
                require(all(x == W.BLANK for x in word.cells[1:]), "erased slot")

    def close(self):
        OBSERVERS.pop(id(self.arena))


def model_step(model, operation):
    """Integer/identity model; no runtime method and no capacity check."""
    backing, live, available = model
    if operation == "z":
        if available:
            slot, available = available[-1], available[:-1]
        else:
            slot, backing = backing, backing + 1
        return backing, live | frozenset((slot,)), available
    slot = operation
    require(slot in live, "legal abstract free")
    return backing, live - frozenset((slot,)), available + (slot,)


def traces(model, capacity, remaining, prefix=()):
    """All labeled legal histories of length at most remaining."""
    yield prefix
    if remaining == 0:
        return
    if len(model[1]) < capacity:
        yield from traces(model_step(model, "z"), capacity, remaining - 1, prefix + ("z",))
    for slot in sorted(model[1]):
        yield from traces(model_step(model, slot), capacity, remaining - 1, prefix + (slot,))


def make_entry(bits, capacity, backing, live, available):
    arena = W.Arena(bits, capacity)
    for _ in range(backing):
        arena.zero()
    for slot in available:
        arena.free(arena.words[slot])
    require(set(arena.live) == set(live), "entry construction")
    return arena


def replay(bits, capacity, initial, history):
    arena = make_entry(bits, capacity, *initial)
    observer = Observer(arena)
    model, high_live = initial, len(initial[1])
    observer.boundary(model, high_live)
    for operation in history:
        model = model_step(model, operation)
        if operation == "z":
            arena.zero()
        else:
            arena.free(arena.words[operation])
        high_live = max(high_live, len(model[1]))
        observer.boundary(model, high_live)
        COUNTS["operations"] += 1
    observer.close()
    COUNTS["histories"] += 1


def exhaustive_small_histories():
    for capacity in range(1, 4):
        for backing in range(capacity + 1):
            for mask in range(1 << backing):
                live = frozenset(slot for slot in range(backing) if (mask >> slot) & 1)
                inactive = tuple(slot for slot in range(backing) if slot not in live)
                for available in permutations(inactive):
                    initial = backing, live, available
                    for history in traces(initial, capacity, 6):
                        for bits in (2, 3):
                            replay(bits, capacity, initial, history)


def array_cells(arena):
    return sum(len(word.cells) for word in arena.words) + len(arena.template.cells)


def counterexamples():
    # A capacity is a guard, not preallocated Word-cell arrays.
    empty = W.Arena(2, 1000)
    require(array_cells(empty) == 4, "template-only entry")
    require(array_cells(empty) != (empty.capacity + 1) * 4, "reject eager-capacity formula")

    # Past allocations remain even after all current numerical content is erased.
    history = make_entry(2, 4, 4, frozenset(), (0, 1, 2, 3))
    word = history.zero()
    history.free(word)
    require(array_cells(history) == 20, "inherited history cells")
    require(array_cells(history) > (len(history.live) + 1) * 4, "reject live-only backing")
    for _ in range(5):
        history.free(history.zero())
    require(len(history.words) == 4 and history.meter.allocations > 4, "reuse versus allocation count")

    # The precise inventory failure precedes construction and preserves state.
    limited = W.Arena(2, 2)
    limited.zero()
    limited.zero()
    before = (array_cells(limited), tuple(limited.available), frozenset(limited.live))
    try:
        limited.zero()
    except ValueError as error:
        require(str(error) == "fixed register inventory", "exact underbudget rejection")
    else:
        raise AssertionError("underbudget trace unexpectedly admitted")
    after = (array_cells(limited), tuple(limited.available), frozenset(limited.live))
    require(after == before, "inventory rejection is before mutation")

    # A successful-only statement says nothing about this failed demand trace.
    demand = ("z", "z", "z")
    abstract, demand_peak = (0, frozenset(), ()), 0
    for operation in demand:
        abstract = model_step(abstract, operation)
        demand_peak = max(demand_peak, len(abstract[1]))
    require(demand_peak == 3 > limited.capacity, "capacity-independent demand witness")

    # A new array exists before live.add. The corrected microstate formula is exact.
    micro = W.Arena(2, 1)
    observer = Observer(micro)
    micro.zero()
    observer.boundary((1, frozenset((0,)), ()), 1)
    require(observer.saw_uncorrected_failure, "detect boundary-only formula at construction")
    observer.close()

    # Suspended arithmetic heads need not all be restored while another slot allocates.
    heads = W.Arena(3, 3)
    first = heads.literal(5)
    first.msb()
    second = heads.zero()
    second.step(-1)
    third = heads.zero()
    require(first.head == 3 and second.head == 0, "unrelated heads remain suspended")
    heads.free(first)
    second.step(1)
    heads.free(second)
    third.step(1)
    heads.free(third)
    require(not heads.live and array_cells(heads) == 20, "legal interior-head frees")

    # Two distinct arenas keep peaks reached in disjoint phases.
    residue, index = W.Arena(2, 3), W.Arena(3, 3)
    occupied_phase_max = 0
    live_array_phase_max = 0
    for residue_count, index_count in ((3, 1), (1, 3)):
        for arena in (residue, index):
            for slot in tuple(arena.live):
                arena.free(arena.words[slot])
        for _ in range(residue_count):
            residue.zero()
        for _ in range(index_count):
            index.zero()
        occupied_phase_max = max(
            occupied_phase_max,
            (residue_count + 1) * 3 + (index_count + 1) * 4,
        )
        live_array_phase_max = max(
            live_array_phase_max,
            (residue_count + 1) * 4 + (index_count + 1) * 5,
        )
    retained = array_cells(residue) + array_cells(index)
    require((len(residue.words), len(index.words)) == (3, 3), "separate retained peaks")
    require(retained == 36 and live_array_phase_max == 28, "same-width phase counterexample")
    require(occupied_phase_max == 22, "separate occupied-content measure")
    require(retained > live_array_phase_max, "reject weighted phase max for backing")
    return {
        "empty_template_cells": array_cells(empty),
        "history_backing_cells": array_cells(history),
        "underbudget_demand_peak": demand_peak,
        "underbudget_capacity": limited.capacity,
        "pending_array_detected": observer.saw_uncorrected_failure,
        "suspended_head_backing_cells": array_cells(heads),
        "phase_retained_cells": retained,
        "phase_max_live_array_cells": live_array_phase_max,
        "phase_max_occupied_nonleft_cells": occupied_phase_max,
    }


def main():
    exhaustive_small_histories()
    witnesses = counterexamples()
    require(not OBSERVERS, "observers released")
    print(json.dumps({
        "status": "PASS_INDEPENDENT_ARENA_BACKING_FINITE_CHECKS",
        "runtime_sha256": RUNTIME_SHA256,
        "domain": {
            "bits": [2, 3], "capacities": [1, 2, 3],
            "maximum_history_length": 6,
            "entries": "all K <= capacity, live-slot subsets, and available-stack orders",
            "entry_values_and_heads": "all live values zero; all heads restored to 1",
        },
        "counts": COUNTS,
        "counterexamples": witnesses,
        "scope": "finite source corroboration; not a formal-kernel proof or caller admission",
    }, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
