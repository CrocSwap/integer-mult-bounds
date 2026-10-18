#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Prepared for haoyan with substantial OpenAI Codex assistance.
# The source circuit is DreamingOfClouds' R480 adaptation of eumemic's
# carrier-skeleton construction; see ../e8-r480-dead-totals/NOTICE.md.
"""Reproduce the first bounded seed-1 quad factorization attempt (Python 3.9+).

The source is pinned by SHA256. Start at quad 1 in the source's 60-quad
phase-A stage. Subtract componentwise dominated rows of its exact integer
transfer matrix, while accumulating the corresponding unsigned literal
reverse transfer. Reject any subtraction whose reverse transfer would
exceed the source entrywise. Choose eligible rows with seed-1 weighted
sampling, using the cube of the source-row sum as the weight.

The completed search consists of one attempt on quad 1, stopped at the
first strict improvement. It establishes a witness, not optimality. This
script repeats only that attempt; it never searches additional quads.
It emits deterministic JSON to stdout, or to --output PATH.
"""

import argparse
import gzip
import hashlib
import json
import random
import sys
from pathlib import Path

SOURCE = "research/e8-r480-dead-totals/data/bitE8mut-r480.json.gz"
SOURCE_SHA256 = "92e399e9a486b55229b5624632ac54f800dd9e022f2aee97f1e5f264bbc0ef5c"
SEED = 1


def require(condition, message):
    """Checks must also run when Python is invoked with -O."""
    if not condition:
        raise ValueError(message)


def identity(n):
    return [[int(i == j) for j in range(n)] for i in range(n)]


def transfer(ops, n):
    rows = identity(n)
    for d, s in ops:
        require(0 <= d < n and 0 <= s < n and d != s,
                "invalid local operation")
        rows[d] = [x + y for x, y in zip(rows[d], rows[s])]
    return rows


def dominated(left, right):
    return all(x <= y for a, b in zip(left, right) for x, y in zip(a, b))


def extract_quad(word):
    runs = []
    for index, gate in enumerate(word["A"]):
        require(len(gate) == 3, "malformed phase-A gate")
        frame = gate[0]
        if runs and runs[-1][2] == frame:
            runs[-1][1] = index + 1
        else:
            runs.append([index, index + 1, frame])
    twelve_line_runs = [run for run in runs if len(word["frames"][run[2]]) == 12]
    require(len(twelve_line_runs) == 70, "expected 60 quads and 10 Q-nodes")
    quads = twelve_line_runs[:60]
    require(all(quads[i][1] == quads[i + 1][0] for i in range(59)),
            "quad stage is not contiguous")
    start, end, frame = quads[SEED % 60]
    require((start, end, frame) == (621, 639, 303), "seed-start quad changed")
    gates = word["A"][start:end]
    require(all(len(sources) == 1 for _, _, sources in gates),
            "quad does not consist of single-source XORs")
    wires = sorted({wire for _, dst, sources in gates for wire in [dst] + sources})
    require(wires == [487, 504, 550, 574, 598, 622], "quad wire set changed")
    indices = {wire: i for i, wire in enumerate(wires)}
    ops = [(indices[dst], indices[source])
           for _, dst, sources in gates for source in sources]
    return start, end, frame, wires, ops


def discover(source_path):
    compressed = source_path.read_bytes()
    require(hashlib.sha256(compressed).hexdigest() == SOURCE_SHA256,
            "source SHA256 mismatch")
    word = json.loads(gzip.decompress(compressed))
    require(word["format"] == "bitE8/1+mut" and word["R"] == 480,
            "unexpected source format or register count")
    start, end, frame, wires, old_ops = extract_quad(word)
    n = len(wires)
    forward = transfer(old_ops, n)
    old_reverse = transfer(list(reversed(old_ops)), n)
    remaining = [row[:] for row in forward]
    reverse = identity(n)
    reduction = []
    rng = random.Random(SEED)

    # One attempt, at most old_count - 1 operations: the candidate must
    # strictly reduce the number of single-source XORs.
    for _ in range(len(old_ops) - 1):
        eligible = []
        for dst in range(n):
            if sum(remaining[dst]) == 1:
                continue
            for src in range(n):
                if dst == src or remaining[dst][dst] <= remaining[src][dst]:
                    continue
                if not all(x >= y for x, y in zip(remaining[dst], remaining[src])):
                    continue
                if not all(x + y <= bound for x, y, bound in
                           zip(reverse[dst], reverse[src], old_reverse[dst])):
                    continue
                eligible.append((dst, src, sum(remaining[src])))
        require(bool(eligible), "the recorded first attempt has no admissible continuation")
        dst, src, _ = rng.choices(eligible, weights=[weight ** 3 for _, _, weight in eligible])[0]
        remaining[dst] = [x - y for x, y in zip(remaining[dst], remaining[src])]
        reverse[dst] = [x + y for x, y in zip(reverse[dst], reverse[src])]
        reduction.append((dst, src))
        if remaining == identity(n):
            break

    require(remaining == identity(n), "first attempt did not finish within its gate budget")
    new_ops = list(reversed(reduction))
    new_reverse = transfer(reduction, n)
    require(len(new_ops) < len(old_ops), "candidate is not a strict gate reduction")
    require(transfer(new_ops, n) == forward, "candidate changes full integer forward transfer")
    require(new_reverse == reverse, "reverse accumulator mismatch")
    require(dominated(new_reverse, old_reverse), "candidate increases reverse transfer")
    require({r for pair in new_ops for r in pair} == set(range(n)),
            "candidate fails to use every original wire at the common frame")

    return {
        "source": SOURCE,
        "seed": SEED,
        "quad_index": SEED % 60,
        "A_start": start,
        "A_end": end,
        "frame_id": frame,
        "wires": wires,
        "old_ops": old_ops,
        "new_ops": new_ops,
        "forward_matrix": forward,
        "old_reverse_matrix": old_reverse,
        "new_reverse_matrix": new_reverse,
        "attempt": 0,
        "coverage_before": [],
        "source_sha256": SOURCE_SHA256,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path,
                        default=Path(__file__).resolve().parents[2] / SOURCE)
    parser.add_argument("--seed", type=int, default=SEED,
                        help="recorded assignment seed (must be 1)")
    parser.add_argument("--output", type=Path, help="write deterministic recipe here instead of stdout")
    args = parser.parse_args()
    require(args.seed == SEED, "this reproduction is restricted to assignment seed 1")
    recipe = discover(args.source)
    encoded = json.dumps(recipe, indent=2) + "\n"
    if args.output is None:
        sys.stdout.write(encoded)
    else:
        args.output.write_text(encoded, encoding="utf-8")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, KeyError, TypeError) as exc:
        print("discovery failed: {}".format(exc), file=sys.stderr)
        sys.exit(1)
