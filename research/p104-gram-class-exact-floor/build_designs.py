#!/usr/bin/env python3
"""Write the 25 explicit Gram designs to a requested output file.

Run from the repository root with an output path outside the checkout.
The independent verifier recomputes every price and determinant.
"""
import argparse
import itertools
import json
from pathlib import Path

SIMPLE = [
    None,
    (1, -1, -1, -1, -1, -1, -1, 1),
    (2, 2, 0, 0, 0, 0, 0, 0),
    (-2, 2, 0, 0, 0, 0, 0, 0),
    (0, -2, 2, 0, 0, 0, 0, 0),
    (0, 0, -2, 2, 0, 0, 0, 0),
    (0, 0, 0, -2, 2, 0, 0, 0),
    (0, 0, 0, 0, -2, 2, 0, 0),
    (0, 0, 0, 0, 0, -2, 2, 0),
]
PAIRS = [(1, 3), (2, 4), (5, 6), (7, 8)]


def root_lines():
    lines = set()
    for i, j in itertools.combinations(range(8), 2):
        for sign in (2, -2):
            root = [0] * 8
            root[i], root[j] = 2, sign
            lines.add(tuple(root))
    for tail in itertools.product((1, -1), repeat=7):
        if tail.count(-1) % 2 == 0:
            lines.add((1,) + tail)
    if len(lines) != 120:
        raise ValueError("wrong E8 line count")
    return sorted(lines)


def design(d, lines):
    deleted_indices = set()
    tau = {i: i for i in range(1, 9)}
    for a, b in PAIRS[:min(d // 2, 4)]:
        deleted_indices.update((a, b))
        tau[a], tau[b] = b, a
    if d < 8 and d % 2:
        a = PAIRS[d // 2][0]
        deleted_indices.add(a)
        b = min(i for i in range(1, 9) if i not in deleted_indices)
        tau[a], tau[b] = b, a
    deleted = [SIMPLE[i] for i in sorted(deleted_indices)]
    extras = [v for v in lines if v not in deleted and tuple(-x for x in v) not in deleted]
    if d >= 8:
        deleted.extend(extras[:d - 8])
    return {"d": d, "claimed_c": 72 - 2 * min(d, 8), "D": deleted,
            "terms": [(SIMPLE[k], SIMPLE[tau[k]]) for k in range(1, 9)]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    lines = root_lines()
    rows = [json.dumps(design(d, lines), sort_keys=True, separators=(",", ":")) for d in range(25)]
    payload = ('{\n "format": "Gram-class E8 designs in doubled integer coordinates",\n'
               ' "designs": [\n' + ",\n".join(rows) + '\n ]\n}\n')
    args.output.write_text(payload, encoding="utf-8")
    print("WROTE_GRAM_DESIGNS designs=25")


if __name__ == "__main__":
    main()
