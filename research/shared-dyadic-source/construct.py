#!/usr/bin/env python3
"""Literal shared-source schedules. Hanson Sun / OpenAI Codex; Apache-2.0.

The dyadic run walk and native lowering are credited to PR953 and PR840.
This module constructs words; verify.py checks their operators independently.
"""
import argparse
from collections import Counter
from fractions import Fraction
import json
from pathlib import Path
import random


def masks_checked(masks):
    if not isinstance(masks, (list, tuple)) or not masks:
        raise ValueError("at least one output is required")
    answer = []
    for mask in masks:
        if not isinstance(mask, (list, tuple)):
            raise ValueError("a mask must be a sequence")
        if any(type(j) is not int or j < 0 for j in mask):
            raise ValueError("indices must be nonnegative integers")
        if len(set(mask)) != len(mask):
            raise ValueError("duplicate indices are not a set")
        answer.append(sorted(mask))
    return answer


def runs(indices):
    groups = []
    for j in sorted(set(indices)):
        if not groups or j != groups[-1][-1] + 1:
            groups.append([])
        groups[-1].append(j)
    return groups


def visits(run):
    return [-(1 << j) for j in reversed(run)] + [1 << j for j in run]


def shared_word(masks):
    masks = masks_checked(masks)
    word = []
    for run in runs(j for mask in masks for j in mask):
        position = 0
        for vertex in visits(run):
            word.append(["Q", 0, vertex - position])
            position = vertex
            j = abs(vertex).bit_length() - 1
            for output, mask in enumerate(masks, 1):
                if j in mask:
                    word.append(["X", output, 0])
        word.append(["Q", 0, -position])
    return word


def separate_word(masks):
    """PR953's completed target batches, one per separate output."""
    word = []
    for output, mask in enumerate(masks_checked(masks), 1):
        for run in runs(mask):
            position = 0
            for vertex in visits(run):
                word.append(["Q", output, vertex - position])
                word.append(["X", output, 0])
                position = vertex
            word.append(["Q", output, -position])
    return word


def lowering(power):
    if type(power) is not int or not power or abs(power) & (abs(power) - 1):
        raise ValueError("a query power must be a nonzero signed power of two")
    c = Fraction(power, 4)

    def affine(target, coefficients):
        return ["A", target, [[j, str(v)] for j, v in sorted(coefficients.items()) if v]]

    return [
        affine(2, {2: 1, 0: -1}),
        affine(3, {3: 1, 0: 1}),
        affine(5, {5: c, 0: 1 + c, 2: -c, 3: -c}),
        ["C", 0, 5],
        affine(2, {2: 1, 0: 1}),
        affine(3, {3: 1, 0: -1}),
        affine(5, {5: -1 / c, 0: 1 / c - 1, 2: 1, 3: 1}),
    ]


def invoice(word):
    histogram = Counter(str(event[2]) for event in word if event[0] == "Q")
    return {
        "queries": sum(histogram.values()),
        "ordinary_children": sum(histogram.values()),
        "affine_events": 6 * sum(histogram.values()),
        "xor_scans": sum(event[0] == "X" for event in word),
        "extra_full_rows": 0,
        "query_powers": dict(sorted(histogram.items(), key=lambda pair: int(pair[0]))),
    }


def certificate():
    rng = random.Random(55)
    masks = [sorted(rng.sample(range(6), 3)) for _ in range(5)]
    shared, separate = shared_word(masks), separate_word(masks)
    powers = sorted({event[2] for word in (shared, separate) for event in word if event[0] == "Q"})
    return {
        "schema": "shared-dyadic-source-v1",
        "assignment_seed": 55,
        "masks": masks,
        "rows": {"source": 0, "outputs": [1, 2, 3, 4, 5], "spectator": 6},
        "source_permission": "exclusive; unobserved until complete batch exit",
        "shared": shared,
        "separate": separate,
        "lowerings": {str(power): lowering(power) for power in powers},
        "invoices": {"shared": invoice(shared), "separate": invoice(separate)},
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    # Deliberate regeneration always requires a fresh path.
    with args.output.open("x") as out:
        json.dump(certificate(), out, indent=2, sort_keys=True)
        out.write("\n")


if __name__ == "__main__":
    main()
