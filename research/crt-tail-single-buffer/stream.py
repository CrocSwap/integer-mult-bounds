"""Sequential payload actions for a complete-fiber controlled switch.

Counters, markers, control preparation and ordinary coordinate exchanges are
outside this payload-action interpreter. No predecessor code is imported.
"""

from dataclasses import dataclass, field

MAX_L = 12
MAX_R = 16


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


@dataclass
class Tape:
    cells: list[int | None]
    name: str
    trace: list[tuple[str, str, int | None]]
    head: int = 0
    immutable: bool = False
    peak: int = 0

    def read(self) -> int:
        require(0 <= self.head < len(self.cells), "read outside payload")
        value = self.cells[self.head]
        require(type(value) is int and value in (0, 1), "read blank payload")
        self.trace.append((self.name, "read", value))
        self.peak = max(self.peak, self.head + 1)
        return value

    def write(self, value: int | None) -> None:
        require(not self.immutable, "source write")
        require(0 <= self.head < len(self.cells), "write outside payload")
        require(value is None or type(value) is int and value in (0, 1),
                "invalid tape symbol")
        self.cells[self.head] = value
        self.trace.append((self.name, "write", value))
        self.peak = max(self.peak, self.head + 1)

    def move(self, direction: int) -> None:
        require(direction in (-1, 1), "nonunit move")
        require(0 <= self.head + direction <= len(self.cells), "head outside tape")
        self.head += direction
        self.trace.append((self.name, "move", direction))


@dataclass
class Run:
    source: Tape
    output: Tape
    scratch: Tape
    trace: list[tuple[str, str, int | None]]
    preparations: list[int] = field(default_factory=list)


def admit(bits: list[int], length: int, suffix: int, width: int,
          controls: list[int]) -> tuple[int, int, int]:
    require(type(length) is int and 1 <= length <= MAX_L, "invalid L")
    require(type(suffix) is int and 0 <= suffix < length, "invalid H")
    require(type(width) is int and 1 <= width <= MAX_R, "invalid R")
    volume = (1 << length) * width
    size = (1 << suffix) * width
    fibers = 1 << (length - suffix - 1)
    require(len(bits) == volume, "incomplete payload")
    require(all(type(x) is int and x in (0, 1) for x in bits), "invalid payload")
    require(len(controls) == fibers, "incomplete controls")
    require(all(type(x) is int and x in (0, 1) for x in controls),
            "non-Boolean control")
    return volume, size, fibers


def copy(source: Tape, target: Tape, count: int, erase: bool = False) -> None:
    # The admitted volume bounds every count by MAX_R * 2**MAX_L.
    require(0 <= count <= MAX_R * (1 << MAX_L), "invalid copy length")
    for _ in range(count):
        value = source.read()
        if erase:
            source.write(None)
        source.move(1)
        target.write(value)
        target.move(1)


def rewind(tape: Tape, count: int) -> None:
    require(0 <= count <= MAX_R * (1 << MAX_L), "invalid rewind length")
    for _ in range(count):
        tape.move(-1)


def switch(bits: list[int], length: int, suffix: int, width: int,
           controls: list[int]) -> Run:
    volume, size, fibers = admit(bits, length, suffix, width, controls)
    trace: list[tuple[str, str, int | None]] = []
    source = Tape(list(bits), "source", trace, immutable=True)
    output = Tape([None] * volume, "output", trace)
    scratch = Tape([None] * size, "scratch", trace)
    run = Run(source, output, scratch, trace)
    for prefix in range(fibers):
        run.preparations.append(prefix)
        control = controls[prefix]
        if control == 0:
            copy(source, output, 2 * size)
        else:
            copy(source, scratch, size)
            rewind(scratch, size)
            copy(source, output, size)
            copy(scratch, output, size, erase=True)
            rewind(scratch, size)
    rewind(source, volume)
    rewind(output, volume)
    require(source.cells == bits, "source changed")
    require(all(x is None for x in scratch.cells), "scratch not erased")
    require(source.head == output.head == scratch.head == 0, "head not returned")
    require(len(run.preparations) == fibers, "preparation count")
    return run
