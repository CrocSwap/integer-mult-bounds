"""Finite two-tape controller for reversed parking records. Apache-2.0."""

from dataclasses import dataclass
from itertools import product

ALPHABET = ("_", "0", "1", "^", "$", "F", "R")
STATES = ("begin", "end", "end_check", "push", "seek", "copy",
          "pop", "deliver", "rewind")
HALTS = ("done", "reject")
MAX_CELLS = 100_000
MAX_STEPS = 200_000


@dataclass(frozen=True)
class Action:
    next_state: str
    write_p: str | None = None
    write_b: str | None = None
    move_p: int = 0
    move_b: int = 0


def transition(state: str, p: str, b: str) -> Action:
    """The only action-selection inputs are a state and two scanned symbols."""
    if state == "begin" and p == "_":
        return Action("done", "F", move_p=1)
    if state == "end" and p == "_":
        return Action("end_check", move_p=-1)
    if state == "end_check" and p == "F":
        return Action("done", "_")
    if state == "end_check":
        return Action("reject", move_p=1)
    if state == "push" and p == "_" and b in ("0", "1", "$"):
        return Action("seek", "R", move_p=1)
    if state == "seek" and p == "_" and b in ("0", "1"):
        return Action("seek", move_b=1)
    if state == "seek" and p == "_" and b == "$":
        return Action("copy", write_b="_", move_b=-1)
    if state == "copy" and p == "_" and b in ("0", "1"):
        return Action("copy", b, "_", 1, -1)
    if state == "copy" and p == "_" and b == "^":
        return Action("done", move_b=1)
    if state == "pop" and p == "_" and b == "_":
        return Action("deliver", move_p=-1)
    if state == "deliver" and p in ("0", "1") and b == "_":
        return Action("deliver", "_", p, -1, 1)
    if state == "deliver" and p == "R" and b == "_":
        return Action("rewind", "_", "$", move_b=-1)
    if state == "deliver" and p == "F" and b == "_":
        return Action("reject", move_p=1)
    if state == "rewind" and p == "_" and b in ("0", "1"):
        return Action("rewind", move_b=-1)
    if state == "rewind" and p == "_" and b == "^":
        return Action("done", move_b=1)
    return Action("reject")


def validate_table(table: dict) -> None:
    if not isinstance(table, dict) or len(table) != len(STATES) * len(ALPHABET)**2:
        raise ValueError("transition table size")
    expected = set(product(STATES, ALPHABET, ALPHABET))
    if set(table) != expected:
        raise ValueError("incomplete or extra transition keys")
    for action in table.values():
        if not isinstance(action, Action):
            raise ValueError("action type")
        if action.next_state not in STATES + HALTS:
            raise ValueError("unknown next state")
        if action.write_p not in (None,) + ALPHABET:
            raise ValueError("parking write outside alphabet")
        if action.write_b not in (None,) + ALPHABET:
            raise ValueError("port write outside alphabet")
        for move in (action.move_p, action.move_b):
            if type(move) is not int or move not in (-1, 0, 1):
                raise ValueError("head move must be a unit integer")


def compile_table() -> dict:
    table = {key: transition(*key) for key in product(STATES, ALPHABET, ALPHABET)}
    validate_table(table)
    return table


def validate_tape(tape: dict) -> None:
    if len(tape) > MAX_CELLS:
        raise ValueError("finite simulator cell budget")
    for position, symbol in tape.items():
        if type(position) is not int or symbol not in ALPHABET[1:]:
            raise ValueError("sparse tapes contain integer positions and nonblanks")


def run(table: dict, tapes: list[dict], heads: list[int], command: str,
        limit: int) -> tuple[str, tuple[int, int, int, int]]:
    """Execute a compiled table. Return halt and steps/reads/writes/moves."""
    validate_table(table)
    if command not in ("begin", "end", "push", "pop"):
        raise ValueError("unknown command")
    if type(limit) is not int or not 1 <= limit <= MAX_STEPS:
        raise ValueError("step budget")
    if len(tapes) != 2 or len(heads) != 2 or tapes[0] is tapes[1]:
        raise ValueError("two distinct tapes required")
    for tape in tapes:
        validate_tape(tape)
    if any(type(head) is not int for head in heads):
        raise ValueError("integer head positions required")
    state = command
    writes = moves = 0
    for step in range(1, limit + 1):
        p, b = (tape.get(head, "_") for tape, head in zip(tapes, heads))
        action = table[state, p, b]
        for i, symbol in enumerate((action.write_p, action.write_b)):
            if symbol is not None:
                writes += 1
                if symbol == "_":
                    tapes[i].pop(heads[i], None)
                else:
                    tapes[i][heads[i]] = symbol
        heads[0] += action.move_p
        heads[1] += action.move_b
        moves += abs(action.move_p) + abs(action.move_b)
        state = action.next_state
        if state in HALTS:
            return state, (step, 2 * step, writes, moves)
    raise RuntimeError("step budget exhausted")
