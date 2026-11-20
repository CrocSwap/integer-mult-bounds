"""Small bounded replay interpreter; runtime operations are only R/W/M/J/H.

Bounds, counters and snapshots are replay instrumentation. Fixed physical
owner disjointness and the supplied backed intervals are entry hypotheses.
"""


class Tape:
    def __init__(self, cells, head=0):
        self.cells = list(cells)
        self.head = head

    def read(self):
        return self.cells[self.head]

    def write(self, symbol):
        self.cells[self.head] = symbol

    def step(self, direction):
        if direction not in (-1, 1) or not 0 <= self.head + direction < len(self.cells):
            raise ValueError("outside supplied backed interval")
        self.head += direction


class WordPort:
    SYMBOLS = ("0", "1", "L", "R", "_")
    VALUES = {s: i for i, s in enumerate(SYMBOLS)}

    def __init__(self, word):
        self.word = word

    @property
    def cells(self):
        return self.word.cells

    @property
    def head(self):
        return self.word.head

    def read(self):
        return self.SYMBOLS[self.word.read()]

    def write(self, symbol):
        self.word.write(self.VALUES[symbol])

    def step(self, direction):
        self.word.step(direction)


class Program:
    def __init__(self, code, metadata):
        self.code, self.metadata = code, metadata
        self.steps = self.calls = 0
        self.histories = [None] * metadata["tapes"]
        self.op_counts = {s: 0 for s in ("R", "W", "M", "J", "H")}

    def run(self, ports, entry, limit=10000000):
        if len(ports) != 68 or len({id(t.cells) for t in ports}) != 68:
            raise ValueError("distinct fixed 64-Word, template, stack and two-selector owners")
        pc = self.metadata["entries"][entry] if isinstance(entry, str) else entry
        steps = 0
        touched = [[t.head, t.head] for t in ports]
        writes = [0] * 68
        while True:
            op, *args = self.code[pc]
            steps += 1
            self.op_counts[op] += 1
            if steps > limit:
                raise ValueError("bounded replay watchdog")
            if op == "R":
                pc = args[1][ports[args[0]].read()]
            elif op == "W":
                ports[args[0]].write(args[1])
                writes[args[0]] += 1
                pc += 1
            elif op == "M":
                tape = args[0]
                ports[tape].step(args[1])
                head = ports[tape].head
                touched[tape][0] = min(touched[tape][0], head)
                touched[tape][1] = max(touched[tape][1], head)
                pc += 1
            elif op == "J":
                pc = args[0]
            elif op == "H":
                self.steps += steps
                self.calls += 1
                for i, extent in enumerate(touched):
                    before = self.histories[i]
                    self.histories[i] = extent if before is None else [min(before[0], extent[0]), max(before[1], extent[1])]
                return {"status": args[0], "instructions": steps, "writes": writes, "history": touched}
            else:
                raise ValueError("nonliteral opcode")
