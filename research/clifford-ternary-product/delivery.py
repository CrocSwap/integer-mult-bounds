"""Consume signed unit events at their current physical output bit positions."""


class _Accumulator:
    def __init__(self):
        self.positive = bytearray([0])
        self.negative = bytearray([0])
        self.head = 0
        self.moves = 0
        self.ripple = 0
        self.emits = 0

    def right(self):
        self.head += 1
        self.moves += 1
        if self.head == len(self.positive):
            self.positive.append(0)
            self.negative.append(0)

    def left(self):
        if not self.head:
            raise ValueError("A movement crossed the physical origin")
        self.head -= 1
        self.moves += 1

    def rewind(self):
        while self.head:
            self.left()

    def emit(self, positive):
        record = self.positive if positive else self.negative
        start = self.head
        self.emits += 1
        while record[self.head]:
            record[self.head] = 0
            self.ripple += 1
            self.right()
        record[self.head] = 1
        # The physical version sets one mark at the caller's starting head.
        while self.head != start:
            self.left()

    def finish(self):
        self.rewind()
        result = bytearray()
        borrow = 0
        for k, (pos, neg) in enumerate(zip(self.positive, self.negative, strict=True)):
            value = pos - neg - borrow
            digit = value % 2
            borrow = int(value < 0)
            if k < 2:
                if digit:
                    raise ValueError("The signed numerator is not divisible by the required power")
            else:
                result.append(digit)
            self.positive[k] = self.negative[k] = 0
        if borrow:
            raise ValueError("The final product is negative")
        while result and not result[-1]:
            result.pop()
        return bytes(result or [0])


def deliver(passes, *, stats=None):
    """Return canonical little-endian bits from four signed numerator passes.

    '>' and '<' move one cell. '+' and '-' add one signed bit at the
    current position. Each new pass starts at the physical origin.
    """
    state = _Accumulator()
    count = 0
    for events in passes:
        count += 1
        if count > 4:
            raise ValueError("Use exactly four signed character passes")
        for event in events:
            if event == ">":
                state.right()
            elif event == "<":
                state.left()
            elif event == "+":
                state.emit(True)
            elif event == "-":
                state.emit(False)
            else:
                raise ValueError("Unknown movement or sign event")
        state.rewind()
    if count != 4:
        raise ValueError("Use exactly four signed character passes")
    answer = state.finish()
    if stats is not None:
        stats.update(emits=state.emits, ripple=state.ripple, moves=state.moves,
                     cells=len(state.positive))
    return answer
