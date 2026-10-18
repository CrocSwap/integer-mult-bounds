"""Compile fixed-low symbolic itineraries, without width or high fields."""
from dataclasses import dataclass
from math import prod

from words import need


@dataclass(frozen=True)
class Reference:
    kind: str
    index: int = 0
    first: int = 0
    second: int = 0
    permutation: tuple = ()
    sign: int = 1


@dataclass(frozen=True)
class Command:
    kind: str
    target: int
    source: int
    reference: Reference


@dataclass
class Request:
    kind: str
    coordinate: object
    reference: object = None
    reverse_adapter: bool = False
    child_kind: str = ""
    field: int = 0
    reverse: bool = False
    negative_inverse: bool = False
    half: bool = False


@dataclass(frozen=True)
class Plan:
    dimension: int
    rank: int
    good: bool
    commands: tuple
    reductions: tuple = ()
    permutation: tuple = ()
    negative_sign: bool = False


def compile_plan(low_projector, rank, q, good):
    """Host arithmetic here depends only on the fixed prime/low vocabulary."""
    m = len(low_projector)
    need(1 <= rank < m <= 64, "compiled residual dimension")
    if good:
        commands = []
        index = 0
        for k in range(rank):
            for i in range(k+1, m):
                commands.append(Command("add", i, k, Reference("head", index, i, k)))
                index += 1
        index = 0
        for k in range(rank):
            column = m-1-k
            for source in range(column):
                commands.append(Command("add", m+column, m+source,
                                        Reference("tail", index, sign=-1)))
                index += 1
        for i in range(m):
            for k in range(m):
                commands.append(Command("add", m+i, k, Reference("cross", i*m+k, i, k)))
        return Plan(m, rank, True, tuple(commands))
    size = 2*m
    rows = [[0]*size for _ in range(size)]
    for i in range(m):
        for j in range(m):
            rows[i][j] = rows[size-1-i][size-1-j] = (int(i == j)-low_projector[i][j]) % q
            rows[i][size-1-j] = rows[size-1-i][j] = low_projector[i][j] % q
    permutation, reductions = list(range(size)), []
    for j in range(size):
        pivot = next(i for i in range(j, size) if rows[i][j] % q)
        if pivot != j:
            reductions.append(("swap", j, pivot, tuple(permutation)))
            rows[j], rows[pivot] = rows[pivot], rows[j]
            permutation[j], permutation[pivot] = permutation[pivot], permutation[j]
        inverse = pow(rows[j][j], -1, q)
        for i in range(size):
            if i != j:
                coefficient = -rows[i][j]*inverse % q
                reductions.append(("shear", i, j, tuple(permutation)))
                rows[i] = [(x+coefficient*y) % q for x, y in zip(rows[i], rows[j])]
    sign = prod(rows[i][i] for i in range(size)) % q
    need(sign in (1, q-1), "compiled terminal sign")
    commands = []
    unit = Reference("unit")
    for i in range(size-1):
        commands.append(Command("child", i, size-1, unit))
        commands.append(Command("child", i, size-1, Reference("pair", i, i, size-1,
                                                              tuple(permutation))))
    if sign != 1:
        commands.append(Command("sign", size-1, -1, Reference("fixed", sign=-1)))
    for index in range(len(reductions)-1, -1, -1):
        kind, i, k, snapshot = reductions[index]
        if kind == "swap":
            commands.append(Command("child", i, k, unit))
        else:
            reference = Reference("shear", index, i, k, snapshot, -1)
            if i > k:
                commands.append(Command("add", i, k, reference))
            else:
                commands.extend((Command("child", i, k, unit), Command("add", k, i, reference),
                                 Command("child", i, k, unit)))
    return Plan(m, rank, False, tuple(commands), tuple(reductions), tuple(permutation), sign != 1)
