#!/usr/bin/env python3
"""Emit one exact output-borrowing schedule; all costs are full-row calls.

Copyright 2026 Ross Richardson. Apache-2.0. Substantial OpenAI Codex assistance.
"""
import argparse
import gzip
import json
from collections import Counter
from pathlib import Path


def inverse(word):
    return [(s, t, f, -sign) for s, t, f, sign in reversed(word)]


def depth(n):
    if n < 1:
        raise ValueError("empty product")
    return (n - 1).bit_length()


def lower(factors, source, target, pool):
    """Balanced binary echo with all ancestor ports excluded from the pool."""
    if source == target or len(set([source, target] + pool)) != len(pool) + 2:
        raise ValueError("aliased roles")
    if not factors or len(pool) < depth(len(factors)):
        raise ValueError("empty product or insufficient scratch")
    if len(factors) == 1:
        return [(source, target, factors[0], 1)]
    middle = len(factors) // 2
    connector, *rest = pool
    right = lower(factors[:middle], source, connector, rest)
    left = lower(factors[middle:], connector, target, rest)
    return inverse(left) + right + left + inverse(right)


def macros(k, pivot, kind):
    if k < 2 or not 0 <= pivot < k:
        raise ValueError("need at least two outputs and a valid pivot")
    ys = [f"y{i}" for i in range(k)]
    word = []

    def echo(indices, connector):
        for i in indices:
            word.append((connector, ys[i], f"A{i}", -1))
        word.append(("x", connector, "B", 1))
        for i in indices:
            word.append((connector, ys[i], f"A{i}", 1))
        word.append(("x", connector, "B", -1))

    if kind == "borrowed":
        echo([i for i in range(k) if i != pivot], ys[pivot])
        echo([pivot], ys[(pivot + 1) % k])
    elif kind == "separate":
        for i in range(k):
            echo([i], ys[(i + 1) % k])
    elif kind == "dedicated":
        echo(list(range(k)), "z")
    else:
        raise ValueError("unknown schedule")
    return word


def case(k, b, lengths, pivot):
    factors = {"B": [f"b{j}" for j in range(b)]}
    factors.update({f"A{i}": [f"a{i}_{j}" for j in range(n)]
                    for i, n in enumerate(lengths)})
    scratch = max(depth(len(f)) for f in factors.values())
    pool = [f"h{i}" for i in range(scratch)]
    schedules = {}
    for kind in ("borrowed", "separate", "dedicated"):
        macro = macros(k, pivot, kind)
        leaves = []
        for source, target, name, sign in macro:
            child = lower(factors[name], source, target, pool)
            leaves.extend(child if sign == 1 else inverse(child))
        roles = ["x"] + [f"y{i}" for i in range(k)] + pool
        if kind == "dedicated":
            roles.append("z")
        schedules[kind] = dict(macros=macro, leaves=leaves, roles=roles,
                               leaf_count=len(leaves),
                               multiplicities=dict(sorted(Counter(t[2] for t in leaves).items())),
                               private_rows=scratch + (kind == "dedicated"))
    return dict(k=k, b=b, left_lengths=lengths, pivot=pivot,
                factors=factors, schedules=schedules)


def certificate():
    cases = [case(k, b, [1 + ((b + 3*i) % 5) for i in range(k)], 59 % k)
             for k in range(2, 7) for b in range(1, 9)]
    # The assignment seed chooses this heterogeneous example, not another search.
    fixture = case(2 + 59 % 2, 1 + 59 % 9,
                   [1 + ((59 + 3*i) % 5) for i in range(3)], 59 % 3)
    return dict(schema=1, seed=59, cases=cases, fixture=fixture)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    payload = (json.dumps(certificate(), sort_keys=True, indent=2) + "\n").encode()
    with args.out.open("wb") as out:
        with gzip.GzipFile(filename="", mode="wb", fileobj=out, mtime=0) as stream:
            stream.write(payload)
