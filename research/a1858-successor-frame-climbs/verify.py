#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Successor frame climbs of the published A1858 contraction.

The four frozen words are the byte-pinned inputs of
research/staged544-a1858-contraction-audit. This verifier does not import that
package or the PR #3998 frame tracer. The chronological bill below is a
separate reading of the same BORROW-WORD contract: a register pays a rank-d
child only when its frame dimension increases.
"""

import gzip
import hashlib
import json
from collections import Counter
from copy import deepcopy
from fractions import Fraction
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
INPUTS = ROOT / "research" / "staged544-a1858-contraction-audit" / "inputs"

V, N, H = 112, 704, 9
FULL_VECTORS = [256, 128, 64, 32, 16, 8, 4, 2, 1]
TRIPLE = [
    ["add", 457, 475, -1, 1, [82, 42]],
    ["add", 456, 457, 1, 1, [82, 42]],
    ["add", 456, 475, 1, 1, [82, 42]],
]
PAIR = [
    ["add", 456, 457, 1, 1, [82, 42]],
    ["add", 457, 475, -1, 1, [82, 42]],
]
WORDS = (
    ("BORROW-WORD-43base.json.gz",
     "5ca4be99851f8878cbfe0fd6c454df926b11218f17feefa1664721cf03156699",
     {1: 2440, 2: 725, 3: 224, 4: 102, 5: 20, 8: 8}),
    ("BORROW-WORD-43extra.json.gz",
     "965268a9be73d3f62e7ef680d18f108cf064bfe1f44b82157baa61443232904e",
     {1: 2440, 2: 725, 3: 224, 4: 102, 5: 20, 8: 8}),
    ("PR3945-WORD-base.json.gz",
     "08e6c96fbe3dfec96cb8451b3867ef8c1a214109ecd1e5af7fcc28e0f05728d0",
     {1: 2482, 2: 712, 3: 218, 4: 109, 5: 20, 8: 8}),
    ("PR3945-WORD-extra.json.gz",
     "d83c2ec9cecc0ad092d34ea4080b28a4fd7199579356b6d5a8fc6cd53ff93299",
     {1: 2482, 2: 712, 3: 218, 4: 109, 5: 20, 8: 8}),
)
LEMMA = (
    "On all four frozen words, the A1858 contraction leaves every "
    "positive-dimension climb of registers 456, 457 and 475 unchanged, and "
    "it leaves the recursive frame histogram unchanged."
)


class AuditFailure(Exception):
    """Explicit failure. python -O does not disable it."""


def need(ok, *why):
    if not ok:
        raise AuditFailure(" ".join(map(str, why)))


def is_target(register):
    return V <= register < 2 * V


def touched(gate):
    return gate[1:3] if gate[0] == "add" else gate[1:2]


_SPAN = {}


def span(vectors):
    key = tuple(vectors)
    mask = _SPAN.get(key)
    if mask is None:
        points = {0}
        for vector in key:
            need(type(vector) is int and 0 <= vector < 512, "frame vector", vector)
            if vector not in points:
                points |= {point ^ vector for point in points}
        mask = sum(1 << point for point in points)
        _SPAN[key] = mask
    return mask


def dim(mask):
    size = bin(mask).count("1")
    need(size and size & (size - 1) == 0, "not a subspace")
    return size.bit_length() - 1


def hyperplane(port):
    return sum(1 << x for x in range(512) if bin(x & port).count("1") % 2 == 0)


def warp_images(columns):
    need(len(columns) == H and all(type(c) is int and 0 <= c < 512 for c in columns), "warp columns")
    images = [0] * 512
    for x in range(1, 512):
        low = x & -x
        images[x] = images[x ^ low] ^ columns[low.bit_length() - 1]
    need(len(set(images)) == 512, "singular warp")
    return images


def image_mask(images, mask):
    return sum(1 << images[x] for x in range(512) if mask >> x & 1)


def frame_bill(word):
    """Chronological rank histogram. A climb of dimension d pays one rank-d child."""
    report = word["report"]
    need((report["v"], 2 * report["v"] + report["R"], report["h"]) == (V, N, H), "geometry")
    removed = set(word["removed"])
    live = [r for r in range(N) if r not in removed]
    liveset = set(live)
    block, warps = word["B"], word["warps"]
    for index, (pos, lender, cols, upper, lower) in enumerate(warps, 1):
        need(0 <= pos <= len(block) and lender in liveset and not is_target(lender), "warp", index)
        images = warp_images(cols)
        need(image_mask(images, span(upper)) == span(lower), "warp frame", index)
    ports = word["ports"]
    start, end = {}, {}
    for register in live:
        if register < V:
            start[register], end[register] = span((ports[register],)), (1 << 512) - 1
        elif register < 2 * V:
            start[register], end[register] = 1, hyperplane(ports[register - V])
        else:
            start[register], end[register] = 1, (1 << 512) - 1
    for name, mask in word["start_extra"].items():
        start[int(name)] = span(mask)
    for name, mask in word["helper_final"].items():
        end[int(name)] = span(mask)
    current, bill, chain = dict(start), Counter(), {}

    def climb(register, mask, where):
        need(current[register] & ~mask == 0, "frame containment fails", where, register)
        gap = dim(mask) - dim(current[register])
        if gap:
            bill[gap] += 1
        chain.setdefault(register, []).append((where, gap))
        current[register] = mask

    prelude = word["prelude_events"]
    for index, gate in enumerate(word["A"]):
        if gate[0] == "warp":
            _, register, op, fr, to = gate
            images = warp_images(warps[abs(op) - 1][2])
            if op < 0:
                inverse = [0] * 512
                for x, y in enumerate(images):
                    inverse[y] = x
                images = inverse
            need(image_mask(images, span(fr)) == span(to), "prelude warp", index)
            current[register] = span(to)
        else:
            for register in touched(gate):
                climb(register, span(gate[-1]), ("A", index))
    levels = {V + int(name): span(mask) for name, mask in word["target_levels"].items()}
    need(all(current[t] == levels.get(t, 1) for t in range(V, 2 * V)), "target levels")
    for centre, frame in zip(word["centers"], word["center_frames"]):
        mask = span(frame)
        need(current[centre] == mask, "centre entry", centre)
        served = {levels.get(gate[1], 1) for gate in word["cut"] if gate[2] == centre}
        for target in sorted(served, key=lambda item: -dim(item)):
            need(target & ~mask == 0, "centre descent", centre)
            gap = dim(mask) - dim(target)
            if gap:
                bill[gap] += 1
            mask = target
    placed = {}
    for index, record in enumerate(warps, 1):
        placed.setdefault(record[0], []).append(index)
    for position in range(len(block) + 1):
        for index in placed.get(position, ()):
            _, lender, _, upper, lower = warps[index - 1]
            need(current[lender] == span(upper), "warp entry", index)
            current[lender] = span(lower)
        if position < len(block):
            for register in touched(block[position]):
                climb(register, span(block[position][-1]), ("B", position))
    for index, gate in enumerate(word["restore"]):
        for register in touched(gate):
            climb(register, span(gate[-1]), ("restore", index))
    for register in live:
        climb(register, end[register], ("end",))
    return dict(sorted(bill.items())), chain


def ordinary_forward(word):
    out = list(word["A"][word["prelude_events"]:])
    placed = {}
    for index, record in enumerate(word["warps"], 1):
        placed.setdefault(record[0], []).append(["warp", record[1], index])
    for position in range(len(word["B"]) + 1):
        out.extend(placed.get(position, []))
        if position < len(word["B"]):
            out.append(word["B"][position])
    return out + list(word["restore"])


def derive_cleanup(word):
    restored = set(map(int, word["helper_final"]))

    def renamed(register):
        return register + N if register in restored else register

    out = []
    for gate in reversed(ordinary_forward(word)):
        if gate[0] == "warp":
            out.append(["warp", renamed(gate[1]), -gate[2], FULL_VECTORS])
        elif is_target(gate[1]):
            continue
        elif gate[0] == "add":
            out.append(["add", renamed(gate[1]), renamed(gate[2]), -gate[3], gate[4], FULL_VECTORS])
        else:
            need(gate[0] == "scale", "unknown gate", gate[0])
            out.append(["scale", renamed(gate[1]), gate[3], gate[2], FULL_VECTORS])
    return out


def load_word(name, digest):
    raw = (INPUTS / name).read_bytes()
    need(hashlib.sha256(raw).hexdigest() == digest, "sha256", name)
    with gzip.GzipFile(fileobj=__import__("io").BytesIO(raw)) as handle:
        return json.load(handle)


def locate(word):
    head = [gate[:5] for gate in TRIPLE]
    found = [i for i in range(len(word["A"]) - 2) if [g[:5] for g in word["A"][i:i + 3]] == head]
    need(found == [1858], "triple site", found)
    return 1858


def contracted(word):
    edited = deepcopy(word)
    index = locate(word)
    edited["A"] = word["A"][:index] + deepcopy(PAIR) + word["A"][index + 3:]
    edited["cleanup"] = derive_cleanup(edited)
    return edited


def matrix(gates):
    state = [[Fraction(i == j) for j in range(3)] for i in range(3)]
    order = {456: 0, 457: 1, 475: 2}
    for gate in gates:
        dst, src, sign = order[gate[1]], order[gate[2]], Fraction(gate[3], gate[4])
        state[dst] = [state[dst][k] + sign * state[src][k] for k in range(3)]
    return state


def positive(chain, register):
    return [event for event in chain[register] if event[1] > 0]


def zero_a(chain, register):
    return [event for event in chain[register] if event[1] == 0 and event[0][0] == "A"]


def main():
    need(LEMMA in (PACKAGE / "README.md").read_text(encoding="utf-8"), "README dropped the lemma")
    need(matrix(TRIPLE) == matrix(PAIR), "contraction map")
    flipped = deepcopy(PAIR)
    flipped[1][3] = 1
    need(matrix(TRIPLE) != matrix(flipped), "flipped sign was not rejected")
    for name, digest, profile in WORDS:
        word = load_word(name, digest)
        need(derive_cleanup(word) == word["cleanup"], "baseline cleanup", name)
        before, chain = frame_bill(word)
        need(before == profile, "baseline histogram", name, before)
        after_word = contracted(word)
        after, chain_after = frame_bill(after_word)
        need(after == before, "histogram moved", name, after)
        for register in (456, 457, 475):
            need(positive(chain, register) == positive(chain_after, register),
                 "paid climb moved", name, register)
        need(chain[457] == chain_after[457], "register 457 sequence moved", name)
        before_456 = zero_a(chain, 456)
        after_456 = zero_a(chain_after, 456)
        need(before_456[-2:] == [(("A", 1859), 0), (("A", 1860), 0)], "456 before", name)
        need(after_456[-1:] == [(("A", 1858), 0)] and after_456[:-1] == before_456[:-2], "456 after", name)
        need(zero_a(chain, 475) == [(("A", 1858), 0), (("A", 1860), 0)], "475 before", name)
        need(zero_a(chain_after, 475) == [(("A", 1859), 0)], "475 after", name)
        widened = deepcopy(word)
        block = deepcopy(word["A"][1858:1861])
        for gate in block:
            gate[-1] = [82, 42, 1]
        widened["A"] = word["A"][:1858] + block + word["A"][1861:]
        widened["cleanup"] = derive_cleanup(widened)
        try:
            frame_bill(widened)
        except AuditFailure as exc:
            need("frame containment fails" in str(exc), "widen control", name, exc)
        else:
            raise AuditFailure("widened frame was accepted " + name)
        dropped = deepcopy(word)
        dropped["A"] = word["A"][:1858] + word["A"][1861:]
        dropped["cleanup"] = derive_cleanup(dropped)
        dropped_bill, _ = frame_bill(dropped)
        need(dropped_bill != before, "dropped block kept the histogram", name)
    print(
        "PASS_A1858_SUCCESSOR_FRAME_CLIMBS words=4 "
        "pr3734={1:2440,2:725,3:224,4:102,5:20,8:8} "
        "pr3945={1:2482,2:712,3:218,4:109,5:20,8:8} paid_climbs=unchanged"
    )


if __name__ == "__main__":
    main()
