#!/usr/bin/env python3
"""Check the rigidity equations with 72 variables over F_107.

Use nine coefficients for each of e_1 through e_8. Add one zero-sum
equation for each vector. Set e_0 to zero. At each port, add all pairs
of equality equations for the totals that must be zero at that port.
Do not import repository modules.
"""

import gzip
import hashlib
import json
import sys
from itertools import combinations


def rank_modulo(rows, prime):
    basis = {}
    for source in rows:
        row = [value % prime for value in source]
        for column in sorted(basis):
            if row[column]:
                scale = row[column]
                row = [(x - scale * y) % prime for x, y in zip(row, basis[column])]
        column = next((i for i, value in enumerate(row) if value), None)
        if column is not None:
            inverse = pow(row[column], -1, prime)
            basis[column] = [(value * inverse) % prime for value in row]
    return len(basis)


def main():
    items = []
    for triple in combinations(range(9), 3):
        vector = [int(i in triple) for i in range(9)]
        items.append((sum(1 << i for i in triple), vector))
    for i, j in combinations(range(9), 2):
        vector = [0] * 9
        vector[i], vector[j] = 1, -1
        items.append((511 - (1 << i) - (1 << j), vector))

    with open(sys.argv[1], "rb") as handle:
        certificate_bytes = handle.read()
    certificate = json.loads(gzip.decompress(certificate_bytes))
    assert certificate["h"] == 9
    assert certificate["v"] == 120
    assert certificate["ports"] == [port for port, vector in items]

    results = []
    for weight in (0, 1, 3, 5, 7):
        normal = sum(1 << i for i in range(1, weight + 1))
        rows = []
        for i in range(1, 9):
            row = [0] * 72
            row[9 * (i - 1):9 * i] = [1] * 9
            rows.append(row)
        for port, vector in items:
            outside = {i for i in range(9) if port & (1 << i)}
            if (port & normal).bit_count() % 2:
                outside.add(0)
            for i, j in combinations(sorted(outside), 2):
                row = [0] * 72
                if i:
                    for k, value in enumerate(vector):
                        row[9 * (i - 1) + k] += value
                if j:
                    for k, value in enumerate(vector):
                        row[9 * (j - 1) + k] -= value
                rows.append(row)
        rank = rank_modulo(rows, 107)
        assert rank == (71 if weight == 0 else 72)
        results.append({
            "extra_normal_weight": weight,
            "rows": len(rows),
            "rank_mod_107": rank,
            "nullity_mod_107": 72 - rank,
        })

    print(json.dumps({
        "certificate_sha256": hashlib.sha256(certificate_bytes).hexdigest(),
        "certificate_ports_match": True,
        "variables": 72,
        "field_prime": 107,
        "results": results,
        "nondegenerate_subframes_of_F0": sum(
            1 for normal in range(2, 512, 2) if normal.bit_count() % 2
        ),
        "scope": "Independent modular check of the normalized equations; no repository modules or Lean execution.",
    }, indent=2))


if __name__ == "__main__":
    main()
