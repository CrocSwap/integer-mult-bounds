"""Five ordered products, Gaussian-integer data, and two clean restored fields."""

from math import gcd

Gaussian = tuple[int, int]
Scalar = tuple[int, int, int]
Instruction = tuple[str, int, int, int, Scalar]
ONE: Scalar = (1, 0, 1)
ZERO: Gaussian = (0, 0)
MAX_BITS = 4096


def multiply(a: Gaussian, b: Gaussian) -> Gaussian:
    return a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0]


def scaled(a: Gaussian, coefficient: Scalar) -> Gaussian:
    real, imag, denominator = coefficient
    if denominator not in (1, 2):
        raise ValueError("only the declared integral or half-integral scalars")
    x, y = multiply(a, (real, imag))
    if x % denominator or y % denominator:
        raise ValueError("inexact Gaussian division")
    return x // denominator, y // denominator


def inverse(instruction: Instruction) -> Instruction:
    kind, target, source, other, (a, b, d) = instruction
    if kind in ("ADD", "PRODUCT"):
        coefficient = (-a, -b, d)
    elif kind == "SCALE":
        norm = a * a + b * b
        common = gcd(gcd(abs(a * d), abs(b * d)), norm)
        if common == 0:
            raise ValueError("zero SCALE")
        coefficient = (a * d // common, -b * d // common, norm // common)
    else:
        raise ValueError("unknown instruction")
    return kind, target, source, other, coefficient


def decoder() -> tuple[Instruction, ...]:
    """Reduce V to I. Output fields are registers 6..10."""
    adds = (
        (7, 6, (-1, 0, 1)), (7, 10, (-1, 0, 1)),
        (8, 6, (-1, 0, 1)), (8, 10, (-1, 0, 1)),
        (9, 6, (-1, 0, 1)), (9, 10, (4, 0, 1)),
        (8, 7, (0, -1, 1)), (9, 7, (-1, -1, 1)),
        (9, 8, (0, 1, 1)), (8, 9, (1, -1, 1)),
    )
    word = [("ADD", t, s, 0, c) for t, s, c in adds]
    word.extend((("SCALE", 8, 0, 0, (-1, 1, 2)),
                 ("SCALE", 9, 0, 0, (-1, -1, 2)),
                 ("ADD", 7, 8, 0, (-1, 0, 1)),
                 ("ADD", 7, 9, 0, (-1, 0, 1))))
    return tuple(word)


def program() -> tuple[Instruction, ...]:
    decode = decoder()
    word = [inverse(op) for op in reversed(decode)]
    word.append(("PRODUCT", 6, 0, 3, ONE))
    for target, z in ((7, (1, 0)), (8, (0, 1)), (9, (1, 1))):
        evaluation = []
        for scratch, start in ((11, 0), (12, 3)):
            for offset, value in enumerate(((1, 0), z, multiply(z, z))):
                evaluation.append(("ADD", scratch, start + offset, 0,
                                   (value[0], value[1], 1)))
        word.extend(evaluation)
        word.append(("PRODUCT", target, 11, 12, ONE))
        word.extend(inverse(op) for op in reversed(evaluation))
    word.append(("PRODUCT", 10, 2, 5, ONE))
    word.extend(decode)
    return tuple(word)


def validate(registers: tuple[Gaussian, ...]) -> None:
    if type(registers) is not tuple or len(registers) != 13:
        raise ValueError("exactly thirteen Gaussian registers")
    for value in registers:
        if type(value) is not tuple or len(value) != 2:
            raise ValueError("Gaussian integers are pairs")
        for component in value:
            if type(component) is not int or component.bit_length() > MAX_BITS:
                raise ValueError("integer component exceeds the input contract")
    if registers[11:] != (ZERO, ZERO):
        raise ValueError("two initially clean evaluation fields are required")


def execute(registers: tuple[Gaussian, ...], word: tuple[Instruction, ...]
            ) -> tuple[Gaussian, ...]:
    validate(registers)
    if len(word) > 128:
        raise ValueError("word exceeds the finite instruction cap")
    state = list(registers)
    for kind, target, source, other, coefficient in word:
        if not 6 <= target < 13 or not 0 <= source < 13 or not 0 <= other < 13:
            raise ValueError("invalid register or modified source")
        if kind == "SCALE":
            state[target] = scaled(state[target], coefficient)
        elif kind in ("ADD", "PRODUCT"):
            value = state[source]
            if kind == "PRODUCT":
                if target in (source, other):
                    raise ValueError("aliased product target")
                value = multiply(value, state[other])
            elif target == source:
                raise ValueError("aliased ADD")
            x, y = scaled(value, coefficient)
            a, b = state[target]
            state[target] = a + x, b + y
        else:
            raise ValueError("unknown instruction")
    return tuple(state)
