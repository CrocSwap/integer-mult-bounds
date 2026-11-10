#!/usr/bin/env python3
"""Source-bound evaluation adapter for the complete PR6338 finite replay."""

import argparse
import hashlib
from itertools import combinations, product
from pathlib import Path


SOURCE = "research/span-lemma-idle-helpers/verify.py"
SOURCE_SHA256 = "66912aab1da6bfe5182088cbfa509dd430df354a9e6bdf5b4f1d9934a7778b52"


def need(condition, message):
    if not condition:
        raise SystemExit(message)


def load_source():
    path = Path(__file__).resolve().parents[2] / SOURCE
    payload = path.read_bytes()
    need(hashlib.sha256(payload).hexdigest() == SOURCE_SHA256, "source hash mismatch")
    namespace = {"__name__": "pinned_idle_helper_source", "__file__": str(path)}
    # Compile authenticated source bytes directly, without consulting bytecode.
    exec(compile(payload, str(path), "exec"), namespace)
    return namespace


def determinant_at(matrix, indices):
    a, b, c, d, e, f, g, h, i = (matrix[index] for index in indices)
    return a * (e * i - f * h) - b * (d * i - f * g) + c * (d * h - e * g)


def check_pair_rank(projectors, observer=None, guard=need):
    """Evaluate the same samples/minors, with one product per ordered pair."""
    guard(1 <= len(projectors) <= 120, "projector count outside adapter domain")
    width = len(projectors[0])
    guard(width in (3, 4), "width outside adapter domain")
    guard(all(len(p) == width and all(len(row) == width for row in p)
              for p in projectors), "projectors are not equally square")
    row_sets = tuple(combinations(range(width), 3))
    minors = tuple(tuple(row * width + col for row in rows for col in cols)
                   for rows in row_sets for cols in row_sets)
    checked = 0
    for left, right in product(projectors, repeat=2):
        mixed = tuple(sum(left[row][mid] * right[mid][col] for mid in range(width))
                      for row in range(width) for col in range(width))
        flat_left = tuple(value for row in left for value in row)
        flat_right = tuple(value for row in right for value in row)
        for scalar_a, scalar_b in product((1, 2, 3, 5), repeat=2):
            coefficient = scalar_a * scalar_b
            difference = tuple(scalar_a * flat_left[j] + scalar_b * flat_right[j]
                               + coefficient * mixed[j] for j in range(width * width))
            if observer is not None:
                observer(difference, width)
            for indices in minors:
                guard(determinant_at(difference, indices) == 0,
                      "two rank-one updates produced rank above 2")
        checked += 1
    return checked


def run(mode):
    source = load_source()
    if mode == "fast":
        source["check_pair_rank"] = check_pair_rank
    source["main"]()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("baseline", "fast"), default="fast")
    run(parser.parse_args().mode)
