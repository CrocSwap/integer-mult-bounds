#!/usr/bin/env python3
"""Exact P111 pairing-rank certificate. Python 3.10+, standard library only.

The all-factorization argument is in PROOF.md. This checks its finite premises,
attaining witness, budget cases and rejection controls; it is not a Lean proof.
No predecessor code, numerical rank routine or solver is imported.
"""

import argparse
from collections import Counter
from fractions import Fraction
import gzip
import hashlib
from itertools import product
import json
from pathlib import Path
import random


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PUNCTURES = (39, 52, 57, 71, 76, 78, 103, 109, 114)
WORD = "research/e8-punctured111-star/data/bitE8mut-v111-r489.json.gz"
DIM = 9
IDENTITY = [1 << i for i in range(DIM)]


class Rejected(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise Rejected(message)


def parity(n):
    return n.bit_count() % 2


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def roots(supplier_order=True):
    """Generate E8 lines, preserving the supplier's Hamming word ordering.

    The historical format-limits utility instead sorts its tetrads. It has the
    same roots but different indices; this distinction is a rejection control.
    """
    generators = ((15, 51, 85, 150) if supplier_order
                  else (15, 60, 240, 170))
    words = []
    for coefficients in product((0, 1), repeat=4):
        word = 0
        for coefficient, generator in zip(coefficients, generators):
            if coefficient:
                word ^= generator
        words.append(tuple((word >> j) & 1 for j in range(8)))
    tetrads = [word for word in words if sum(word) == 4]
    if not supplier_order:
        tetrads.sort()
    require(len(set(words)) == 16 and len(tetrads) == 14, "Hamming code")
    lines = [tuple(2 * int(i == j) for j in range(8)) for i in range(8)]
    for word in tetrads:
        support = [j for j, bit in enumerate(word) if bit]
        for signs in product((1, -1), repeat=3):
            line = [0] * 8
            for j, sign in zip(support, (1,) + signs):
                line[j] = sign
            lines.append(tuple(line))
    return lines


def rational_basis(rows):
    """Row basis over Q, using normalized Fraction elimination."""
    echelon, selected = {}, []
    for original in rows:
        row = list(map(Fraction, original))
        for pivot, existing in sorted(echelon.items()):
            coefficient = row[pivot]
            if coefficient:
                row = [x - coefficient * y for x, y in zip(row, existing)]
        pivot = next((j for j, x in enumerate(row) if x), None)
        if pivot is not None:
            coefficient = row[pivot]
            echelon[pivot] = [x / coefficient for x in row]
            selected.append(original)
    return selected


def binary_rank(rows):
    pivots = {}
    for row in rows:
        while row:
            pivot = row.bit_length() - 1
            if pivot not in pivots:
                pivots[pivot] = row
                break
            row ^= pivots[pivot]
    return len(pivots)


def inverse(rows):
    n = len(rows)
    augmented = [row | (1 << (n + i)) for i, row in enumerate(rows)]
    for j in range(n):
        pivot = next((i for i in range(j, n) if (augmented[i] >> j) & 1), None)
        require(pivot is not None, "singular binary matrix")
        augmented[j], augmented[pivot] = augmented[pivot], augmented[j]
        for i in range(n):
            if i != j and (augmented[i] >> j) & 1:
                augmented[i] ^= augmented[j]
    return [row >> n for row in augmented]


def multiply(a, b):
    result = []
    for row in a:
        value = 0
        for j, b_row in enumerate(b):
            if (row >> j) & 1:
                value ^= b_row
        result.append(value)
    return result


def columns(rows):
    return [sum(((row >> j) & 1) << i for i, row in enumerate(rows))
            for j in range(DIM)]


def unit_index(x):
    return x.bit_length() - 1 if x and x & (x - 1) == 0 else None


def factor_sum(terms):
    rows = [0] * DIM
    for x, y in terms:
        require(0 < x < 512 and 0 < y < 512, "nonzero 9-bit factors")
        for i in range(DIM):
            if (x >> i) & 1:
                rows[i] ^= y
    return rows


def term_cost(x, y, cheap):
    a, b = unit_index(x), unit_index(y)
    if a is not None and b is not None and (cheap[a] >> b) & 1:
        return 6
    return 7 if a is not None or b is not None else 8


def validate_geometry(lines):
    require(len(lines) == len(set(lines)) == 120, "120 distinct lines")
    require(all(len(line) == 8 and dot(line, line) == 4 for line in lines),
            "root norms")
    require(all(dot(a, b) % 2 == 0 for a in lines for b in lines), "integral Gram")
    require(all(abs(dot(lines[i], lines[j])) <= 2
                for i in range(120) for j in range(i)), "off-diagonal Gram")


def validate_word(lines, word):
    live = [i for i in range(120) if i not in PUNCTURES]
    require(word["punctured"] == list(PUNCTURES), "word punctures")
    require(word["ports_geom"] == live, "word port order")
    require(word["lines"] == [list(lines[i]) for i in live], "word geometry")


def validate_algebra(c, m, cheap):
    require(len(c) == len(m) == len(cheap) == DIM, "matrix dimensions")
    require(all(0 <= row < 512 for rows in (c, m, cheap) for row in rows), "matrix bits")
    require(columns(c) == c, "symmetric C")
    require(all((row >> i) & 1 for i, row in enumerate(c)), "unit diagonal C")
    require(multiply(c, m) == multiply(m, c) == IDENTITY, "inverse identity")
    require(cheap == [row ^ (1 << i) for i, row in enumerate(c)], "cheap mask")
    return ten_term_obstructions(m, cheap)


def ten_term_obstructions(m, cheap):
    diagonal = [i for i, row in enumerate(m) if (row >> i) & 1]
    require(len(diagonal) > 2, "ten-term diagonal obstruction")
    # A 2x2 block untouched by ANY cost-six term, yet rank two in M.
    block = (3, 5)
    require(all(((cheap[i] >> j) & 1) == 0 for i in block for j in block),
            "ten-term forbidden block")
    require(all(((m[i] >> j) & 1) == int(i == j) for i in block for j in block),
            "ten-term rank-two block")
    return diagonal, list(block)


def validate_factorization(terms, m, cheap, expected_cost=None):
    require(factor_sum(terms) == m, "factorization identity")
    counts = Counter(term_cost(x, y, cheap) for x, y in terms)
    cost = sum(k * v for k, v in counts.items())
    if expected_cost is not None:
        require(cost == expected_cost, "factorization price")
    if len(terms) == DIM:
        require(binary_rank(x for x, _ in terms) == DIM, "X basis")
        require(binary_rank(y for _, y in terms) == DIM, "Y basis")
        require(counts[6] <= counts[8], "nine-term discount compensation")
    return cost, counts


def budget_cases(diagonal_size):
    cases = []
    for n in (9, 10):
        for n6 in range(n + 1):
            for n8 in range(n - n6 + 1):
                n7 = n - n6 - n8
                cost = 6 * n6 + 7 * n7 + 8 * n8
                if cost > 62:
                    continue
                if n == 9:
                    require(n6 > n8, "nine-term budget exclusion")
                    reason = "basis-counting"
                elif n8 == 0:
                    require(n7 < diagonal_size, "ten-term diagonal budget exclusion")
                    reason = "diagonal-support"
                else:
                    require((n6, n7, n8) == (9, 0, 1), "ten-term remaining budget")
                    reason = "rank-two-block"
                cases.append({"n": n, "counts_6_7_8": [n6, n7, n8],
                              "cost": cost, "excluded_by": reason})
    return cases


def source_pins():
    manifest = json.loads((HERE / "SOURCES.json").read_text())
    for path, expected in manifest["local_sha256"].items():
        require(hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == expected,
                "source pin: " + path)
    return manifest


def verify():
    manifest = source_pins()
    lines = roots()
    validate_geometry(lines)
    word = json.loads(gzip.decompress((ROOT / WORD).read_bytes()))
    validate_word(lines, word)
    live = [i for i in range(120) if i not in PUNCTURES]
    gram = [[dot(a, b) // 2 for b in lines] for a in lines]
    b = [sum(((1 + value) % 2) << j for j, value in enumerate(row)) for row in gram]
    c = [sum(((b[i] >> j) & 1) << k for k, j in enumerate(PUNCTURES))
         for i in PUNCTURES]
    m = inverse(c)
    w = [sum(((b[i] >> j) & 1) << k for k, j in enumerate(PUNCTURES)) for i in live]
    require(binary_rank(w) == DIM, "full-rank live label coordinates")
    wm = multiply(w, m)
    require(all(parity(wm[i] & w[j]) == ((b[s] >> t) & 1)
                for i, s in enumerate(live) for j, t in enumerate(live)), "live decoder factor")

    support_bases, rank_counts = {}, Counter()
    for x in range(1, 512):
        support = [lines[i] for i, row in zip(live, w) if parity(row & x)]
        basis = rational_basis(support)
        support_bases[x] = basis
        rank_counts[len(basis)] += 1
        a = unit_index(x)
        require(len(basis) == (7 if a is not None else 8), "support rank classification")
        if a is not None:
            require(all(dot(v, lines[PUNCTURES[a]]) == 0 for v in support), "support hyperplane")
    # For full spans the nondegenerate Q^8 pairing has rank equal to the other
    # span's dimension. Only these 81 hyperplane/hyperplane pairs remain.
    pair_ranks, cheap = [], []
    for a in range(DIM):
        ranks, mask = [], 0
        for d in range(DIM):
            left, right = support_bases[1 << a], support_bases[1 << d]
            pairing = [[dot(v, u) for u in right] for v in left]
            rank = len(rational_basis(pairing))
            expected = 6 if a != d and gram[PUNCTURES[a]][PUNCTURES[d]] == 0 else 7
            require(rank == expected, "pairing rank classification")
            ranks.append(rank)
            if rank == 6:
                mask |= 1 << d
        pair_ranks.append(ranks)
        cheap.append(mask)
    diagonal, block = validate_algebra(c, m, cheap)
    histogram = Counter(term_cost(x, y, cheap) for x in range(1, 512) for y in range(1, 512))
    star = list(zip(columns(m), IDENTITY))
    require(all(x.bit_count() > 1 for x, _ in star), "nonunit star reader columns")
    validate_factorization(star, m, cheap, 63)
    cases = budget_cases(len(diagonal))

    # Calibration: other decompositions of this same M, never used as a proof
    # of the universal nine-term argument. A fixed seed makes them reproducible.
    rng = random.Random(45)
    x_rows = IDENTITY.copy()
    prices = Counter()
    for _ in range(128):
        for _ in range(9):
            a, d = rng.sample(range(DIM), 2)
            x_rows[a] ^= x_rows[d]
        y_transpose = multiply(inverse(x_rows), m)
        cost, _ = validate_factorization(list(zip(columns(x_rows), y_transpose)), m, cheap)
        prices[cost] += 1

    controls = []

    def reject(name, function):
        try:
            function()
        except Rejected:
            controls.append(name)
        else:
            raise Rejected("negative control accepted: " + name)

    bad_lines = lines.copy()
    bad_lines[45] = (0,) * 8
    reject("zero-root", lambda: validate_geometry(bad_lines))
    bad_word = dict(word, punctured=list(PUNCTURES[:-1]) + [115])
    reject("wrong-puncture", lambda: validate_word(lines, bad_word))
    bad_c = c.copy()
    bad_c[0] ^= 1
    reject("missing-diagonal-premise", lambda: validate_algebra(bad_c, m, cheap))
    bad_m = m.copy()
    bad_m[0] ^= 1
    reject("wrong-inverse", lambda: validate_algebra(c, bad_m, cheap))
    bad_cheap = cheap.copy()
    bad_cheap[3] |= 1 << 5
    reject("forbidden-pair-discount", lambda: validate_algebra(c, m, bad_cheap))
    reject("omitted-star-total", lambda: validate_factorization(star[:-1], m, cheap))
    reject("underpriced-star", lambda: validate_factorization(star, m, cheap, 62))
    changed_star = star.copy()
    changed_star[0] = (changed_star[0][0] ^ 1, changed_star[0][1])
    reject("changed-source-functional", lambda: validate_factorization(changed_star, m, cheap))
    # Dropping all nine punctures is essential: at least one omitted direction
    # has full support rank in the unpunctured 120-line geometry.
    full_support = [lines[i] for i in range(120) if (b[i] >> PUNCTURES[0]) & 1]
    reject("unpunctured-rank-seven", lambda: require(len(rational_basis(full_support)) == 7,
                                                    "unpunctured rank is eight"))
    missing_diagonal = [row & ~(1 << i) for i, row in enumerate(m)]
    reject("missing-diagonal-obstruction", lambda: ten_term_obstructions(missing_diagonal, cheap))
    missing_block = m.copy()
    missing_block[3] ^= 1 << 5
    missing_block[5] ^= 1 << 3
    reject("rank-one-in-place-of-rank-two", lambda: ten_term_obstructions(missing_block, cheap))
    # A second abstract algebra instance is accepted, and a determinant-one
    # rational rank example cannot collapse through floating-point rounding.
    validate_algebra(IDENTITY, IDENTITY, [0] * DIM)
    big = 2 ** 54
    require(len(rational_basis([[big, big - 1], [big + 1, big]])) == 2, "exact rank control")
    legacy_lines = roots(supplier_order=False)
    require(set(legacy_lines) == set(lines), "same E8 root set")
    reject("different-line-numbering", lambda: validate_word(legacy_lines, word))
    legacy_indices = {line: i for i, line in enumerate(legacy_lines)}
    mapped_punctures = [legacy_indices[lines[i]] for i in PUNCTURES]
    legacy_cheap_pairs = sum(a != d and dot(legacy_lines[a], legacy_lines[d]) == 0
                             for a in PUNCTURES for d in PUNCTURES)

    return {
        "status": "PASS_P111_PAIRING_FLOOR",
        "base_commit": manifest["base_commit"],
        "punctures": list(PUNCTURES),
        "conventions": "bit j is column j; puncture positions and ports are zero-based",
        "C_rows": c, "M_inverse_rows": m, "cheap_rows": cheap,
        "numbering_control": {"supplier_punctures_in_sorted_tetrad_order": mapped_punctures,
                              "unchanged_indices_in_sorted_order_cheap_pairs": legacy_cheap_pairs,
                              "actual_supplier_cheap_pairs": histogram[6]},
        "live_label_rank": binary_rank(w), "live_decoder_entries": len(live) ** 2,
        "support_ranks": dict(sorted(rank_counts.items())),
        "unit_pair_ranks": pair_ranks,
        "term_cost_histogram": dict(sorted(histogram.items())),
        "diagonal_ones": diagonal, "forbidden_identity_block": block,
        "excluded_budgets_at_most_62": cases,
        "terms_below_nine": "excluded by rank(M)=9",
        "terms_at_least_eleven": "cost at least 6*n >= 66",
        "attaining_star": [{"x": x, "y": y, "cost": term_cost(x, y, cheap)} for x, y in star],
        "minimum_pairing_cost": 63,
        "calibration_seed": 45, "calibration_nine_term_prices": dict(sorted(prices.items())),
        "negative_controls": controls,
        "scope": "Fixed B0 label factorizations on this P111 geometry; no new kappa or physical word",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", type=Path, help="write the deterministic receipt instead of comparing it")
    args = parser.parse_args()
    result = verify()
    payload = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.write:
        args.write.write_text(payload)
    else:
        require(payload == (HERE / "RESULTS.json").read_text(), "committed receipt differs")
    print("PASS_P111_PAIRING_FLOOR: cost 63; 511 exact supports; 261121 support pairs; "
          + str(len(result["negative_controls"])) + " negative controls")


if __name__ == "__main__":
    main()
