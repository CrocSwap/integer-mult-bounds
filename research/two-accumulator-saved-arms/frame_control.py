#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Replay the feasible raw CF0 frame schedule that motivated the construction."""
import gzip
import json
import sys
from functools import lru_cache
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from audit_local import basis

REGISTERS = (124, 125, 148, 149, 231, 283, 281, 299, 297, 591, 471, 483, 703)
OPERATIONS = {
    "r1": (125, 231), "r2": (124, 231), "r3": (124, 283), "r4": (125, 281),
    "a3": (591, 283), "a1": (591, 281), "s1": (149, 231), "s2": (148, 231),
    "s3": (148, 299), "s4": (149, 297), "b9": (703, 299), "b7": (703, 297),
    "W1": (283, 281), "W2": (299, 297), "e1": (471, 283), "e2": (483, 299),
    "q1": (125, 299), "q2": (149, 283), "W3": (283, 299),
    "z1": (124, 483), "z2": (148, 471),
}
PRECEDENCE = (
    ("r3", "W1"), ("a3", "W1"), ("W1", "e1"), ("W1", "q2"),
    ("e1", "W3"), ("q2", "W3"), ("s3", "W2"), ("b9", "W2"),
    ("W2", "e2"), ("W2", "q1"), ("W2", "W3"), ("e2", "z1"),
    ("e1", "z2"), ("W1", "W3"), ("q1", "W3"), ("e2", "W3"),
)
CAPS = ((124, 12), (125, 13), (148, 36), (149, 37),
        (591, 58), (591, 63), (703, 58), (703, 63))


def verify():
    if not __debug__:
        raise RuntimeError("verification requires assertions; do not use -O")
    word = json.loads(gzip.decompress((HERE / "inputs/CF0-FRAME-CONTROL.json.gz").read_bytes()))
    ports = word["ports"]
    frames = {r: (p,) for r, p in enumerate(ports)}
    frames.update({int(r): basis(f) for r, f in word.get("start_extra", {}).items()})
    for gate in word["A"] + word["B"][:239]:
        for r in gate[1:3] if gate[0] == "add" else gate[1:2]:
            frames[r] = basis(frames.get(r, ()) + tuple(gate[-1]))
    frames[703] = ()
    initial = tuple(frames.get(r, ()) for r in REGISTERS)
    names = list(OPERATIONS)
    index = {r: i for i, r in enumerate(REGISTERS)}
    gates = [tuple(index[r] for r in OPERATIONS[n]) for n in names]
    predecessors = [sum(1 << names.index(a) for a, b in PRECEDENCE if b == n) for n in names]
    seen = set()

    @lru_cache(None)
    def join(a, b):
        return basis(a + b)

    @lru_cache(None)
    def admissible(r, frame):
        return all(not ((v & ports[t]).bit_count() % 2)
                   for rr, t in CAPS if rr == r for v in frame)

    def search(done, current):
        if done == (1 << len(names)) - 1:
            return []
        key = done, current
        if key in seen:
            return None
        seen.add(key)
        for i, (a, b) in enumerate(gates):
            if done >> i & 1 or predecessors[i] & ~done:
                continue
            frame = join(current[a], current[b])
            if not admissible(REGISTERS[a], frame) or not admissible(REGISTERS[b], frame):
                continue
            changed = list(current)
            changed[a] = changed[b] = frame
            tail = search(done | (1 << i), tuple(changed))
            if tail is not None:
                return [names[i]] + tail
        return None

    order = search(0, initial)
    assert order is not None and len(seen) == 57478
    assert set(order) == set(names)
    assert all(order.index(a) < order.index(b) for a, b in PRECEDENCE)
    # Check the found order with explicit spans, without the cached joins.
    spans = {r: {0} for r in REGISTERS}
    for r, frame in zip(REGISTERS, initial):
        for v in frame:
            spans[r] |= {x ^ v for x in tuple(spans[r])}
    for name in order:
        a, b = OPERATIONS[name]
        merged = {x ^ y for x in spans[a] for y in spans[b]}
        spans[a] = spans[b] = merged
        for r, target in CAPS:
            assert all((v & ports[target]).bit_count() % 2 == 0 for v in spans[r])
    return {"status": "PASS_FEASIBLE_TWO_ACCUMULATOR_FRAME_CONTROL", "states": len(seen),
            "order": order, "scope": "Raw CF0 frame and precedence control only; no scalar or complete supplier admission is claimed."}


if __name__ == "__main__":
    print(json.dumps(verify(), indent=2))
