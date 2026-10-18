#!/usr/bin/env python3
"""Literal finite-table controls for the five-tape parking controller.

Independent operational replay, not a replacement for the Lean proof. Four
symbols, ninety fixed states, unit moves, and writes only under the old heads.
Movement follows PR1379 3a45bd089ad56c38b55da8d80d7b056f2d90e5fa;
parking tables follow the credited Apache-2.0 PR64/ParkStack lineage.
No upstream Python/source body is copied. Mathematical tape specifications and
expected costs occur in tests only, never in the transition table.
"""
from __future__ import annotations
from collections import Counter
from dataclasses import dataclass
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
from typing import Callable

BLANK, SEP, ZERO, ONE = range(4)
COPY, REWIND, DONE = range(3)
ENTER_DELIMITER, ENTER_PAYLOAD, COPY_PARK, COPY_OUTPUT, REWIND_OUTPUT, POP_DONE = range(6)
PHASES = {"move": range(3), "push": range(3), "child": range(3), "pop": range(6)}
ENTRIES = (("move", COPY), ("push", COPY), ("move", COPY),
           ("child", COPY), ("move", COPY), ("pop", ENTER_DELIMITER))
Control = tuple[int, str, int]
Scan = tuple[int, ...]
Actions = tuple[tuple[int, int], ...]
STATES = tuple((stage, tag, phase) for stage in range(6)
               for tag, phases in PHASES.items() for phase in phases)
SCANS = tuple(product(range(4), repeat=5))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def actions(scanned: Scan, updates: dict[int, tuple[int, int]]) -> Actions:
    return tuple(updates.get(tape, (scanned[tape], 0)) for tape in range(5))


def move_table(phase: int, r: Scan, source: int, dest: int):
    if phase == COPY and r[source] in (ZERO, ONE) and r[dest] == BLANK:
        return COPY, actions(r, {source: (BLANK, 1), dest: (r[source], 1)})
    if phase == COPY and r[source] == BLANK and r[dest] == BLANK:
        return REWIND, actions(r, {source: (BLANK, -1), dest: (BLANK, -1)})
    if phase == REWIND and r[source] == BLANK and r[dest] in (ZERO, ONE):
        return REWIND, actions(r, {source: (BLANK, -1), dest: (r[dest], -1)})
    if phase == REWIND and r[source] == SEP and r[dest] == SEP:
        return DONE, actions(r, {source: (SEP, 1), dest: (SEP, 1)})
    return None


def push_table(phase: int, r: Scan):
    source, park = 1, 3
    if phase == DONE:
        return None
    if phase == COPY:
        if r[source] in (ZERO, ONE):
            return COPY, actions(r, {source: (BLANK, 1), park: (r[source], 1)})
        if r[source] == BLANK:
            return REWIND, actions(r, {source: (BLANK, -1), park: (SEP, 1)})
        return DONE, actions(r, {})
    if r[source] == BLANK:
        return REWIND, actions(r, {source: (BLANK, -1)})
    if r[source] == SEP:
        return DONE, actions(r, {source: (SEP, 1)})
    return DONE, actions(r, {})


def flip_table(phase: int, r: Scan):
    source = 2
    if phase == COPY and r[source] in (ZERO, ONE):
        return COPY, actions(r, {source: (ONE if r[source] == ZERO else ZERO, 1)})
    if phase == COPY and r[source] == BLANK:
        return REWIND, actions(r, {source: (BLANK, -1)})
    if phase == REWIND and r[source] in (ZERO, ONE):
        return REWIND, actions(r, {source: (r[source], -1)})
    if phase == REWIND and r[source] == SEP:
        return DONE, actions(r, {source: (SEP, 1)})
    return None


def pop_table(phase: int, r: Scan):
    source, temp, park = 1, 4, 3
    if phase == POP_DONE:
        return None
    if phase == ENTER_DELIMITER:
        return ENTER_PAYLOAD, actions(r, {park: (r[park], -1)})
    if phase == ENTER_PAYLOAD:
        return COPY_PARK, actions(r, {park: (BLANK, -1)})
    if phase == COPY_PARK:
        if r[park] in (ZERO, ONE):
            return COPY_PARK, actions(r, {temp: (r[park], 1), park: (BLANK, -1)})
        if r[park] == SEP:
            return COPY_OUTPUT, actions(r, {temp: (r[temp], -1), park: (SEP, 1)})
        return POP_DONE, actions(r, {})
    if phase == COPY_OUTPUT:
        if r[temp] in (ZERO, ONE):
            return COPY_OUTPUT, actions(r, {source: (r[temp], 1), temp: (BLANK, -1)})
        if r[temp] == SEP:
            return REWIND_OUTPUT, actions(r, {source: (r[source], -1), temp: (SEP, 1)})
        return POP_DONE, actions(r, {})
    if phase == REWIND_OUTPUT and r[source] in (ZERO, ONE):
        return REWIND_OUTPUT, actions(r, {source: (r[source], -1)})
    if phase == REWIND_OUTPUT and r[source] == SEP:
        return POP_DONE, actions(r, {source: (SEP, 1)})
    return POP_DONE, actions(r, {})


def transition(q: Control, r: Scan):
    stage, tag, phase = q
    child = None
    if stage == 1 and tag == "push":
        child = push_table(phase, r)
    elif stage in (2, 4) and tag == "move":
        child = move_table(phase, r, 0 if stage == 2 else 2, 2 if stage == 2 else 0)
    elif stage == 3 and tag == "child":
        child = flip_table(phase, r)
    elif stage == 5 and tag == "pop":
        child = pop_table(phase, r)
    if child is not None:
        next_phase, commands = child
        return (stage, tag, next_phase), commands
    if stage < 5:
        next_tag, next_phase = ENTRIES[stage + 1]
        return (stage + 1, next_tag, next_phase), actions(r, {})
    return None


# Compile every state/head-symbol combination into a genuinely fixed finite table.
TABLE = {(q, scanned): transition(q, scanned) for q in STATES for scanned in SCANS}


@dataclass
class Tape:
    background: Callable[[int], int]
    changes: dict[int, int]

    def read(self, position: int) -> int:
        return self.changes.get(position, self.background(position))

    def write(self, position: int, symbol: int) -> None:
        if symbol == self.background(position):
            self.changes.pop(position, None)
        else:
            self.changes[position] = symbol


@dataclass
class Machine:
    state: Control
    heads: list[int]
    tapes: list[Tape]

    def step(self, table=TABLE) -> bool:
        scanned = tuple(tape.read(head) for tape, head in zip(self.tapes, self.heads))
        result = table[self.state, scanned]
        if result is None:
            return False
        next_state, commands = result
        # Simultaneous local writes use the old heads, then all unit moves happen.
        for index, (symbol, offset) in enumerate(commands):
            self.tapes[index].write(self.heads[index], symbol)
        self.heads = [head + command[1] for head, command in zip(self.heads, commands)]
        self.state = next_state
        return True


def initial_machine(x: tuple[bool, ...], y: tuple[bool, ...], base: int, past):
    blank = lambda coordinate: BLANK
    park_background = lambda coordinate: past(coordinate) if coordinate < base - 1 else BLANK
    backgrounds = [blank, blank, blank, park_background, blank]
    contents = [{-1: SEP, **{i: ONE if bit else ZERO for i, bit in enumerate(x)}},
                {-1: SEP, **{i: ONE if bit else ZERO for i, bit in enumerate(y)}},
                {-1: SEP}, {base - 1: SEP}, {-1: SEP}]
    tapes = [Tape(background, dict(cells)) for background, cells in zip(backgrounds, contents)]
    expected = [dict(cells) for cells in contents]
    expected[0] = {-1: SEP, **{i: ZERO if bit else ONE for i, bit in enumerate(x)}}
    return Machine((0, "move", COPY), [0, 0, 0, base, 0], tapes), backgrounds, expected


def check_case(x, y, base, past, table=TABLE):
    machine, backgrounds, expected = initial_machine(x, y, base, past)
    budget = 6 * len(x) + 5 * len(y) + 18
    runtime = 0
    handoffs = 0
    stage_times = Counter()
    while True:
        previous = machine.state
        if not machine.step(table):
            break
        runtime += 1
        require(runtime <= budget + 1, "controller failed to halt within the expected bound")
        if machine.state[0] != previous[0]:
            handoffs += 1
        else:
            stage_times[previous[0]] += 1
    require(runtime == budget, "literal transition count differs from 6|x|+5|y|+18")
    require(handoffs == 5, "scheduler did not charge all five actual handoffs")
    require(machine.state == (5, "pop", POP_DONE), "wrong terminal finite control")
    require(machine.heads == [0, 0, 0, base, 0], "heads not restored literally")
    require([stage_times[i] for i in range(6)] ==
            [0, 2 * len(y) + 2, 2 * len(x) + 2, 2 * len(x) + 2,
             2 * len(x) + 2, 3 * len(y) + 5], "component costs differ")
    for index, tape in enumerate(machine.tapes):
        # Same background callable plus exactly equal finite overrides establishes
        # equality at EVERY integer coordinate, not just a sampled window.
        require(tape.background is backgrounds[index], "background function changed")
        require(tape.changes == expected[index], "full cell functions not restored")
    return runtime


def all_words(maximum: int):
    return [word for length in range(maximum + 1) for word in product((False, True), repeat=length)]


def test_controller():
    require(len(STATES) == 90 and len(TABLE) == 90 * 4**5, "finite table cardinality mismatch")
    for result in TABLE.values():
        if result is not None:
            state, commands = result
            require(state in STATES and len(commands) == 5, "table exits finite control")
            require(all(symbol in range(4) and move in (-1, 0, 1)
                        for symbol, move in commands), "nonlocal transition action")
    patterns = [lambda coordinate: BLANK, lambda coordinate: SEP,
                lambda coordinate: (coordinate * coordinate + 3 * coordinate + 7) % 4]
    count = 0
    maximum = 0
    for x, y, base, past in product(all_words(3), all_words(3), (-7, -1, 0, 6), patterns):
        maximum = max(maximum, check_case(x, y, base, past))
        count += 1
    for length_x, length_y in ((0, 23), (17, 0), (5, 31), (29, 2)):
        x = tuple(i % 3 == 0 for i in range(length_x))
        y = tuple(i % 2 == 0 for i in range(length_y))
        maximum = max(maximum, check_case(x, y, -37, patterns[2]))
        count += 1
    return {"cases": count, "states": len(STATES), "alphabet": 4, "tapes": 5,
            "table_entries": len(TABLE), "maximum_runtime": maximum,
            "full_cell_equality": "unchanged background identity and normalized override equality"}


def test_negative_controls():
    # Wrong flip output is caught by complete output-cell comparison.
    bad_flip = dict(TABLE)
    key = ((3, "child", COPY), (BLANK, BLANK, ZERO, BLANK, BLANK))
    state, commands = bad_flip[key]
    wrong = list(commands)
    wrong[2] = (ZERO, 1)
    bad_flip[key] = state, tuple(wrong)
    failures = 0
    try:
        check_case((False,), (), -3, lambda coordinate: SEP, bad_flip)
    except RuntimeError:
        failures += 1
    # Leaving the pushed delimiter unerased must also be detected.
    bad_erase = dict(TABLE)
    for key, result in list(bad_erase.items()):
        if key[0] == (5, "pop", ENTER_PAYLOAD) and result is not None:
            state, commands = result
            wrong = list(commands)
            wrong[3] = (key[1][3], -1)
            bad_erase[key] = state, tuple(wrong)
    try:
        check_case((), (True, False), 0, lambda coordinate: ONE, bad_erase)
    except RuntimeError:
        failures += 1
    require(failures == 2, "negative control failed to detect a faulty literal table")
    return failures


# The compiler's actual finite AST/microphase expansion for the two-stack output
# converter. Seven syntax nodes, three microphases, six register values.
NODES = ("pop", "isSome", "seen", "push", "goto", "halt", "stopped")
CONVERTER_STATES = tuple(product(NODES, range(3), range(2), (-1, 0, 1)))
CONVERTER_SCANS = tuple(product((BLANK, ZERO, ONE), repeat=2))


def converter_transition(q, r):
    node, phase, seen, held = q
    idle = ((r[0], 0), (r[1], 0))
    if node == "stopped":
        return None
    if phase == 0:
        if node == "pop":
            return (node, 2, seen, held), ((r[0], 1), (r[1], 0))
        if node == "isSome":
            return ("seen" if held != -1 else "halt", 0, seen, held), idle
        if node == "seen":
            return ("push" if seen else "goto", 0, seen, held), idle
        if node == "push":
            return ("goto", 0, seen, held), ((r[0], 0), (ONE if held == 1 else ZERO, -1))
        if node == "goto":
            return ("pop", 0, seen, held), idle
        return ("stopped", 0, seen, held), idle
    if phase == 2 and node == "pop":
        current = -1 if r[0] == BLANK else (1 if r[0] == ONE else 0)
        state = ("isSome", 0, int(bool(seen) or current == 1), current)
        return state, ((BLANK, -1 if current == -1 else 0), (r[1], 0))
    # No peek syntax nodes exist, so microphase1 is unreachable and halts.
    return None


CONVERTER_TABLE = {(q, scanned): converter_transition(q, scanned)
                   for q in CONVERTER_STATES for scanned in CONVERTER_SCANS}


def test_converter():
    require(len(CONVERTER_STATES) == 126 and len(CONVERTER_TABLE) == 1134,
            "converter finite-control cardinality mismatch")
    for result in CONVERTER_TABLE.values():
        if result is not None:
            state, commands = result
            require(state in CONVERTER_STATES and len(commands) == 2, "invalid converter control")
            require(all(symbol in (BLANK, ZERO, ONE) and offset in (-1, 0, 1)
                        for symbol, offset in commands), "nonlocal converter action")
    count = 0
    for source, suffix in product(all_words(7), all_words(2)):
        blank = lambda coordinate: BLANK
        machine = Machine(("pop", 0, 0, -1), [0, 0],
                          [Tape(blank, {i + 1: ONE if bit else ZERO for i, bit in enumerate(source)}),
                           Tape(blank, {i + 1: ONE if bit else ZERO for i, bit in enumerate(suffix)})])
        runtime = 0
        macrosteps = 0
        while machine.step(CONVERTER_TABLE):
            runtime += 1
            require(runtime <= 10 * (len(source) + 1), "converter exceeded proved physical bound")
            if machine.state[0] in ("pop", "stopped") and machine.state[1] == 0:
                macrosteps += 1
        first_one = next((i for i, bit in enumerate(source) if bit), len(source))
        kept = source[first_one:]
        prefix = tuple(reversed(kept))
        expected = {1 - len(prefix) + i: ONE if bit else ZERO for i, bit in enumerate(prefix)}
        expected.update({i + 1: ONE if bit else ZERO for i, bit in enumerate(suffix)})
        require(machine.state == ("stopped", 0, int(any(source)), -1), "converter did not truly halt")
        require(machine.heads == [len(source), -len(prefix)], "wrong encoded stack heads")
        require(machine.tapes[0].changes == {}, "converter source was not fully erased")
        require(machine.tapes[1].changes == expected, "converter lost canonical prefix or suffix")
        require(all(tape.background is blank for tape in machine.tapes), "converter backdrop changed")
        require(macrosteps == len(source) + 1, "converter source macrostep count differs")
        value = 0
        for bit in source:
            value = 2 * value + int(bit)
        require(sum(int(bit) * 2**i for i, bit in enumerate(prefix)) == value,
                "converter changed the numeric value")
        require(not prefix or prefix[-1] is True, "converter prefix has a high zero")
        count += 1
    return {"cases": count, "states": 126, "alphabet": 3, "tapes": 2,
            "table_entries": len(CONVERTER_TABLE), "macrosteps": "length+1",
            "physical_bound": "10*(length+1)", "suffix_preserved": True}


def source_hashes(source_root: Path):
    modules = (("MultitapeMarkedStreams20261014", "MarkedStreams"),
               ("MultitapeParkStack20261014", "ParkStack"),
               ("MultitapeParkingController20261014", "ParkingController"),
               ("MultitapeOutputNormalization20261014", "OutputNormalization"))
    result = {}
    for canonical, public in modules:
        candidate = source_root / (public + ".lean")
        if not candidate.is_file():
            candidate = source_root / (canonical + ".lean")
        require(candidate.is_file(), "missing requested proof-source binding: " + public)
        result[public] = sha256(candidate.read_bytes()).hexdigest()
    return result


def run_tests():
    return {"controller": test_controller(), "converter": test_converter(),
            "negative_controls_rejected": test_negative_controls(),
            "proof_status": "supporting operational fixtures; Lean certificates are separate"}


def main():
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path,
                        help="Optionally bind the replay to frozen public or canonical proof sources")
    parser.add_argument("--report", type=Path, help="Optional JSON report destination")
    args = parser.parse_args()
    frozen = source_hashes(args.source_root) if args.source_root is not None else None
    report = run_tests()
    if frozen is not None:
        require(source_hashes(args.source_root) == frozen,
                "frozen proof sources changed during operational replay")
        report["source_sha256"] = frozen
    if args.report is not None:
        args.report.write_text(json.dumps(report, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, sort_keys=True))


if __name__ == "__main__":
    main()


