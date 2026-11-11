"""Smaller lifted-record allocation and an exact finite algebraic reference.

Produced by Nick Petalas. Apache-2.0.
This is not an implementation of the retained physical tape provider.
"""
from dataclasses import dataclass

MAX_PARAMETER = 4096
MAX_AXES = 8
Pair = tuple[int, int]
Monomial = tuple[tuple[int, ...], tuple[int, ...]]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


@dataclass(frozen=True)
class Allocation:
    axes: int
    public_width: int
    lift: int
    extension: int
    width: int


def allocate(h: int, rank: int, columns: int) -> Allocation:
    require(type(h) is int and 2 <= h <= MAX_PARAMETER, 'public width')
    require(type(rank) is int and 1 <= rank <= 8, 'source rank')
    require(type(columns) is int and 1 <= columns <= MAX_PARAMETER, 'columns')
    axes = rank * columns
    reserve = (axes + 1) // 2
    return Allocation(axes, h, reserve, reserve + 1, h + 2 * reserve + 1)


def rotate(value: Pair, phase: int) -> Pair:
    a, b = value
    require(type(phase) is int and 0 <= phase < 4, 'unit phase')
    return ((a, b), (-b, a), (-a, -b), (b, -a))[phase]


def monomial(values: tuple[Pair, ...], word: Monomial) -> tuple[Pair, ...]:
    order, phases = word
    size = len(values)
    require(1 <= size <= 1 << MAX_AXES, 'monomial size')
    require(len(order) == len(phases) == size, 'complete monomial')
    require(sorted(order) == list(range(size)), 'monomial permutation')
    return tuple(rotate(values[order[i]], phases[i]) for i in range(size))


def axis(values: tuple[Pair, ...], index: int) -> tuple[Pair, ...]:
    size = len(values)
    require(2 <= size <= 1 << MAX_AXES and size & (size - 1) == 0, 'tensor size')
    require(type(index) is int and 0 <= index < size.bit_length() - 1, 'axis')
    result = list(values)
    stride = 1 << index
    for start in range(0, size, 2 * stride):
        for offset in range(stride):
            left, right = start + offset, start + offset + stride
            a, b = values[left]
            c, d = values[right]
            numerators = (a - b + c + d, a + b - c + d,
                          a + b + c - d, -a + b + c + d)
            require(all(n % 2 == 0 for n in numerators), 'nonintegral Gaussian half')
            result[left] = numerators[0] // 2, numerators[1] // 2
            result[right] = numerators[2] // 2, numerators[3] // 2
    return tuple(result)


def exact_run(values: tuple[Pair, ...], plan: Allocation,
              entrance: Monomial, exit_word: Monomial) -> tuple[Pair, ...]:
    require(1 <= plan.axes <= MAX_AXES, 'reference axis limit')
    require(2 <= plan.public_width <= MAX_PARAMETER, 'reference public width')
    require(plan.width <= MAX_PARAMETER + 3 * MAX_AXES + 1, 'reference word limit')
    require(len(values) == 1 << plan.axes, 'complete tensor input')
    cap = 1 << (plan.public_width - 1)
    require(all(type(v) is int and -cap <= v < cap
                for pair in values for v in pair), 'signed public input')
    require(0 <= plan.lift <= MAX_AXES and plan.width >= plan.public_width + plan.lift,
            'reference allocation')
    scale = 1 << plan.lift
    current = monomial(tuple((a * scale, b * scale) for a, b in values), entrance)
    internal = 1 << (plan.width - 2)
    require(all(abs(v) <= internal for pair in current for v in pair), 'entrance margin')
    for index in range(plan.axes):
        current = axis(current, index)
        require(all(abs(v) <= internal for pair in current for v in pair), 'prefix margin')
    current = monomial(current, exit_word)
    require(all(abs(v) <= internal for pair in current for v in pair), 'exit margin')
    return current


def lift_word(value: int, plan: Allocation) -> str:
    require(2 <= plan.public_width <= MAX_PARAMETER, 'codec public width')
    require(0 <= plan.lift <= MAX_AXES and 1 <= plan.extension <= MAX_AXES + 1,
            'codec count limits')
    cap = 1 << (plan.public_width - 1)
    require(type(value) is int and -cap <= value < cap, 'signed codec input')
    public = format(value % (2 * cap), f'0{plan.public_width}b')
    word = public[0] * plan.extension + public + '0' * plan.lift
    require(len(word) == plan.width, 'complete lifted word')
    return word


def drop_word(value: int, plan: Allocation) -> int:
    require(2 <= plan.public_width <= MAX_PARAMETER, 'codec public width')
    require(2 <= plan.width <= MAX_PARAMETER + 3 * MAX_AXES + 1, 'codec word limit')
    cap = 1 << (plan.width - 1)
    require(type(value) is int and -cap <= value < cap, 'signed widened input')
    require(1 <= plan.lift < plan.width, 'positive drop')
    word = format(value % (2 * cap), f'0{plan.width}b')
    high, low = word[:-plan.lift], word[-plan.lift:]
    retained = int(high, 2)
    if high[0] == '1':
        retained -= 1 << len(high)
    rounded = retained + int(low[0])
    public_cap = 1 << (plan.public_width - 1)
    if not -public_cap <= rounded < public_cap:
        raise OverflowError('true final public-width overflow')
    return rounded
