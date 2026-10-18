#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""B509 boundary certificate; @CubeJerry with substantial OpenAI Codex assistance.

Standard library only. No predecessor implementation is imported. See README.md
for the all-length argument: these finite checks are not a formal proof of it.
"""
from collections import Counter
from fractions import Fraction
from pathlib import Path
import argparse
import gzip
import hashlib
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
FRAME, SOURCE = 509, 22
INPUTS = (
    "research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz",
    "research/r439-bsection-stars-seed01/composition.json.gz",
    "research/r439-bsection-stars-seed01/candidate.json.gz",
)


def need(ok, message):
    if not ok:
        raise ValueError(message)


def support(mask, n):
    return [i for i in range(n) if mask >> i & 1]


def basis(rows):
    """Rational row reduction; frame entries are never reduced modulo two."""
    rows = [[Fraction(x) for x in row] for row in rows]
    pivot = 0
    for col in range(len(rows[0]) if rows else 0):
        found = next((i for i in range(pivot, len(rows)) if rows[i][col]), None)
        if found is None:
            continue
        rows[pivot], rows[found] = rows[found], rows[pivot]
        scale = rows[pivot][col]
        rows[pivot] = [x / scale for x in rows[pivot]]
        for i in range(len(rows)):
            if i != pivot and rows[i][col]:
                scale = rows[i][col]
                rows[i] = [x - scale * y for x, y in zip(rows[i], rows[pivot])]
        pivot += 1
        if pivot == len(rows):
            break
    return tuple(tuple(row) for row in rows[:pivot])


def inverse(rows):
    n = len(rows)
    a = [row | (1 << (n + i)) for i, row in enumerate(rows)]
    for col in range(n):
        p = next((i for i in range(col, n) if a[i] >> col & 1), None)
        need(p is not None, "singular matrix")
        a[col], a[p] = a[p], a[col]
        for i in range(n):
            if i != col and a[i] >> col & 1:
                a[i] ^= a[col]
    return [row >> n for row in a]


def matrix(ops, n):
    rows = [1 << i for i in range(n)]
    for d, s in ops:
        need(0 <= d < n and 0 <= s < n and d != s, "invalid XOR")
        rows[d] ^= rows[s]
    return rows


class Geometry:
    def __init__(self, word):
        self.lines, self.frames = word["lines"], word["frames"]
        self.bases = [basis(self.lines[i] for i in frame) for frame in self.frames]
        self.ranks = [len(b) for b in self.bases]
        self.cache = {}

    def contains(self, outer, inner):
        key = outer, inner
        if key not in self.cache:
            self.cache[key] = basis(self.bases[outer] + self.bases[inner]) == self.bases[outer]
        return self.cache[key]

    def join_rank(self, frames):
        return len(basis(row for f in set(frames) for row in self.bases[f]))


def trace(word, geo):
    """Original-register frames and scalar map, not physical COPY/ERASE replay."""
    v, n = word["v"], 2 * word["v"] + word["R"]
    need((v, n, word["h"]) == (111, 661, 8), "word dimensions")
    current = list(word["start"])
    paths = [[f] for f in current]
    rows = [1 << i for i in range(n)]
    profile, ops = Counter(), []
    ids = [i for i, gate in enumerate(word["B"]) if gate[0] == FRAME]
    need(ids and ids == list(range(ids[0], ids[-1] + 1)), "noncontiguous B509")
    first, end, entry = ids[0], ids[-1] + 1, None

    def move(r, f):
        old = current[r]
        if old != f:
            need(geo.contains(f, old) and geo.ranks[f] > geo.ranks[old], "illegal frame move")
            profile[geo.ranks[f] - geo.ranks[old]] += 1
            current[r] = f
            paths[r].append(f)

    for section in ("D", "A", "scatter", "B", "C"):
        if section == "scatter":
            need(all(geo.ranks[current[v + t]] == 0 for t in range(v)), "scatter target frame")
            copies = [geo.ranks[current[r]] for r in word["ret"]]
            profile.update(copies)
            # Exact additive quotient of the retained-total COPY/ERASE stream.
            for t, indices in enumerate(word["scatter"]):
                for k in indices:
                    s = word["ret"][k]
                    rows[v + t] ^= rows[s]
                    ops.append((v + t, s))
            continue
        for i, (f, d, ss) in enumerate(word[section]):
            if section == "B" and i == first:
                entry = list(current)
            need(ss and len({d, *ss}) == len(ss) + 1, "gate operands")
            for r in (d, *ss):
                move(r, f)
            for s in ss:
                rows[d] ^= rows[s]
                ops.append((d, s))
    for r, f in enumerate(word["final"]):
        move(r, f)
    expected = [1 << i for i in range(n)]
    for t in range(v):
        expected[v + t] ^= 1 << t
    need(rows == expected, "forward dirty endpoint")
    need(matrix(reversed(ops), n) == expected, "reverse dirty endpoint")
    full = next(i for i, rank in enumerate(geo.ranks) if rank == 8)
    cleanup = [[full, d, ss] for sec in ("A", "B") for _, d, ss in word[sec] if not v <= d < 2 * v]
    need(word["C"] == list(reversed(cleanup)), "stale literal cleanup")
    return dict(slice=[first, end], entry=entry, paths=paths, profile=dict(sorted(profile.items())),
                copy_ranks=copies, adds=len(ops), columns_each_direction=n)


def required_donors(m, inv, i):
    return {i, *support(m[i], len(m)), *(j for j in range(len(m)) if inv[j] >> i & 1)}


def check_exits(m, inv, entry, exits, geo):
    """Necessary only: passing this test is not a circuit existence certificate."""
    for i, f in enumerate(exits):
        need(all(geo.contains(f, entry[j]) for j in required_donors(m, inv, i)),
             "exit misses a forward or inverse-column dependency")


def analyze(word):
    geo = Geometry(word)
    audit = trace(word, geo)
    first, end = audit["slice"]
    gates = word["B"][first:end]
    regs = sorted({r for _, d, ss in gates for r in (d, *ss)})
    need(regs == [17, 22, 33, 38, 50, 60, 67, 77, 87, 92, 468], "block registers")
    idx = {r: i for i, r in enumerate(regs)}
    ops = [(idx[d], idx[s]) for _, d, ss in gates for s in ss]
    m = matrix(ops, len(regs))
    inv = inverse(m)
    need(all(m[i] != 1 << i or any(j != i and m[j] >> i & 1 for j in range(len(regs)))
             for i in range(len(regs))), "an original wire is inessential")
    need(matrix(reversed(ops), len(regs)) == inv, "literal reverse / Gaussian inverse mismatch")
    entry = [audit["entry"][r] for r in regs]
    footprints = []
    for i, r in enumerate(regs):
        forward = {i, *support(m[i], len(regs))}
        back = [j for j in range(len(regs)) if inv[j] >> i & 1]
        footprints.append(dict(register=r, forward_support=[regs[j] for j in support(m[i], len(regs))],
                               inverse_column=[regs[j] for j in back],
                               forward_rank=geo.join_rank(entry[j] for j in forward),
                               two_sided_rank=geo.join_rank(entry[j] for j in required_donors(m, inv, i))))
    s = idx[SOURCE]
    need(m[s] == 1 << s and footprints[s]["forward_rank"] == 2, "missing source22 exception")
    need(geo.ranks[FRAME] == 4 and all(row["two_sided_rank"] == 4 for row in footprints),
         "not every exit is forced to rank four")
    check_exits(m, inv, entry, [FRAME] * len(regs), geo)
    full_donors = [r for r in footprints[s]["inverse_column"] if audit["entry"][r] == FRAME]
    need(full_donors == [17, 468], "full-frame inverse donors")
    need(all(r in word["frames"][FRAME] for r in [17, 22, 33, 60])
         and len(basis(word["lines"][r] for r in [17, 22, 33, 60])) == 4,
         "rational rank witness")
    climbs = Counter(4 - geo.ranks[f] for f in entry if geo.ranks[f] < 4)
    result = dict(B_slice=[first, end], registers=regs, block_adds=len(ops), matrix_rows=m, inverse_rows=inv,
                  entry_frames=entry, entry_ranks=[geo.ranks[f] for f in entry], footprints=footprints,
                  full_frame_inverse_donors=full_donors, minimal_block_climbs=dict(sorted(climbs.items())),
                  block_frame_roots=word["frames"][FRAME], rank_witness_roots=[17, 22, 33, 60],
                  rank_witness_vectors=[word["lines"][r] for r in [17, 22, 33, 60]],
                  full_word_adds=audit["adds"], full_word_profile=audit["profile"], copy_ranks=audit["copy_ranks"],
                  full_word_rank_mass=sum(r * c for r, c in audit["profile"].items()), columns_each_direction=661,
                  ordered_paths_sha256=hashlib.sha256(json.dumps(audit["paths"], separators=(",", ":")).encode()).hexdigest())
    return result, (geo, m, inv, entry, ops)


def rejected(action, label):
    try:
        action()
    except ValueError:
        return label
    raise ValueError("control not rejected: " + label)


def controls(context):
    geo, m, inv, entry, ops = context
    n, s = len(m), 1
    # Deliberately outside the catalogue: the proof concerns all rational planes.
    plane_roots = [17, 22, 33]
    plane = len(geo.bases)
    geo.bases.append(basis(geo.lines[r] for r in plane_roots))
    geo.ranks.append(len(geo.bases[-1]))
    need(geo.ranks[plane] == 3 and geo.contains(FRAME, plane) and geo.contains(plane, entry[s]),
         "synthetic rank-three plane")
    bad = []
    for f, label in [(entry[s], "rank_two_source_exit"), (plane, "rank_three_source_exit")]:
        exits = [FRAME] * n
        exits[s] = f
        need(m[s] == 1 << s and geo.contains(f, entry[s]), "forward-only control must pass")
        bad.append(rejected(lambda: check_exits(m, inv, entry, exits, geo), label))
    bad.append(rejected(lambda: need(matrix(ops[:-1], n) == m, "wrong map"), "omitted_block_gate"))
    bad.append(rejected(lambda: need(matrix([(b, a) for a, b in ops], n) == m, "wrong direction"),
                        "reversed_gate_directions"))
    changed = list(inv)
    changed[0] ^= 1 << s
    bad.append(rejected(lambda: need(changed == inverse(m), "wrong inverse"), "missing_inverse_donor"))
    bad.append(rejected(lambda: need(geo.contains(entry[s], FRAME), "descent"), "frame_descent"))
    wrong = list(m)
    wrong[s] ^= 1
    bad.append(rejected(lambda: need(wrong[s] == 1 << s, "source dirt"), "source_dirt_leak"))
    bad.append(rejected(lambda: need(len(basis(geo.lines[r] for r in [17, 22, 33, 33])) == 4,
                                    "dependent roots"), "dependent_rank_witness"))
    identity = [1 << i for i in range(n)]
    check_exits(identity, identity, entry, entry, geo)
    line = next(f for f, rank in enumerate(geo.ranks) if rank == 1)
    simple = matrix([(1, 0)], 2)
    check_exits(simple, inverse(simple), [line, line], [line, line], geo)
    return dict(rejected=bad, positive=["identity_keeps_entry_frames", "rank_one_xor_stays_rank_one"],
                rejected_rank_three_span_roots=plane_roots)


def build_receipt():
    pins = json.loads((HERE / "SOURCES.json").read_text())
    inputs = {row["path"]: row for row in pins["files"] if row["usage"] == "input"}
    need(set(inputs) == set(INPUTS), "input inventory")
    results, contexts = [], []
    for path in INPUTS:
        raw = (ROOT / path).read_bytes()
        need(hashlib.sha256(raw).hexdigest() == inputs[path]["sha256"], "source digest: " + path)
        result, context = analyze(json.loads(gzip.decompress(raw)))
        results.append(dict(path=path, sha256=inputs[path]["sha256"], **result))
        contexts.append(context)
    need([r["full_word_adds"] for r in results] == [24305, 11515, 11500], "full ADD counts")
    need(all(r["full_word_rank_mass"] == 5129 and r["copy_ranks"] == [7] * 9 for r in results), "local invoice")
    variable = {"path", "sha256", "B_slice", "block_adds", "full_word_adds"}
    shared = {key: value for key, value in results[0].items() if key not in variable}
    need(all({k: v for k, v in row.items() if k not in variable} == shared for row in results),
         "shared boundary or invoice differs between fixtures")
    fixtures = [{key: row[key] for key in sorted(variable)} for row in results]
    return dict(status="PASS_R439_B509_INVERSE_FOOTPRINT", no_new_kappa=True,
                scope="Fixed B509 map; same wires; common-frame XORs; nested rational frames inside F509; fixed external charges.",
                forced_rank_four_exits=11, minimal_block_climbs=results[0]["minimal_block_climbs"],
                moment_domain="0 < a < 1; sum d_j^(1-a) >= (sum d_j)^(1-a)",
                shared=shared, fixtures=fixtures, controls=controls(contexts[0]))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="regenerate the deterministic certificate")
    args = parser.parse_args()
    receipt = build_receipt()
    # JSON object keys are strings in both the regenerated and committed form.
    receipt = json.loads(json.dumps(receipt))
    certificate = HERE / "CERTIFICATE.json"
    if args.write:
        certificate.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    else:
        need(receipt == json.loads(certificate.read_text()), "certificate differs from exact replay")
    print("PASS_R439_B509_INVERSE_FOOTPRINT fixtures=3 exits=11 source22=2->4 "
          "block_climbs=7H2+2H3 controls=8 no_new_kappa")


if __name__ == "__main__":
    main()
