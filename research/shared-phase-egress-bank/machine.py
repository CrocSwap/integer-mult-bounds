"""Bounded local-symbol interpreter for the new composed graph.

It imports no predecessor machine. History is an observer and never controls
an instruction, an address, a branch, or a component boundary.
"""
from dataclasses import dataclass, field

BLANK = "_"


@dataclass(slots=True)
class Tape:
    cells: dict[int, str]
    origin: int
    head: int = field(init=False)
    low: int = field(init=False)
    high: int = field(init=False)

    def __post_init__(self):
        self.head = self.low = self.high = self.origin


def run(code, tapes, entry, budget):
    if len(tapes) != 20 or len({id(t) for t in tapes}) != 20:
        raise ValueError("twenty distinct physical tapes required")
    if not 0 <= entry < len(code) or not 1 <= budget <= 20000000:
        raise ValueError("bounded execution domain")
    pc = entry
    visits = [set() for _ in tapes]
    for steps in range(1, budget + 1):
        instruction = code[pc]
        op = instruction[0]
        pc += 1
        if op in ("read", "write", "move"):
            tape = tapes[instruction[1]]
            visits[instruction[1]].add(tape.head)
        if op == "read":
            symbol = tape.cells.get(tape.head, BLANK)
            if symbol not in instruction[2]:
                raise ValueError("literal rejection")
            pc = instruction[2][symbol]
        elif op == "write":
            symbol = instruction[2]
            if symbol == BLANK:
                tape.cells.pop(tape.head, None)
            else:
                tape.cells[tape.head] = symbol
        elif op == "move":
            tape.head += instruction[2]
            tape.low = min(tape.low, tape.head)
            tape.high = max(tape.high, tape.head)
            visits[instruction[1]].add(tape.head)
        elif op == "goto":
            pc = instruction[1]
        elif op == "halt":
            return steps, visits
        else:
            raise ValueError("unknown literal opcode")
    raise ValueError("finite execution budget exhausted")
