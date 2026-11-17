#!/usr/bin/env python3
"""Exact finite corroboration of PROOF.md; no predecessor code is executed."""
from __future__ import annotations

from dataclasses import dataclass, replace
from hashlib import sha256
from itertools import permutations
import json
from pathlib import Path
import sys

MAX_PORTS = 104
MAX_EVENTS = 8 * MAX_PORTS
PACKAGE_FILES = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json",
                 "VERIFY.json", "verify.py")
Frame = frozenset[int]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def span(vectors: tuple[int, ...]) -> Frame:
    require(len(vectors) <= 128, "too many frame generators")
    result = {0}
    for vector in vectors:
        require(0 <= vector < 128, "frame vector out of bounds")
        result |= {entry ^ vector for entry in result}
    return frozenset(result)


@dataclass(frozen=True)
class Event:
    op: str
    target: int
    source: int = -1
    scalar: int = 1
    frame: Frame | None = None


@dataclass(frozen=True)
class Program:
    lines: tuple[Frame, ...]
    permutation: tuple[int, ...]  # source i goes to permutation[i]
    scales: tuple[int, ...]
    events: tuple[Event, ...]
    modulus: int = 0


def validate(program: Program) -> int:
    n = len(program.lines)
    require(1 <= n <= MAX_PORTS, "port count outside finite checker domain")
    require(len(set(program.lines)) == n, "lines must be distinct")
    for frame in program.lines:
        require(len(frame) == 2 and 0 in frame, "not a binary line")
        require(all(0 <= v < 128 for v in frame), "line outside ambient space")
    require(sorted(program.permutation) == list(range(n)), "not a permutation")
    require(len(program.scales) == n, "wrong scale count")
    require(program.modulus in (0, 2, 3, 5), "unsupported finite check field")
    for scale in program.scales:
        require(isinstance(scale, int), "scale must be integral in checker")
        require(scale != 0 if program.modulus == 0
                else scale % program.modulus != 0, "zero scale")
    require(len(program.events) <= MAX_EVENTS, "event capacity exceeded")
    return n


def build(permutation: tuple[int, ...], modulus: int = 0) -> Program:
    n = len(permutation)
    lines = tuple(frozenset((0, i + 1)) for i in range(n))
    scales = tuple((-1) ** i * (i + 1) if modulus == 0
                   else 1 + i % (modulus - 1) for i in range(n))
    draft = Program(lines, permutation, scales, (), modulus)
    validate(draft)
    events = []
    for i, j in enumerate(permutation):
        if i == j:
            events.append(Event("SCALE", i, scalar=scales[i]))
        else:
            carrier = n + 3 + i
            events.extend((Event("INIT", carrier, frame=lines[i]),
                           Event("ADD", carrier, i),
                           Event("ADD", i, carrier, -1)))
    for i, j in enumerate(permutation):
        if i != j:
            carrier = n + 3 + i
            plane = span(tuple(lines[i] | lines[j]))
            events.extend((Event("MOVE", carrier, frame=plane),
                           Event("MOVE", carrier, frame=lines[j]),
                           Event("ADD", j, carrier, scales[i]),
                           Event("CLEAR", carrier)))
    result = replace(draft, events=tuple(events))
    validate(result)
    return result


def frame_move(old: Frame, new: Frame) -> int:
    require(bool(new) and len(new) <= 128 and 0 in new, "invalid frame size")
    require(span(tuple(new)) == new, "frame is not a binary subspace")
    require(old < new or new < old, "MOVE frames are not strictly nested")
    return abs(len(old).bit_length() - len(new).bit_length())


def row_operation(event: Event, rows: list[list[int]],
                  frames: list[Frame | None], modulus: int) -> None:
    target = event.target
    if event.op == "ADD":
        require(0 <= event.source < len(rows), "source role out of bounds")
        require(frames[event.source] is not None, "read of dead carrier")
        require(frames[target] == frames[event.source], "nonlocal scalar ADD")
        source = rows[event.source].copy()
        rows[target] = [a + event.scalar * b
                        for a, b in zip(rows[target], source, strict=True)]
    elif event.op == "SCALE":
        require(event.scalar != 0 if modulus == 0
                else event.scalar % modulus != 0, "singular scalar SCALE")
        rows[target] = [event.scalar * entry for entry in rows[target]]
    else:
        raise ValueError("unknown scalar operation")
    if modulus:
        rows[target] = [entry % modulus for entry in rows[target]]


def endpoints(program: Program, rows: list[list[int]],
              frames: list[Frame | None], initial: list[Frame | None]) -> None:
    n = len(program.lines)
    columns = n + 3
    expected = [[0] * columns for _ in range(columns)]
    for i, j in enumerate(program.permutation):
        expected[j][i] = program.scales[i]
    for i in range(n, columns):
        expected[i][i] = 1
    if program.modulus:
        expected = [[entry % program.modulus for entry in row]
                    for row in expected]
    require(rows[:columns] == expected, "wrong complete public endpoint")
    require(frames == initial, "wrong final frames or live owned carrier")
    require(all(not any(row) for row in rows[columns:]), "uncleared payload")


def replay(program: Program, frozen: bool = True) -> dict:
    n = validate(program)
    columns = n + 3
    full = span(tuple(range(1, n + 1)))
    initial = list(program.lines) + [frozenset((0,)), full, program.lines[0]]
    initial += [None] * n
    frames = initial.copy()
    rows = [[int(i == j) for j in range(columns)] for i in range(columns)]
    rows += [[0] * columns for _ in range(n)]
    moves = []
    live = peak = 0
    for event in program.events:
        target = event.target
        require(0 <= target < len(rows), "target role out of bounds")
        owned = target >= columns
        if event.op == "INIT":
            require(owned and frames[target] is None, "invalid owned INIT")
            require(event.frame is not None, "missing INIT frame")
            require(span(tuple(event.frame)) == event.frame, "invalid INIT frame")
            frames[target] = event.frame
            rows[target] = [0] * columns
            live += 1
            peak = max(peak, live)
        else:
            require(frames[target] is not None, "operation on dead carrier")
            if event.op == "CLEAR":
                require(owned, "public CLEAR is forbidden")
                frames[target] = None
                rows[target] = [0] * columns
                live -= 1
            elif event.op == "MOVE":
                require(owned or not frozen, "public MOVE violates fixed frames")
                require(event.frame is not None, "missing MOVE frame")
                old = frames[target]
                require(old is not None, "missing departure frame")
                rank = frame_move(old, event.frame)
                moves.append((old, event.frame, rank, owned))
                frames[target] = event.frame
            else:
                row_operation(event, rows, frames, program.modulus)
    endpoints(program, rows, frames, initial)
    require(live == 0, "owned lifetime imbalance")
    moved = [i for i, j in enumerate(program.permutation) if i != j]
    for i in moved:
        require(any(old == program.lines[i] for old, _, _, _ in moves), "no exit")
        require(any(new == program.lines[i] for _, new, _, _ in moves), "no entry")
    owned_ranks = [rank for _, _, rank, owned in moves if owned]
    return {"moves": len(owned_ranks), "rank_mass": sum(owned_ranks), "peak": peak}


def all_subspaces(dimension: int) -> tuple[Frame, ...]:
    require(1 <= dimension <= 4, "lattice enumeration domain")
    spaces = {frozenset((0,))}
    for _ in range(dimension):
        require(len(spaces) <= 67, "subspace capacity exceeded")
        spaces |= {span(tuple(frame) + (vector,))
                   for frame in tuple(spaces) for vector in range(1 << dimension)}
    return tuple(sorted(spaces, key=lambda frame: (len(frame), tuple(sorted(frame)))))


def check_lattice_edges() -> dict:
    counts, edges = [], 0
    for dimension in range(1, 5):
        spaces = all_subspaces(dimension)
        require(len(spaces) == (2, 5, 16, 67)[dimension - 1], "wrong lattice")
        counts.append(len(spaces))
        for old in spaces:
            for new in spaces:
                if old < new or new < old:
                    rank = frame_move(old, new)
                    require(rank >= 1, "nonpositive rank")
                    # An edge cannot satisfy both a designated-line exit and entry.
                    require(int(len(old) == 2) + int(len(new) == 2) <= 1,
                            "nested MOVE joins two line boundaries")
                    edges += 1
    return {"subspace_counts": counts, "nested_edges": edges}


def check_permutations() -> dict:
    cases = 0
    maximum_moves = 0
    for n in range(1, 7):
        for permutation in permutations(range(n)):
            moved = sum(i != j for i, j in enumerate(permutation))
            for modulus in (0, 2, 3, 5):
                answer = replay(build(permutation, modulus))
                require(answer["moves"] == answer["rank_mass"] == 2 * moved,
                        "attainer misses sharp tariff")
                require(answer["peak"] == moved, "unexpected carrier peak")
                maximum_moves = max(maximum_moves, answer["moves"])
                cases += 1
    permutation = tuple(i ^ 1 for i in range(MAX_PORTS))
    large = replay(build(permutation))
    require(large == {"moves": 208, "rank_mass": 208, "peak": 104},
            "104-port size fixture failed")
    return {"small_matrix_cases": cases, "small_maximum_moves": maximum_moves,
            "large_generic_fixture": large}


def reject(program: Program) -> None:
    try:
        replay(program)
    except ValueError:
        return
    raise ValueError("invalid circuit unexpectedly accepted")


def check_controls() -> int:
    base = build((1, 0))
    events = base.events
    first_move = next(i for i, event in enumerate(events) if event.op == "MOVE")
    controls = [replace(base, permutation=(0, 0)),
                replace(base, lines=(base.lines[0], base.lines[0])),
                replace(base, scales=(0, 1)),
                replace(base, events=events[1:]),
                replace(base, events=events[:first_move] + events[first_move + 1:]),
                replace(base, events=events[:-1]),
                replace(base, events=(Event("CLEAR", 0),) + events),
                replace(base, events=(Event("ADD", 0, 1),) + events),
                replace(base, events=(Event("ADD", 0, 5),) + events),
                replace(base, events=(Event("MOVE", 0, frame=frozenset((0, 1, 2, 3))),) + events)]
    for index, replacement in ((first_move, Event("MOVE", 5, frame=base.lines[1])),
                               (first_move, Event("MOVE", 5, frame=frozenset((0, 1, 2)))),
                               (first_move + 2, Event("ADD", 1, 5, 2)),
                               (2, Event("ADD", 0, 5, 1)),
                               (1, Event("INIT", 5, frame=base.lines[0]))):
        controls.append(replace(base, events=events[:index] + (replacement,) + events[index + 1:]))
    for program in controls:
        reject(program)
    for permutation, modulus in (((), 0), (tuple(range(105)), 0), ((0,), 7)):
        try:
            build(permutation, modulus)
        except ValueError:
            continue
        raise ValueError("invalid builder domain unexpectedly accepted")
    return len(controls) + 3


def check_changed_contract() -> dict:
    base = Program((frozenset((0, 1)), frozenset((0, 2))), (1, 0), (1, 1), ())
    plane = frozenset((0, 1, 2, 3))
    events = (Event("MOVE", 0, frame=plane), Event("MOVE", 1, frame=plane),
              Event("ADD", 0, 1), Event("ADD", 1, 0, -1),
              Event("ADD", 0, 1), Event("SCALE", 1, scalar=-1),
              Event("MOVE", 0, frame=base.lines[0]),
              Event("MOVE", 1, frame=base.lines[1]))
    program = replace(base, events=events)
    reject(program)
    answer = replay(program, frozen=False)
    require(answer["moves"] == 0, "changed-contract escape failed")
    return {"public_moves": 4, "owned_moves": answer["moves"]}


def main() -> None:
    require(len(sys.argv) == 1, "this checker takes no arguments")
    report = {"claim_type": "scoped written proof with exact finite corroboration",
              "lattice": check_lattice_edges(), "attainers": check_permutations(),
              "rejected_controls": check_controls(),
              "changed_contract": check_changed_contract()}
    here = Path(__file__).resolve().parent
    report["source_sha256"] = {name: sha256((here / name).read_bytes()).hexdigest()
                               for name in PACKAGE_FILES}
    print(json.dumps(report, sort_keys=True))
    print("PASS_FIXED_LINE_CROSSING_FLOOR")


if __name__ == "__main__":
    main()
