#!/usr/bin/env python3
"""Bounded positive-integer factor search for selected R420 phase-B block 8.

Prepared by Jerry Lin with substantial OpenAI Codex assistance; Apache-2.0.
The search starts from the pinned integer forward matrix. Each step removes
one elementary positive row or column factor without making any entry negative
or reducing a diagonal entry below one. A completed factorization must end at
the ordered identity. Its literal reverse positive matrix must be entrywise
at most the original reverse matrix. This is a finite heuristic search, not a
claim of minimum length among all circuits or within the reduction class.

Run from any directory with Python 3; this writes CANDIDATE.json beside this file.
Only the Python standard library is required.
"""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import random

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "research/e8-bit-r420/data/bitE8mut-r420.json.gz"
SOURCE_SHA256 = "9721a3819efd68307f66f00d84a952eb28eb7c3ad2ce79653ce295c98a764784"
BASE_COMMIT = "66849e1475c930fd7732b1a0067ffee7e1e95f60"
BLOCK = 8
FRAME = 550
N = 12
IDENTITY = [[int(i == j) for j in range(N)] for i in range(N)]
STAGES = [(801018, 10000)]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def transfer(operations):
    matrix = [row[:] for row in IDENTITY]
    for dst, src in operations:
        matrix[dst] = [x + y for x, y in zip(matrix[dst], matrix[src])]
    return matrix


def dominated(left, right):
    return all(x <= y for a, b in zip(left, right) for x, y in zip(a, b))


def extract():
    raw = SOURCE.read_bytes()
    require(hashlib.sha256(raw).hexdigest() == SOURCE_SHA256, "source hash mismatch")
    word = json.loads(gzip.decompress(raw))
    indexed = [(i, gate) for i, gate in enumerate(word["B"]) if gate[0] == FRAME]
    first, last = indexed[0][0], indexed[-1][0] + 1
    require([i for i, _ in indexed] == list(range(first, last)), "block is not contiguous")
    registers = sorted({r for _, (_, dst, srcs) in indexed for r in [dst, *srcs]})
    require(len(registers) == N, "wrong register count")
    require(all(len(gate[2]) == 1 for _, gate in indexed), "source gate is not unary")
    operations = [(registers.index(dst), registers.index(srcs[0]))
                  for _, (_, dst, srcs) in indexed]
    require([first, last] == [512, 559], "wrong phase-B slice")
    require(len(operations) == 47, "wrong source operation count")
    return registers, [first, last], operations


def choices(matrix):
    moves = []
    for i in range(N):
        for j in range(N):
            if i == j:
                continue
            # Remove a left factor: row i := row i - row j.
            if matrix[i][i] > matrix[j][i] and all(
                    x >= y for x, y in zip(matrix[i], matrix[j])):
                moves.append((sum(matrix[j]), "r", i, j))
            # Remove a right factor: column j := column j - column i.
            if matrix[j][j] > matrix[j][i] and all(
                    matrix[k][j] >= matrix[k][i] for k in range(N)):
                moves.append((sum(matrix[k][i] for k in range(N)), "c", i, j))
    return moves


def select(moves, mode, rng):
    if mode == 0:
        return rng.choice(moves)
    if mode == 1:
        return max(moves, key=lambda move: move[0] + rng.random() * 3)
    if mode == 2:
        return max(moves, key=lambda move: move[0] * rng.random())
    if mode == 3:
        return rng.choices(moves, weights=[move[0] ** 2 for move in moves])[0]
    if mode == 4:
        return min(moves, key=lambda move: move[0] + rng.random() * 3)
    return max(moves, key=lambda move: move[0] ** 0.5 * rng.random())


def search(original):
    target = transfer(original)
    reverse_limit = transfer(original[::-1])
    best = original
    records = []
    for seed, trials in STAGES:
        rng = random.Random(seed)
        record = {"seed": seed, "trials": trials, "completed": 0,
                  "successes": 0, "improvements": [], "reduction_steps": 0,
                  "dead_ends": 0, "length_cutoffs": 0}
        for trial in range(trials):
            matrix = [row[:] for row in target]
            rows, columns = [], []
            while matrix != IDENTITY:
                moves = choices(matrix)
                if not moves:
                    record["dead_ends"] += 1
                    break
                _, kind, i, j = select(moves, trial % 6, rng)
                if kind == "r":
                    matrix[i] = [x - y for x, y in zip(matrix[i], matrix[j])]
                    rows.append((i, j))
                else:
                    for k in range(N):
                        matrix[k][j] -= matrix[k][i]
                    columns.append((i, j))
                record["reduction_steps"] += 1
                if len(rows) + len(columns) >= len(best):
                    if matrix != IDENTITY:
                        record["length_cutoffs"] += 1
                    break
            if matrix != IDENTITY:
                continue
            record["completed"] += 1
            candidate = columns + rows[::-1]
            require(transfer(candidate) == target, "search factorization mismatch")
            if dominated(transfer(candidate[::-1]), reverse_limit):
                record["successes"] += 1
                if len(candidate) < len(best):
                    best = candidate
                    record["improvements"].append(
                        {"trial_one_based": trial + 1, "operations": len(best)})
        records.append(record)
        print(f"seed {seed}: {trials} trials; best {len(best)} operations", flush=True)
    return best, records


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path(__file__).with_name("CANDIDATE.json"))
    args = parser.parse_args()
    registers, b_slice, original = extract()
    candidate, records = search(original)
    forward = transfer(original)
    original_reverse = transfer(original[::-1])
    candidate_reverse = transfer(candidate[::-1])
    require(transfer(candidate) == forward, "candidate forward matrix mismatch")
    require(dominated(candidate_reverse, original_reverse), "candidate reverse matrix exceeds source")
    result = {
        "format": "r420-positive-block-candidate-v1",
        "base_commit": BASE_COMMIT,
        "source": str(SOURCE.relative_to(ROOT)),
        "source_sha256": SOURCE_SHA256,
        "block_index": BLOCK,
        "frame": FRAME,
        "b_slice": b_slice,
        "slice_convention": "zero-based, start inclusive, end exclusive",
        "registers": registers,
        "operations": candidate,
        "seed": 801018,
        "assignment_seed": 18,
        "search_seed": 801018,
        "seed_role": "assignment seed 18 selects block 8; search RNG uses 801018",
        "search_seed_choice": "Manually fixed before the first search trial; arbitrary and distinct from assignment seed.",
        "original_operations": original,
        "original_count": len(original),
        "candidate_count": len(candidate),
        "forward_plus_cleanup_saving": 2 * (len(original) - len(candidate)),
        "integer_forward_matrix": forward,
        "original_positive_reverse_matrix": original_reverse,
        "candidate_positive_reverse_matrix": candidate_reverse,
        "search": {
            "method": "seeded two-sided nonnegative elementary-factor reduction",
            "trials": sum(r["trials"] for r in records),
            "completed": sum(r["completed"] for r in records),
            "successes": sum(r["successes"] for r in records),
            "stages": records,
            "move_order": "i then j; row before column; indices ascending",
            "selection_cycle": [
                "uniform", "maximum gain plus uniform [0,3)",
                "maximum gain times uniform [0,1)", "gain-squared weights",
                "minimum gain plus uniform [0,3)",
                "maximum square-root gain times uniform [0,1)"],
            "cutoff": "stop a trial at current best length",
            "complete_definition": "residual equals the ordered identity",
            "success_definition": "complete and positive reverse matrix dominated",
            "optimality_claim": False,
            "excluded_exploration": {
                "seed": 18, "requested_trials": 50000,
                "completed_trial_count": None,
                "status": "interrupted before completion; partial count was not retained",
                "improvements_observed": 0,
                "used_to_select_candidate": False,
            },
        },
        "limitations": [
            "Only the pinned phase-B block 8 is searched.",
            "No claim of minimum length or exhaustive coverage is made.",
            "Search includes only nonnegative row and column subtraction paths with diagonal entries at least one.",
            "Integer transfer checks are finite circuit checks, not a formal verification of the multiplication theorem.",
        ],
    }
    destination = args.output
    destination.write_text(json.dumps(result, indent=2) + "\n")
    print(f"wrote {destination}; saves {result['forward_plus_cleanup_saving']} primitive operations")


if __name__ == "__main__":
    main()
