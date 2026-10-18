"""Bounded fixtures and a literal allocation/occupied-cell census."""
from __future__ import annotations

from algebra import check_form, projector_values


def need(condition, message):
    if not condition:
        raise ValueError(message)


def allowance(kind, m, rank):
    need(kind in ("good", "fallback") and 1 <= m <= 64, "bounded constructor domain")
    need(1 <= rank <= min(42, m) and (kind != "good" or rank < m), "bounded rank")
    if kind == "good":
        return 6 * m * m + 4 * m * rank - rank * rank + 10
    size = 2 * m
    return max(size * size + (size - 1) ** 2 + 10,
               size * size + size * (size - 1) + 5)


class Census:
    def __init__(self, modules, arena, budget):
        self.modules, self.arena, self.budget = modules, arena, budget
        self.entry = self.peak = len(arena.live)
        self.zero = modules.words.Arena.zero
        self.scans, self.next_scan = 0, 1

    def scan(self):
        arena, words = self.arena, self.modules.words
        occupied = sum(cell not in (words.LEFT, words.BLANK)
                       for word in (*arena.words, arena.template) for cell in word.cells)
        need(occupied == (len(arena.live) + 1) * (arena.bits + 1), "literal occupied-cell census")
        self.scans += 1

    def allocate(self, arena):
        word = self.zero(arena)
        need(arena is self.arena, "one explicit numerical arena")
        live = len(arena.live)
        need(live <= self.entry + self.budget, "numerical word budget exceeded")
        if live > self.peak:
            self.peak = live
            if live >= self.next_scan or live >= self.entry + self.budget - 10:
                self.scan()
                self.next_scan = max(2 * live, self.next_scan)
        return word

    def __enter__(self):
        need(self.arena.template.head == 1 and
             all(self.arena.words[slot].head == 1 for slot in self.arena.live),
             "restored entry heads")
        self.scan()
        self.modules.words.Arena.zero = lambda arena: self.allocate(arena)
        return self

    def __exit__(self, *_exception):
        self.modules.words.Arena.zero = self.zero


def fixture(modules, kind, m, rank, modulus, borrowed):
    need(modulus in (3, 9) and borrowed in (3, 7), "finite fixture ring/residents")
    arena = modules.words.Arena(modulus.bit_length() + 1, 65536)
    mod = arena.literal(modulus)
    ring = modules.words.Ring(mod)
    residents = [arena.literal(i % modulus) for i in range(borrowed)]
    values = projector_values(m, rank, modulus, kind)
    projector = [[arena.literal(value) for value in row] for row in values]
    return arena, mod, ring, residents, projector, values


def check_preserved(arena, saved):
    need(all(slot in arena.live and bytes(arena.words[slot].cells) == raw
             and arena.words[slot].head == 1 for slot, raw in saved.items()),
         "all borrowed numerical values and heads preserved")
    need(arena.template.head == 1, "template head preserved")


def owned_slots(form, kind):
    if kind == "good":
        words = [*form.pivots, *(value for _, _, value in form.rows + form.columns),
                 *(value for row in form.cross for value in row)]
    else:
        words = [*form.diagonal, *(item.scalar for item in form.reductions if item.scalar is not None)]
    slots = [word.slot for word in words]
    need(len(slots) == len(set(slots)), "distinct owned form Words")
    return set(slots)


def run_case(modules, kind, m, rank, modulus, borrowed, budget=None):
    bound = allowance(kind, m, rank)
    arena, mod, ring, residents, projector, values = fixture(modules, kind, m, rank, modulus, borrowed)
    saved = {slot: bytes(arena.words[slot].cells) for slot in arena.live}
    try:
        with Census(modules, arena, bound if budget is None else budget) as census:
            if kind == "good":
                form = modules.forms.good_form(projector, rank, ring)
            else:
                form = modules.forms.fallback_form(projector, ring)
            census.scan()
        check_preserved(arena, saved)
        expected = m * m + 2 * m * rank - rank * rank if kind == "good" else 4 * m * m
        owned = owned_slots(form, kind)
        need(len(owned) == expected and arena.live == set(saved) | owned,
             "exact retained form inventory and no leaked scratch")
        need(not set(saved) & owned, "form does not borrow input storage")
        check_form(form, kind, values, rank, modulus)
        record = {"kind": kind, "dimension": m, "rank": rank, "modulus": modulus,
                  "borrowed": borrowed, "entry": census.entry, "allowance": bound,
                  "peak_extra": census.peak - census.entry, "stored": expected,
                  "cell_scans": census.scans}
        form.close(ring)
        need(arena.live == set(saved), "form close restores exact entry ownership")
        check_preserved(arena, saved)
        return record
    finally:
        # The original constructors do not promise arbitrary exception safety.
        # The checker owns and explicitly rolls back their temporary arena slots.
        arena.rollback(set(saved))
        modules.matrices.Matrices(ring).free(projector)
        for word in residents:
            arena.free(word)
        ring.close()
        arena.free(mod)
        need(not arena.live, "complete fixture erasure")
        Census(modules, arena, 0).scan()
