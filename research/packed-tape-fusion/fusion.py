"""Straight-line packed-tape access fusion. Apache-2.0."""

from dataclasses import dataclass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


@dataclass(frozen=True)
class Layout:
    """Bounded executable domain; the written identity has no 64-tape limit."""

    tapes: int
    field_log: int
    block_log: int
    width: int

    def __post_init__(self) -> None:
        for value in (self.tapes, self.field_log, self.block_log, self.width):
            require(type(value) is int, "integer layout parameters required")
        require(1 <= self.tapes <= 64, "tape count outside 1..64")
        require(0 <= self.field_log <= 4, "field log outside 0..4")
        require(0 <= self.block_log <= 8, "block log outside 0..8")
        require(10 <= self.width <= 256, "word width outside 10..256")
        require(self.field_bits * self.block_size <= self.width, "fields overflow")
        require(self.base + self.stride <= self.word_mask, "address region overflow")

    @property
    def field_bits(self) -> int:
        return 1 << self.field_log

    @property
    def block_size(self) -> int:
        return 1 << self.block_log

    @property
    def stride_log(self) -> int:
        return (2 * self.tapes - 1).bit_length()

    @property
    def stride(self) -> int:
        return 1 << self.stride_log

    @property
    def base(self) -> int:
        return 1 << max(7, (8 + 16 * self.tapes - 1).bit_length())

    @property
    def word_mask(self) -> int:
        return (1 << self.width) - 1


def register(tape: int) -> int:
    require(type(tape) is int and 0 <= tape < 64, "invalid tape register")
    return 8 + 16 * tape


def read_code(layout: Layout, tape: int) -> list[tuple]:
    """Retain address, offset, loaded word and observed field in this slab."""
    require(0 <= tape < layout.tapes, "tape not in layout")
    r = register(tape)
    return [
        ("shiftr", r + 3, r, 0),
        ("and", r + 4, r, 1),
        ("set", r + 5, layout.field_log),
        ("shiftl", r + 6, r + 4, r + 5),
        ("set", r + 7, layout.stride_log),
        ("shiftl", r + 8, r + 3, r + 7),
        ("add", r + 8, r + 8, r + 1),
        ("set", r + 9, layout.base),
        ("add", r + 8, r + 8, r + 9),
        ("load", r + 10, r + 8),
        ("shiftr", r + 11, r + 10, r + 6),
        ("set", r + 12, (1 << layout.field_bits) - 1),
        ("and", r + 13, r + 11, r + 12),
    ]


def commit_code(layout: Layout, tape: int) -> list[tuple]:
    require(0 <= tape < layout.tapes, "tape not in layout")
    r = register(tape)
    return [
        ("xor", r + 14, r + 13, r + 2),
        ("shiftl", r + 14, r + 14, r + 6),
        ("xor", r + 10, r + 10, r + 14),
        ("store", r + 8, r + 10),
    ]


def execute(code: list[tuple], memory: dict[int, int], width: int) -> int:
    """Execute the bounded straight-line RamStd subset; return successful steps."""
    require(type(width) is int and 10 <= width <= 256, "invalid VM width")
    require(len(code) <= 2048, "program exceeds straight-line replay bound")
    require(len(memory) <= 4096, "memory exceeds replay capacity")
    mask = (1 << width) - 1
    for address, value in memory.items():
        require(type(address) is int and 0 <= address <= mask, "invalid address")
        require(type(value) is int and 0 <= value <= mask, "invalid word")
    for record in code:
        require(len(record) in (3, 4), "malformed instruction")
        op, destination, *args = record
        require(type(destination) is int and 0 <= destination <= mask, "bad register")
        require(all(type(x) is int and 0 <= x <= mask for x in args), "bad argument")
        if op == "set" and len(args) == 1:
            memory[destination] = args[0]
        elif op == "load" and len(args) == 1:
            memory[destination] = memory.get(memory.get(args[0], 0), 0)
        elif op == "store" and len(args) == 1:
            memory[memory.get(destination, 0)] = memory.get(args[0], 0)
        else:
            require(len(args) == 2, "binary instruction needs two arguments")
            x, y = (memory.get(a, 0) for a in args)
            if op == "add":
                result = x + y
            elif op == "and":
                result = x & y
            elif op == "xor":
                result = x ^ y
            elif op == "shiftl":
                result = x << y if y < width else 0
            elif op == "shiftr":
                result = x >> y
            else:
                raise ValueError("unsupported instruction")
            memory[destination] = result & mask
        require(len(memory) <= 4096, "memory exceeds replay capacity")
    return len(code)


def prepare(layout: Layout, heads: list[int], words: list[int]) -> dict[int, int]:
    require(len(heads) == len(words) == layout.tapes, "one head and word per tape")
    memory = {0: layout.block_log, 1: layout.block_size - 1}
    for tape, (head, word) in enumerate(zip(heads, words, strict=True)):
        require(type(head) is int, "signed integer head required")
        require(type(word) is int and 0 <= word <= layout.word_mask, "word overflow")
        index = head if head >= 0 else -head - 1
        require(index <= layout.word_mask, "head index overflows word")
        tag = 2 * tape + (head < 0)
        address = layout.base + layout.stride * (index // layout.block_size) + tag
        require(address <= layout.word_mask, "head address wraps")
        r = register(tape)
        memory[r], memory[r + 1] = index, tag
        memory[address] = word
    return memory
