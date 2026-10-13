#!/usr/bin/env python3
"""Whole-word admission of the unchanged PR952 Gaussian nominees. Apache-2.0.

Prepared for Gareth Davidson (@bitplane), with OpenAI Codex assistance.
"""
import argparse
import gzip
import hashlib
import itertools
import json
from pathlib import Path
import random
import runpy

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PARENT = "research/r439-six-wire-boolean"


def canonical(x):
    return json.dumps(x, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def positive(word, reverse=False):
    values = [1] * (2 * word["v"] + word["R"])
    peak = 1
    sections = ("C", "B", "scatter", "A", "D") if reverse else ("D", "A", "scatter", "B", "C")
    for section in sections:
        if section == "scatter":
            centers = range(len(word["ret"]) - 1, -1, -1) if reverse else range(len(word["ret"]))
            for j in centers:
                for i, sources in enumerate(word["scatter"]):
                    if j in sources:
                        values[word["v"] + i] += values[word["ret"][j]]
                        peak = max(peak, values[word["v"] + i])
        else:
            for _, d, sources in (reversed(word[section]) if reverse else word[section]):
                values[d] += sum(values[s] for s in sources)
                peak = max(peak, values[d])
    return peak


def bill(word):
    f, b = positive(word), positive(word, True)
    local = 64 * f ** 3 * b ** 2
    nine = (1 << 18) * f ** 5 * b ** 4
    return {"ADDs": sum(len(ss) for section in "DABC" for _, _, ss in word[section])
                    + sum(map(len, word["scatter"])), "F": f, "B": b,
            "local_bits": local.bit_length(), "nine_bits": nine.bit_length(),
            "local_upper": str(local), "nine_upper": str(nine),
            "admitted": local < 1 << 104 and nine < 1 << 192}


def assemble(parent, blocks, replacements):
    # Only A and its required literal cleanup change.
    result = dict(parent)
    a, cursor = [], 0
    for frame, start, end, wires, old in blocks:
        a.extend(parent["A"][cursor:start])
        if frame in replacements:
            a.extend([[frame, wires[d], [wires[s]]] for d, s in replacements[frame]])
        else:
            a.extend(parent["A"][start:end])
        cursor = end
    a.extend(parent["A"][cursor:])
    result["A"] = a
    v = parent["v"]
    result["C"] = [[1, d, list(ss)] for _, d, ss in
                   [g for section in ("A", "B") for g in result[section] if not v <= g[1] < 2*v][::-1]]
    return result


def run(root, output):
    root, output = Path(root).resolve(), Path(output).resolve()
    output.mkdir(parents=True, exist_ok=False)
    source = runpy.run_path(str(root / PARENT / "build.py"))
    parent = json.loads(gzip.decompress((root / PARENT / "candidate.json.gz").read_bytes()))
    blocks = source["blocks"](parent)
    strict_word, strict = source["build"](parent)
    if strict["summary"]["selected"] != 0 or canonical(strict_word) != canonical(parent):
        raise ValueError("strict same-domain repeat is not saturated")
    priorities = [[1, 2, 3, 4, 5, 0], [0, 5, 4, 3, 2, 1]]
    orders = list(itertools.permutations(range(6)))
    nominees, summaries = {}, []
    for frame, start, end, wires, old in blocks:
        target = source["binary"](old)
        programs = {source["nominate"](target, order, mode, priority)
                    for mode in ("row", "mixed") for priority in priorities for order in orders}
        shorter = sorted((p for p in programs if len(p) < len(old) and {r for op in p for r in op} == set(range(6))),
                         key=lambda p: (len(p), p))
        nominees[frame] = shorter[:32]
        summaries.append({"frame": frame, "start": start, "end": end, "wires": wires, "old": old,
                          "trials": 2880, "distinct_programs": len(programs), "shorter_programs": len(shorter),
                          "retained_nominees": len(nominees[frame])})
    block_order = [b[0] for b in blocks]
    random.Random(3).shuffle(block_order)
    replacements, attempts, selected = {}, [], []
    for frame in block_order:
        for rank, program in enumerate(nominees[frame]):
            trial_replacements = dict(replacements)
            trial_replacements[frame] = program
            candidate = assemble(parent, blocks, trial_replacements)
            price = bill(candidate)
            attempts.append({"frame": frame, "rank": rank, "program": program, "bill": price})
            if price["admitted"]:
                replacements[frame] = program
                selected.append({"frame": frame, "rank": rank, "program": program, "bill": price})
                print("admit", frame, "length", len(program), price, flush=True)
                break
    candidate = assemble(parent, blocks, replacements)
    certificate = {"format": "r439-global-prefix/1", "seed": 3, "nomination_priorities": priorities,
                   "parent_sha256": hashlib.sha256(canonical(parent)).hexdigest(),
                   "candidate_sha256": hashlib.sha256(canonical(candidate)).hexdigest(),
                   "nomination_seed_from_pr952": 19, "strict_repeat": strict["summary"],
                   "strict_certificate": strict, "blocks": summaries, "block_order": block_order,
                   "max_nominees_per_block": 32, "attempts": attempts, "selected": selected,
                   "baseline_bill": bill(parent), "candidate_bill": bill(candidate)}
    for name, obj in (("CERTIFICATE.json", certificate),):
        with (output / name).open("x") as stream:
            json.dump(obj, stream, indent=2, sort_keys=True, allow_nan=False)
            stream.write("\n")
    (output / "candidate.json.gz").write_bytes(gzip.compress(canonical(candidate), mtime=0))
    print("DONE", len(selected), "blocks", len(attempts), "priced words", certificate["candidate_bill"], flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, default=ROOT)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    run(args.source_root, args.out)
