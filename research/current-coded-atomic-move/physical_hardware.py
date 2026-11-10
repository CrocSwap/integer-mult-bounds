"""Independent primitive tape checker with literal unit-action semantics.

Only Python observation overhead changes. There is no bulk read, movement,
payload callback or virtual-symbol shortcut. Prepared for @CubeJerry with
substantial OpenAI assistance. Apache-2.0.
"""
import random


class Tape:
    def __init__(self, origin=1):
        self.cells = bytearray([6])*(origin+1)
        self.cells[origin-1] = 2
        self.origin = self.head = self.high = origin
        self.reads = self.writes = self.moves = 0

    def read(self):
        self.reads += 1
        if self.head < len(self.cells):
            return self.cells[self.head]
        return 6

    def write(self, value):
        if value < 0 or value > 6:
            raise ValueError("physical alphabet")
        self.writes += 1
        index = self.head
        if index >= len(self.cells):
            self.cells.extend(bytearray([6])*(index+1-len(self.cells)))
        self.cells[index] = value
        if index+1 > self.high:
            self.high = index+1

    def move(self, direction):
        if direction != 1 and direction != -1:
            raise ValueError("physical unit move")
        self.head += direction
        self.moves += 1
        if self.head < 0:
            raise ValueError("physical boundary")

    def actions(self):
        return self.reads+self.writes+self.moves


def check(reference):
    """Independent finite hardware regression, not a new machine theorem."""
    randomizer = random.Random(19658963)
    commands = 0
    for origin in (1, 5, 9):
        a, b = Tape(origin), reference(origin)
        for _ in range(10000):
            op = randomizer.randrange(3)
            if op == 0:
                value = randomizer.randrange(7)
                a.write(value); b.write(value)
            elif op == 1:
                if a.read() != b.read():
                    raise ValueError("primitive read mismatch")
            else:
                direction = 1 if a.head == 0 else randomizer.choice((-1, 1))
                a.move(direction); b.move(direction)
            commands += 1
        if (a.cells, a.head, a.high, a.reads, a.writes, a.moves) != (
            b.cells, b.head, b.high, b.reads, b.writes, b.moves):
            raise ValueError("complete primitive hardware state mismatch")
    rejections = 0
    for operation, argument in (("write", -1), ("write", 7), ("move", 0), ("move", 2)):
        for cls in (Tape, reference):
            try:
                getattr(cls(), operation)(argument)
            except ValueError:
                rejections += 1
            else:
                raise ValueError("invalid physical instruction accepted")
    return dict(seed=19658963, primitive_commands=commands, invalid_instruction_rejections=rejections,
                bulk_operations=False, algorithmic_time_improvement_claim=False)
