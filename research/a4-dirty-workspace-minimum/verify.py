#!/usr/bin/env python3
"""Corroborate tight-rank compression without replaying predecessor censuses."""

from __future__ import annotations

import hashlib
import itertools
import json
import sys
from pathlib import Path


def require(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError(message)


def mul4(a: int, b: int) -> int:
    value = (a & 1) * b
    if a & 2:
        value ^= (b << 1) ^ (7 if b & 2 else 0)
    return value


def rank4(rows: list[list[int]]) -> int:
    require(1 <= len(rows) <= 8, "row bound")
    width = len(rows[0])
    require(1 <= width <= 8, "column bound")
    require(all(len(row) == width for row in rows), "ragged matrix")
    require(
        all(type(v) is int and 0 <= v < 4 for row in rows for v in row),
        "invalid field entry",
    )
    work = [row[:] for row in rows]
    pivots = 0
    for col in range(width):
        candidates = [i for i in range(pivots, len(work)) if work[i][col]]
        if not candidates:
            continue
        p = candidates[0]
        work[pivots], work[p] = work[p], work[pivots]
        inverse = (0, 1, 3, 2)[work[pivots][col]]
        require(mul4(work[pivots][col], inverse) == 1, "invalid pivot inverse")
        work[pivots] = [mul4(inverse, v) for v in work[pivots]]
        for i in range(len(work)):
            if i != pivots and work[i][col]:
                scale = work[i][col]
                work[i] = [
                    v ^ mul4(scale, w)
                    for v, w in zip(work[i], work[pivots], strict=True)
                ]
        pivots += 1
    return pivots


def saturation_checks() -> dict[str, int]:
    counts = {"triples": 0, "full_rank": 0, "compatible": 0}
    targets = ((0, 2, 3, 2, 0), (3, 0, 1, 2, 0))
    for columns in itertools.product(range(1, 32), repeat=3):
        counts["triples"] += 1
        rows = [[(x >> i) & 1 for x in columns] for i in range(5)]
        if rank4(rows) != 3:
            continue
        counts["full_rank"] += 1
        # A separate binary oracle enumerates the entire column span.
        span = {0}
        for x in columns:
            span |= {v ^ x for v in tuple(span)}
        for target in targets:
            augmented = [
                row + [target[i] if i == j else 0 for j in range(5)]
                for i, row in enumerate(rows)
            ]
            compatible = rank4(augmented) == 3
            oracle = all((1 << i) in span for i, v in enumerate(target) if v)
            require(compatible == oracle, "field/binary span disagreement")
            if compatible:
                support = sum(1 << i for i, v in enumerate(target) if v)
                require(all(x & ~support == 0 for x in columns), "support escape")
                counts["compatible"] += 1
    require(counts["triples"] == 31**3, "incomplete domain")
    require(counts["full_rank"] == 31 * 30 * 28, "basis count")
    require(counts["compatible"] == 2 * 7 * 6 * 4, "target basis count")
    return counts


def group() -> tuple[list[list[int]], int, int]:
    perms = [
        p
        for p in itertools.permutations(range(4))
        if sum(p[i] > p[j] for i in range(4) for j in range(i + 1, 4)) % 2 == 0
    ]
    table = [
        [perms.index(tuple(p[q[i]] for i in range(4))) for q in perms] for p in perms
    ]
    require(len(perms) == 12, "A4 size")
    return table, perms.index((1, 2, 0, 3)), perms.index((1, 3, 2, 0))


def apply_word(
    word: list[tuple[int, int, int]], roles: int, basis: int, table: list[list[int]]
) -> tuple[int, ...]:
    require(4 <= roles <= 7 and 0 <= basis < 12 * roles, "action bounds")
    require(len(word) <= 8, "word bound")
    state = [0] * roles
    state[basis // 12] = 1 << (basis % 12)
    for x, y, label in word:
        require(0 < x < 16 and 0 < y < 1 << roles, "coupling bounds")
        require(
            (x & y).bit_count() % 2 == 1 and 0 <= label < 12,
            "rank-one idempotent contract",
        )
        source = 0
        for j in range(roles):
            if y >> j & 1:
                source ^= state[j]
        moved = sum(1 << table[label][j] for j in range(12) if source >> j & 1)
        for i in range(4):
            if x >> i & 1:
                state[i] ^= source ^ moved
    return tuple(state)


def restriction_checks() -> dict[str, int]:
    table, a, b = group()
    result = {"factors": 0, "words": 0, "basis_columns": 0, "dirty_reads": 0}
    for roles in range(4, 8):
        factors = [
            (x, y, g)
            for x in range(1, 16)
            for y in range(1, 1 << roles)
            if (x & y).bit_count() % 2
            for g in (a, b)
        ]
        result["factors"] += len(factors)
        words = [[f] for f in factors]
        words += [
            [
                factors[(37 * seed + 19 * j + j * j) % len(factors)]
                for j in range(2 + seed % 7)
            ]
            for seed in range(64)
        ]
        for word in words:
            restricted = [(x, y & 15, g) for x, y, g in word]
            result["words"] += 1
            result["dirty_reads"] += sum(y >> 4 != 0 for _, y, _ in word)
            for basis in range(12 * roles):
                full = apply_word(word, roles, basis, table)
                tail = tuple(
                    (1 << (basis % 12)) if basis // 12 == i else 0
                    for i in range(4, roles)
                )
                require(full[4:] == tail, "dirty output changed")
                if basis < 48:
                    small = apply_word(restricted, 4, basis, table)
                    require(full[:4] == small, "restriction not multiplicative")
                result["basis_columns"] += 1
    require(result["dirty_reads"] > 0, "dirty reads missing")
    return result


def direct_checks() -> int:
    table, a, b = group()
    identity = next(i for i in range(12) if table[i] == list(range(12)))
    # Chronological left action reverses displayed group products.
    word = [
        (1, 1, a),
        (2, 2, b),
        (4, 4, a),
        (4, 4, b),
        (4, 4, b),
        (4, 4, a),
        (8, 8, b),
        (8, 8, a),
    ]
    c = table[table[table[a][b]][table[a][a]]][table[b][b]]
    d = table[a][b]
    columns = 0
    for roles in range(4, 8):
        labels = [a, b, c, d] + [identity] * (roles - 4)
        for basis in range(12 * roles):
            expected = [0] * roles
            expected[basis // 12] = 1 << table[labels[basis // 12]][basis % 12]
            require(
                apply_word(word, roles, basis, table) == tuple(expected),
                "eight-call boundary",
            )
            columns += 1
    return columns


def controls() -> int:
    # One slack term permits dirty-column cancellation; each summand is nonzero.
    xs = (1 | 16, 2, 4, 16)
    vs = ((1, 0, 0), (0, 2, 0), (0, 0, 3), (1, 0, 0))
    total = [[0] * 3 for _ in range(5)]
    for x, row in zip(xs, vs, strict=True):
        for i in range(5):
            for j in range(3):
                if x >> i & 1:
                    total[i][j] ^= row[j]
    require(rank4(total) == 3 and total[4] == [0, 0, 0], "slack control")
    require(any(x & 16 for x in xs), "slack dirty column")
    rejected = 0
    for rows in ([], [[1, 0], [1]], [[4]], [[True]]):
        try:
            rank4(rows)
        except ValueError:
            rejected += 1
    table, a, _ = group()
    identity = next(i for i in range(12) if table[i] == list(range(12)))
    expected = ((1 << a) ^ (1 << identity), 0, 0, 0, 1 << identity)
    require(
        apply_word([(1, 17, a)], 5, 48 + identity, table) == expected,
        "dirty input must contribute to target",
    )
    for word in ([(1, 2, a)], [(16, 16, a)], [(1, 1, 12)]):
        try:
            apply_word(word, 5, 0, table)
        except ValueError:
            rejected += 1
    require(rejected == 7, "boundary rejection missing")
    return rejected + 2


def main() -> None:
    require(sys.argv[1:] in ([], ["--emit"]), "usage: verify.py [--emit]")
    require(mul4(2, 2) == 3 and mul4(2, 3) == 1, "field polynomial")
    for a, b, c in itertools.product(range(4), repeat=3):
        require(mul4(a, mul4(b, c)) == mul4(mul4(a, b), c), "field associativity")
        require(mul4(a, b ^ c) == mul4(a, b) ^ mul4(a, c), "field distributivity")
    result = {
        "saturation": saturation_checks(),
        "restriction": restriction_checks(),
        "direct_basis_columns": direct_checks(),
        "controls": controls(),
    }
    package = Path(__file__).resolve().parent
    names = (
        "PROOF.md",
        "README.md",
        "SOURCES.json",
        "TASK.json",
        "VERIFY.json",
        "verify.py",
    )
    require(
        all((package / name).stat().st_size <= 131072 for name in names),
        "package file size bound",
    )
    hashes = {
        name: hashlib.sha256((package / name).read_bytes()).hexdigest()
        for name in names
    }
    receipt = {"result": result, "sha256": hashes}
    canonical = json.dumps(receipt, sort_keys=True, indent=2) + "\n"
    if sys.argv[1:] == ["--emit"]:
        print(canonical, end="")
        return
    print(canonical, end="")
    print("PASS_A4_DIRTY_WORKSPACE_MINIMUM")


if __name__ == "__main__":
    main()
