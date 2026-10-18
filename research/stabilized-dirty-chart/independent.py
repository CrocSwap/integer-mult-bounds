#!/usr/bin/env python3
"""Exhaust auxiliary kernels directly, and compose literal Boolean gate matrices.

No imports from the chart construction/replay implementation. Apache-2.0.
Prepared for ywz65 with OpenAI Codex assistance.
"""
import itertools
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def require(ok, why):
    if not ok:
        raise ValueError(why)


def kernel(rows):
    return frozenset(x for x in range(4) if all((r & x).bit_count() % 2 == 0 for r in rows))


def main():
    observed = {}
    maps = list(itertools.product(range(4), repeat=2))
    possible = {(b, h): {kernel(b + d) for d in itertools.product(range(4), repeat=h)}
                for b in maps for h in range(3)}
    for left in maps:
        for right in maps:
            least = next(h for h in range(3) if possible[left, h] & possible[right, h])
            # Independently compute each image size by evaluating all four inputs.
            def dim(rows):
                image = {tuple((r & x).bit_count() % 2 for r in rows) for x in range(4)}
                return len(image).bit_length() - 1
            require(least == dim(left + right) - min(dim(left), dim(right)), 'sharp helper formula')
            observed[str(least)] = observed.get(str(least), 0) + 1
    result = json.loads((HERE / 'RESULT.json').read_bytes())
    require(observed == result['helper_histogram'], 'independent census differs')
    rows = [1 << i for i in range(17)]
    for source, target, _ in result['literal_word']:
        rows[target] ^= rows[source]
    p = result['pilot']
    expected = [1 << i for i in range(17)]
    for a, b, offset in ((p['a0'], p['b0'], 9), (p['a1'], p['b1'], 13)):
        for i, row in enumerate(a):
            for j in range(4):
                if row >> j & 1:
                    expected[offset + i] ^= b[j]
    require(rows == expected, 'independent full Boolean operator')
    counts = {}
    for _, _, label in result['literal_word']:
        counts[label] = counts.get(label, 0) + 1
    require(counts == dict(A0=10, A1=10, B0=12, B1=12, D=3, E=3, R=3, Rinv=3),
            'complete primitive invoice')
    require(sum(counts.values()) == 56, 'invoice sum')
    print('PASS_STABILIZED_INDEPENDENT: all256 minimum-kernel cases; full17-bit operator and invoice')


if __name__ == '__main__':
    main()
