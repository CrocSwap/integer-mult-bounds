#!/usr/bin/env python3
"""Minimum paid sign restorations at checkpoint-correct batch cuts. Apache-2.0."""
import argparse
import json
from pathlib import Path


def need(ok, message):
    if not ok:
        raise ValueError(message)


def plan(children, prices, required=(), overhead=0):
    """Children read D += reader*W, then W *= signs, component by component."""
    need(isinstance(children, list), "children must be a list")
    need(isinstance(prices, list) and prices, "prices must be a nonempty list")
    need(all(type(p) is int and p > 0 for p in prices), "prices must be positive integers")
    need(type(overhead) is int and overhead >= 0, "overhead must be a nonnegative integer")
    n, r = len(prices), len(children)
    need(isinstance(required, (list, tuple)), "required must be a list or tuple")
    need(all(type(k) is int and 0 < k <= r for k in required), "required cut out of range")
    need(len(set(required)) == len(required), "duplicate required cut")
    for child in children:
        need(isinstance(child, dict) and set(child) == {"signs", "reader"}, "invalid child fields")
        for key in ("signs", "reader"):
            need(isinstance(child[key], list) and len(child[key]) == n, "child dimension mismatch")
            need(all(type(x) is int for x in child[key]), "child entries must be integers")
        need(all(x in (-1, 1) for x in child["signs"]), "sign must be -1 or 1")

    intervals = {}
    for start in range(r):
        prefix, residual = [1] * n, [0] * n
        for stop in range(start + 1, r + 1):
            child = children[stop - 1]
            for j in range(n):
                residual[j] += child["reader"][j] * (prefix[j] - 1)
                prefix[j] *= child["signs"][j]
            if any(start < k < stop for k in required):
                continue
            if not any(residual):
                negative = [j for j, sign in enumerate(prefix) if sign == -1]
                cost = sum(prices[j] for j in negative) + (overhead if negative else 0)
                intervals[start, stop] = {"start": start, "stop": stop,
                                          "negate": negative, "cost": cost}
    best = [(0, 0, ())] + [None] * r
    for stop in range(1, r + 1):
        choices = []
        for start in range(stop):
            if (start, stop) in intervals and best[start] is not None:
                cost, count, cuts = best[start]
                choices.append((cost + intervals[start, stop]["cost"], count + 1, cuts + (stop,)))
        best[stop] = min(choices)
    cost, _, cuts = best[r]
    starts = (0,) + cuts[:-1]
    return {"cost": cost, "cuts": list(cuts),
            "segments": [intervals[a, b] for a, b in zip(starts, cuts)]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="JSON with children, prices, optional required and overhead")
    args = parser.parse_args()
    try:
        data = json.loads(args.input.read_text())
        need(isinstance(data, dict) and {"children", "prices"} <= set(data), "missing input fields")
        need(set(data) <= {"children", "prices", "required", "overhead"}, "unknown input fields")
        print(json.dumps(plan(**data), indent=2, sort_keys=True))
    except (OSError, ValueError, TypeError) as exc:
        parser.exit(1, "FAIL_RESTORATION_PLAN: " + str(exc) + "\n")


if __name__ == "__main__":
    main()
