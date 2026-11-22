# SPDX-License-Identifier: Apache-2.0
"""Regenerate the complete one-rank-8-hyperplane recipient-stock screen."""
from collections import Counter, defaultdict
from hashlib import sha256
from pathlib import Path
import gzip
import json

HERE = Path(__file__).resolve().parent
PIN = "74e93daf2b7acf794ffb51f92f03f51556f68126d41ee13a8969bddb4cbe6326"
PLAIN_PIN = "b096d6df2a0c4688296b13ab0cfd50fec1c7dec732819c624ddd7a745a144b69"


def authenticate(data):
    if sha256(data).hexdigest() != PIN:
        raise ValueError("Literal compressed graph SHA-256 differs")
    plain = gzip.decompress(data)
    if sha256(plain).hexdigest() != PLAIN_PIN:
        raise ValueError("Literal expanded graph SHA-256 differs")
    return json.loads(plain)


def member(x, basis):
    while x:
        bit = 1 << (x.bit_length() - 1)
        row = basis.get(bit)
        if row is None:
            return False
        x ^= row
    return True


def insert(basis, x):
    while x:
        bit = 1 << (x.bit_length() - 1)
        if bit not in basis:
            basis[bit] = x
            return True
        x ^= basis[bit]
    return False


def screen(graph):
    n = graph["public"]
    assert n == 630 and len(graph["program"]) == 39600
    dims = {int(k): value["dim"] for k, value in graph["frames"].items()}
    rank8 = [i for i in range(222, n)
             if (graph["start"][i], graph["final"][i]) == (0, 1)]
    assert len(rank8) == 391 and dims[0] == 0 and dims[1] == 8
    hmask = sum(1 << i for i in rank8)
    outside = ((1 << n) - 1) ^ hmask
    frames = dict(enumerate(graph["start"]))
    values = {i: 1 << i for i in range(n)}

    # Each row (b, f) has b = f restricted outside the 391-dimensional
    # helper family. Eliminated dependencies in the full forms are exactly
    # the recipient's stock intersection with that helper family.
    projected = defaultdict(dict)
    kernels = defaultdict(dict)
    cosets = []

    def project(chart, bad, full):
        while bad:
            bit = 1 << (bad.bit_length() - 1)
            row = projected[chart].get(bit)
            if row is None:
                break
            bad ^= row[0]
            full ^= row[1]
        return bad, full

    def observe(register):
        chart = frames[register]
        bad, full = project(chart, values[register] & outside, values[register])
        if bad:
            projected[chart][1 << (bad.bit_length() - 1)] = (bad, full)
        elif full:
            assert not full & outside
            insert(kernels[chart], full)

    for register in range(n):
        observe(register)

    ops = Counter()
    for clock, (op, dest, *args) in enumerate(graph["program"]):
        ops[op] += 1
        touched = [dest]
        if op == "MOVE":
            first, last = args
            assert frames[dest] == first and dest >= n
            bad, h = project(last, values[dest] & outside, values[dest])
            if not bad:
                kernel = dict(kernels[last])
                assert h and not h & outside
                # No move is already reconstructible with unrestricted inputs.
                assert not member(h, kernel)
                cosets.append({"clock": clock, "owner": dest, "first": first,
                               "last": last, "rank": abs(dims[first] - dims[last]),
                               "h": h, "kernel": kernel})
            frames[dest] = last
        elif op == "INIT":
            assert dest >= n and dest not in frames
            frames[dest], values[dest] = args[0], 0
        elif op == "ADD":
            source, chart = args
            assert frames[dest] == frames[source] == chart
            values[dest] ^= values[source]
        elif op == "SWAP":
            source, = args
            frames[dest], frames[source] = frames[source], frames[dest]
            values[dest], values[source] = values[source], values[dest]
            touched.append(source)
        elif op == "CLEAR":
            assert dest >= n and frames.pop(dest) == args[0]
            del values[dest]
            touched = []
        else:
            raise ValueError(op)
        for register in touched:
            observe(register)

    assert ops == {"ADD": 29301, "INIT": 3433, "CLEAR": 3433,
                   "MOVE": 2803, "SWAP": 630}
    assert frames == dict(enumerate(graph["final"])) and set(values) == set(range(n))
    for i in range(n):
        expected = (1 << i) ^ ((1 << (i - 111)) if 111 <= i < 222 else 0)
        assert values[i] == expected
    assert len(cosets) == 768
    return cosets, rank8


def exhaust(cosets, rank8):
    final = [e for e in cosets if e["last"] == 1]
    others = [e for e in cosets if e["last"] != 1]
    assert len(final) == 391 and len(others) == 377
    assert [len(e["kernel"]) for e in final] == list(range(391))

    # Verify the successive chart-1 kernels are nested and acquire each
    # previous coset representative. Thus their 391 disjoint affine cosets
    # partition all nonzero vectors in the entire rank-8 helper space.
    for a, b in zip(final, final[1:]):
        assert set(a["kernel"].values()) <= set(b["kernel"].values())
        assert member(a["h"], b["kernel"])
    assert not member(final[-1]["h"], final[-1]["kernel"])

    # Coordinate each helper-space vector by the preceding 391 independent
    # representatives. The highest nonzero coefficient locates its sole
    # chart-1 coset; this avoids enumerating the 2^391-1 vectors.
    basis = {}
    for i, e in enumerate(final):
        x, expression = e["h"], 1 << i
        while x:
            bit = 1 << (x.bit_length() - 1)
            if bit not in basis:
                basis[bit] = (x, expression)
                break
            a, b = basis[bit]
            x, expression = x ^ a, expression ^ b
        else:
            raise AssertionError("Chart-1 representatives are dependent")
    assert len(basis) == len(rank8)

    def locate(h):
        x, expression = h, 0
        while x:
            bit = 1 << (x.bit_length() - 1)
            a, b = basis[bit]
            x, expression = x ^ a, expression ^ b
        assert expression
        item = final[expression.bit_length() - 1]
        assert member(h ^ item["h"], item["kernel"])
        return item

    # Every other coset is small, so enumerate it fully. No point occurs in
    # two of them. Distinct h not in this dictionary get one chart-1 move.
    points = {}
    assert max(len(e["kernel"]) for e in others) == 3
    for e in others:
        values = [e["h"]]
        for row in e["kernel"].values():
            values += [x ^ row for x in values]
        assert len(values) == len(set(values)) and all(values)
        for h in values:
            assert h not in points
            points[h] = (e, locate(h))
    assert len(points) == 549
    hist = Counter(tuple(sorted((a["rank"], b["rank"]))) for a, b in points.values())
    assert set(hist) <= {(1, 1), (1, 2), (1, 4), (2, 2)}
    assert Counter(e["rank"] for e in final) == {1: 301, 2: 90}
    assert (1, 4) in hist
    control = points[1 << 625]
    assert [(e["clock"], e["owner"], e["rank"]) for e in control] == [
        (6911, 2220, 4), (10570, 3006, 1)]
    return hist


def rank_four_corollary(graph):
    """Check every nonzero XOR within an exact co-endpoint rank-four class."""
    n = graph["public"]
    dims = {int(k): value["dim"] for k, value in graph["frames"].items()}
    groups = defaultdict(list)
    for helper in range(222, n):
        start, end = graph["start"][helper], graph["final"][helper]
        if abs(dims[start] - dims[end]) == 4:
            groups[start, end].append(helper)
    assert sum(map(len, groups.values())) == 17
    assert Counter(map(len, groups.values())) == {1: 3, 2: 7}
    candidates = [sum(1 << helper for index, helper in enumerate(group) if mask >> index & 1)
                  for group in groups.values() for mask in range(1, 1 << len(group))]
    assert len(candidates) == len(set(candidates)) == 24

    frames = dict(enumerate(graph["start"]))
    values = {i: 1 << i for i in range(n)}
    bases = defaultdict(dict)
    images = {}
    matches = {h: [] for h in candidates}

    def signatures(chart):
        if chart not in images:
            images[chart] = candidates.copy()
        return images[chart]

    def reduce(chart, value):
        remainder = 0
        while value:
            bit = 1 << (value.bit_length() - 1)
            if bit in bases[chart]:
                value ^= bases[chart][bit]
            else:
                remainder |= bit
                value ^= bit
        return remainder

    def observe(register):
        chart = frames[register]
        row = reduce(chart, values[register])
        if not row:
            return
        bit = 1 << (row.bit_length() - 1)
        bases[chart][bit] = row
        projected = signatures(chart)
        for j, h in enumerate(projected):
            if h & bit:
                projected[j] = h ^ row

    for register in range(n):
        observe(register)
    for clock, (op, dest, *args) in enumerate(graph["program"]):
        touched = [dest]
        if op == "MOVE":
            first, last = args
            assert frames[dest] == first
            wanted = reduce(last, values[dest])
            assert wanted
            for h, image in zip(candidates, signatures(last)):
                if image == wanted:
                    matches[h].append((clock, abs(dims[first] - dims[last])))
            frames[dest] = last
        elif op == "INIT":
            assert dest not in frames
            frames[dest], values[dest] = args[0], 0
        elif op == "ADD":
            source, chart = args
            assert frames[dest] == frames[source] == chart
            values[dest] ^= values[source]
        elif op == "SWAP":
            source, = args
            frames[dest], frames[source] = frames[source], frames[dest]
            values[dest], values[source] = values[source], values[dest]
            touched.append(source)
        elif op == "CLEAR":
            assert frames.pop(dest) == args[0]
            del values[dest]
            touched = []
        else:
            raise ValueError(op)
        for register in touched:
            observe(register)
    assert frames == dict(enumerate(graph["final"]))
    for i in range(n):
        expected = (1 << i) ^ ((1 << (i - 111)) if 111 <= i < 222 else 0)
        assert values[i] == expected
    histogram = Counter((h.bit_count(), tuple(sorted(rank for _, rank in rows)))
                        for h, rows in matches.items())
    assert histogram == {(1, (1, 2)): 17, (2, (2,)): 6, (2, (1,)): 1}
    return histogram


def concrete_control(graph):
    """Replace both named arrivals using only live original-chart owners."""
    original = graph["program"]
    assert original[6909:6912] == [["INIT", 2220, 0], ["ADD", 2220, 625, 0],
                                  ["MOVE", 2220, 0, 507]]
    assert original[10568:10571] == [["INIT", 3006, 583], ["ADD", 3006, 2361, 583],
                                    ["MOVE", 3006, 583, 1]]
    donors = [2976, 2977, 2979, 2987, 2988, 2989, 3004]
    replacements = {6909: [["INIT", 2220, 507]],
                    10568: [["INIT", 3006, 1]] + [["ADD", 3006, d, 1] for d in donors]}

    def apply(frames, values, instruction):
        op, dest, *args = instruction
        if op == "INIT":
            assert dest not in frames
            frames[dest], values[dest] = args[0], 0
        elif op == "MOVE":
            assert frames[dest] == args[0]
            frames[dest] = args[1]
        elif op == "ADD":
            source, chart = args
            assert frames[dest] == frames[source] == chart
            values[dest] ^= values[source]
        elif op == "SWAP":
            source, = args
            frames[dest], frames[source] = frames[source], frames[dest]
            values[dest], values[source] = values[source], values[dest]
        elif op == "CLEAR":
            assert frames.pop(dest) == args[0]
            del values[dest]
        else:
            raise ValueError(op)

    oldf = dict(enumerate(graph["start"]))
    oldv = {i: (0 if i == 625 else 1 << i) for i in range(630)}
    newf, newv = dict(oldf), dict(oldv)
    clock = 0
    while clock < len(original):
        if clock in replacements:
            for row in original[clock:clock + 3]:
                apply(oldf, oldv, row)
            for row in replacements[clock]:
                apply(newf, newv, row)
            assert oldf == newf and oldv == newv
            clock += 3
        else:
            apply(oldf, oldv, original[clock])
            apply(newf, newv, original[clock])
            clock += 1
    assert oldf == newf == dict(enumerate(graph["final"])) and oldv == newv
    for i in range(630):
        want = (0 if i == 625 else 1 << i) ^ ((1 << (i - 111)) if 111 <= i < 222 else 0)
        assert oldv[i] == want
    # The same original private CLEARs run in the same order; no extra owner
    # is introduced. Both replacement macro states agree before any later read.
    def first_use(owner, after):
        for time in range(after + 1, len(original)):
            op, dest, *args = original[time]
            if (op in ("ADD", "SWAP") and (dest == owner or args[0] == owner)) or (
                    dest == owner and op in ("MOVE", "CLEAR")):
                return time, original[time]
        raise AssertionError("The owner is never read or retired")

    assert first_use(2220, 6911) == (6937, ["ADD", 2223, 2220, 507])
    assert first_use(3006, 10570) == (29573, ["ADD", 3495, 3006, 1])


def main():
    data = (HERE / "strong-bit.json.gz").read_bytes()
    graph = authenticate(data)
    try:
        authenticate(bytes([data[0] ^ 1]) + data[1:])
    except ValueError:
        pass
    else:
        raise AssertionError("One-byte source corruption was accepted")
    cosets, rank8 = screen(graph)
    hist = exhaust(cosets, rank8)
    rank4_hist = rank_four_corollary(graph)
    concrete_control(graph)
    print("PASS_LITERAL", len(graph["program"]), "instructions", 2803, "MOVEs")
    print("PASS_HYPERPLANES", len(rank8), "rank-8 helpers", len(cosets),
          "eligible MOVEs", 549, "two-MOVE hyperplanes", sorted(hist.items()))
    print("PASS_RANK4_HYPERPLANES", 24, "co-endpoint constraints", sorted(rank4_hist.items()))
    print("PASS_LIVE_CONTROL helper=625 removed-ranks=4,1 first-reads=6937,29573")
    print("PASS_CORRUPTION_REJECTED")


if __name__ == "__main__":
    main()
