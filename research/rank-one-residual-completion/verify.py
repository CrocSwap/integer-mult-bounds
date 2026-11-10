"""Finite corroboration of the new r>=3 rank-one-residual theorem.

Produced by Nick Petalas. Apache-2.0. Standard library only.
No predecessor executable or scientific receipt is imported or replayed.
"""

import hashlib
import importlib.util
import json
from pathlib import Path


PACKAGE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("rank_one_completion", PACKAGE / "completion.py")
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("cannot load local completion module")
C = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(C)


def check(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def coordinates(x: int, dimension: int) -> list[int]:
    return [(x >> j) & 1 for j in range(dimension)]


def dense_pair(x: list[int], y: list[int], n: int) -> int:
    return sum(x[j] * y[n + j] + x[n + j] * y[j] for j in range(n)) % 2


def dense_word(n: int, word: tuple[int, ...]) -> list[list[int]]:
    columns = [coordinates(1 << j, 2 * n) for j in range(2 * n)]
    for axis in word:
        a = coordinates(axis, 2 * n)
        for column in columns:
            if dense_pair(column, a, n):
                for j in range(2 * n):
                    column[j] ^= a[j]
    return columns


def dense_apply(columns: list[list[int]], x: int) -> int:
    dimension = len(columns)
    bits = coordinates(x, dimension)
    return sum((sum(bits[i] * columns[i][j] for i in range(dimension)) % 2) << j
               for j in range(dimension))


def dense_rank(matrix: list[list[int]]) -> int:
    rows = [row[:] for row in matrix]
    if not rows:
        return 0
    height, width, pivot_row = len(rows), len(rows[0]), 0
    for j in range(width):
        found = next((i for i in range(pivot_row, height) if rows[i][j]), None)
        if found is None:
            continue
        rows[pivot_row], rows[found] = rows[found], rows[pivot_row]
        for i in range(pivot_row + 1, height):
            if rows[i][j]:
                rows[i] = [a ^ b for a, b in zip(rows[i], rows[pivot_row])]
        pivot_row += 1
        if pivot_row == height:
            break
    return pivot_row


def fixture(rows: tuple[int, ...]) -> tuple[int, tuple[int, ...], tuple[int, ...]]:
    """Realize any r-square residual matrix, with two prescribed spectators."""
    r = len(rows)
    n = 2 * r + 1
    source = tuple(1 << i for i in range(r))
    displacement = []
    for j in range(r):
        first_f = sum(((rows[i] >> j) & 1) << (n + i) for i in range(r))
        second_f = sum(((rows[i] >> j) & 1) << (n + r + i) for i in range(r))
        displacement.append((1 << (r + j)) ^ first_f ^ second_f)
    image = tuple(x ^ d for x, d in zip(source, displacement))
    fixed = (1 << (2 * r), 1 << (n + 2 * r))
    return n, source + fixed, image + fixed


def compact_fixture(r: int, spectators: bool = True
                    ) -> tuple[int, tuple[int, ...], tuple[int, ...]]:
    """Use x^(r-1)+x+1 to avoid eigenvalues zero and one on the e block."""
    k = r - 1
    n = r + int(spectators)
    source = tuple(1 << i for i in range(k)) + (1 << (n + k),)
    columns = tuple(1 << (i + 1) for i in range(k - 1)) + (3,)
    image = tuple((1 << i) ^ columns[i] for i in range(k))
    image += ((1 << (n + k)) ^ (1 << k),)
    if spectators:
        fixed = (1 << r, 1 << (n + r))
        source, image = source + fixed, image + fixed
    return n, source, image


def check_case(n: int, source: tuple[int, ...], image: tuple[int, ...], r: int
               ) -> tuple[int, ...]:
    word = C.complete(n, source, image)
    check(len(word) == 2 * r - 1, "wrong exact length")
    check(all(0 < a < 1 << (2 * n) for a in word), "axis left original space")
    columns = dense_word(n, word)
    check(tuple(dense_apply(columns, x) for x in source) == image,
          "literal dense word failed prescribed map or fixed spectators")
    for i, x in enumerate(columns):
        for j, y in enumerate(columns):
            expected = int((i < n and j == i + n) or (j < n and i == j + n))
            check(dense_pair(x, y, n) == expected, "full word is not symplectic")
    delta = [[value ^ int(i == j) for j, value in enumerate(column)]
             for i, column in enumerate(columns)]
    check(dense_rank(delta) == 2 * r - 1, "full displacement does not attain bound")
    check(dense_rank([coordinates(x ^ y, 2 * n) for x, y in zip(source, image)]) == r,
          "fixture has wrong displacement rank")
    return word


def exhaustive_forms() -> tuple[int, int, int]:
    cases = 0
    off_diagonal = 0
    omissions = 0
    for r in range(3, 6):
        for p in range(1, 1 << r):
            for q in range(1, 1 << r):
                rows = tuple(q if (p >> i) & 1 else 0 for i in range(r))
                n, source, image = fixture(rows)
                word = check_case(n, source, image, r)
                cases += 1
                if not p & q:
                    off_diagonal += 1
                if p == 1 and q in (1, 2):
                    for j in range(len(word)):
                        shorter = word[:j] + word[j + 1:]
                        columns = dense_word(n, shorter)
                        check(tuple(dense_apply(columns, x) for x in source) != image,
                              "a one-turn omission still realizes the contract")
                        omissions += 1
    return cases, off_diagonal, omissions


def larger_cases() -> tuple[int, int]:
    cases = 0
    omissions = 0
    for r in range(3, 13):
        n, source, image = compact_fixture(r)
        for seed in range(5):
            limit = (1 << (2 * n)) - 1
            axes = tuple(((seed + 1) * (j + 3) * 7919) % limit + 1
                         for j in range(8)) if seed else ()
            change = dense_word(n, axes)
            moved_source = tuple(dense_apply(change, x) for x in source)
            moved_image = tuple(dense_apply(change, y) for y in image)
            word = check_case(n, moved_source, moved_image, r)
            cases += 1
            if seed == 1:
                for j in range(len(word)):
                    columns = dense_word(n, word[:j] + word[j + 1:])
                    check(tuple(dense_apply(columns, x) for x in moved_source) != moved_image,
                          "a conjugated one-turn omission still realizes the contract")
                    omissions += 1
    # A rank-three example already fits the six-dimensional original space.
    n, source, image = compact_fixture(3, spectators=False)
    check_case(n, source, image, 3)
    # Exercise the public dimension cap while keeping displacement rank three.
    n, source, image = compact_fixture(3)
    cap = C.MAX_QUBITS
    mask = (1 << n) - 1
    cap_source = tuple((x & mask) | ((x >> n) << cap) for x in source)
    cap_image = tuple((x & mask) | ((x >> n) << cap) for x in image)
    check_case(cap, cap_source, cap_image, 3)
    return cases + 2, omissions


def rejecting_controls() -> int:
    n, source, image = compact_fixture(3)
    invalid = [
        (0, source, image),
        (C.MAX_QUBITS + 1, source, image),
        (True, source, image),
        (n, list(source), image),
        (n, source, image[:-1]),
        (n, (True,) + source[1:], image),
        (n, ((1 << (2 * n)),) + source[1:], image),
        (n, source + (source[0],), image + (image[0],)),
        (n, source, (0,) + image[1:]),
        (n, source, (image[0] ^ (1 << (n + 1)),) + image[1:]),
        (n, source, source),
        fixture((1, 2, 0)),
        fixture((2, 1, 0)),
    ]
    for args in invalid:
        try:
            C.complete(*args)
        except ValueError:
            continue
        raise RuntimeError("malformed or out-of-scope contract was accepted")
    try:
        C.solve_pairings(1, ((1, 0), (1, 1)))
    except ValueError:
        return len(invalid) + 1
    raise RuntimeError("inconsistent pairing system was accepted")


def main() -> None:
    forms, off_diagonal, form_omissions = exhaustive_forms()
    larger, large_omissions = larger_cases()
    rejected = rejecting_controls()
    check(forms == sum(((1 << r) - 1) ** 2 for r in range(3, 6)),
          "rank-one form census incomplete")
    files = sorted(path for path in PACKAGE.iterdir() if path.is_file())
    receipt = {
        "status": "PASS_RANK_ONE_RESIDUAL_COMPLETION",
        "claim_type": "scoped algebraic proof with finite corroboration",
        "new_displacement_ranks": "3 through 12 in finite checks; all r in written proof",
        "exhaustive_rank_one_forms_r3_r4_r5": forms,
        "zero_diagonal_forms_requiring_sum_pivot": off_diagonal,
        "larger_and_conjugated_contracts": larger,
        "rejected_one_turn_omissions": form_omissions + large_omissions,
        "rejecting_controls": rejected,
        "source_sha256": {path.name: hashlib.sha256(path.read_bytes()).hexdigest()
                          for path in files},
        "no_new_kappa": True,
    }
    print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
