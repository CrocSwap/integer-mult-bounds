#!/usr/bin/env python3
"""Extra wires cannot lower the n - v + z floor of a unit-ADD data block.

Checks, in order:
1. The pinned PR5840 controller: both programs replay to the stored sides,
   each has length 38, and each side's data-block floor n - v + z is 38.
2. Extended-wire controls on that boundary: words with a clean scratch wire,
   a garbage scratch wire and a restored dirty external wire realize the same
   32-wire data block, cost more than 38, and respect the floor.
3. The potential invariant of the written proof, step by step, on seeded
   random words with added wires.
4. A complete finite check at width four: every element of GL(4, F2), at its
   exact unit-ADD distance, respects the floor for every choice of data wires.

Standard library only. No file is written.
"""

import hashlib
import json
import random
import sys
from collections import deque
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONTROLLER = ROOT / "research/g20-isolated-exchange-floor/inputs/CONTROLLER.json"
CONTROLLER_SHA256 = "978536e852c0cfbc150f143e19d2cfddbb434bac6017d914974eb99f641593a8"
WIDTH = 32
SIDE_FLOOR = 38
RANDOM_WORDS = 400
SEED = 20261103


def require(ok, message):
    if not ok:
        raise SystemExit("FAIL: " + message)


def apply_word(word, wires):
    rows = [1 << i for i in range(wires)]
    for dest, source in word:
        require(0 <= dest < wires and 0 <= source < wires and dest != source, "invalid gate")
        rows[dest] ^= rows[source]
    return rows


def expand_program(program):
    word = []
    for op, dest, source in program:
        require(op in ("ADD", "SWAP"), "unknown opcode")
        if op == "ADD":
            word.append((dest, source))
        else:
            word.extend(((dest, source), (source, dest), (dest, source)))
    return word


def data_block(rows, data):
    """Top-left block on the listed data wires, re-indexed 0..len(data)-1."""
    block = []
    for r in data:
        value = 0
        for j, c in enumerate(data):
            if (rows[r] >> c) & 1:
                value |= 1 << j
        block.append(value)
    return block


def floor_bound(block):
    """n - v + z for a square binary block given as row bitmasks."""
    n = len(block)
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for i in range(n):
        for j in range(n):
            if i != j and (block[i] >> j) & 1:
                a, b = find(i), find(j)
                if a != b:
                    parent[a] = b
    v = len({find(i) for i in range(n)})
    z = sum(1 for i in range(n) if not (block[i] >> i) & 1)
    return n - v + z


def check_controller():
    raw = CONTROLLER.read_bytes()
    require(hashlib.sha256(raw).hexdigest() == CONTROLLER_SHA256, "controller hash changed")
    boundary = json.loads(raw)["boundaries"]
    words = {}
    for side in ("left", "right"):
        word = expand_program(boundary[side + "_program"])
        rows = apply_word(word, WIDTH)
        require(rows == boundary[side + "_rows"], side + " program does not replay")
        require(len(word) == SIDE_FLOOR, side + " word length is not 38")
        require(floor_bound(rows) == SIDE_FLOOR, side + " floor is not 38")
        words[side] = word
    require(boundary["boundary_unit_ADDs_per_port"] == 2 * SIDE_FLOOR, "port invoice changed")
    return boundary, words


def express(rows, target, wires):
    """Return wire indices whose current rows XOR to target (Gaussian elimination)."""
    basis = []  # (pivot row value, set of wires)
    for w in wires:
        value, combo = rows[w], {w}
        for b_value, b_combo in basis:
            if value ^ b_value < value:
                value ^= b_value
                combo ^= b_combo
        if value:
            basis.append((value, combo))
            basis.sort(key=lambda item: -item[0])
    value, combo = target, set()
    for b_value, b_combo in basis:
        if value ^ b_value < value:
            value ^= b_value
            combo ^= b_combo
    require(value == 0, "target not in span")
    return sorted(combo)


def relabel(word, old, new):
    return [(new if d == old else d, new if s == old else s) for d, s in word]


def check_extended_controls(boundary, words):
    """Each control realizes the same 32-wire data block on 33 wires; S = wire 32.

    clean:   S starts at zero, copies x0, and is cleared from final data rows.
    garbage: S starts at zero and ends holding x3.
    relay:   S starts at zero and carries wire 31's data through the whole word.
    dirty:   S holds unknown live data, carries wire 31 and is restored.
    """
    data = list(range(WIDTH))
    s = WIDTH
    full = (1 << WIDTH) - 1
    lengths = []
    for side in ("left", "right"):
        target = boundary[side + "_rows"]
        word = words[side]
        final = apply_word(word, WIDTH)
        clear = [(s, w) for w in express(final, 1, data)]
        swap = [(s, 31), (31, s), (s, 31)]
        controls = {
            "clean": [(s, 0)] + word + clear,
            "garbage": [(s, 3)] + word,
            "relay": [(s, 31), (31, s)] + relabel(word, 31, s) + [(31, s), (s, 31)],
            "dirty": swap + relabel(word, 31, s) + swap,
        }
        for name, control in controls.items():
            rows = apply_word(control, WIDTH + 1)
            # Rows over 33 input coordinates; bit 32 is the extra wire's input.
            require(data_block(rows, data) == target, side + " " + name + " data block differs")
            if name in ("clean", "relay"):
                require(rows[s] & full == 0, side + " " + name + " scratch not clean")
            if name == "garbage":
                require(rows[s] & full == 1 << 3, side + " garbage contents")
            if name == "dirty":
                require(rows[s] == 1 << s, side + " dirty wire not restored")
                require(all(not (rows[r] >> s) & 1 for r in data), side + " dirty leak")
            bound = floor_bound(data_block(rows, data))
            require(bound == SIDE_FLOOR < len(control), side + " " + name + " floor")
            lengths.append(len(control))
    return lengths


def potential_run(word, wires, data):
    """Check the written potential step by step; return final (bound, length)."""
    rows = [1 << i for i in range(wires)]
    parent = list(range(wires))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    blocks = wires
    zeros = 0
    for step, (dest, source) in enumerate(word, 1):
        joins = find(dest) != find(source)
        before = (rows[dest] >> dest) & 1
        if joins:
            require(not (rows[source] >> dest) & 1, "cross-block entry before a join")
        rows[dest] ^= rows[source]
        after = (rows[dest] >> dest) & 1
        if joins:
            require(before == after, "join changed a diagonal entry")
            parent[find(dest)] = find(source)
            blocks -= 1
        zeros += (before == 1 and after == 0) - (before == 0 and after == 1)
        require(zeros == sum(1 for i in range(wires) if not (rows[i] >> i) & 1), "zero count")
        # Support invariant: every nonzero entry lies inside one gate block.
        for i in range(wires):
            for j in range(wires):
                if (rows[i] >> j) & 1:
                    require(find(i) == find(j), "entry crosses gate blocks")
        require(wires - blocks + zeros <= step, "potential exceeds length")
    block = data_block(rows, data)
    return floor_bound(block), len(word)


def check_random_words():
    rng = random.Random(SEED)
    tight = 0
    for _ in range(RANDOM_WORDS):
        n = rng.randint(1, 6)
        k = rng.randint(1, 3)
        wires = n + k
        length = rng.randint(0, 14)
        word = []
        for _ in range(length):
            d, s = rng.sample(range(wires), 2)
            word.append((d, s))
        data = sorted(rng.sample(range(wires), n))
        bound, used = potential_run(word, wires, data)
        require(bound <= used, "random word beats the floor")
        tight += bound == used
    return tight


def check_width_four():
    """Exact distances on GL(4, F2); every data subset of every state obeys the floor."""
    wires = 4
    start = tuple(1 << i for i in range(wires))
    dist = {start: 0}
    queue = deque([start])
    gates = [(d, s) for d in range(wires) for s in range(wires) if d != s]
    while queue:
        state = queue.popleft()
        for d, s in gates:
            nxt = list(state)
            nxt[d] ^= nxt[s]
            nxt = tuple(nxt)
            if nxt not in dist:
                dist[nxt] = dist[state] + 1
                queue.append(nxt)
    require(len(dist) == 20160, "GL(4, F2) order")
    subsets = [[i for i in range(wires) if (mask >> i) & 1] for mask in range(1, 1 << wires)]
    checks = 0
    best = {}
    for state, d in dist.items():
        for data in subsets:
            block = tuple(data_block(state, data))
            require(floor_bound(list(block)) <= d, "width-four state beats the floor")
            checks += 1
            if len(data) < wires:
                key = (len(data), block)
                if key not in best or d < best[key]:
                    best[key] = d
    # Statistic only: data blocks (widths one to three, the other wires as
    # unrestricted extras) whose least exact distance equals the floor.
    attained = sum(1 for (n, block), d in best.items() if floor_bound(list(block)) == d)
    return len(dist), checks, len(best), attained


def main():
    require(sys.version_info[:2] == (3, 12), "CPython 3.12 required")
    boundary, words = check_controller()
    controls = check_extended_controls(boundary, words)
    tight = check_random_words()
    states, checks, blocks, attained = check_width_four()
    print(
        "PASS_G20_EXTENDED_WIRE_FLOOR side=38 port=76 witness=38/38 "
        f"controls={len(controls)} control_lengths={sorted(set(controls))} "
        f"random_words={RANDOM_WORDS} random_tight={tight} "
        f"gl4_states={states} gl4_checks={checks} gl4_blocks={blocks} gl4_attained={attained} "
        "no_new_kappa"
    )


if __name__ == "__main__":
    main()
