#!/usr/bin/env python3
"""Exact subspace audit of PR2111's anti-Fano exchange proof. Apache-2.0."""
# Copyright 2026 Nick Petalas
import hashlib
import itertools
import json
import math
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
CONFIG_SHA256 = "670ed90924b601ade22f0d4adaff46d1667e5449326a0f7ba7b88dd8f5906f93"

type Config = list[list[list[int]]]
type Incidence = tuple[tuple[bool, ...], ...]
type ColumnOption = tuple[int, int, tuple[int, ...]]
type Census = tuple[int, int, list[int] | None]


# The boolean is an assertion predicate, not a behavior-selection flag.
def require(condition: bool | int, message: str) -> None:  # noqa: FBT001
    """Reject a failed boundary check or mathematical obligation, including under -O."""
    if not condition:
        raise ValueError(message)


def load_configuration(payload: bytes) -> Config:
    """Parse only the pinned, capacity-bounded twelve-line configuration."""
    require(len(payload) <= 4096, "configuration capacity")
    require(hashlib.sha256(payload).hexdigest() == CONFIG_SHA256, "configuration pin")
    config = json.loads(payload)
    require(len(config) == 12, "twelve lines required")
    for pair in config:
        require(len(pair) == 2 and all(len(v) == 3 for v in pair), "vector shape")
        p, q = pair
        require(all(type(x) is int and abs(x) == 1 for x in p), "point support")
        require(all(type(x) is int and x in (-1, 0, 1) for x in q), "line entries")
        require(sum(x != 0 for x in q) == 2 and dot(p, q) != 0, "line support/diagonal")
    return config


def dot(a: list[int], b: list[int]) -> int:
    """Compute an exact integer inner product with equal-length operands."""
    return sum(x * y for x, y in zip(a, b, strict=True))


def binary_rank(vectors: list[int]) -> int:
    """Eliminate at most twelve vectors of at most twelve bits, without recursion."""
    require(len(vectors) <= 12 and all(0 <= x < 4096 for x in vectors), "rank capacity")
    pivots = [0] * 12
    for original in vectors:
        vector = original
        for bit in range(11, -1, -1):
            if not (vector >> bit) & 1:
                continue
            if pivots[bit]:
                vector ^= pivots[bit]
            else:
                pivots[bit] = vector
                break
    return sum(x != 0 for x in pivots)


def incidence(config: Config) -> Incidence:
    """Derive all optional off-diagonal entries directly from rational orthogonality."""
    return tuple(tuple(t != s and dot(config[t][0], config[s][1]) == 0
                       for s in range(12)) for t in range(12))


def block_columns(config: Config, j: int) -> tuple[int, ...]:
    """Return the column support of coordinate j."""
    return tuple(s for s in range(12) if config[s][1][j] != 0)


def triangular_pivot(allowed: Incidence, columns: tuple[int, ...]) -> tuple[int, ...]:
    """Find a principal unit upper-triangular minor valid for every admissible B."""
    for pivot in itertools.permutations(columns, 3):
        if all(not allowed[t][s] for i, t in enumerate(pivot) for s in pivot[:i]):
            return pivot
    message = "no universal rank-three minor"
    raise ValueError(message)


def column_options(allowed: Incidence, s: int) -> ColumnOption:
    """List one column's complete alphabet and mandatory-bit constraint."""
    free = tuple(t for t in range(12) if allowed[t][s])
    require(len(free) <= 6, "column alphabet exceeds 64")
    values = tuple((1 << s) | sum(((mask >> i) & 1) << t for i, t in enumerate(free))
                   for mask in range(1 << len(free)))
    fixed = 4095 ^ sum(1 << t for t in free)
    return fixed, 1 << s, values


def column_census(options: tuple[ColumnOption, ...], basis_indices: tuple[int, ...]) -> Census:
    """Count all rank-three completions, retaining only the first as a witness.

    The caller supplies three columns with a universal nonsingular minor.
    Each matrix therefore has exactly one tuple of those three basis columns.
    """
    require(3 <= len(options) <= 8 and len(basis_indices) == 3
            and len(set(basis_indices)) == 3, "census shape")
    require(all(0 <= i < len(options) for i in basis_indices), "basis indices")
    require(all(1 <= len(o[2]) <= 64 for o in options), "census alphabet")
    rest = tuple(i for i in range(len(options)) if i not in basis_indices)
    trials = completions = 0
    witness = None
    for basis in itertools.product(*(options[i][2] for i in basis_indices)):
        trials += 1
        a, b, c = basis
        space = (0, a, b, c, a ^ b, a ^ c, b ^ c, a ^ b ^ c)
        require(len(set(space)) == 8, "basis is not independent")
        choices = []
        for i in rest:
            fixed, diagonal, _ = options[i]
            matches = tuple(x for x in space if x & fixed == diagonal)
            if not matches:
                break
            choices.append(matches)
        if len(choices) != len(rest):
            continue
        completions += math.prod(len(values) for values in choices)
        if witness is None:
            by_index = dict(zip(basis_indices, basis, strict=True))
            by_index.update((i, values[0]) for i, values in zip(rest, choices, strict=True))
            witness = [by_index[i] for i in range(len(options))]
    require(trials == math.prod(len(options[i][2]) for i in basis_indices),
            "column census coverage")
    return trials, completions, witness


def row_census(config: Config, columns: tuple[int, ...], pivot: tuple[int, ...]) -> Census:
    """Run the transpose census using eight-bit rows, sets and row-span doubling."""
    require(len(columns) == 8 and len(pivot) == 3 and len(set(pivot)) == 3,
            "row census shape")
    choices = []
    for t in range(12):
        diagonal = sum(1 << i for i, s in enumerate(columns) if t == s)
        forbidden = sum(1 << i for i, s in enumerate(columns)
                        if t != s and dot(config[t][0], config[s][1]) != 0)
        choices.append(frozenset(x for x in range(256)
                                if x & forbidden == 0 and x & diagonal == diagonal))
    require(all(len(values) == 16 for values in choices), "row alphabet")
    trials = completions = 0
    first = None
    for rows in itertools.product(*(choices[t] for t in pivot)):
        trials += 1
        space = {0}
        for row in rows:
            space |= {x ^ row for x in tuple(space)}
        require(len(space) == 8, "row basis is not independent")
        matches = []
        for t in range(12):
            possible = {rows[pivot.index(t)]} if t in pivot else space & choices[t]
            if not possible:
                break
            matches.append(possible)
        if len(matches) != 12:
            continue
        completions += math.prod(len(values) for values in matches)
        if first is None:
            first = [min(values) for values in matches]
    require(trials == 4096, "row census coverage")
    return trials, completions, first


def as_rows(columns: list[int]) -> list[int]:
    """Transpose the packed column witness for entrywise oracle comparison."""
    return [sum(((value >> t) & 1) << i for i, value in enumerate(columns))
            for t in range(12)]


def exchange_properties(
    config: Config, j: int, columns: tuple[int, ...], values: list[int],
) -> dict[str, list[int]]:
    """Check every finite premise used by the credited projection argument."""
    require(binary_rank(values) == 3, "rank-three witness")
    missing = tuple(t for t in range(12) if config[t][1][j] == 0)
    require(all(all(not ((value >> t) & 1) for t in missing) for value in values),
            "missing-class rows must vanish")
    ranks = []
    for k in range(3):
        if k != j:
            group = [value for s, value in zip(columns, values, strict=True)
                     if config[s][1][k] == 0]
            ranks.append(binary_rank(group))
    require(ranks == [3, 3], "two class spaces must both equal the rank-three union")
    pair = next(((a, b) for a, b in itertools.combinations(missing, 2)
                 if dot(config[a][0], config[b][1]) != 0
                 and dot(config[b][0], config[a][1]) != 0), None)
    require(pair is not None, "missing-class universal identity minor")
    return {"class_space_ranks": ranks, "zero_rows": list(missing),
            "projection_identity_minor": list(pair)}


def block_ranks(config: Config, rows: list[int]) -> list[int]:
    """Compute all three raw coordinate-block ranks of a packed matrix."""
    return [binary_rank([sum(((row >> s) & 1) << i
                             for i, s in enumerate(block_columns(config, j)))
                         for row in rows]) for j in range(3)]


def validate_upper(config: Config, rows: list[int]) -> list[int]:
    """Reject inadmissible or non-cost-twelve upper-bound witnesses."""
    allowed = incidence(config)
    require(len(rows) == 12 and all(type(x) is int and 0 <= x < 4096 for x in rows),
            "upper witness shape")
    for t in range(12):
        require((rows[t] >> t) & 1, "upper witness diagonal")
        require(all(not ((rows[t] >> s) & 1) or t == s or allowed[t][s]
                    for s in range(12)), "upper witness forbidden entry")
    ranks = block_ranks(config, rows)
    require(ranks == [4, 4, 4], "upper witness must have cost twelve")
    return ranks


def audit(config: Config) -> dict[str, object]:
    """Reconstruct both censuses, the exchange premises and a sharp upper bound."""
    allowed = incidence(config)
    require(sum(map(sum, allowed)) == 72, "incidence count")
    blocks = []
    for j in range(3):
        columns = block_columns(config, j)
        require(len(columns) == 8, "eight columns per block")
        pivot = triangular_pivot(allowed, columns)
        options = tuple(column_options(allowed, s) for s in columns)
        indices = tuple(columns.index(s) for s in pivot)
        trials, count, values = column_census(options, indices)
        rtrials, rcount, rows = row_census(config, columns, pivot)
        require((trials, count, rtrials, rcount) == (262144, 1, 4096, 1), "uniqueness census")
        if values is None or rows is None:
            message = "missing census witness"
            raise ValueError(message)
        require(as_rows(values) == rows, "row/column census disagreement")
        properties = exchange_properties(config, j, columns, values)
        blocks.append({"coordinate": j, "columns": list(columns), "triangular_minor": list(pivot),
                       "column_trials": trials, "row_trials": rtrials, "completions": count,
                       "unique_columns": values, **properties})
    upper = [9, 258, 36, 9, 2064, 36, 576, 1152, 258, 576, 1152, 2064]
    ranks = validate_upper(config, upper)
    full_rows = [(1 << t) | sum(1 << s for s in range(12) if allowed[t][s])
                 for t in range(12)]
    return {"lines": 12, "incidences": 72, "blocks": blocks,
            "lower_bound": min(3 * 4, 3 + 2 * (3 + 2)),
            "rank_three_case_floor": 3 + 2 * (3 + 2),
            "upper_rows": upper, "upper_ranks": ranks,
            "full_pattern_ranks": block_ranks(config, full_rows)}


def compare_report(actual: object, expected: object) -> None:
    """Reject any difference between reconstructed evidence and the stored receipt."""
    require(actual == expected, "receipt mismatch")


def main() -> None:
    """Run the bounded standalone audit without writing artifacts."""
    config_path = PACKAGE / "CONFIGURATION.json"
    expected_path = PACKAGE / "EXPECTED.json"
    require(config_path.stat().st_size <= 4096, "configuration capacity")
    require(expected_path.stat().st_size <= 16384, "receipt capacity")
    config = load_configuration(config_path.read_bytes())
    report = audit(config)
    compare_report(report, json.loads(expected_path.read_bytes()))
    print("PASS_ANTIFANO_SUBSPACE_AUDIT minimum=12 blocks=3 "
          "column_trials=786432 row_trials=12288 unique_rank3=1,1,1 no_new_kappa")


if __name__ == "__main__":
    main()
