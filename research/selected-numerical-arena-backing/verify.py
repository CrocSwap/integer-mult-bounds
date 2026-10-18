#!/usr/bin/env python3
"""Exact numerical-cell audit. Ross Richardson / Codex, Apache-2.0."""
import argparse
from collections import deque
import hashlib
import json
from pathlib import Path
import types

ROOT = Path(__file__).resolve().parent


def need(test, message):
    if not test:
        raise ValueError(message)


def source(root=ROOT):
    manifest = json.loads((root / "INPUTS.json").read_text())
    for row in manifest["files"]:
        data = (root / row["path"]).read_bytes()
        need(hashlib.sha256(data).hexdigest() == row["sha256"], "source SHA256: " + row["path"])
        blob = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
        need(blob == row["git_blob"], "source Git blob: " + row["path"])
    module = types.ModuleType("authenticated_words")
    path = root / "vendor/words.py"
    exec(compile(path.read_bytes(), str(path), "exec"), module.__dict__)
    return module


def state(arena):
    return len(arena.words), tuple(sorted(arena.live)), tuple(arena.available)


def inspect(w, a, expected, peak):
    b, live, available = expected
    need(state(a) == expected, "allocator partition/order")
    need(b == peak, "high-water equality")
    need(set(live).isdisjoint(available), "disjoint free/live")
    need(len(set(available)) == len(available), "duplicate free slot")
    need(set(live) | set(available) == set(range(b)), "complete partition")
    need(cells(a) == (b + 1) * (a.bits + 2), "complete array cells")
    need(a.template.cells == bytes([w.LEFT] + [w.ZERO] * a.bits + [w.RIGHT]), "template")
    need(a.template.head == 1, "template head")
    for slot, word in enumerate(a.words):
        need(word.slot == slot and word.arena is a and word.head == 1, "slot identity/head")
        suffix = [w.ZERO] * a.bits + [w.RIGHT] if slot in live else [w.BLANK] * (a.bits + 1)
        need(word.cells == bytes([w.LEFT] + suffix), "literal content/erasure")


def successor(s, op):
    b, live0, free0 = s
    live, free = set(live0), list(free0)
    if op == "alloc":
        slot = free.pop() if free else b
        b += not free0
        live.add(slot)
    else:
        slot = op
        live.remove(slot)
        free.append(slot)
    return (int(b), tuple(sorted(live)), tuple(free)), slot


def replay(w, cap, bits, path):
    a = w.Arena(bits, capacity=cap)
    expected, peak = (0, (), ()), 0
    inspect(w, a, expected, peak)
    for op in path:
        expected, slot = successor(expected, op)
        if op == "alloc":
            need(a.zero().slot == slot, "allocation identity")
        else:
            a.free(a.words[slot])
        peak = max(peak, len(expected[1]))
        inspect(w, a, expected, peak)
    return a


def graph(w, cap, bits):
    """All reachable canonical zero/free states and every legal outgoing edge."""
    paths = {(0, (), ()): ()}
    queue = deque(paths)
    edges = rejects = 0
    while queue:
        s = queue.popleft()
        path = paths[s]
        if len(s[1]) == cap:
            a = replay(w, cap, bits, path)
            before = (state(a), tuple(bytes(x.cells) for x in a.words))
            try:
                a.zero()
            except ValueError as error:
                need(str(error) == "fixed register inventory", "capacity rejection reason")
            else:
                raise ValueError("capacity guard omitted")
            need(before == (state(a), tuple(bytes(x.cells) for x in a.words)), "guard mutated arena")
            rejects += 1
        for op in list(s[1]) + (["alloc"] if len(s[1]) < cap else []):
            nxt, _ = successor(s, op)
            replay(w, cap, bits, path + (op,))
            edges += 1
            if nxt not in paths:
                paths[nxt] = path + (op,)
                queue.append(nxt)
    return {"capacity": cap, "bits": bits, "reachable_states": len(paths),
            "legal_edges": edges, "capacity_rejections": rejects}


def cells(a):
    return sum(len(w.cells) for w in [a.template, *a.words])


def witnesses(w):
    warm = w.Arena(3, capacity=7)
    old = [warm.zero() for _ in range(7)]
    warm.free_many(*old)
    fresh = w.Arena(3, capacity=7)
    need(not warm.live and not fresh.live and cells(warm) == 40 and cells(fresh) == 5,
         "history counterexample")
    for a in (warm, fresh):
        x = a.zero()
        a.free(x)
    need(cells(warm) == 40 and cells(fresh) == 10, "one-call history counterexample")
    # Both sides use complete cell widths, isolating history from marker charges.
    residue, index = w.Arena(2, 3), w.Arena(3, 2)
    live = [residue.zero() for _ in range(3)]
    residue.free_many(*live)
    live = [index.zero() for _ in range(2)]
    index.free_many(*live)
    phase_max = 4 + 5 + max(3 * 4, 2 * 5)
    actual = cells(residue) + cells(index)
    need(actual == 31 and phase_max == 21, "sequential peak counterexample")
    a = w.Arena(5, 8)
    borrowed = [a.literal(7), a.literal(19)]
    saved = [(x, bytes(x.cells), x.head) for x in borrowed]
    a.copy(borrowed[0])
    a.literal(23)
    a.rollback({x.slot for x in borrowed})
    need(a.live == {x.slot for x in borrowed} and len(a.words) == 4, "rollback backing")
    for x, data, head in saved:
        need(bytes(x.cells) == data and x.head == head, "borrowed preservation")
    for slot in a.available:
        need(a.words[slot].cells == bytes([w.LEFT] + [w.BLANK] * 6), "rollback erasure")
    return {"warm_empty_cells": 40, "fresh_empty_cells": 5, "after_one_call": [40, 10],
            "phase_max_cells": phase_max, "retained_cells": actual, "rollback_slots": 4}


def microstates():
    w = source()
    original = w.Word
    objects, budgets, cuts = {}, {}, []

    class ObservedWord(original):
        def __init__(self, arena, slot):
            super().__init__(arena, slot)
            objects.setdefault(id(arena), []).append(self)
            scan(arena, "constructed")

        def write(self, symbol):
            super().write(symbol)
            scan(self.arena, "write")

    def scan(a, label):
        count = sum(len(x.cells) for x in objects[id(a)])
        need(count <= (budgets.get(id(a), 0) + 1) * (a.bits + 2), "microstate cell budget")
        cuts.append((label, len(a.words), len(a.live), count))

    w.Word = ObservedWord
    a = w.Arena(3, 2)
    for _ in range(2):
        budgets[id(a)] = len(a.words) + 1
        a.zero()
    for x in tuple(a.words):
        a.free(x)
    a.zero()
    need(any(label == "constructed" and allocated == live == 0 and count == 10
             for label, allocated, live, count in cuts), "pending constructor witness")
    need(len(objects[id(a)]) == 3 and cells(a) == 15, "reuse does not construct")
    return {"sampled_construction_write_cuts": len(cuts), "pending_allocation_witness": True,
            "peak_word_cells": 15}


def selected_ledger(w):
    """A schedule in the rectangle relaxation, NOT an actual caller run."""
    lr, li, ar, ai = 2, 3, 37672, 41
    r, i = w.Arena(2, lr + ar), w.Arena(5, li + ai)
    parents = ([r.literal(1) for _ in range(lr)], [i.literal(3) for _ in range(li)])
    for nr, ni in ((37672, 34), (20494, 41)):
        rw = [r.zero() for _ in range(nr)]
        iw = [i.zero() for _ in range(ni)]
        r.free_many(*rw)
        i.free_many(*iw)
    expected = (lr + ar + 1) * 4 + (li + ai + 1) * 7
    need(cells(r) + cells(i) == expected, "selected rectangle backing")
    need(r.live == {x.slot for x in parents[0]} and i.live == {x.slot for x in parents[1]},
         "selected relaxation restoration")
    need(all(x.inspect() == value for group, value in zip(parents, (1, 3)) for x in group),
         "selected relaxation parent values")
    return {"kind": "synthetic_rectangle_schedule_not_Consumer_apply", "entry_live": [lr, li],
            "additional_capacities": [ar, ai], "word_extents_with_LEFT": [4, 7],
            "retained_cells": expected}


def result():
    w = source()
    return {"schema_version": 1, "status": "PASS_SELECTED_NUMERICAL_ARENA_BACKING",
            "graphs": [graph(w, cap, bits) for bits in (2, 5) for cap in range(1, 6)],
            "witnesses": witnesses(w), "microstates": microstates(),
            "selected_ledger": selected_ledger(w), "no_new_kappa": True}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--emit", action="store_true")
    args = ap.parse_args()
    fresh = result()
    if not args.emit:
        expected = json.loads((ROOT / "RESULT.json").read_text())
        need(json.dumps(fresh, sort_keys=True) == json.dumps(expected, sort_keys=True), "typed receipt mismatch")
    print(json.dumps(fresh, indent=2))


if __name__ == "__main__":
    main()
