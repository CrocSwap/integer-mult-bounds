#!/usr/bin/env python3
"""Exact finite research verification; Python 3.10+, standard library only.

Copyright 2026 Sam Sung. Apache-2.0. Substantial OpenAI Codex assistance.
Finite checks supplement the written proofs; they are not formal proofs.
"""
import argparse
from pathlib import Path
import subprocess
import sys
import tempfile
from itertools import combinations, product
import json


def require(condition, message):
    if not condition:
        raise ValueError(message)


def rank(rows):
    pivots = {}
    for row in rows:
        while row:
            pivot = row.bit_length() - 1
            if pivot in pivots:
                row ^= pivots[pivot]
            else:
                pivots[pivot] = row
                break
    return len(pivots)


def rref_spaces(dimension, size):
    for pivots in combinations(range(dimension), size):
        free = [(i, j) for i, pivot in enumerate(pivots)
                for j in range(pivot + 1, dimension) if j not in pivots]
        for values in product((0, 1), repeat=len(free)):
            rows = [1 << pivot for pivot in pivots]
            for value, (i, j) in zip(values, free):
                rows[i] |= value << j
            yield tuple(rows)


def evaluate(coefficient):
    return sum(1 << point for point in range(16)
               if (coefficient & (1 | point << 1)).bit_count() % 2)


def union(rows):
    result = 0
    for row in rows:
        result |= row
    return result


def restrict(row, targets):
    return sum(((row >> point) & 1) << i for i, point in enumerate(targets))


def unit_decoders(rows, targets):
    rows = list(rows)
    for i, point in enumerate(targets):
        pivot = next(j for j in range(i, len(rows)) if rows[j] >> point & 1)
        rows[i], rows[pivot] = rows[pivot], rows[i]
        for j in range(len(rows)):
            if j != i and rows[j] >> point & 1:
                rows[j] ^= rows[i]
    require(all(restrict(row, targets) == 1 << i for i, row in enumerate(rows)),
            "target elimination failed")
    return rows


def verify():
    counts = {3: (155, 120, 560), 4: (31, 16, 1680), 5: (1, 1, 2688)}
    minimum = {3: 14, 4: 15, 5: 16}
    all_rows = [evaluate(1 << i) for i in range(5)]
    results = []
    for size in (3, 4, 5):
        spaces = [tuple(evaluate(c) for c in coefficients)
                  for coefficients in rref_spaces(5, size)]
        supports = [union(rows) for rows in spaces]
        require(min(mask.bit_count() for mask in supports) == minimum[size],
                "wrong generalized weight")
        optimal = [(rows, mask) for rows, mask in zip(spaces, supports)
                   if mask.bit_count() == minimum[size]]
        require((len(spaces), len(optimal)) == counts[size][:2], "subspace count")
        feasible = 0
        restored = 0
        rejected = 0
        total = 0
        for targets in combinations(range(16), size):
            total += 1
            witness = next(((rows, mask) for rows, mask in optimal
                            if rank(restrict(row, targets) for row in rows) == size), None)
            affine_independent = rank(1 | point << 1 for point in targets) == size
            require(bool(witness) == affine_independent, "affine criterion disagreement")
            if witness is None:
                rejected += 1
                continue
            feasible += 1
            rows, mask = witness
            target_mask = sum(1 << point for point in targets)
            require(mask & target_mask == target_mask, "target outside support")
            deleted = mask ^ target_mask
            require(deleted.bit_count() == 11, "incorrect deletion count")
            surviving = ((1 << 16) - 1) ^ deleted
            decoders = unit_decoders(rows, targets)
            require(all(row & surviving == 1 << point
                        for row, point in zip(decoders, targets)), "retained unit identity")
            for point in range(16):
                if not (deleted >> point) & 1:
                    continue
                restored += 1
                new_surviving = surviving | 1 << point
                restrictions = [row & new_surviving for row in all_rows]
                old_rank = rank(restrictions)
                require(any(rank(restrictions + [1 << target]) > old_rank for target in targets),
                        "one restored deletion unexpectedly allows full-cube recovery")
        require(feasible == counts[size][2], "feasible target count")
        results.append(dict(rank=size, all_subspaces=len(spaces), optimal_subspaces=len(optimal),
                            support_minimum=minimum[size], target_sets=total,
                            feasible=feasible, rejected=rejected,
                            single_restoration_controls=restored))
    # Four vertices of an affine plane defeat the tempting distinct-target rule.
    require(rank(1 | point << 1 for point in (0, 1, 2, 3)) == 3,
            "affine-plane negative control")
    return dict(status="PASS", scope="All subspaces of RM(1,4) of ranks3,4,5 and all target subsets. "
                "This is finite cube verification, not global optimizer localization.", cases=results)



RECEIPT = 'OPTIMIZER-RESULTS.json'


def self_test(result):
    with tempfile.TemporaryDirectory() as directory:
        directory = Path(directory)
        script = directory / Path(__file__).name
        script.write_bytes(Path(__file__).read_bytes())
        receipt = directory / RECEIPT
        receipt.write_text(json.dumps(result))
        command = [sys.executable, "-I", "-O", "-B", str(script)]
        run = subprocess.run(command, capture_output=True, text=True)
        require(run.returncode == 0, f"isolated optimized relocated replay failed: {run.stderr}")
        receipt.write_text(json.dumps(dict(result, status="CORRUPTED")))
        protected = directory / "protected.json"
        protected.write_text("preserve this output\n")
        run = subprocess.run(command + ["--check", str(receipt), "--write", str(protected)],
                             capture_output=True, text=True)
        require(run.returncode != 0, "corrupt receipt accepted")
        require(protected.read_text() == "preserve this output\n", "failed check overwrote output")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", type=Path)
    parser.add_argument("--check", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    result = json.loads(json.dumps(verify()))
    if args.check or not args.write:
        receipt = args.check or Path(__file__).resolve().with_name(RECEIPT)
        require(json.loads(receipt.read_text()) == result, f"receipt mismatch: {receipt}")
    if args.self_test:
        self_test(result)
    if args.write:
        args.write.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print("PASS", Path(__file__).name)


if __name__ == "__main__":
    main()
