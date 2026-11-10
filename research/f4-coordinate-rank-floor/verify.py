#!/usr/bin/env python3
"""Check the nine-ray F4 rank obstruction without predecessor code."""

from collections import Counter
from hashlib import sha256
from itertools import combinations, product
import json
from pathlib import Path
import platform


GADGET = (
    (1, -1, -1, -1), (1, -1, -1, 1), (1, -1, 0, 0),
    (1, 0, -1, 0), (1, 0, 0, 0), (1, -1, 1, -1),
    (1, -1, 1, 1), (1, 0, 0, -1), (1, 0, 0, 1),
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def dot(left: tuple[int, ...], right: tuple[int, ...]) -> int:
    require(len(left) == len(right) == 4, "four real coordinates required")
    return sum(left[i] * right[i] for i in range(4))


def canonical(vector: tuple[int, ...]) -> tuple[int, ...]:
    require(len(vector) == 4 and any(vector), "nonzero four-vector required")
    sign = next(x for x in vector if x)
    return tuple(-x for x in vector) if sign < 0 else vector


def root_rays() -> tuple[tuple[int, ...], ...]:
    rays = set()
    for support in combinations(range(4), 1):
        rays.add(tuple(int(i in support) for i in range(4)))
    for support in combinations(range(4), 2):
        for sign in (-1, 1):
            rays.add(tuple(1 if i == support[0] else sign if i == support[1]
                           else 0 for i in range(4)))
    for signs in product((-1, 1), repeat=3):
        rays.add((1, *signs))
    require(len(rays) == 24, "F4 ray count")
    return tuple(sorted(rays))


def check_geometry() -> list[list[int]]:
    rays = root_rays()
    witnesses = []
    masks_expected = (0b01010, 0b01001, 0b00010, 0b00001)
    for coordinate in range(4):
        gadget = []
        for original in GADGET:
            vector = list(original)
            vector[0], vector[coordinate] = vector[coordinate], vector[0]
            gadget.append(canonical(tuple(vector)))
        require(len(set(gadget)) == 9, "nine distinct rays")
        require(all(v in rays and v[coordinate] for v in gadget), "support")
        require(all(dot(gadget[i], gadget[j]) != 0
                    for i, j in combinations(range(5), 2)), "forced I5")
        masks = tuple(sum((dot(v, gadget[j]) == 0) << j for j in range(5))
                      for v in gadget[5:])
        require(masks == masks_expected, "factor support masks")
        for i, j in ((5, 7), (6, 8), (5, 6)):
            require(dot(gadget[i], gadget[j]) != 0, "required forbidden pair")
        witnesses.append([rays.index(v) for v in gadget])
    return witnesses


def rank_basis(rows: list[int]) -> int:
    require(len(rows) == 9 and all(0 <= x < 512 for x in rows), "binary rows")
    basis = [0] * 9
    count = 0
    for original in rows:
        value = original
        for bit in range(8, -1, -1):
            if value & (1 << bit):
                if basis[bit]:
                    value ^= basis[bit]
                else:
                    basis[bit] = value
                    count += 1
                    break
    return count


def rank_elimination(rows: list[int]) -> int:
    require(len(rows) == 9 and all(0 <= x < 512 for x in rows), "binary rows")
    work = list(rows)
    pivot = 0
    for column in range(9):
        candidates = [i for i in range(pivot, 9) if work[i] >> column & 1]
        if not candidates:
            continue
        index = candidates[0]
        work[pivot], work[index] = work[index], work[pivot]
        for i in range(pivot + 1, 9):
            if work[i] >> column & 1:
                work[i] ^= work[pivot]
        pivot += 1
    return pivot


def exhaustive_binary() -> dict[str, object]:
    free = [(i, j) for i in range(9) for j in range(9)
            if i != j and dot(GADGET[i], GADGET[j]) == 0]
    require(len(free) == 18, "eighteen independent directed entries")
    rows = [1 << i for i in range(9)]
    spectrum: Counter[int] = Counter()
    witness = None
    for index in range(1 << 18):
        if index:
            bit = (index & -index).bit_length() - 1
            i, j = free[bit]
            rows[i] ^= 1 << j
        left, right = rank_basis(rows), rank_elimination(rows)
        require(left == right, "independent rank engines disagree")
        require(left >= 6, "rank below six")
        spectrum[left] += 1
        if left == 6 and witness is None:
            witness = list(rows)
    require(sum(spectrum.values()) == 262144 and witness is not None,
            "complete census and rank-six nine-ray witness")
    return {"matrices": 262144, "rank_spectrum": dict(sorted(spectrum.items())),
            "nine_ray_rank_six_rows": witness}


def factor_tuples() -> dict[str, int]:
    masks = (0b01010, 0b01001, 0b00010, 0b00001)
    domains = []
    for mask in masks:
        domains.append([(u, v) for u in range(32) for v in range(32)
                        if not (u | v) & ~mask and (u & v).bit_count() % 2])
    require([len(d) for d in domains] == [6, 6, 1, 1], "factor domains")
    failures = Counter()
    for a, b, u, v in product(*domains):
        for name, left, right in (("a_u", a, u), ("b_v", b, v), ("a_b", a, b)):
            if (left[0] & right[1]).bit_count() % 2 or (
                    right[0] & left[1]).bit_count() % 2:
                failures[name] += 1
                break
        else:
            raise AssertionError("rank-five factor tuple survives")
    require(sum(failures.values()) == 36, "all thirty-six tuples rejected")
    return dict(failures)


def controls() -> int:
    # Relax the forbidden a/b pair. This rank-five matrix now fits the gadget.
    labels = (1, 2, 4, 8, 16, 8, 8, 2, 1)
    rows = [sum(bool(x & y) << j for j, y in enumerate(labels)) for x in labels]
    require(rank_basis(rows) == rank_elimination(rows) == 5, "relaxed fixture")
    faults = [(i, j) for i in range(9) for j in range(9)
              if i != j and dot(GADGET[i], GADGET[j]) != 0 and rows[i] >> j & 1]
    require(faults == [(5, 6), (6, 5)], "exactly the removed zero pair fails")
    for i in range(9):
        require(rows[i] >> i & 1, "nonzero fixture diagonals")
    for bad in ([], [512] * 9, [-1] * 9):
        try:
            rank_basis(bad)
        except AssertionError:
            continue
        raise AssertionError("invalid rank input accepted")
    return 4


def main() -> None:
    witnesses = check_geometry()
    factors = factor_tuples()
    census = exhaustive_binary()
    checked_controls = controls()
    package = Path(__file__).resolve().parent
    names = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py")
    hashes = {name: sha256((package / name).read_bytes()).hexdigest() for name in names}
    receipt = {"status": "PASS_F4_COORDINATE_RANK_SIX", "python": platform.python_version(),
               "coordinate_witnesses": witnesses, "factor_tuple_failures": factors,
               "binary_census": census, "controls": checked_controls,
               "scope": "all-field written lower bound; complete nine-ray binary census",
               "sha256": hashes}
    print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
