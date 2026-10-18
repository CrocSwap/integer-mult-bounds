#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Audit fixed P111 Parseval blocks in the inherited scalar-copy model.

Adam Gall, with substantial OpenAI Codex assistance. No predecessor executable
is imported. The exact interval engine is reused unchanged and source-pinned.
"""

import argparse
from collections import Counter
from fractions import Fraction
from functools import lru_cache
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
WORD = "research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz"
EXPECTED = "research/e8-bit-p111-tuned/tune/EXPECTED.json"
CEILING = "research/complex-local-word-ceiling/ceiling.py"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def combine(vectors, coefficients):
    value = 0
    for i, vector in enumerate(vectors):
        if coefficients >> i & 1:
            value ^= vector
    return value


def binary_rank(vectors):
    pivots = {}
    for value in vectors:
        while value:
            bit = value.bit_length() - 1
            if bit not in pivots:
                pivots[bit] = value
                break
            value ^= pivots[bit]
    return len(pivots)


def rational_basis(rows):
    """Incremental exact row reduction; no numerical rank tolerance."""
    pivots = {}
    for original in rows:
        row = [Fraction(value) for value in original]
        for col, pivot in sorted(pivots.items()):
            coefficient = row[col]
            if coefficient:
                row = [a - coefficient * b for a, b in zip(row, pivot)]
        col = next((i for i, value in enumerate(row) if value), None)
        if col is not None:
            coefficient = row[col]
            pivots[col] = [value / coefficient for value in row]
    return list(pivots.values())


def modular_rank(rows, prime=101):
    """Separate full-matrix elimination supplies a certified rank lower bound."""
    matrix = [[value % prime for value in row] for row in rows]
    if not matrix:
        return 0
    rank = 0
    for col in range(len(matrix[0])):
        pivot = next((i for i in range(rank, len(matrix)) if matrix[i][col]), None)
        if pivot is None:
            continue
        matrix[rank], matrix[pivot] = matrix[pivot], matrix[rank]
        inverse = pow(matrix[rank][col], -1, prime)
        matrix[rank] = [(value * inverse) % prime for value in matrix[rank]]
        for i in range(rank + 1, len(matrix)):
            factor = matrix[i][col]
            if factor:
                matrix[i] = [(a - factor * b) % prime
                             for a, b in zip(matrix[i], matrix[rank])]
        rank += 1
    return rank


def decoder_map(left, right, targets):
    return [combine(right, sum(((column >> target) & 1) << i
                               for i, column in enumerate(left)))
            for target in range(targets)]


def outer2(left, right):
    return sum(1 << (2 * i + j) for i in range(2) for j in range(2)
               if left >> i & 1 and right >> j & 1)


def apply2(matrix, vector):
    return sum(((matrix >> (2 * i) & 3 & vector).bit_count() % 2) << i
               for i in range(2))


def parseval(columns):
    return all(sum(((c >> i) & 1) * ((c >> j) & 1) for c in columns) % 2
               == (i == j) for i in range(9) for j in range(9))


def audit():
    sources = json.loads((PACKAGE / "SOURCES.json").read_text())
    for entry in sources["files"]:
        if entry["usage"] == "input":
            require(hashlib.sha256((ROOT / entry["path"]).read_bytes()).hexdigest()
                    == entry["sha256"], "source pin mismatch: " + entry["path"])
    claim = json.loads((PACKAGE / "SOURCE-CLAIM.json").read_text())
    selection = json.loads((PACKAGE / "SELECTION.json").read_text())
    require(selection["seed"] == "3cc9f4c8f3719f13f4ae6bf28c9ba982"
            and selection["track"] == "recursive-interfaces", "selection changed")
    require(claim["head_commit"] == "9a891c9cb25b15f5a189bcad1d022198adeaf885",
            "audited predecessor head changed")
    columns = claim["frame_columns_little_endian"]
    blocks = claim["blocks_zero_based"]
    require(columns == [3, 5, 6, 7, 8, 16, 32, 64, 128, 256]
            and blocks == [[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]],
            "audited factorization changed")

    word = json.loads(gzip.decompress((ROOT / WORD).read_bytes()))
    expected = json.loads((ROOT / EXPECTED).read_text())
    ports = word["v"]
    registers = 2 * ports + word["R"]
    require((ports, registers, word["h"]) == (111, 661, 8), "not selected P111")
    require(word["punctured"] == [10, 15, 51, 53, 56, 66, 72, 89, 111],
            "selected puncture changed")
    values = [1 << i for i in range(registers)]
    for section in ("D", "A"):
        for _frame, destination, sources in word[section]:
            for source in sources:
                values[destination] ^= values[source]
    left = [sum(1 << t for t, row in enumerate(word["scatter"]) if i in row)
            for i in range(9)]
    right = [values[index] for index in word["ret"]]
    require(len(right) == 9, "retained channel count changed")
    old_map = decoder_map(left, right, ports)
    source_mask = (1 << ports) - 1
    lines = word["lines"]
    gram = [[sum(a * b for a, b in zip(t, s)) for s in lines] for t in lines]
    require(all(value % 2 == 0 for row in gram for value in row), "nonintegral G")
    b0 = [sum(((1 + value // 2) & 1) << s for s, value in enumerate(row))
          for row in gram]
    require([row & source_mask for row in old_map] == b0, "selected B0 map mismatch")
    require(binary_rank(b0) == 9, "selected source decoder must have rank nine")
    require(binary_rank(left) == binary_rank(right) == 9, "channels not independent")
    require(parseval(columns), "Parseval identity failed")
    new_left = [combine(left, column) for column in columns]
    new_right = [combine(right, column) for column in columns]
    require(decoder_map(new_left, new_right, ports) == old_map,
            "valid Parseval decoder differs on a dirty column")

    @lru_cache(None)
    def support_basis(mask):
        return rational_basis([row for i, row in enumerate(lines) if mask >> i & 1])

    @lru_cache(None)
    def pairing_cost(target_mask, input_mask):
        input_mask &= source_mask
        targets = support_basis(target_mask)
        inputs = support_basis(input_mask)
        small = [[sum(a * b for a, b in zip(t, s)) for s in inputs] for t in targets]
        rank = len(rational_basis(small))
        # Independent elimination on the original (not basis-compressed) Gram
        # matrix proves the matching lower bound over Q; equality is required.
        full = [[gram[t][s] for s in range(ports) if input_mask >> s & 1]
                for t in range(ports) if target_mask >> t & 1]
        require(modular_rank(full) == rank, "modular/rational rank disagreement")
        return rank

    baseline_costs = [pairing_cost(a, b) for a, b in zip(left, right)]
    require(baseline_costs == expected["word"]["copy_ranks"] == [7] * 9,
            "baseline copy ranks changed")
    reports = []
    winning_ranks = Counter()
    rank_one_controls = 0
    gl2_count = 0
    for number, (i, j) in enumerate(blocks):
        ls = [new_left[i], new_left[j]]
        rs = [new_right[i], new_right[j]]
        require(binary_rank(ls) == binary_rank(rs) == 2, "rank-two block collapsed")
        require(binary_rank([r & source_mask for r in rs]) == 2,
                "source-restricted block collapsed")
        block_map = decoder_map(ls, rs, ports)
        require(binary_rank(block_map) == 2, "block operator has wrong rank")
        terms = [(a, b, outer2(a, b), pairing_cost(combine(ls, a), combine(rs, b)))
                 for a in (1, 2, 3) for b in (1, 2, 3)]
        union_cost = pairing_cost(ls[0] | ls[1], rs[0] | rs[1])
        require(union_cost == 8, "predecessor union-support rank changed")
        # Nine possible nonzero scalar products, any repeated product cancels
        # modulo two while its strictly positive price cannot improve a bill.
        # Therefore these 512 subsets cover arbitrary finite scalar words in
        # the declared two-dimensional factor spans, not merely two terms.
        feasible = []
        for subset in range(1 << len(terms)):
            matrix = charge = 0
            chosen_left, chosen_right = [], []
            for bit, (a, b, product, price) in enumerate(terms):
                if subset >> bit & 1:
                    matrix ^= product
                    charge += price
                    chosen_left.append(combine(ls, a))
                    chosen_right.append(combine(rs, b))
            if matrix == 9:  # row-major identity matrix over F2
                require(decoder_map(chosen_left, chosen_right, ports) == block_map,
                        "coefficient equality did not preserve the dirty block")
                feasible.append({"subset": subset, "charge": charge,
                                 "terms": subset.bit_count()})
        require(len(feasible) == 32, "incomplete subset census")
        feasible.sort(key=lambda item: (item["charge"], item["subset"]))
        best = feasible[0]
        winners = [term for bit, term in enumerate(terms) if best["subset"] >> bit & 1]
        for _a, _b, _product, price in winners:
            winning_ranks[price] += 1
        # Each ordered GL2 basis has a unique dual; all six are represented by
        # the three unordered two-term factorizations in the full subset list.
        two_term = [item for item in feasible if item["terms"] == 2]
        require(len(two_term) == 3, "missing GL2 factorization")
        gl2_count += 2 * len(two_term)
        one_channel_witnesses = []
        for a, b, product, _price in terms:
            require(product != 9, "one scalar channel unexpectedly has rank two")
            require(decoder_map([combine(ls, a)], [combine(rs, b)], ports) != block_map,
                    "one-channel dirty counterexample missing")
            witness = next(x for x in (1, 2, 3) if apply2(product, x) != x)
            one_channel_witnesses.append({"left": a, "right": b, "input": witness,
                                          "expected": witness,
                                          "actual": apply2(product, witness)})
            rank_one_controls += 1
        for omitted in range(len(winners)):
            retained = winners[:omitted] + winners[omitted + 1:]
            require(decoder_map([combine(ls, a) for a, _b, _p, _c in retained],
                                [combine(rs, b) for _a, b, _p, _c in retained],
                                ports) != block_map,
                    "deleting a winning term failed to break the dirty endpoint")
        reports.append({
            "block": number, "columns": [i, j], "operator_rank": 2,
            "union_support_charge": union_cost,
            "term_cost_grid": [term[3] for term in terms],
            "direct_scalar_charge": terms[0][3] + terms[4][3],
            "minimum_scalar_charge": best["charge"],
            "witness": [[a, b, price] for a, b, _product, price in winners],
            "feasible_subsets": feasible,
            "one_channel_counterexamples": one_channel_witnesses,
        })
    minima = [report["minimum_scalar_charge"] for report in reports]
    require(minima == [16, 15, 14, 14, 14], "fixed-block optimum changed")
    require(dict(winning_ranks) == {8: 3, 7: 7}, "winning copy profile changed")

    union_left = [new_left[i] | new_left[j] for i, j in blocks]
    union_right = [new_right[i] | new_right[j] for i, j in blocks]
    union_map = decoder_map(union_left, union_right, ports)
    differences = [a ^ b for a, b in zip(old_map, union_map)]
    source_differences = sum((row & source_mask).bit_count() for row in differences)
    dirty_differences = sum(row.bit_count() for row in differences)
    require((source_differences, dirty_differences) == (5838, 17146),
            "literal one-union-copy counterexample changed")
    require((old_map[0] & 1, union_map[0] & 1) == (1, 0), "small witness changed")

    broken = columns.copy()
    broken[3] ^= 256
    require(not parseval(broken), "broken-frame control accepted")
    require(decoder_map(new_left[:-2], new_right[:-2], ports) != old_map,
            "omitted-block control accepted")
    switched = new_right.copy()
    switched[0], switched[1] = switched[1], switched[0]
    require(decoder_map(new_left, switched, ports) != old_map,
            "switched-channel control accepted")
    field_fixture = [[1, 1, 0], [1, 0, 1], [0, 1, 1]]
    require(len(rational_basis(field_fixture)) == 3
            and binary_rank([3, 5, 6]) == 2, "rank field control failed")

    profile = {int(rank): count for rank, count in expected["word"]["local_histogram"].items()}
    changed = profile.copy()
    changed[7] -= 9
    for rank, count in winning_ranks.items():
        changed[rank] = changed.get(rank, 0) + count
    # No extra basis, route, storage or cleanup credit is assumed. Setting all
    # of those nonnegative charges to zero is deliberately favorable.
    spec = importlib.util.spec_from_file_location("pinned_ceiling", ROOT / CEILING)
    ceiling = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ceiling)
    screens = {}
    for name, local, centre in (("baseline_line", profile, 63),
                                ("blockwise_scalar_copy_only", changed, 73)):
        model = ceiling.model(local, 64, 888, 9, centre, R=42, unpaid=1)
        bracket = ceiling.ceiling(local, 64, 888, 9, centre, R=42, unpaid=1,
                                  grid=Fraction(1, 10**12))
        screens[name] = {"profile": {str(k): n for k, n in sorted(local.items())},
                         "centre": centre, "unpaid": 1,
                         "model": {k: str(value) for k, value in model.items()},
                         "a_bracket": [str(value) for value in bracket]}
    require(screens["blockwise_scalar_copy_only"]["a_bracket"]
            == ["87582827/62500000000", "1401325233/1000000000000"],
            "changed exact ceiling mismatch")
    require(screens["baseline_line"]["a_bracket"]
            == ["973733779/500000000000", "1947467559/1000000000000"],
            "baseline exact ceiling mismatch")
    require(Fraction(screens["blockwise_scalar_copy_only"]["a_bracket"][1])
            < Fraction(screens["baseline_line"]["a_bracket"][0]),
            "copy-only route does not fail the target")
    width = (registers + 7) // 8
    digest = hashlib.sha256(b"".join(row.to_bytes(width, "little") for row in old_map)).hexdigest()
    return {
        "status": "PASS_P111_PARSEVAL_COPY_INTERFACE",
        "seed": selection["seed"], "track": selection["track"],
        "predecessor_head": claim["head_commit"],
        "targets": ports, "dirty_input_columns": registers,
        "source_decoder_rank": 9, "dirty_map_sha256": digest,
        "parseval_identity": "PASS", "baseline_scalar_charge": sum(baseline_costs),
        "direct_ten_channel_charge": sum(r["direct_scalar_charge"] for r in reports),
        "best_blockwise_scalar_charge": sum(minima),
        "union_support_sum_not_scalar_invoice": sum(r["union_support_charge"] for r in reports),
        "enumerated_subsets": 5 * 512, "exact_factorizations": 5 * 32,
        "ordered_gl2_bases": gl2_count, "blocks": reports,
        "literal_union_copy_failure": {"source_entries": source_differences,
                                       "dirty_entries": dirty_differences,
                                       "input": "source port 0 = 1, all other inputs = 0",
                                       "target": 0, "expected": 1, "actual": 0},
        "controls": {"rank_one_rejections": rank_one_controls,
                     "winning_term_omissions": 10, "broken_frame": "REJECTED",
                     "omitted_block": "REJECTED", "switched_channel": "REJECTED",
                     "rational_vs_binary_rank": [3, 2]},
        "copy_only_line_port_screens": screens,
        "scope": "Exact all-length floor only within each fixed rank-two coefficient block; no cross-block rebasing, new physical block-copy primitive, new plane geometry, complete supplier or kappa claim.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="regenerate deterministic RESULT.json")
    args = parser.parse_args()
    report = audit()
    result = PACKAGE / "RESULT.json"
    if args.write:
        result.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    else:
        require(json.loads(result.read_text()) == report, "RESULT.json differs from exact replay")
    print(report["status"], "blocks=5 subsets=2560 factorizations=160",
          "dirty_columns=661 copy_min=73 baseline=63 union_failure_entries=17146")


if __name__ == "__main__":
    main()
