#!/usr/bin/env python3
"""Optional cross-check with SymPy; does not import verify.py or its generator.

Read the parent word's stored 120 coordinates directly, then independently
check the premises recorded in RESULTS.json. This is extra finite evidence,
not a formal proof or a replay of either supplier.
"""

import gzip
import hashlib
from itertools import product
import json
from pathlib import Path

from sympy import Matrix
import sympy


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read_pinned(path):
    payload = (ROOT / path).read_bytes()
    expected = json.loads((HERE / "SOURCES.json").read_text())["local_sha256"][path]
    require(hashlib.sha256(payload).hexdigest() == expected, "source pin: " + path)
    return json.loads(gzip.decompress(payload))


def main():
    receipt = json.loads((HERE / "RESULTS.json").read_text())
    parent = read_pinned("research/e8-bit-carrier-skeleton/data/bit/bitE8mut-r489.json.gz")
    child = read_pinned("research/e8-punctured111-star/data/bitE8mut-v111-r489.json.gz")
    labels = Matrix(parent["lines"])
    p = child["punctured"]
    live = child["ports_geom"]
    require(labels.rows == 120 and labels.cols == 8, "parent geometry dimensions")
    require(labels.extract(live, range(8)) == Matrix(child["lines"]), "parent/child coordinates")
    gram = labels * labels.T / 2
    binary = gram.applyfunc(lambda x: (x + 1) % 2)
    c = binary.extract(p, p)
    m = c.inv_mod(2)
    w = binary.extract(live, p)
    require((w * m * w.T).applyfunc(lambda x: x % 2) == binary.extract(live, live),
            "restricted decoder identity")
    require([sum(int(m[i, j]) << j for j in range(9)) for i in range(9)]
            == receipt["M_inverse_rows"], "independent inverse")
    bases = {}
    ranks = {7: 0, 8: 0}
    for mask in range(1, 512):
        x = Matrix([(mask >> j) & 1 for j in range(9)])
        response = (w * x).applyfunc(lambda z: z % 2)
        support = [live[i] for i, z in enumerate(response) if z]
        rows = labels.extract(support, range(8))
        basis = Matrix.vstack(*rows.rowspace())
        expected = 7 if mask & (mask - 1) == 0 else 8
        require(basis.rows == expected, "independent rational support rank")
        ranks[expected] += 1
        if expected == 7:
            bases[mask.bit_length() - 1] = basis
    require(ranks == {7: 9, 8: 502}, "support rank census")
    pairings = [[int((bases[i] * bases[j].T).rank()) for j in range(9)] for i in range(9)]
    require(pairings == receipt["unit_pair_ranks"], "81 independent pairing ranks")

    # Exhaust every dimension-three unit-diagonal symmetric form and every
    # binary basis. This checks the general counting lemma in a small domain;
    # its proof, not these examples, covers dimension nine.
    invertibles = []
    for entries in product((0, 1), repeat=9):
        x = Matrix(3, 3, entries)
        if x.det() % 2:
            invertibles.append((x, x.inv_mod(2)))
    forms, cases = 0, 0
    for a, b, d in product((0, 1), repeat=3):
        c3 = Matrix([[1, a, b], [a, 1, d], [b, d, 1]])
        if not c3.det() % 2:
            continue
        forms += 1
        for x, xi in invertibles:
            y = (xi * c3.inv_mod(2)).T.applyfunc(lambda z: z % 2)
            different_units = generic = 0
            for j in range(3):
                xu, yu = sum(x[:, j]) == 1, sum(y[:, j]) == 1
                different_units += xu and yu and x[:, j] != y[:, j]
                generic += not xu and not yu
            require(different_units <= generic, "dimension-three counting lemma")
            cases += 1
    require((forms, len(invertibles), cases) == (4, 168, 672), "exhaustive small domain")
    print(f"PASS_INDEPENDENT_P111: SymPy {sympy.__version__}; 511 supports; "
          "81 pairings; 672 small-basis factorizations")


if __name__ == "__main__":
    main()
