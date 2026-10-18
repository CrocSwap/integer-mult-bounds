#!/usr/bin/env python3
"""Exact bitset census; independent checking is in check.py.

Hanson Sun, with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
import gzip
import hashlib
import json
import math
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WORD = "research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz"


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def nullspace(rows):
    a = [[Fraction(x) for x in row] for row in rows]
    pivots = []
    for col in range(8):
        rank = len(pivots)
        p = next((i for i in range(rank, len(a)) if a[i][col]), None)
        if p is None:
            continue
        a[rank], a[p] = a[p], a[rank]
        scale = a[rank][col]
        a[rank] = [x / scale for x in a[rank]]
        for i in range(len(a)):
            if i != rank:
                scale = a[i][col]
                a[i] = [x - scale * y for x, y in zip(a[i], a[rank])]
        pivots.append(col)
    normals = []
    for col in range(8):
        if col in pivots:
            continue
        x = [Fraction(0)] * 8
        x[col] = 1
        for i, pivot in enumerate(pivots):
            x[pivot] = -a[i][col]
        scale = math.lcm(*(v.denominator for v in x))
        normals.append([int(v * scale) for v in x])
    return normals


def events(word):
    out = []
    current = list(word["start"])
    for section in ("A", "B"):
        for index, (frame, dest, sources) in enumerate(word[section]):
            out.append((section, index, frame, dest, sources))
            for r in [dest, *sources]:
                current[r] = frame
        if section == "A":
            for index, helper in enumerate(word["ret"]):
                out.append(("COPY", index, current[helper], helper, []))
    return out


def clean_reads(word):
    v = word["v"]
    rows = [1 << r if r < v else 0 for r in range(2 * v + word["R"])]
    reads = {q: [] for q in range(2 * v, len(rows)) if q not in word["ret"]}
    for section, index, frame, dest, sources in events(word):
        if section == "COPY":
            for target, copies in enumerate(word["scatter"]):
                if index in copies:
                    rows[v + target] ^= rows[dest]
            continue
        for q in sources:
            if q in reads:
                reads[q].append({
                    "section": section, "gate": index, "frame": frame,
                    "clean_row": hex(rows[q]),
                    "sources": [s for s in range(v) if s != dest and rows[s] == rows[q]],
                })
        for source in sources:
            rows[dest] ^= rows[source]
    return reads


def frame_barrier(word, helper, reads):
    """Drop EVERY changed gate when finding fixed anchors: an optimistic relaxation."""
    ev = events(word)
    before, after = {}, {}
    current = [(f, ["start", r]) for r, f in enumerate(word["start"])]
    for k, (section, index, frame, dest, sources) in enumerate(ev):
        if dest == helper:
            continue
        if helper in sources:
            before[k] = list(current)
            continue
        for r in [dest, *sources]:
            current[r] = (frame, [section, index])
    current = [(f, ["final", r]) for r, f in enumerate(word["final"])]
    for k in reversed(range(len(ev))):
        section, index, frame, dest, sources = ev[k]
        if dest == helper:
            continue
        if helper in sources:
            after[k] = list(current)
            continue
        for r in [dest, *sources]:
            current[r] = (frame, [section, index])
    choices = {(r["section"], r["gate"]): r["sources"] for r in reads}
    # On this pinned object every surviving read has exactly one possible donor.
    if not all(len(x) == 1 for x in choices.values()):
        raise ValueError("non-unique source assignments require a different search")
    for k in before:
        section, index, _, dest, sources = ev[k]
        donor = choices[section, index][0]
        touched = [dest, *sorted(set(sources) ^ {helper, donor})]
        for lower_reg in touched:
            low, previous = before[k][lower_reg]
            for upper_reg in touched:
                high, following = after[k][upper_reg]
                outside = sorted(set(word["frames"][low]) - set(word["frames"][high]))
                if not outside:
                    continue
                line = outside[0]
                normals = nullspace([word["lines"][i] for i in word["frames"][high]])
                normal = next(n for n in normals if sum(a*b for a, b in zip(n, word["lines"][line])))
                return {
                    "section": section, "gate": index, "source": donor,
                    "lower_register": lower_reg, "lower_frame": low, "previous": previous,
                    "upper_register": upper_reg, "upper_frame": high, "following": following,
                    "separating_line": line, "normal": normal,
                }
    return None


def census(word):
    reads = clean_reads(word)
    helpers = list(reads)
    helpers = helpers[11:] + helpers[:11]
    results = []
    counts = {"retained": len(word["ret"]), "clean_row_obstruction": 0,
              "frame_obstruction": 0, "surviving": 0}
    for q in helpers:
        rr = reads[q]
        if not rr:
            raise ValueError("unread helper needs explicit treatment")
        bad = next((r for r in rr if not r["sources"]), None)
        result = {"helper": q, "reads": rr}
        if bad:
            result["status"] = "clean_row_obstruction"
            result["obstruction"] = {"section": bad["section"], "gate": bad["gate"]}
        else:
            barrier = frame_barrier(word, q, rr)
            result["status"] = "frame_obstruction" if barrier else "surviving"
            result["obstruction"] = barrier
        counts[result["status"]] += 1
        results.append(result)
    return {
        "schema": "bit-source-substitution-census/1",
        "assignment_seed": 11, "word_sha256": hashlib.sha256(canonical(word)).hexdigest(),
        "retained_helpers": word["ret"], "helper_domain": [2*word["v"], 2*word["v"]+word["R"]],
        "counts": counts, "read_occurrences": sum(len(x) for x in reads.values()),
        "source_comparisons": word["v"] * sum(len(x) for x in reads.values()),
        "helpers": results,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, help="New output file; defaults to checking CERTIFICATE.json")
    args = parser.parse_args()
    word = json.loads(gzip.decompress((ROOT / WORD).read_bytes()))
    result = census(word)
    if args.output:
        with args.output.open("x") as out:
            json.dump(result, out, indent=2)
            out.write("\n")
    elif result != json.loads((HERE / "CERTIFICATE.json").read_text()):
        raise SystemExit("REJECT: regenerated certificate differs")
    print("PASS_SOURCE_SUBSTITUTION_CENSUS", json.dumps(result["counts"], sort_keys=True))


if __name__ == "__main__":
    main()
