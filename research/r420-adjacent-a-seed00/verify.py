#!/usr/bin/env python3
"""Exact R420 adjacent A-gate frame rigidity. Apache-2.0.

Prepared for GitHub contributor thakrarsagar with substantial OpenAI Codex assistance.
The predecessor word and its full audit are eumemic's PR543 contribution.
"""
import copy
import gzip
import hashlib
import importlib.util
import json
import sys
from collections import Counter
from fractions import Fraction
from functools import lru_cache
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WORD = "research/e8-bit-r420/data/bitE8mut-r420.json.gz"


def need(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def basis(rows):
    """Exact row-echelon basis in Q^8, indexed by leading coordinate."""
    out = {}
    for vector in rows:
        row = list(map(Fraction, vector))
        for col, pivot in sorted(out.items()):
            multiple = row[col]
            row = [a - multiple * b for a, b in zip(row, pivot)]
        col = next((i for i, x in enumerate(row) if x), None)
        if col is not None:
            divisor = row[col]
            out[col] = tuple(x / divisor for x in row)
    return out


def perpendicular(rows):
    pivots = basis(rows)
    out = []
    for free in range(8):
        if free in pivots:
            continue
        row = [Fraction(0)] * 8
        row[free] = 1
        for col in sorted(pivots, reverse=True):
            row[col] = -sum(pivots[col][j] * row[j] for j in range(col + 1, 8))
        out.append(tuple(row))
    return out


def operands(gate):
    return {gate[1], *gate[2]}


def commute(a, b):
    return a[1] not in b[2] and b[1] not in a[2]


def boundaries(word):
    current = word["start"][:]
    for frame, target, sources in word["D"]:
        for reg in {target, *sources}:
            current[reg] = frame
    before = []
    for gate in word["A"]:
        before.append(current[:])
        for reg in operands(gate):
            current[reg] = gate[0]
    after = [None] * len(word["A"])
    for i in reversed(range(len(word["A"]))):
        after[i] = current[:]
        for reg in operands(word["A"][i]):
            current[reg] = word["A"][i][0]
    return before, after


def paid(word, masks, dims):
    current = word["start"][:]
    histogram = Counter()

    def climb(reg, frame):
        old = current[reg]
        need(not masks[old] & ~masks[frame], "illegal frame descent")
        delta = dims[frame] - dims[old]
        if delta:
            histogram[delta] += 1
        current[reg] = frame

    for section in "DABC":
        for gate in word[section]:
            for reg in operands(gate):
                climb(reg, gate[0])
        if section == "A":
            histogram.update(dims[current[reg]] for reg in word["ret"])
    for reg, frame in enumerate(word["final"]):
        climb(reg, frame)
    need(0 not in histogram, "zero-rank copy")
    return dict(sorted(histogram.items()))


def mirror_cleanup(word):
    full = next(i for i, f in enumerate(word["frames"]) if len(f) == word["v"])
    z = [g for g in word["A"] + word["B"]
         if not word["v"] <= g[1] < 2 * word["v"]]
    word["C"] = [[full, t, list(ss)] for _, t, ss in reversed(z)]


def controls(word, audit, masks, dims, baseline):
    # These planes meet in a line absent from the supplied list of root lines.
    e = [tuple(int(i == j) for j in range(8)) for i in range(8)]
    u = [e[0], e[1]]
    v = [tuple(a + b for a, b in zip(e[0], e[2])),
         tuple(a + b for a, b in zip(e[1], e[2]))]
    need(8 - len(basis(perpendicular(u) + perpendicular(v))) == 1,
         "lost non-root intersection")
    need(len(basis([e[0]])) < 8 - len(basis(perpendicular(u))),
         "control must expose a flexible, nonrigid interval")
    need(not commute([0, 1, [0]], [0, 2, [1]]), "dependency control")
    need(commute([0, 2, [0]], [0, 2, [1]]), "same-destination control")

    def rejected(candidate, message):
        try:
            checked = audit.check(candidate)
        except audit.Reject:
            return
        need(not all(checked[3].values()) or not all(checked[4].values()), message)

    changed = copy.deepcopy(word)
    changed["A"][0], changed["A"][1] = changed["A"][1], changed["A"][0]
    rejected(changed, "unmirrored cleanup accepted")
    mirror_cleanup(changed)
    result = audit.check(changed)
    need(all(result[3].values()) and all(result[4].values()), "legal mirrored swap rejected")
    need(paid(changed, masks, dims) == baseline, "mirrored swap changed full price")

    bad = copy.deepcopy(word)
    bad["A"][240], bad["A"][241] = bad["A"][241], bad["A"][240]
    mirror_cleanup(bad)
    rejected(bad, "noncommuting swap accepted")
    bad = copy.deepcopy(word)
    bad["A"][0][0] = 3  # Wrong line, with the same rank as frame 2.
    rejected(bad, "equal-rank wrong subspace accepted")
    return 8


def verify():
    sources = json.loads((HERE / "SOURCES.json").read_text())
    for path, expected in sources["inputs_sha256"].items():
        need(hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == expected,
             "source pin mismatch: " + path)
    word = json.loads(gzip.decompress((ROOT / WORD).read_bytes()))
    spec = importlib.util.spec_from_file_location("r420_audit", ROOT / "research/e8-bit-r420/code/xcheck.py")
    audit = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(audit)
    checked = audit.check(word)
    need(all(checked[3].values()) and all(checked[4].values()), "baseline interface failed")
    frames = [tuple(basis(word["lines"][i] for i in frame).values()) for frame in word["frames"]]
    normals = [perpendicular(frame) for frame in frames]
    dims = [len(frame) for frame in frames]
    masks = [sum(1 << i for i in frame) for frame in word["frames"]]
    before, after = boundaries(word)

    @lru_cache(None)
    def lower_rank(ids):
        return len(basis(row for f in ids for row in frames[f]))

    @lru_cache(None)
    def upper_rank(ids):
        return 8 - len(basis(row for f in ids for row in normals[f]))

    counts = Counter()
    census = Counter()
    rows = []
    for i, (a, b) in enumerate(zip(word["A"], word["A"][1:])):
        if not commute(a, b):
            counts["noncommuting"] += 1
            continue
        counts["commuting"] += 1
        counts["same_destination"] += int(a[1] == b[1])
        witnesses = []
        for gate in (a, b):
            pre = tuple(sorted({before[i][r] for r in operands(gate)}))
            post = tuple(sorted({after[i + 1][r] for r in operands(gate)}))
            frame = gate[0]
            need(all(not masks[f] & ~masks[frame] for f in pre), "lower containment")
            need(all(not masks[frame] & ~masks[f] for f in post), "upper containment")
            low, high = lower_rank(pre), upper_rank(post)
            need(low == dims[frame] == high, "frame freedom at pair %d" % i)
            census[low] += 1
            witnesses.append([frame, list(pre), list(post), low, high])
        # Only shared operands could reverse their frame path when the gates swap.
        need(not operands(a) & operands(b) or masks[a[0]] == masks[b[0]],
             "swapped pair descends")
        rows.append([i, witnesses])

    histogram = paid(word, masks, dims)
    expected = json.loads((ROOT / "research/e8-bit-r420/EXPECTED.json").read_text())
    need(histogram == {int(k): v for k, v in expected["word"]["local_histogram"].items()},
         "full paid profile mismatch")
    control_count = controls(word, audit, masks, dims, histogram)
    return {
        "status": "PASS_R420_ADJACENT_A_RIGIDITY",
        "positions": len(word["A"]) - 1,
        "counts": dict(sorted(counts.items())),
        "forced_gate_occurrences": sum(census.values()),
        "forced_dimension_census": dict(sorted(census.items())),
        "rational_frame_gaps": 0,
        "witness_rows_sha256": hashlib.sha256(canonical(rows)).hexdigest(),
        "full_local_paid_profile": histogram,
        "rank_mass": sum(k * v for k, v in histogram.items()),
        "controls": control_count,
    }


if __name__ == "__main__":
    result = verify()
    if sys.argv[1:] == ["--print-certificate"]:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        need(not sys.argv[1:], "usage: verify.py [--print-certificate]")
        expected = json.loads((HERE / "CERTIFICATE.json").read_text())
        need(json.loads(canonical(result)) == expected, "certificate mismatch")
        print("PASS_R420_ADJACENT_A_RIGIDITY positions=2063 commuting=1735 forced=3470 gaps=0 rank_mass=5112 controls=8")
