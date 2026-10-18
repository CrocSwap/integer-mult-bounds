#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Finite local microinstructions and a sparse, unit-step tape interpreter.

Only the interpreter stores integer head positions and a step statistic. The
program can observe neither: it branches solely on one scanned tape symbol.
Assembly resolves finite labels and never consumes runtime shape descriptors.
Prepared for David Arias with substantial OpenAI Codex assistance.
"""
from dataclasses import dataclass

BLANK, LEFT, RIGHT, ZERO, ONE, UNIT, MARK = range(7)
ALPHABET = frozenset(range(7))


def need(ok, message):
    if not ok:
        raise ValueError(message)


@dataclass(frozen=True)
class Program:
    instructions: tuple
    tapes: int
    entry: int = 0

    def __post_init__(self):
        need(isinstance(self.tapes, int) and self.tapes > 0, "positive fixed tape count")
        need(bool(self.instructions), "nonempty finite program")
        n = len(self.instructions)
        target = lambda p: isinstance(p, int) and 0 <= p < n
        tape = lambda t: isinstance(t, int) and 0 <= t < self.tapes
        need(target(self.entry), "finite entry state")
        for pc, row in enumerate(self.instructions):
            need(isinstance(row, tuple) and row, "instruction tuple")
            op = row[0]
            if op == "branch":
                need(len(row) == 4 and tape(row[1]), "branch tape")
                pairs = row[2]
                need(isinstance(pairs, tuple) and len({p[0] for p in pairs}) == len(pairs), "unique finite branches")
                need(all(len(p) == 2 and p[0] in ALPHABET and target(p[1]) for p in pairs)
                     and target(row[3]), "finite branch destinations")
            elif op == "write":
                need(len(row) == 3 and tape(row[1]) and row[2] in ALPHABET and pc+1 < n,
                     "local write and successor")
            elif op == "move":
                need(len(row) == 3 and tape(row[1]) and row[2] in (-1, 1) and pc+1 < n,
                     "unit movement and successor")
            elif op == "goto":
                need(len(row) == 2 and target(row[1]), "finite jump")
            elif op == "halt":
                need(len(row) == 1, "halt instruction")
            elif op == "reject":
                need(len(row) == 2 and isinstance(row[1], str), "finite rejection label")
            else:
                raise ValueError("unsupported machine instruction: " + str(op))


class Assembler:
    """Finite macro assembler; emitted instructions have no runtime callbacks."""
    def __init__(self, tape_count):
        self.tapes = tape_count
        self.instructions = []
        self.labels = {}
        self.serial = 0

    def fresh(self, prefix="label"):
        self.serial += 1
        return str(prefix) + "_" + str(self.serial)

    def label(self, name):
        need(name not in self.labels, "unique program label")
        self.labels[name] = len(self.instructions)

    def branch(self, tape, cases, default):
        self.instructions.append(("branch", tape, tuple(sorted(cases.items())), default))

    def write(self, tape, symbol):
        self.instructions.append(("write", tape, symbol))

    def move(self, tape, direction):
        self.instructions.append(("move", tape, direction))

    def goto(self, label):
        self.instructions.append(("goto", label))

    def halt(self):
        self.instructions.append(("halt",))

    def reject(self, reason):
        self.instructions.append(("reject", str(reason)))

    def finish(self, entry=0):
        def resolve(label):
            if isinstance(label, int):
                return label
            need(label in self.labels, "unresolved finite label: " + str(label))
            return self.labels[label]
        rows = []
        for row in self.instructions:
            if row[0] == "branch":
                rows.append((row[0], row[1], tuple((s, resolve(p)) for s, p in row[2]), resolve(row[3])))
            elif row[0] == "goto":
                rows.append((row[0], resolve(row[1])))
            else:
                rows.append(row)
        return Program(tuple(rows), self.tapes, resolve(entry))


class Tape:
    """Sparse physical tape. Fixtures may load cells; programs cannot inspect it."""
    def __init__(self, cells=None, head=0):
        self.cells = dict(cells or {})
        need(all(isinstance(k, int) and v in ALPHABET for k, v in self.cells.items()), "tape alphabet")
        self.cells = {k: v for k, v in self.cells.items() if v != BLANK}
        need(isinstance(head, int), "physical head")
        self.head = head

    def read(self):
        return self.cells.get(self.head, BLANK)

    def write(self, symbol):
        if symbol == BLANK:
            self.cells.pop(self.head, None)
        else:
            self.cells[self.head] = symbol


class Rejected(ValueError):
    pass


class Machine:
    """One microinstruction is one transition with local access/unit motion.

    Resource statistics and the optional execution cap are observations of
    the simulation. They are never read by an executed program instruction.
    """
    def __init__(self, program, tapes=None):
        self.program = program
        if tapes is None:
            self.tapes = [Tape() for _ in range(program.tapes)]
        elif isinstance(tapes, dict):
            self.tapes = [tapes.get(i, Tape()) for i in range(program.tapes)]
        else:
            self.tapes = list(tapes)
        need(len(self.tapes) == program.tapes and all(isinstance(t, Tape) for t in self.tapes), "fixed tape bank")
        self.pc, self.halted = program.entry, False
        self.steps = self.reads = self.writes = self.moves = 0
        self.visits = [set() for _ in self.tapes]
        self.write_positions = [set() for _ in self.tapes]
        self.peak_nonblank = sum(len(t.cells) for t in self.tapes)

    def step(self):
        need(not self.halted, "machine already halted")
        row = self.program.instructions[self.pc]
        op = row[0]
        self.steps += 1
        if op == "branch":
            tape = self.tapes[row[1]]
            self.visits[row[1]].add(tape.head)
            symbol = tape.read()
            self.reads += 1
            self.pc = dict(row[2]).get(symbol, row[3])
        elif op == "write":
            tape = self.tapes[row[1]]
            self.visits[row[1]].add(tape.head)
            self.write_positions[row[1]].add(tape.head)
            old = tape.read()
            tape.write(row[2])
            self.writes += 1
            # Counting support here is instrumentation, not an instruction.
            if (old == BLANK) != (row[2] == BLANK):
                current = sum(len(t.cells) for t in self.tapes)
                self.peak_nonblank = max(self.peak_nonblank, current)
            self.pc += 1
        elif op == "move":
            tape = self.tapes[row[1]]
            self.visits[row[1]].add(tape.head)
            tape.head += row[2]
            self.visits[row[1]].add(tape.head)
            self.moves += 1
            self.pc += 1
        elif op == "goto":
            self.pc = row[1]
        elif op == "halt":
            self.halted = True
        else:
            raise Rejected(row[1])

    def run(self, max_steps=None):
        while not self.halted:
            if max_steps is not None and self.steps >= max_steps:
                raise RuntimeError("external simulation step limit")
            self.step()
        return self


def marked(symbols):
    """Test-only input constructor; no machine instruction invokes it."""
    values = tuple(symbols)
    return Tape({0: LEFT, **{i+1: v for i, v in enumerate(values)}, len(values)+1: RIGHT}, 1)


def binary(value):
    """Test-only positive canonical LSB-first descriptor constructor."""
    need(isinstance(value, int) and value > 0, "positive fixture extent")
    return marked(ONE if value >> i & 1 else ZERO for i in range(value.bit_length()))
