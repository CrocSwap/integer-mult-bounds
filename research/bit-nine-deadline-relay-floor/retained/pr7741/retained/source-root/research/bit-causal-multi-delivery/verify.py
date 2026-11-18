#!/usr/bin/env python3
"""Verify the fixed-library direct-delivery obstruction on the selected BIT word."""

from collections import Counter
from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from fractions import Fraction
from hashlib import sha256
from itertools import combinations
from math import lcm
from pathlib import Path
import gzip
import json

ROOT = Path(__file__).resolve().parents[2]
WORD = ROOT / "research/paired-query-only-bit/retained/inputs/BIT-NATIVE-WORD.json.gz"
WORD_SHA256 = "51203e7fc75ba10bd3ac3f8e675759f47e13d262bea66b6600d1e515095cad78"
AMBIENT = 8
CHARTS = 636
PUBLIC = 659
OWNED = 237
STEPS = 34_137


@dataclass(frozen=True)
class Arrival:
    clock: int
    source: int
    destination: int
    row: int


def require(ok: bool, problem: str) -> None:
    if not ok:
        raise ValueError(problem)


def integer_row(raw: list[int | str]) -> tuple[int, ...]:
    require(len(raw) == AMBIENT, "frame row width")
    rational = tuple(map(Fraction, raw))
    scale = lcm(*(x.denominator for x in rational))
    return tuple(int(x * scale) for x in rational)


def rational_rank(rows: list[tuple[int, ...]]) -> int:
    basis: dict[int, tuple[Fraction, ...]] = {}
    for row in rows:
        value = list(map(Fraction, row))
        for pivot, donor in basis.items():
            if value[pivot]:
                factor = value[pivot]
                value = [a - factor * b for a, b in zip(value, donor, strict=True)]
        for pivot, coefficient in enumerate(value):
            if coefficient:
                basis[pivot] = tuple(x / coefficient for x in value)
                break
    return len(basis)


def orthogonal(v: tuple[int, ...], w: tuple[int, ...]) -> bool:
    return sum(a * b for a, b in zip(v, w, strict=True)) == 0


def nested_donors(frames: dict) -> tuple[list[int], list[list[tuple[int, int]]]]:
    require(len(frames) == CHARTS, "chart count")
    dims, spans, complements = [], [], []
    for chart in range(CHARTS):
        frame = frames[str(chart)]
        dim = frame["dim"]
        span = [integer_row(row) for row in frame["B"]]
        complement = [integer_row(row) for row in frame["A"]]
        require(len(span) == rational_rank(span) == dim, "frame basis")
        require(len(complement) == rational_rank(complement) == AMBIENT - dim,
                "complement basis")
        require(all(orthogonal(v, a) for v in span for a in complement),
                "complement orthogonality")
        dims.append(dim)
        spans.append(span)
        complements.append(complement)

    containing = {
        row: {i for i, comp in enumerate(complements) if all(orthogonal(row, a) for a in comp)}
        for row in {v for span in spans for v in span}
    }
    donors: list[list[tuple[int, int]]] = [[] for _ in range(CHARTS)]
    for small, span in enumerate(spans):
        supersets = set.intersection(set(range(CHARTS)), *(containing[v] for v in span))
        for large in sorted(supersets):
            rank = dims[large] - dims[small]
            if small == large:
                continue
            require(rank > 0, "distinct frames with equal spans")
            donors[small].append((large, rank))
            donors[large].append((small, rank))
    return dims, donors


def entrance(word: dict, reverse: bool) -> list[int]:
    return word["final" if reverse else "start"]


def arrivals(word: dict, reverse: bool) -> Iterator[Arrival]:
    charts: list[int | None] = entrance(word, reverse) + [None] * OWNED
    rows = [1 << role for role in range(PUBLIC)] + [0] * OWNED
    instructions = reversed(word["program"]) if reverse else word["program"]
    for clock, (op, role, *args) in enumerate(instructions):
        require(0 <= role < len(rows), "lane index")
        if op == "MOVE":
            source, destination = args[::-1] if reverse else args
            require(charts[role] == source, "MOVE source chart")
            yield Arrival(clock, source, destination, rows[role])
            charts[role] = destination
        elif op == "ADD":
            donor, chart = args
            require(0 <= donor < len(rows) and donor != role, "ADD donor")
            require(charts[role] == charts[donor] == chart, "ADD chart")
            if reverse:
                rows[donor] ^= rows[role]
            else:
                rows[role] ^= rows[donor]
        elif op == "SWAP":
            (other,) = args
            require(0 <= other < len(rows) and other != role, "SWAP lane")
            charts[role], charts[other] = charts[other], charts[role]
            rows[role], rows[other] = rows[other], rows[role]
        elif op in ("INIT", "CLEAR"):
            (chart,) = args
            require(role >= PUBLIC, "lifetime operation on public lane")
            if (op == "INIT") != reverse:
                require(charts[role] is None, "INIT on a live lane")
                charts[role] = chart
            else:
                require(charts[role] == chart, "CLEAR chart")
                charts[role] = None
            rows[role] = 0
        else:
            raise ValueError(f"unknown instruction {op!r}")
    require(charts == entrance(word, not reverse) + [None] * OWNED, "exit charts")


def residue(row: int, basis: dict[int, int]) -> int:
    # Each XOR clears the leading bit, so at most PUBLIC XORs are possible.
    for _ in range(PUBLIC):
        if not row:
            return 0
        pivot = row.bit_length() - 1
        if pivot not in basis:
            return row
        row ^= basis[pivot]
    require(row == 0, "row exceeds the public input width")
    return row


def insert(row: int, basis: dict[int, int]) -> None:
    remaining = residue(row, basis)
    if remaining:
        basis[remaining.bit_length() - 1] = remaining


def span_basis(rows: Iterable[int], initial: dict[int, int]) -> dict[int, int]:
    basis = initial.copy()
    for row in rows:
        insert(row, basis)
    return basis


def quotient(row: int, destination: list[tuple[int, int]]) -> int:
    for pivot, donor in destination:
        if row >> pivot & 1:
            row ^= donor
    return row


def affordable_bundles(donors: list[tuple[int, int]], old_rank: int) -> Iterator[tuple[int, ...]]:
    for chart, rank in donors:
        if rank < old_rank:
            yield (chart,)
    for (a, a_rank), (b, b_rank) in combinations(donors, 2):
        if a_rank + b_rank < old_rank:
            yield a, b


def check_small_bundles(
    arrival: Arrival, old_rank: int, donors: list[tuple[int, int]], banks: list[dict[int, int]]
) -> Counter[int]:
    destination = sorted(banks[arrival.destination].items(), reverse=True)
    target = quotient(arrival.row, destination)
    require(target != 0, f"destination alone at clock {arrival.clock}")
    projected = {
        chart: tuple(quotient(row, destination) for row in banks[chart].values())
        for chart, _ in donors
    }
    cases = Counter()
    for bundle in affordable_bundles(donors, old_rank):
        joined = span_basis((row for c in bundle for row in projected[c]), {})
        require(residue(target, joined) != 0,
                f"cheaper bundle {bundle} at clock {arrival.clock}")
        cases[len(bundle)] += 1
    return cases


def check_orientation(
    word: dict, dims: list[int], donors: list[list[tuple[int, int]]], reverse: bool
) -> tuple[int, list[tuple[int, int, int, int]], Counter[int]]:
    banks: list[dict[int, int]] = [{} for _ in range(CHARTS)]
    for row, chart in enumerate(entrance(word, reverse)):
        insert(1 << row, banks[chart])
    total = 0
    exceptions = []
    cases = Counter()
    for arrival in arrivals(word, reverse):
        old_rank = abs(dims[arrival.source] - dims[arrival.destination])
        require(old_rank > 0, "original MOVE rank")
        eligible = [(chart, rank) for chart, rank in donors[arrival.destination]
                    if rank < old_rank and banks[chart]]
        joined = span_basis(
            (row for chart, _ in eligible for row in banks[chart].values()),
            banks[arrival.destination],
        )
        total += 1
        if residue(arrival.row, joined) == 0:
            exceptions.append((arrival.clock, arrival.source, arrival.destination, old_rank))
            cases.update(check_small_bundles(arrival, old_rank, eligible, banks))
        # This arrival joins its chart's stock only after the test at its own deadline.
        insert(arrival.row, banks[arrival.destination])
    return total, exceptions, cases


def check_controls() -> None:
    # A common dual for individual donors need not exist. With free row 4,
    # neither donor alone supplies 7, and rows 1 and 2 together do.
    destination = {2: 4}
    reduced_target = quotient(7, sorted(destination.items(), reverse=True))
    require(reduced_target == 3, "quotient control")
    for row in (1, 2):
        require(residue(reduced_target, span_basis((row,), {})) != 0, "single control")
    require(residue(reduced_target, span_basis((1, 2), {})) == 0, "joint control")
    ranks = [(10, 1), (20, 2), (30, 3)]
    require(list(affordable_bundles(ranks, 3)) == [(10,), (20,)], "strict budget control")
    require(list(affordable_bundles(ranks, 4)) == [(10,), (20,), (30,), (10, 20)],
            "affordable pair control")


def main() -> None:
    raw = WORD.read_bytes()
    require(sha256(raw).hexdigest() == WORD_SHA256, "selected BIT word bytes")
    word = json.loads(gzip.decompress(raw))
    require(word["public"] == PUBLIC and word["owned_fields"] == OWNED, "lane count")
    require(len(word["program"]) == STEPS, "program length")
    require(all(len(entrance(word, reverse)) == PUBLIC for reverse in (False, True)),
            "entrance length")
    check_controls()
    dims, donors = nested_donors(word["frames"])
    forward = check_orientation(word, dims, donors, False)
    transpose = check_orientation(word, dims, donors, True)
    exceptions = [(26861 + 8 * i, 510 + i, 0, 7) for i in range(9)]
    require(forward == (2871, exceptions, {1: 4626, 2: 478764}),
            f"unexpected forward counts {forward}")
    require(transpose == (2871, [], {}), f"unexpected transpose counts {transpose}")
    print("PASS_BIT_CAUSAL_MULTI_DELIVERY arrivals=5742 union_excluded=5733 "
          "exceptional_singles=4626 exceptional_pairs=478764")


if __name__ == "__main__":
    main()
