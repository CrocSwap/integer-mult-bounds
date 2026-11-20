"""A literal one-head controller for nested reservations on one physical tape."""

from collections import Counter
from itertools import product


BLANK = "_"
START = "["
STOP = "]"
DATA = ("e", "0", "1")
ACTIVE = tuple((symbol, False) for symbol in DATA)
SAVED = tuple((symbol, True) for symbol in DATA)
ALPHABET = (BLANK, START, STOP, *ACTIVE, *SAVED)
DONE = "done"

def expect(value, description):
    if not value:
        raise ValueError(description)


def table():
    moves = {}

    def rule(state, symbol, next_state, write=None, move=0):
        key = (state, symbol)
        expect(key not in moves, "duplicate table key")
        moves[key] = (next_state, symbol if write is None else write, move)

    rule("init", BLANK, "init_data", START, 1)
    rule("init_data", BLANK, "init_tip", ("e", False), 1)
    rule("init_tip", BLANK, DONE, STOP, -1)
    for symbol in DATA:
        value = (symbol, False)
        for written in DATA:
            rule("write_" + written, value, DONE, (written, False))
        rule("right", value, "probe_right", move=1)
        rule("probe_right", value, DONE)
        rule("left", value, "probe_left", move=-1)
        rule("probe_left", value, DONE)
        rule("push", value, "seek_tip", (symbol, True), 1)
        rule("seek_tip", value, "seek_tip", move=1)
        rule("leave", value, "leave", move=1)
        rule("clear", value, "clear", BLANK, -1)
        rule("find_parent", value, "find_parent", move=-1)
        rule("find_parent", (symbol, True), DONE, value)
    rule("probe_right", STOP, "extend_tip", ("e", False), 1)
    rule("extend_tip", BLANK, DONE, STOP, -1)
    rule("probe_left", START, DONE, move=1)
    rule("seek_tip", STOP, "init", move=1)
    rule("leave", STOP, "clear", BLANK, -1)
    rule("clear", START, "parent_tip", BLANK, -1)
    rule("parent_tip", STOP, "find_parent", move=-1)
    return moves


TABLE = table()


class Tape:
    """The dictionary and counters measure the single physical head."""

    def __init__(self, cells, head):
        self.cells = dict(cells)
        self.head = head
        self.visits = Counter()

    def run(self, state):
        first, last = self.head, self.head
        count = 0
        while state != DONE:
            raw = self.cells.get(self.head, BLANK)
            state, write, move = TABLE[state, raw]
            self.visits[self.head] += 1
            if write == BLANK:
                self.cells.pop(self.head, None)
            else:
                self.cells[self.head] = write
            self.head += move
            count += 1
            first, last = min(first, self.head), max(last, self.head)
        return count, first, last


def enumerate_frames():
    opaque = {i - len(ALPHABET) : sym for i, sym in enumerate(ALPHABET) if sym != BLANK}
    checked = 0
    for n in range(1, 4):
        for parent in product(DATA, repeat=n):
            for j in range(n):
                entry = dict(opaque)
                entry[0], entry[n + 1] = START, STOP
                entry.update((i+1, (sym,False)) for i,sym in enumerate(parent))
                for m in range(1, 4):
                    for child in product(DATA, repeat=m):
                        for k in range(m):
                            machine = Tape(entry, j+1)
                            steps, first, last = machine.run("push")
                            expect((steps, first, last) == (n-j+4, j+1, n+4), "push trace")
                            expect(machine.head == n+3, "child entry")
                            for i, sym in enumerate(child):
                                if i:
                                    machine.run("right")
                                machine.run("write_"+sym)
                            for _ in range(m-1-k):
                                machine.run("left")
                            steps, first, last = machine.run("leave")
                            expect((steps, first, last) ==
                                   (m-k + 1 + m + 1 + 1 + n-1-j + 1, j+1, n+m+3),
                                   "retirement trace")
                            expect(machine.cells == entry, "restored cells")
                            expect(machine.head == j+1, "restored head")
                            checked += 1
    return checked


def deeply_nested(depth):
    machine = Tape({}, 0)
    machine.run("init")
    widths = [1 + ((11 * i + 7) % 23) for i in range(depth)]
    for i, width in enumerate(widths):
        for j in range(width):
            if j:
                machine.run("right")
            machine.run("write_" + str((i + j) % 2))
        machine.run("push")
    for i, width in reversed(list(enumerate(widths))):
        machine.run("leave")
        expect(machine.cells[machine.head] == (str((i + width - 1) % 2), False),
               "deep restored data")
        for _ in range(width-1):
            machine.run("left")
    expect(max(machine.visits) == sum(width + 2 for width in widths) + 2,
           "historical extent")
    expect(min(machine.visits) == 0, "old prefix scanned")


if __name__ == "__main__":
    n = enumerate_frames()
    deeply_nested(1000)
    print(f"PASS {n} frame returns, depth 1000, {len(TABLE)} literal transitions")
