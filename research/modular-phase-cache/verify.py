"""Exact modular phase-cache construction and finite conformance checks."""

import hashlib
import itertools
import json
import math
from pathlib import Path
import sys


def need(condition, message):
    if not condition:
        raise ValueError(message)


def domain(t, b):
    need(type(t) is int and 0 <= t <= 10, "axis capacity")
    need(type(b) is int and 1 <= b <= 16, "precision capacity")


def bit_count(t, b):
    domain(t, b)
    return sum(math.comb(t, j) * max(b - j, 0) for j in range(t + 1))


def layout(t, b):
    domain(t, b)
    result = []
    offset = 0
    for mask in range(1 << t):
        width = b - mask.bit_count()
        if width > 0:
            result.append((mask, width, offset))
            offset += width
    need(offset == bit_count(t, b), "layout width")
    return tuple(result)


def valid_state(state, t, b):
    need(type(state) is int and 0 <= state < (1 << bit_count(t, b)),
         "cache state")


def encode(source, t, b):
    domain(t, b)
    modulus = 1 << b
    need(type(source) is tuple and len(source) == 1 << t, "source length")
    need(all(type(x) is int and 0 <= x < modulus for x in source),
         "source residue")
    values = list(source)
    for axis in range(t):
        bit = 1 << axis
        for mask in range(1 << t):
            if not mask & bit:
                values[mask] = (values[mask] + values[mask | bit]) % modulus
    state = 0
    for mask, width, offset in layout(t, b):
        state |= (values[mask] % (1 << width)) << offset
    valid_state(state, t, b)
    return state


def representative(state, t, b):
    """A source attaining any packed cache state, by inverse zeta transform."""
    valid_state(state, t, b)
    values = [0] * (1 << t)
    for mask, width, offset in layout(t, b):
        values[mask] = (state >> offset) & ((1 << width) - 1)
    for axis in range(t):
        bit = 1 << axis
        for mask in range(1 << t):
            if not mask & bit:
                values[mask] = (values[mask] - values[mask | bit]) % (1 << b)
    return tuple(values)


def flip(state, t, b, axis):
    """Two ordered passes: additions first, then negate their source fields."""
    valid_state(state, t, b)
    need(type(axis) is int and 0 <= axis < t, "update axis")
    fields = {mask: (width, offset) for mask, width, offset in layout(t, b)}
    bit = 1 << axis
    updated = state
    for mask, (width, offset) in fields.items():
        if not mask & bit and (mask | bit) in fields:
            source_width, source_offset = fields[mask | bit]
            source = (updated >> source_offset) & ((1 << source_width) - 1)
            target_mask = (1 << width) - 1
            target = (updated >> offset) & target_mask
            value = (target - 2 * source) & target_mask
            updated = (updated & ~(target_mask << offset)) | (value << offset)
    for mask, (width, offset) in fields.items():
        if mask & bit:
            field_mask = (1 << width) - 1
            value = (-(updated >> offset)) & field_mask
            updated = (updated & ~(field_mask << offset)) | (value << offset)
    valid_state(updated, t, b)
    return updated


def read(state, t, b):
    valid_state(state, t, b)
    return state & ((1 << b) - 1)


def literal_query(source, phase, b):
    return sum((-x if (a & phase).bit_count() % 2 else x)
               for a, x in enumerate(source)) % (1 << b)


def query_table(source, t, b):
    return tuple(literal_query(source, phase, b) for phase in range(1 << t))


def direct_encode(source, t, b):
    """Independent literal subset sums, without zeta-transform updates."""
    state = 0
    for mask, width, offset in layout(t, b):
        value = sum(x for a, x in enumerate(source) if a & mask == mask)
        state |= (value % (1 << width)) << offset
    return state


def exhaustive_sources():
    cases = [(0, 1), (0, 4), (1, 1), (1, 2), (1, 3),
             (2, 1), (2, 2), (2, 3), (2, 4), (3, 1), (3, 2)]
    sources = transitions = distinct = 0
    for t, b in cases:
        transcripts = {}
        for source in itertools.product(range(1 << b), repeat=1 << t):
            state = encode(source, t, b)
            table = query_table(source, t, b)
            need(state == direct_encode(source, t, b), "subset encoding")
            if state in transcripts:
                need(transcripts[state] == table, "cache collision")
            else:
                transcripts[state] = table
            need(read(state, t, b) == table[0], "initial read")
            for axis in range(t):
                changed = tuple((-x if a & (1 << axis) else x) % (1 << b)
                                for a, x in enumerate(source))
                updated = flip(state, t, b, axis)
                need(updated == encode(changed, t, b), "literal update")
                need(flip(updated, t, b, axis) == state, "involution")
                transitions += 1
            sources += 1
        need(len(transcripts) == 1 << bit_count(t, b), "image cardinality")
        need(len(set(transcripts.values())) == len(transcripts),
             "distinct states have distinct full query tables")
        distinct += len(transcripts)
    return {"cases": len(cases), "sources": sources,
            "source_axis_transitions": transitions, "distinct_states": distinct}


def exhaustive_states():
    states = transitions = comparisons = 0
    for t in range(5):
        for b in range(1, 5):
            if bit_count(t, b) > 12:
                continue
            for state in range(1 << bit_count(t, b)):
                source = representative(state, t, b)
                need(encode(source, t, b) == state, "surjective cache")
                table = query_table(source, t, b)
                for axis in range(t):
                    moved = flip(state, t, b, axis)
                    moved_table = query_table(representative(moved, t, b), t, b)
                    need(moved_table == tuple(table[s ^ (1 << axis)]
                                             for s in range(1 << t)),
                         "query translation")
                    need(flip(moved, t, b, axis) == state, "state restoration")
                    transitions += 1
                for left in range(t):
                    for right in range(left):
                        a = flip(flip(state, t, b, left), t, b, right)
                        z = flip(flip(state, t, b, right), t, b, left)
                        need(a == z, "commuting updates")
                        comparisons += 1
                states += 1
    return {"states": states, "state_axis_transitions": transitions,
            "commuting_pairs": comparisons}


def wider_histories():
    fixtures = updates = 0
    for t in range(11):
        for b in (1, 2, 3, 8, 16):
            for pattern in range(4):
                source = tuple(((a + 1) ** (pattern + 1) + 3 * pattern) % (1 << b)
                               for a in range(1 << t))
                state = encode(source, t, b)
                need(state == direct_encode(source, t, b), "wide subset sums")
                initial = state
                phase = 0
                word = tuple(range(t)) + tuple(reversed(range(t)))
                for axis in word:
                    state = flip(state, t, b, axis)
                    phase ^= 1 << axis
                    need(read(state, t, b) == literal_query(source, phase, b),
                         "history read")
                    updates += 1
                need(state == initial and phase == 0, "whole history restoration")
                fixtures += 1
    return {"fixtures": fixtures, "updates": updates}


def rejected(call, message):
    try:
        call()
    except ValueError as error:
        need(str(error) == message, "wrong rejection")
        return 1
    raise ValueError("invalid input accepted")


def controls():
    count = 0
    count += rejected(lambda: bit_count(True, 2), "axis capacity")
    count += rejected(lambda: bit_count(11, 2), "axis capacity")
    count += rejected(lambda: bit_count(1, 0), "precision capacity")
    count += rejected(lambda: bit_count(1, 17), "precision capacity")
    count += rejected(lambda: encode((1,), 1, 2), "source length")
    count += rejected(lambda: encode((0, 4), 1, 2), "source residue")
    count += rejected(lambda: encode((True, 0), 1, 2), "source residue")
    count += rejected(lambda: read(-1, 1, 2), "cache state")
    count += rejected(lambda: read(1 << bit_count(2, 3), 2, 3), "cache state")
    count += rejected(lambda: flip(0, 1, 2, 1), "update axis")
    count += rejected(lambda: flip(0, 1, 2, False), "update axis")
    x, y = (1, 0), (0, 1)
    need(literal_query(x, 0, 2) == literal_query(y, 0, 2), "same initial read")
    need(literal_query(x, 1, 2) != literal_query(y, 1, 2), "later separator")
    need(encode((0, 0), 1, 2) == encode((2, 2), 1, 2), "true modular quotient")
    need((0, 0) != (2, 2), "source erasure boundary")
    state = encode((0, 1), 1, 2)
    correct = flip(state, 1, 2, 0)
    need(read(correct, 1, 2) == 3, "signed update fixture")
    need(read(state, 1, 2) != read(correct, 1, 2), "omitted update detected")
    need(bit_count(2, 3) == 8 and bit_count(3, 2) == 5, "memory examples")
    return {"invalid_inputs": count}


def formulas():
    checks = 0
    for t in range(11):
        need(bit_count(t, 1) == 1, "modulo two collapse")
        need(bit_count(t, 2) == t + 2, "modulo four law")
        for b in range(max(1, t), 17):
            expected = b if t == 0 else b * (1 << t) - t * (1 << (t - 1))
            need(bit_count(t, b) == expected, "large precision law")
            checks += 1
    return checks


def source_hashes():
    root = Path(__file__).resolve().parent
    hashes = {}
    for name in ("README.md", "PROOF.md", "TASK.json", "SOURCES.json",
                 "VERIFY.json", "verify.py"):
        with (root / name).open("rb") as stream:
            data = stream.read(262145)
        need(len(data) <= 262144, "receipt file capacity")
        hashes[name] = hashlib.sha256(data).hexdigest()
    return hashes


def main():
    need(len(sys.argv) == 1, "no arguments supported")
    result = {"sources": exhaustive_sources(), "states": exhaustive_states(),
              "histories": wider_histories(), "controls": controls(),
              "formula_cases": formulas(), "package_sha256": source_hashes(),
              "python": sys.version, "status": "PASS_MODULAR_PHASE_CACHE"}
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
