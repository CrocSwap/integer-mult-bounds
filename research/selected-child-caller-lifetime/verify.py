#!/usr/bin/env python3
"""Source caller probes and complete small Boolean primitives; Apache-2.0.

Ross Richardson with substantial OpenAI Codex assistance. Source construction
and inherited component proofs retain their authors' credit in README.md.
"""
import argparse
from collections import Counter
from contextlib import ExitStack
from dataclasses import replace
import json
from pathlib import Path
import sys
from types import SimpleNamespace
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
from runtime import ROOT, authenticate_dependencies, need, read_json, runtime


def state(arena):
    return {slot: (bytes(arena.words[slot].cells), arena.words[slot].head)
            for slot in arena.live}


class Census:
    def __init__(self, m, arenas, bounds):
        self.m, self.arenas, self.bounds = m, arenas, bounds
        self.saved = tuple(state(a) for a in arenas)
        self.entry = tuple(len(a.live) for a in arenas)
        self.peaks = [0] * len(arenas)
        self.allocations = self.scans = 0
        self.original = m.words.Arena.zero

    def sample(self, scan=False):
        delta = tuple(len(a.live) - n for a, n in zip(self.arenas, self.entry))
        for j, count in enumerate(delta):
            self.peaks[j] = max(self.peaks[j], count)
            need(count <= self.bounds[j], "numerical budget")
        if scan:
            for a in self.arenas:
                occupied = sum(c not in (self.m.words.LEFT, self.m.words.BLANK)
                               for w in (*a.words, a.template) for c in w.cells)
                need(occupied == (len(a.live) + 1) * (a.bits + 1), "occupied numerical cells")
                self.scans += 1
        return delta

    def allocate(self, arena):
        result = self.original(arena)
        if arena in self.arenas:
            self.allocations += 1
            self.sample()
        return result

    def install(self, stack):
        census = self
        stack.enter_context(patch.object(self.m.words.Arena, "zero", lambda a: census.allocate(a)))

    def restored(self):
        need(tuple(state(a) for a in self.arenas) == self.saved, "entry values heads and ownership")
        self.sample(scan=True)


class Specifications(dict):
    """Numerically neutral fixture metadata; no catalogue membership claim."""
    def __init__(self, spec, plan):
        super().__init__({0: spec})
        self.fixed_plan = plan
        self.catalogue = SimpleNamespace(requests=[SimpleNamespace(kind="LOCAL")])

    def bind(self, request_id, common, low):
        need(request_id == 0 and common and low == self[0].low, "fixture binding")
        return self[0]

    def plan(self, code):
        need(code == 0, "fixture plan")
        return self.fixed_plan


def caller_fixture(m, good, rank, width, depth, borrowed):
    residues = m.words.Arena(3, 5000)
    indices = m.words.Arena(max(8, (width * 64**depth).bit_length()+1), 96)
    ring = m.words.Ring(residues.literal(3))
    identity = tuple(tuple(int(i == j) for j in range(64)) for i in range(64))
    low = [list(row) for row in identity]
    if not good:
        low[0], low[63] = low[63], low[0]
    low = tuple(map(tuple, low))
    projector = [[int(i == j and (i < rank if good else i == 63))
                  for j in range(64)] for i in range(64)]
    plan = m.plan.compile_plan(projector, rank, 3, good)
    spec = SimpleNamespace(code=0, good=good, low=low,
                           template=SimpleNamespace(q=3, rank=rank, preparation=identity))
    specs = Specifications(spec, plan)
    if depth:
        specs[1] = SimpleNamespace(code=1, good=True, low=identity,
                                  template=SimpleNamespace(q=3, rank=1, preparation=identity))
    program = m.records.Program.fixture(indices, residues, width*64**depth, 2,
                                        [(0, 1, 1, 0, 0, 0)]*depth, code_bits=8)
    high = [[0]*64 for _ in range(64)]
    fields = m.records.Fields.fixture(indices, residues, [(1, high)]*depth, code_bits=8)
    parent, level = indices.literal(width), indices.literal(depth)
    for j in range(borrowed):
        residues.literal(j % 3)
        indices.literal(j)
    codes = SimpleNamespace(q=3, dimension=64, bits=8, limit=256)
    context = m.directory.Context(ring, codes)
    counts = [m.cardinal_counts.Count.literal(1) for _ in range(4)]
    consumer = m.consumer.Consumer(context, indices, program, specs, parent, level)
    return SimpleNamespace(**locals())


def caller_case(m, good=True, rank=1, width=64, depth=0, borrowed=3,
                child_limit=None, extra_scratch=False, wrong_parent=False,
                leak_callback=False, callee_indices=0):
    f = caller_fixture(m, good, rank, width, depth, borrowed)
    census = Census(m, (f.residues, f.indices), (4096, 41))
    saved_tapes = bytes(f.program.tape.cells), bytes(f.fields.tape.cells)
    inventory, sampled, callbacks, boundary = Counter(), set(), Counter(), Counter()
    original_action = m.stream_runner.action
    original_execute = m.trace.execute
    event_count = 0

    def key(event):
        if event.kind == "add":
            r = event.request
            return ("adapter", r.reference.kind, r.reverse_adapter) if r.kind == "adapter" else (
                "child", r.child_kind, r.reverse, r.half, r.negative_inverse)
        return (event.kind,)

    def trace(geometry):
        nonlocal event_count
        iterator = original_execute(geometry)
        try:
            for event in iterator:
                event_count += 1
                need(event_count <= 200000, "bounded trace")
                census.sample()
                if wrong_parent and event.kind == "return":
                    event = replace(event, parent_identity=object())
                yield event
        finally:
            iterator.close()

    def coefficient(_plan, ring, *_args):
        request = _args[-1]
        expected = 12 if request.kind == "adapter" else 18 + int(not good)
        need(census.sample(scan=True) == (0, expected), "exact callback entry")
        if request.kind == "child" and child_limit is not None:
            need(expected <= child_limit, "child entry budget")
        callbacks[request.kind] += 1
        if request.kind == "child":
            scratch = [f.indices.zero() for _ in range(callee_indices)]
            for value in scratch:
                f.indices.free(value)
        if leak_callback:
            ring.arena.zero()
        return ring.arena.copy(ring.one)

    def add_pass(_source, ring, *_args, **_kwargs):
        prepare = _args[-1]
        scratch = f.indices.zero() if extra_scratch else None
        try:
            for _ in range(2):
                result = prepare()
                ring.arena.free(result)
        finally:
            if scratch is not None:
                f.indices.free(scratch)
        return m.records.Tape(), {}

    def action(source, event, layout, callback, factory):
        tag = key(event)
        inventory[tag] += 1
        delta = census.sample()
        if event.kind == "add":
            expected = 12 if event.request.kind == "adapter" else 18+int(not good)
            need(delta == (0, expected), "trace ADD inventory")
            if tag not in sampled:
                sampled.add(tag)
                return original_action(source, event, layout, callback, factory)
        return factory()

    def prefix(directory, _fields):
        directory.head = len(directory.cells)
        return m.records.Tape()

    def observe(kind):
        boundary[(kind, census.sample())] += 1

    with ExitStack() as stack:
        census.install(stack)
        stack.enter_context(patch.object(m.consumer, "selected_coefficient", coefficient))
        stack.enter_context(patch.object(m.consumer, "execute", trace))
        stack.enter_context(patch.object(m.packet_engine, "action", action))
        stack.enter_context(patch.object(m.packet_engine, "copy_bits", lambda *_: None))
        stack.enter_context(patch.object(m.packet_engine, "read_prefix", prefix))
        stack.enter_context(patch.object(m.stream_runner, "add_pass", add_pass))
        # Serialized movement is outside this numerical claim, as in PR2801.
        stack.enter_context(patch.object(m.records.Tape, "rewind", lambda t: setattr(t, "head", 1)))
        source = m.records.Tape()
        result = f.consumer.apply(source, 0, True, f.spec.low, f.fields.tape,
                                  f.counts[0], *f.counts[1:], observe=observe)
        need(result.read() == m.words.BLANK, "abstract payload result")
        result.clear()
    census.restored()
    need((bytes(f.program.tape.cells), bytes(f.fields.tape.cells)) == saved_tapes,
         "serialized entry preservation")
    need(f.program.tape.head == f.fields.tape.head == 1, "serialized heads")
    need(callbacks["child"] > 0, "child callback exercised")
    expected_boundary = 12 + int(not good)
    need(set(boundary) == {("enter", (0, expected_boundary)), ("return", (0, expected_boundary))},
         "complete child boundary inventory")
    need(boundary[("enter", (0, expected_boundary))] == boundary[("return", (0, expected_boundary))],
         "paired child returns")
    return {"good": good, "rank": rank, "width": width, "depth": depth, "borrowed": borrowed,
            "trace_events": event_count, "peaks_with_abstract_coefficient": census.peaks,
            "callback_samples": dict(sorted(callbacks.items())), "cell_scans": census.scans,
            "inventory": [[list(k), v] for k, v in sorted(inventory.items(), key=lambda kv: str(kv[0]))],
            "boundaries": [[kind, list(delta), count] for (kind, delta), count in sorted(boundary.items())]}


def tape_values(tape):
    return list(tape.cells[1:])


def primitive_case(m, kind, q, exponent, before=1, middle=1, suffix=1, budget=6,
                   omit_translation=False):
    modulus = q**exponent
    arena = m.words.Arena(modulus.bit_length()+1, 24)
    ring = m.words.Ring(arena.literal(modulus))
    for j in range(3):
        arena.literal(j % modulus)
    counts = []
    for value in (before, middle, suffix):
        count = m.cardinal_counts.Count.literal(value)
        counts.append(count.marginal())
        count.close()
    size = before * modulus * suffix * (middle*modulus if kind == "swap" else 1)
    values = [int(((j*37+11) ^ (j >> 2)) % 11 < 5) for j in range(size)]
    source = m.records.Tape()
    for bit in values:
        source.append(bit)
    source.rewind()
    census = Census(m, (arena,), (budget,))
    with ExitStack() as stack:
        census.install(stack)
        if omit_translation:
            stack.enter_context(patch.object(m.bitstream, "translate_one", lambda src, *_: src))
        if kind == "swap":
            output = m.bitstream.atom_swap(source, ring, q, *counts)
            expected = [values[((((b*modulus+y)*middle+k)*modulus+x)*suffix+t)]
                        for b in range(before) for x in range(modulus) for k in range(middle)
                        for y in range(modulus) for t in range(suffix)]
        else:
            output = m.bitstream.sign_address(source, ring, q, counts[0], counts[2])
            expected = [values[(b*modulus+(-x % modulus))*suffix+t]
                        for b in range(before) for x in range(modulus) for t in range(suffix)]
    need(tape_values(output) == expected, "complete Boolean permutation")
    need(tape_values(source) == values and source.head == 1, "borrowed payload preservation")
    census.restored()
    need(census.peaks == [6], "sharp non-ADD peak")
    output.clear()
    source.clear()
    for count in counts:
        count.close()
    return {"kind": kind, "q": q, "exponent": exponent, "before": before, "middle": middle,
            "suffix": suffix, "payload_bits": size, "additional_residue_peak": census.peaks[0],
            "allocations": census.allocations, "cell_scans": census.scans}


def run():
    authenticate_dependencies()
    with runtime() as m:
        callers = []
        for good, rank, width, depth, borrowed in (
                       (True, 1, 64, 0, 3), (True, 42, 127, 4, 7),
                       (False, 1, 64, 0, 3), (False, 1, 127, 4, 7)):
            callers.append(caller_case(m, good, rank, width, depth, borrowed))
            print("checked caller", good, rank, width, depth, file=sys.stderr)
        primitives = [primitive_case(m, kind, q, exponent, before, middle, suffix)
                      for kind in ("swap", "sign")
                      for q, exponent, before, middle, suffix in (
                          (3, 1, 1, 1, 1), (3, 2, 2, 2, 2), (3, 3, 1, 2, 2),
                          (5, 1, 2, 1, 2), (5, 2, 1, 1, 2))]
    return {"status": "PASS_CHILD_CALLER_NUMERICAL_LIFETIME", "callers": callers,
            "primitives": primitives, "child_entry_indices": {"good": 18, "fallback": 19},
            "conditional_child_allowance": [20494, 41],
            "conditional_full_call_weighted_envelope": "max(37672*r+34*i,20494*r+41*i)",
            "no_new_kappa": True, "full_GL64_payload_executed": False}


def compare_receipt(result, expected):
    need(json.dumps(result, sort_keys=True) == json.dumps(expected, sort_keys=True), "typed receipt equality")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--emit", action="store_true")
    args = parser.parse_args()
    result = run()
    if not args.emit:
        expected = read_json(ROOT / "RESULT.json")
        compare_receipt(result, expected)
    print(json.dumps(result, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
