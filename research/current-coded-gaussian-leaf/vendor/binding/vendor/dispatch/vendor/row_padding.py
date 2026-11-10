"""Finite local control for full-fibre compatible ROW padding.

JoyboyBrian, with substantial OpenAI Codex assistance. Apache-2.0.
Semantics follow Jose Manuel PR2786 and Nick Petalas PR3503; neither frozen
implementation is changed. Each executed instruction observes one local cell.
"""
from dataclasses import dataclass

BLANK = "_"
LEFT = "|"
SOURCE, PD, RD, SD, BD, P, R, S, B, D, TEMP, ROWS, PAD, RETURN, OUTPUT = range(15)
TAPES = 15


def need(ok, message):
    if not ok:
        raise ValueError(message)


class Builder:
    def __init__(self):
        self.code = []
        self.labels = {}
        self.serial = 0
        self.rejection = "reject"

    def fresh(self, prefix):
        self.serial += 1
        return prefix + str(self.serial)

    def mark(self, name):
        need(name not in self.labels, "unique control label")
        self.labels[name] = len(self.code)

    def read(self, tape, branches):
        complete = {symbol: ("quarantine" if symbol == LEFT else self.rejection)
                    for symbol in ("0", "1", BLANK, LEFT)}
        complete.update(branches)
        self.code.append(("read", tape, complete))

    def write(self, tape, symbol):
        self.code.append(("write", tape, symbol))

    def move(self, tape, direction):
        self.code.append(("move", tape, direction))

    def go(self, label):
        self.code.append(("goto", label))

    def rewind(self, tape):
        loop, done = self.fresh("rewind"), self.fresh("rewound")
        self.mark(loop)
        self.read(tape, {LEFT: done, "0": loop + "step", "1": loop + "step", BLANK: loop + "step"})
        self.mark(loop + "step")
        self.move(tape, -1)
        self.go(loop)
        self.mark(done)
        self.move(tape, 1)

    def clear(self, tape):
        self.rewind(tape)
        loop, erase, done = self.fresh("clear"), self.fresh("erase"), self.fresh("cleared")
        self.mark(loop)
        self.read(tape, {"0": erase, "1": erase, BLANK: done})
        self.mark(erase)
        self.write(tape, BLANK)
        self.move(tape, 1)
        self.go(loop)
        self.mark(done)
        self.rewind(tape)

    def boundary(self, tape):
        good = self.fresh("boundary")
        previous = self.rejection
        self.rejection = "quarantine"
        self.move(tape, -1)
        self.read(tape, {LEFT: good})
        self.mark(good)
        self.move(tape, 1)
        self.rejection = previous

    def unary(self, descriptor, output):
        # Canonical LSF positive binary input; last digit must be one.
        zero, one, done = self.fresh("lastzero"), self.fresh("lastone"), self.fresh("copied")
        self.mark(zero)
        self.read(descriptor, {"0": zero + "bit", "1": one + "bit"})
        self.mark(one)
        self.read(descriptor, {"0": zero + "bit", "1": one + "bit", BLANK: done})
        for state, bit in ((zero, "0"), (one, "1")):
            self.mark(state + "bit")
            self.write(TEMP, bit)
            self.move(TEMP, 1)
            self.move(descriptor, 1)
            self.go(state)
        self.mark(done)
        self.rewind(descriptor)
        self.rewind(TEMP)
        loop, borrow, unit, tail, trim, append, end = [self.fresh("decode") for _ in range(7)]
        self.mark(loop)
        self.read(TEMP, {BLANK: end, "0": borrow, "1": unit})
        self.mark(borrow)
        self.write(TEMP, "1")
        self.move(TEMP, 1)
        self.read(TEMP, {"0": borrow, "1": unit})
        self.mark(unit)
        self.write(TEMP, "0")
        self.move(TEMP, 1)
        self.read(TEMP, {BLANK: trim, "0": tail, "1": tail})
        self.mark(trim)
        self.move(TEMP, -1)
        self.write(TEMP, BLANK)
        self.mark(tail)
        self.rewind(TEMP)
        self.mark(append)
        self.write(output, "1")
        self.move(output, 1)
        self.go(loop)
        self.mark(end)
        self.rewind(output)

    def increment(self, tape):
        loop, carry, setone, done = [self.fresh("increment") for _ in range(4)]
        self.mark(loop)
        self.read(tape, {"1": carry, "0": setone, BLANK: setone})
        self.mark(carry)
        self.write(tape, "0")
        self.move(tape, 1)
        self.go(loop)
        self.mark(setone)
        self.write(tape, "1")
        self.mark(done)
        self.rewind(tape)

    def plan(self):
        compare, more, fits = [self.fresh("cover") for _ in range(3)]
        self.mark(compare)
        self.read(S, {BLANK: fits, "1": more})
        self.mark(more)
        good = self.fresh("covered")
        self.read(R, {"1": good})
        self.mark(good)
        self.move(S, 1)
        self.move(R, 1)
        self.go(compare)
        self.mark(fits)
        self.rewind(R)
        self.rewind(S)
        row, group, exact, partial, drain, padding, finish = [self.fresh("plan") for _ in range(7)]
        self.mark(row)
        self.increment(ROWS)
        self.move(R, 1)
        self.move(S, 1)
        self.read(S, {BLANK: exact, "1": partial})
        self.mark(exact)
        self.rewind(S)
        self.read(R, {BLANK: finish, "1": row})
        self.mark(partial)
        self.read(R, {BLANK: drain, "1": row})
        self.mark(drain)
        self.read(S, {BLANK: finish, "1": padding})
        self.mark(padding)
        self.write(D, "1")
        self.move(D, 1)
        self.increment(ROWS)
        self.move(S, 1)
        self.go(drain)
        self.mark(finish)
        for tape in (R, S, D):
            self.rewind(tape)

    def rows(self, source, output, count, mode):
        rows, row, body, bit, zero, one, endbody, end = [self.fresh("scan") for _ in range(8)]
        self.mark(rows)
        self.read(count, {"1": row, BLANK: end})
        self.mark(row)
        self.mark(body)
        self.read(B, {"1": bit, BLANK: endbody})
        self.mark(bit)
        if mode == "zero":
            self.write(output, "0")
            self.move(output, 1)
        else:
            self.read(source, {"0": zero, **({"1": one} if mode == "copy" else {})})
            self.mark(zero)
            if mode == "copy":
                self.write(output, "0")
                self.go(one + "copied")
                self.mark(one)
                self.write(output, "1")
                self.mark(one + "copied")
                self.move(output, 1)
            self.move(source, 1)
        self.move(B, 1)
        self.go(body)
        self.mark(endbody)
        self.rewind(B)
        self.move(count, 1)
        self.go(rows)
        self.mark(end)
        self.rewind(count)

    def transform(self, source, output, restricting):
        prefix, run, end, exact = [self.fresh("transform") for _ in range(4)]
        self.mark(prefix)
        self.read(P, {"1": run, BLANK: end})
        self.mark(run)
        self.rows(source, output, R, "copy")
        self.rows(source, output, D, "discard" if restricting else "zero")
        self.move(P, 1)
        self.go(prefix)
        self.mark(end)
        self.read(source, {BLANK: exact})
        self.mark(exact)
        for tape in (P, source, output):
            self.rewind(tape)

    def finish(self):
        result = []
        for instruction in self.code:
            if instruction[0] == "goto":
                result.append(("goto", self.labels[instruction[1]]))
            elif instruction[0] == "read":
                result.append(("read", instruction[1],
                               {k: self.labels[v] for k, v in instruction[2].items()}))
            else:
                result.append(instruction)
        return tuple(result)


def program():
    b = Builder()
    for descriptor, output in ((PD, P), (RD, R), (SD, S), (BD, B)):
        b.unary(descriptor, output)
    b.plan()
    b.transform(SOURCE, PAD, False)
    b.code.append(("call",))
    # Borrowed contents are a semantic callee premise. These local checks
    # enforce only the returned boundary-marker positions, not that premise.
    for tape in (SOURCE, PD, RD, SD, BD, ROWS, PAD, RETURN):
        b.boundary(tape)
    b.transform(RETURN, OUTPUT, True)
    for tape in (P, R, S, B, D, TEMP, ROWS, PAD, RETURN):
        b.clear(tape)
    b.code.append(("done",))
    # Well-formed-tape data errors retain reliable left markers. Recover
    # borrowed heads and erase owned work using the same local scans.
    b.mark("reject")
    b.rejection = "quarantine"
    for tape in (P, R, S, B, D, TEMP, ROWS, PAD, RETURN, OUTPUT):
        b.clear(tape)
    for tape in (SOURCE, PD, RD, SD, BD):
        b.rewind(tape)
    b.code.append(("rejected",))
    b.mark("quarantine")
    b.code.append(("quarantined",))
    return b.finish()


PROGRAM = program()


@dataclass
class Tape:
    cells: dict
    head: int = 1
    low: int = 0
    high: int = 0

    @classmethod
    def fixture(cls, text="", origin=0):
        return cls({origin: LEFT, **{origin + i + 1: c for i, c in enumerate(text)}},
                   origin + 1, origin, origin + len(text))

    def read(self):
        self.low = min(self.low, self.head)
        self.high = max(self.high, self.head)
        return self.cells.get(self.head, BLANK)


class Machine:
    """A table interpreter, not a host implementation of padding/counting."""
    def __init__(self, tapes):
        need(len(tapes) == TAPES, "fixed fifteen tapes")
        need(len({id(tape) for tape in tapes}) == TAPES, "distinct physical tape ports")
        self.tapes = tapes
        self.pc = 0
        self.steps = 0
        self.calls = 0

    def run(self, budget=10000000):
        need(len({id(tape) for tape in self.tapes}) == TAPES, "distinct physical tape ports")
        while self.steps < budget:
            instruction = PROGRAM[self.pc]
            op = instruction[0]
            self.steps += 1
            if op in ("rejected", "quarantined"):
                raise ValueError(op)
            if op in ("done", "call"):
                if op == "call":
                    self.pc += 1
                    self.calls += 1
                return op
            if op == "goto":
                self.pc = instruction[1]
                continue
            tape = self.tapes[instruction[1]]
            if op == "read":
                symbol = tape.read()
                need(symbol in instruction[2], "local guard rejected at state " + str(self.pc))
                self.pc = instruction[2][symbol]
                continue
            if op == "write":
                tape.read()
                tape.cells[tape.head] = instruction[2]
            elif op == "move":
                tape.head += instruction[2]
                tape.read()
            else:
                raise ValueError("unknown local opcode")
            self.pc += 1
        raise ValueError("test execution budget exhausted")
