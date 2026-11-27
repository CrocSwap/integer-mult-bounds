#!/usr/bin/env python3
"""Physical recovered-coefficient carry, capped source positioning and raw output."""
from dataclasses import dataclass
from itertools import product
import json
import random

BLANK, HOME = ".", "^"
SOURCE, CARRY_A, CARRY_B, LOW, LIMIT, OUTPUT = range(6)
LOW_CODES, HIGH_CODES = "ab", "cd"


@dataclass(frozen=True)
class Act:
    target: tuple
    writes: tuple = ()
    moves: tuple = ()


START, MARK, WARM, WARM_BACK = ((label,) for label in ("start", "mark", "warm", "warm_back"))
GO_HOME, SEEK, EMIT, HALT = ((label,) for label in ("go_home", "seek", "emit", "halt"))


def rule(state, scanned):
    """Read only the six scanned symbols and the finite control state."""
    if state == START:
        return Act(MARK, moves=((CARRY_A, -1), (CARRY_B, -1), (LOW, -1)))
    if state == MARK:
        banks = (CARRY_A, CARRY_B, LOW)
        return Act(WARM, tuple((t, HOME) for t in banks), tuple((t, 1) for t in banks))
    if state == WARM:
        if scanned[SOURCE] == "z":
            return Act(WARM, ((CARRY_A, "0"),), ((SOURCE, 1), (CARRY_A, 1)))
        assert scanned[SOURCE] == ":"
        return Act(WARM_BACK, moves=((SOURCE, 1),))
    if state == WARM_BACK:
        if scanned[CARRY_A] == HOME:
            return Act(("row", 0, 0), moves=((CARRY_A, 1),))
        return Act(WARM_BACK, moves=((CARRY_A, -1),))
    if state[0] in ("row", "pad", "back"):
        phase, parity = state[:2]
        old, new = (CARRY_A, CARRY_B) if parity == 0 else (CARRY_B, CARRY_A)
        if phase == "row":
            incoming = state[2]
            tag = scanned[SOURCE]
            if tag == "$":
                return Act(GO_HOME)
            if tag == "|":
                return Act(("pad", parity), ((new, str(incoming)),), ((SOURCE, 1), (new, 1)))
            assert tag in LOW_CODES + HIGH_CODES and scanned[old] in "01"
            destination = LOW if tag in LOW_CODES else new
            a = 0 if tag in "ac" else 1
            total = a + int(scanned[old]) + incoming
            return Act(("row", parity, total // 2), ((destination, str(total % 2)), (old, BLANK)),
                       ((SOURCE, 1), (old, 1), (destination, 1)))
        if phase == "pad":
            if scanned[SOURCE] == "z":
                return Act(state, ((new, "0"),), ((SOURCE, 1), (new, 1)))
            assert scanned[SOURCE] == ";"
            return Act(("back", parity), moves=((SOURCE, 1),))
        if scanned[old] == HOME:
            assert scanned[new] == HOME
            return Act(("row", 1-parity, 0), moves=((old, 1), (new, 1)))
        return Act(state, moves=((old, -1), (new, -1)))
    if state == GO_HOME:
        if scanned[LOW] == HOME:
            return Act(SEEK, moves=((LOW, 1),))
        return Act(GO_HOME, moves=((LOW, -1),))
    if state == SEEK:
        if scanned[LIMIT] == "*":
            return Act(SEEK, moves=((LOW, 1), (LIMIT, 1)))
        assert scanned[LIMIT] == BLANK
        return Act(EMIT, moves=((LOW, -1),))
    if state == EMIT:
        if scanned[LOW] == HOME:
            return None
        assert scanned[LOW] in "01"
        return Act(EMIT, ((OUTPUT, scanned[LOW]),), ((LOW, -1), (OUTPUT, 1)))
    raise AssertionError(state)


def known_states():
    return (START, MARK, WARM, WARM_BACK, GO_HOME, SEEK, EMIT,
            *(("row", p, c) for p, c in product((0, 1), repeat=2)),
            *(("pad", p) for p in (0, 1)), *(("back", p) for p in (0, 1)))


def source_stream(width, limb, coefficients):
    initial_zeros = "z"*width + ":"
    records = []
    for coefficient in coefficients:
        assert 0 <= coefficient < 1 << width
        digits = [(LOW_CODES if j < limb else HIGH_CODES)[(coefficient >> j) & 1]
                  for j in range(width)]
        records.append("".join(digits) + "|" + "z"*(limb-1) + ";")
    return initial_zeros + "".join(records) + "$"


def format_rule(state, scanned):
    """Raw nonnegative u-bit records, a single reusable split mask, and the formatted output."""
    raw, mask, dest = 0, 1, 2
    q = state
    if q == "warm":
        if scanned[mask] in "lh":
            return Act(q, ((dest, "z"),), ((mask, 1), (dest, 1)))
        return Act("rewarm", ((dest, ":"),), ((dest, 1),))
    if q in ("rewarm", "redata", "repad"):
        if scanned[mask] == HOME:
            return Act({"rewarm": "data", "redata": "skip", "repad": "data"}[q],
                       moves=((mask, 1),))
        return Act(q, moves=((mask, -1),))
    if q == "data":
        if scanned[raw] == "$":
            return Act("done", ((dest, "$"),))
        if scanned[raw] == "|":
            assert scanned[mask] == BLANK
            return Act("redata", ((dest, "|"),), ((dest, 1), (raw, 1)))
        assert scanned[raw] in "01" and scanned[mask] in "lh"
        tags = LOW_CODES if scanned[mask] == "l" else HIGH_CODES
        return Act(q, ((dest, tags[int(scanned[raw])]),), ((dest, 1), (raw, 1), (mask, 1)))
    if q == "skip":
        assert scanned[mask] == "l"
        return Act("pad", moves=((mask, 1),))
    if q == "pad":
        if scanned[mask] == "l":
            return Act(q, ((dest, "z"),), ((mask, 1), (dest, 1)))
        return Act("repad", ((dest, ";"),), ((dest, 1),))
    if q == "done":
        return None
    raise AssertionError(q)


def format_recovered(width, limb, coefficients):
    raw = "".join(format(a, f"0{width}b")[::-1] + "|" for a in coefficients) + "$"
    mask = "l"*limb + "h"*(width-limb)
    raw_tape = dict(enumerate(raw))
    mask_tape = {-1: HOME, **dict(enumerate(mask))}
    data = [raw_tape, mask_tape, {}]
    heads = [0, 0, 0]
    state, count = "warm", 0
    while True:
        scans = tuple(t.get(p, BLANK) for t, p in zip(data, heads))
        act = format_rule(state, scans)
        if act is None:
            break
        for t, sym in act.writes:
            data[t][heads[t]] = sym
        for t, delta in act.moves:
            heads[t] += delta
        state = act.target
        count += 1
    # A warm scan and rewind, followed by two linear mask resets per row.
    assert count == 2*width+4 + len(coefficients)*(2*width+2*limb+6)
    result = "".join(data[2][p] for p in range(len(data[2])))
    assert result == source_stream(width, limb, coefficients)
    return result, count


def clock(width, limb, rows, cap):
    # Opening, warm word, alternating coefficient rows, ending sentinel,
    # rewind over the entire limb tape, capped forward positioning, raw reverse copy.
    return (2 + 2*width + 3 + rows*(2*width + limb + 3)
            + 1 + rows*limb + 2 + cap + 1 + cap)


def simulate(width, limb, coefficients, cap):
    assert 1 <= limb <= width and 0 <= cap <= len(coefficients)*limb
    source, _ = format_recovered(width, limb, coefficients)
    heads = [0]*6
    data = [dict(enumerate(source)), {}, {}, {}, dict(enumerate("*"*cap)), {}]
    visited = [{0} for _ in heads]
    state, count = START, 0
    seen = set()
    while True:
        scanned = tuple(t.get(p, BLANK) for t, p in zip(data, heads))
        seen.add(state)
        action = rule(state, scanned)
        if action is None:
            break
        for t, symbol in action.writes:
            if symbol == BLANK:
                data[t].pop(heads[t], None)
            else:
                data[t][heads[t]] = symbol
        for t, delta in action.moves:
            assert delta in (-1, 1)
            heads[t] += delta
            visited[t].add(heads[t])
        state = action.target
        count += 1
        assert count <= clock(width, limb, len(coefficients), cap)
    assert seen <= set(known_states())
    assert count == clock(width, limb, len(coefficients), cap)
    value = sum(a << (limb*i) for i, a in enumerate(coefficients))
    mask = (1 << cap) - 1
    expected = format(value & mask, f"0{cap}b") if cap else ""
    assert data[OUTPUT] == dict(enumerate(expected))
    carry_tape = CARRY_A if len(coefficients)%2 == 0 else CARRY_B
    carry = value >> (limb*len(coefficients))
    assert carry < 1 << width
    assert data[carry_tape] == {-1: HOME, **{j: str(carry >> j & 1) for j in range(width)}}
    assert heads[OUTPUT] == cap and heads[LOW] == -1
    # Include both initial and final head positions in every union.
    cells = sum(map(len, visited))
    upper = len(source) + 2*(width+2) + len(coefficients)*limb+2 + 2*(cap+1)
    assert cells <= upper
    return count, cells, seen


def main():
    rng = random.Random(9140839)
    cases = []
    for width in range(1, 5):
        for limb in range(1, width+1):
            for cs in product(range(1 << width), repeat=2):
                for cap in {0, 1, limb, 2*limb}:
                    cases.append((width, limb, cs, cap))
    for width in (1, 7, 31, 72, 257):
        for limb in sorted({1, width, max(1, width//2)}):
            for size in (0, 1, 2, 13):
                for cs in ([0]*size, [(1 << width)-1]*size,
                           [rng.getrandbits(width) for _ in range(size)]):
                    cap = rng.randrange(1+size*limb)
                    cases.append((width, limb, cs, cap))
    all_states, peak_steps, peak_cells = set(), 0, 0
    for case in cases:
        steps, cells, used = simulate(*case)
        peak_steps, peak_cells = max(peak_steps, steps), max(peak_cells, cells)
        all_states.update(used)
    assert all_states == set(known_states())
    print(json.dumps(dict(cases=len(cases), tapes=6, reached_states=len(all_states),
                          maximum_steps=peak_steps, maximum_visited=peak_cells)))


if __name__ == "__main__":
    main()
