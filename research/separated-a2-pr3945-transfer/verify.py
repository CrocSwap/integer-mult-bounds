#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Transfer of the seven separated A2 sites onto the frozen PR3945 words.

The sites and removed positions are the published witness of PR #4019. The
words are the byte-pinned inputs of research/staged544-a1858-contraction-audit,
which already freezes both PR3734 providers and both PR3945 words. No
predecessor Python is imported. A rank-d child is charged only when a
register's frame dimension increases.
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
SITES = (
    {"section": "B", "indices": (4, 53, 54), "removed_position": 0},
    {"section": "B", "indices": (7, 49, 50), "removed_position": 0},
    {"section": "restore", "indices": (20, 21, 36), "removed_position": 2},
    {"section": "restore", "indices": (22, 23, 38), "removed_position": 2},
    {"section": "restore", "indices": (26, 27, 51), "removed_position": 2},
    {"section": "restore", "indices": (30, 31, 62), "removed_position": 2},
    {"section": "restore", "indices": (32, 33, 73), "removed_position": 2},
)
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
    "On both frozen PR3945 words, the seven separated A2 sites occur at the "
    "published indices, and contracting them removes seven forward ADDs and "
    "five cleanup ADDs without changing the recursive frame histogram."
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


def gate_registers(gate):
    return {gate[1], gate[2]} if gate[0] == "add" else {gate[1]}


def segments(word, section):
    if section == "B":
        cuts = sorted({0, len(word["B"])} | {record[0] for record in word["warps"]})
    else:
        cuts = [0, len(word[section])]
    return list(zip(cuts, cuts[1:]))


def matrix(gates, registers):
    order = {register: index for index, register in enumerate(registers)}
    state = [[Fraction(i == j) for j in range(3)] for i in range(3)]
    for gate in gates:
        dst, src = order[gate[1]], order[gate[2]]
        sign = Fraction(gate[3], gate[4])
        state[dst] = [state[dst][k] + sign * state[src][k] for k in range(3)]
    return state


def certify(word, site):
    section, indices, position = site["section"], site["indices"], site["removed_position"]
    need(any(low <= indices[0] and indices[2] < high for low, high in segments(word, section)),
         "warp boundary", section, indices)
    gates = [word[section][i] for i in indices]
    need(all(gate[0] == "add" for gate in gates), "not an ADD site", section, indices)
    support = set().union(*(gate_registers(gate) for gate in gates))
    need(len(support) == 3, "support", section, indices, support)
    need(all(gate[-1] == gates[0][-1] for gate in gates), "frame split", section, indices)
    for index in range(indices[0], indices[2] + 1):
        if index not in indices:
            need(gate_registers(word[section][index]).isdisjoint(support),
                 "intervening dependency", section, index)
    remaining = [deepcopy(gate) for offset, gate in enumerate(gates) if offset != position]
    replacement = remaining[::-1]
    registers = tuple(sorted(support))
    need(matrix(gates, registers) == matrix(replacement, registers), "identity", section, indices)
    wrong = [deepcopy(gate) for gate in gates]
    wrong_remaining = [gate for offset, gate in enumerate(wrong) if offset != (position + 1) % 3]
    need(matrix(gates, registers) != matrix(wrong_remaining[::-1], registers),
         "wrong removal was not rejected", section, indices)
    return replacement


def contract(word, remap=True):
    changed = deepcopy(word)
    body_positions = None
    for section in ("A", "B", "restore"):
        local = [site for site in SITES if site["section"] == section]
        starts = {}
        skipped = set()
        for site in local:
            starts[site["indices"][0]] = certify(word, site)
            skipped.update(site["indices"][1:])
        result, positions = [], {}
        for index, gate in enumerate(word[section]):
            positions[index] = len(result)
            if index in starts:
                result.extend(deepcopy(starts[index]))
            elif index not in skipped:
                result.append(deepcopy(gate))
        positions[len(word[section])] = len(result)
        changed[section] = result
        if section == "B":
            body_positions = positions
    if remap:
        for record in changed["warps"]:
            record[0] = body_positions[record[0]]
    changed["cleanup"] = derive_cleanup(changed)
    return changed


def add_count(word, key):
    return sum(gate[0] == "add" for gate in word[key])


def main():
    need(LEMMA in (PACKAGE / "README.md").read_text(encoding="utf-8"), "README dropped the lemma")
    pr3945 = 0
    for name, digest, profile in WORDS:
        word = load_word(name, digest)
        need(derive_cleanup(word) == word["cleanup"], "baseline cleanup", name)
        before, _chain = frame_bill(word)
        need(before == profile, "baseline histogram", name, before)
        edited = contract(word)
        after, _after_chain = frame_bill(edited)
        need(after == before, "histogram moved", name, after)
        forward = (add_count(word, "A") + add_count(word, "B") + add_count(word, "restore")
                   - add_count(edited, "A") - add_count(edited, "B") - add_count(edited, "restore"))
        cleanup = add_count(word, "cleanup") - add_count(edited, "cleanup")
        need(forward == 7 and cleanup == 5, "saving", name, forward, cleanup)
        need(add_count(word, "B") - add_count(edited, "B") == 2, "B saving", name)
        need(add_count(word, "restore") - add_count(edited, "restore") == 5, "restore saving", name)
        bare = contract(word, remap=False)
        try:
            frame_bill(bare)
        except AuditFailure as exc:
            need("frame containment fails" in str(exc), "remap control", name, exc)
        else:
            raise AuditFailure("missing warp remap was accepted " + name)
        if name.startswith("PR3945"):
            pr3945 += 1
    need(pr3945 == 2, "PR3945 words", pr3945)
    print(
        "PASS_SEPARATED_A2_PR3945_TRANSFER words=4 sites=7 "
        "forward_add_delta=-7 cleanup_add_delta=-5 histograms=unchanged"
    )


if __name__ == "__main__":
    main()
