#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Small independent exact checks, NOT a Lean replay or universal proof.

No dependencies, network, file mutation, random search, supplier suite, or BFS.
Checks use full dirty-input bit vectors and output-row/input-column matrices.
Every check remains active under Python -O.
"""
from __future__ import annotations

import itertools
import json
import platform
from typing import Iterable, Sequence


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def xor_all(values: Iterable[int]) -> int:
    result = 0
    for value in values:
        result ^= value
    return result


def dot(row: int, x: int) -> int:
    return (row & x).bit_count() & 1


def action(matrix: Sequence[int], x: int) -> int:
    return sum(dot(row, x) << r for r, row in enumerate(matrix))


def combine(rows: Sequence[int], mask: int) -> int:
    return xor_all(row for j, row in enumerate(rows) if (mask >> j) & 1)


def measurements(rows: Sequence[int], x: int) -> tuple[int, ...]:
    return tuple(dot(row, x) for row in rows)


def bits_code(bits: Sequence[int]) -> int:
    code = 0
    for bit in reversed(bits):
        require(bit in (0, 1), "non-Boolean bit")
        code = bit + 2 * code
    return code


def decode(masks: Sequence[int], values: Sequence[int]) -> int:
    code = bits_code(values)
    return sum(((mask & code).bit_count() & 1) << r for r, mask in enumerate(masks))


def check_factorization(n: int, rows: Sequence[int], masks: Sequence[int]) -> int:
    """Every input is checked; choose first input witness of each output."""
    k = len(rows)
    require(len(masks) == n, "wrong number of output rows")
    require(all(0 <= v < (1 << n) for v in rows), "bad full row")
    require(all(0 <= c < (1 << k) for c in masks), "bad coefficient mask")
    matrix = tuple(combine(rows, mask) for mask in masks)
    chosen_codes: dict[int, int] = {}
    for x in range(1 << n):
        values = measurements(rows, x)
        require(len(values) == k, "wrong measurement length")
        code = bits_code(values)
        require(0 <= code < (1 << k), "binary code bound")
        output = action(matrix, x)
        require(output == decode(masks, values), "oriented factorization failed")
        chosen_codes.setdefault(output, code)
    require(len(set(chosen_codes.values())) == len(chosen_codes), "image code collision")
    require(len(chosen_codes) <= (1 << k), "finite image bound failed")
    return len(chosen_codes)


def check_general_small() -> dict[str, int]:
    models = 0
    input_checks = 0
    # All full rows and exact-length coefficient masks in these small sizes.
    for n in range(3):
        for k in range(3):
            for rows in itertools.product(range(1 << n), repeat=k):
                for masks in itertools.product(range(1 << k), repeat=n):
                    check_factorization(n, rows, masks)
                    models += 1
                    input_checks += 1 << n
    bit_lists = 0
    for k in range(9):
        values = tuple(itertools.product((0, 1), repeat=k))
        codes = tuple(bits_code(value) for value in values)
        require(len(set(codes)) == len(codes), "equal-length injectivity failed")
        require(set(codes) == set(range(1 << k)), "binary enumeration failed")
        bit_lists += len(values)
    require(bits_code(()) == bits_code((0,)), "padding collision control failed")
    return {"factor_models_n_0_to_2_k_0_to_2": models,
            "factor_input_evaluations": input_checks,
            "bit_lists_lengths_0_to_8": bit_lists}


def scan(n: int, y: int, word: Sequence[tuple[int, int]]) -> dict[str, object]:
    require(0 <= y < n, "target not a register")
    identity = tuple(1 << i for i in range(n))
    raw = list(identity)
    projected = list(identity)
    donors: list[int] = []
    masks = [0] * n
    target_count = 0
    for dst, src in word:
        require(0 <= dst < n and 0 <= src < n and dst != src, "illegal gate")
        if dst == y:
            # Raw PRE-gate donor, including ALL initial input columns.
            donors.append(raw[src])
            masks[y] ^= 1 << target_count
            target_count += 1
        else:
            projected[dst] ^= projected[src]
            masks[dst] ^= masks[src]
        raw[dst] ^= raw[src]
        difference = tuple(a ^ b for a, b in zip(raw, projected))
        require(len(donors) == target_count, "donor occurrence count")
        require(tuple(combine(donors, c) for c in masks) == difference,
                "prefix row certificate failed")
        require(raw[y] == (identity[y] ^ xor_all(donors)), "target telescope failed")
    return {"raw": tuple(raw), "projected": tuple(projected),
            "donors": tuple(donors), "masks": tuple(masks), "m": target_count}


def restored_case(name: str, n: int, y: int, word: Sequence[tuple[int, int]],
                  expected_outputs: int) -> dict[str, object]:
    result = scan(n, y, word)
    identity = tuple(1 << i for i in range(n))
    raw = result["raw"]
    projected = result["projected"]
    donors = result["donors"]
    masks = result["masks"]
    m = result["m"]
    require(raw == identity, name + ": not restored")
    require(isinstance(projected, tuple) and isinstance(donors, tuple)
            and isinstance(masks, tuple) and isinstance(m, int), "internal types")
    defect = tuple(a ^ b for a, b in zip(identity, projected))
    if m == 0:
        require(projected == identity, name + ": zero target projection")
        image_size = len({action(defect, x) for x in range(1 << n)})
        require(image_size == 1, name + ": zero image not singleton")
        bound = 1
    else:
        require(xor_all(donors) == 0, name + ": nonzero donor sum")
        retained = donors[1:]
        require(len(retained) == m - 1, name + ": wrong tail length")
        all_tail_bits = (1 << len(retained)) - 1
        reduced = tuple((c >> 1) ^ (all_tail_bits if c & 1 else 0) for c in masks)
        require(tuple(combine(retained, c) for c in reduced) == defect,
                name + ": wrong reduced row certificate")
        image_size = check_factorization(n, retained, reduced)
        bound = 1 << (m - 1)
    require(image_size == expected_outputs, name + ": unexpected exact small image")
    return {"name": name, "n": n, "target_writes": m,
            "actual_output_count": image_size, "upper_bound": bound}


def check_words() -> list[dict[str, object]]:
    feedback = [(1, 0), (0, 1)] * 3
    commutator = [(2, 0), (1, 2), (2, 0), (1, 2), (1, 0)]
    cases = [
        restored_case("feedback", 2, 1, feedback, 2),
        restored_case("commutator", 3, 2, commutator, 2),
        restored_case("nonempty_zero", 3, 2, [(0, 2), (0, 2)], 1),
        restored_case("empty_one_register", 1, 0, [], 1),
        restored_case("repeated_donors", 2, 1, [(1, 0), (1, 0)], 1),
        restored_case("feedback_with_spectators", 4, 3, [(3, 0), (0, 3)] * 3, 2),
    ]
    result = scan(3, 2, commutator)
    proj = result["projected"]
    require(isinstance(proj, tuple), "internal projected type")
    defect = tuple((1 << r) ^ proj[r] for r in range(3))
    transposed = tuple(sum(((defect[r] >> c) & 1) << r for r in range(3))
                       for c in range(3))
    require(action(defect, 1) == 2, "output/input orientation witness failed")
    require(action(defect, 1) != action(transposed, 1), "transpose failure control")
    result = scan(2, 1, feedback)
    proj = result["projected"]
    donors = result["donors"]
    require(isinstance(proj, tuple) and isinstance(donors, tuple), "internal feedback type")
    defect = tuple((1 << r) ^ proj[r] for r in range(2))
    require(action(defect, 2) == 1 and action(defect, 0) == 0, "dirty target witness")
    require(action(defect, 0) == action(defect, 1), "same-output witness")
    require(bits_code(measurements(donors[1:], 0)) !=
            bits_code(measurements(donors[1:], 1)), "noncanonical measurements control")
    chronology = scan(3, 2, [(0, 2), (2, 1), (1, 0)])["projected"]
    forward = scan(3, 2, [(0, 2), (1, 0)])["raw"]
    reverse = scan(3, 2, [(1, 0), (0, 2)])["raw"]
    require(chronology == forward and chronology != reverse,
            "chronological projection failure control")
    return cases


def main() -> None:
    summary = {
        "status": "PASS: independent small exact checks only; NOT a Lean kernel replay",
        "python": platform.python_version(),
        "checks": check_general_small(),
        "word_fixtures": check_words(),
        "controls": ["transpose changes observed action", "dirty target cannot be cleaned",
                     "same output can have different input measurement codes",
                     "unequal-length binary lists can share a code",
                     "retained-gate order cannot be reversed"],
    }
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
