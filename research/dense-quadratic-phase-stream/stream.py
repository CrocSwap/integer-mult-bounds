"""Lexicographic Z/4 quadratic phases by reversible cofactoring.

Rows of ``cross`` are strict lower triangular: cross[j][i] multiplies x_i*x_j.
The finite reference accepts at most 20 address bits. See PROOF.md for all L.
"""

from typing import Iterator

MAX_BITS = 20


class Meter:
    def __init__(self) -> None:
        self.events = 0
        self.updates = 0
        self.matrix_reads = 0
        self.outputs = 0
        self.max_stack = 1
        self.restored = False


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def validate(linear: tuple[int, ...], cross: tuple[tuple[int, ...], ...],
             constant: int, meter: Meter) -> int:
    require(type(linear) is tuple and type(cross) is tuple, "immutable tuples required")
    n = len(linear)
    require(n <= MAX_BITS and len(cross) == n, "dimension outside reference domain")
    require(type(constant) is int and 0 <= constant < 4, "constant outside Z/4")
    require(type(meter) is Meter, "meter type")
    require((meter.events, meter.updates, meter.matrix_reads, meter.outputs,
             meter.max_stack, meter.restored) == (0, 0, 0, 0, 1, False),
            "fresh meter required")
    for j in range(n):
        require(type(cross[j]) is tuple and len(cross[j]) == j, "triangular shape")
        for value in (linear[j], *cross[j]):
            require(type(value) is int and 0 <= value < 4, "coefficient outside Z/4")
    return n


def phase_stream(linear: tuple[int, ...], cross: tuple[tuple[int, ...], ...],
                 constant: int, meter: Meter) -> Iterator[int]:
    """Yield q(0),...,q(2**L-1); exhausting the iterator restores its cofactors.

    This is a residue-operation model, not a fixed-tape implementation.
    A caller that abandons the iterator has not completed the return contract.
    """
    n = validate(linear, cross, constant, meter)
    current = list(linear)
    phase = constant
    # visit=0, enter-one=1, leave-one=2. Lower-index bits vary fastest.
    stack = [(0, n)]
    for _ in range(4 * (1 << n) - 3):
        require(bool(stack), "early event exhaustion")
        action, j = stack.pop()
        meter.events += 1
        if action == 0:
            if j == 0:
                meter.outputs += 1
                yield phase
            else:
                stack.extend(((2, j), (0, j - 1), (1, j), (0, j - 1)))
                meter.max_stack = max(meter.max_stack, len(stack))
        else:
            sign = 1 if action == 1 else -1
            phase = (phase + sign * current[j - 1]) % 4
            meter.updates += 1
            for i in range(j - 1):
                current[i] = (current[i] + sign * cross[j - 1][i]) % 4
                meter.updates += 1
                meter.matrix_reads += 1
    require(not stack, "unconsumed events")
    require(current == list(linear) and phase == constant, "cofactor restoration")
    meter.restored = True
    require(meter.outputs == 1 << n, "output census")
    require(meter.updates == 4 * (1 << n) - 2 * n - 4, "arithmetic census")
    require(meter.matrix_reads == 2 * ((1 << n) - n - 1), "matrix census")
    require(meter.max_stack == 3 * n + 1, "stack census")
