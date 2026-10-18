#!/usr/bin/env python3
"""Reproduce one bounded fixed-output F2 resynthesis, never an optimum claim.

Prepared for ToikY with substantial OpenAI Codex assistance. Apache-2.0.
The source word is DreamingOfClouds's PR503/510 R480 adaptation of eumemic's
PR493 carrier skeleton. Related bounded F2 synthesis precedents: PR904,
PR936 and PR952; PR823 resynthesizes a different, six-wire R480 quad.
This standalone Gauss-Jordan search is independently implemented here.
"""

import argparse
from collections import Counter
import gzip
import hashlib
import json
from pathlib import Path
import random


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = "research/e8-r480-dead-totals/data/bitE8mut-r480.json.gz"
SOURCE_SHA256 = "92e399e9a486b55229b5624632ac54f800dd9e022f2aee97f1e5f264bbc0ef5c"
BASE = "407d52ff15b2217b6e22bce44728b4c3907b6515"
LO, HI, FRAME, SEED, TRIALS = 2250, 2302, 484, 2, 1000
REGISTERS = [17, 25, 32, 43, 52, 58, 64, 77, 82, 90, 99, 104]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def transfer(n, operations):
    rows = [1 << i for i in range(n)]
    for dst, src in operations:
        require(0 <= dst < n and 0 <= src < n and dst != src, "illegal XOR")
        rows[dst] ^= rows[src]
    return rows


def positive(n, operations):
    """Actual nonnegative coefficient matrix for cancellation-free replay.

    This is a local comparison in independent block-input columns; native
    prefix admission uses the complete chronological word instead.
    """
    rows = [[int(i == j) for j in range(n)] for i in range(n)]
    maximum = 1
    for dst, src in operations:
        rows[dst] = [a + b for a, b in zip(rows[dst], rows[src])]
        maximum = max(maximum, sum(rows[dst]))
    return {"endpoint_matrix": rows, "endpoint_row_sums": list(map(sum, rows)),
            "maximum_prefix_row_l1": maximum}


def synthesize(rows):
    """Exactly 1000 trajectories, including a random pivot only if necessary."""
    n = len(rows)
    rng = random.Random(SEED)
    best = None
    first_best = None
    histogram = Counter()
    improvements = []
    best_words = set()
    for trial in range(TRIALS):
        reduced = list(rows)
        operations = []
        columns = list(range(n))
        rng.shuffle(columns)
        for position, col in enumerate(columns):
            choices = [p for p in columns[position:] if (reduced[p] >> col) & 1]
            pivot = col if (reduced[col] >> col) & 1 else rng.choice(choices)
            if pivot != col:
                for dst, src in ((col, pivot), (pivot, col), (col, pivot)):
                    reduced[dst] ^= reduced[src]
                    operations.append((dst, src))
            for dst in columns:
                if dst != col and (reduced[dst] >> col) & 1:
                    reduced[dst] ^= reduced[col]
                    operations.append((dst, col))
        require(reduced == [1 << i for i in range(n)], "elimination failed")
        candidate = list(reversed(operations))
        require(transfer(n, candidate) == rows, "fixed-output replay failed")
        cost = len(candidate)
        histogram[cost] += 1
        if best is None or cost < len(best):
            best, first_best = candidate, trial
            best_words = {tuple(candidate)}
            improvements.append({"trial_zero_based": trial, "xor_count": cost})
        elif cost == len(best):
            best_words.add(tuple(candidate))
    return best, {
        "seed": SEED, "rng": "Python random.Random (MT19937)",
        "trials_completed": TRIALS,
        "stopping_rule": "Exactly 1000 trajectories; no early stop or restart.",
        "domain": "One 12x12 fixed-output F2 map; shuffled column order; keep diagonal pivot when nonzero, otherwise uniformly choose an unprocessed nonzero pivot row; three XORs per row swap; eliminate every other row in shuffled order; reverse elimination to synthesize.",
        "tie_rule": "Keep the first shortest encountered word.",
        "first_best_trial_zero_based": first_best,
        "best_length_occurrences": histogram[len(best)],
        "distinct_best_words_encountered": len(best_words),
        "length_histogram": {str(k): histogram[k] for k in sorted(histogram)},
        "strict_improvements": improvements,
        "optimality_claim": False,
    }


def receipt():
    raw = (ROOT / SOURCE).read_bytes()
    require(hashlib.sha256(raw).hexdigest() == SOURCE_SHA256, "source hash mismatch")
    word = json.loads(gzip.decompress(raw))
    block = word["A"][LO:HI]
    actual_registers = sorted({r for _, dst, sources in block for r in [dst] + sources})
    require(actual_registers == REGISTERS, "source registers changed")
    require(all(f == FRAME and len(s) == 1 for f, _, s in block), "source block changed")
    index = {r: i for i, r in enumerate(REGISTERS)}
    old = [(index[d], index[s[0]]) for _, d, s in block]
    rows = transfer(len(REGISTERS), old)
    best, search = synthesize(rows)
    require(len(best) == 43, "frozen search result changed")
    identity = [1 << i for i in range(len(REGISTERS))]
    require(transfer(len(REGISTERS), best + list(reversed(old))) == identity,
            "old/new composition is not identity")
    return {
        "schema": "r480-qnode-seed02/1", "base_commit": BASE,
        "source": {"path": SOURCE, "sha256": SOURCE_SHA256},
        "object": {"phase": "A", "slice_start_inclusive": LO,
                   "slice_end_exclusive": HI, "frame": FRAME,
                   "registers_in_matrix_order": REGISTERS},
        "search": search,
        "fixed_output_f2_rows": rows,
        "old_xor_count": len(old), "new_xor_count": len(best),
        "complete_A_plus_literal_C_xor_saving": 2 * (len(old) - len(best)),
        "replacement_A_events": [[FRAME, REGISTERS[d], [REGISTERS[s]]] for d, s in best],
        "positive_local": {
            "scope": "Independent block-input columns only; not complete native prefix admission.",
            "old_forward": positive(len(REGISTERS), old),
            "new_forward": positive(len(REGISTERS), best),
            "old_inverse": positive(len(REGISTERS), list(reversed(old))),
            "new_inverse": positive(len(REGISTERS), list(reversed(best))),
        },
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", type=Path, help="write a new receipt (refuse overwrite)")
    args = parser.parse_args()
    result = receipt()
    encoded = json.dumps(result, sort_keys=True, indent=2) + "\n"
    if args.write is not None:
        with args.write.open("x") as output:
            output.write(encoded)
    else:
        require((HERE / "RECIPE.json").read_text() == encoded, "recipe differs from exact reproduction")
    print("PASS_R480_QNODE_SEED02_SEARCH trials=1000 old=52 new=43 A_plus_C_saved=18 no_optimality_claim")


if __name__ == "__main__":
    main()
