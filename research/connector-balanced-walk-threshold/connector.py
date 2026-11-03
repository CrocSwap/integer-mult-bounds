"""Bounded literal compiler for the balanced closed-walk connector theorem."""

from collections import Counter
from dataclasses import dataclass

MAX_DIMENSION = 10
MAX_CHARACTERISTIC = 512


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def threshold(dimension: int) -> int:
    """Exact closed-covering-walk threshold; arithmetic API stops at 4096."""
    require(type(dimension) is int and 1 <= dimension <= 4096, "dimension")
    half = 1 << (dimension - 1)
    return 2 * ((half + dimension - 1) // dimension)


def closed_walk(dimension: int, transitions: tuple[int, ...]) -> tuple[int, ...]:
    require(type(dimension) is int and 1 <= dimension <= MAX_DIMENSION, "dimension")
    require(2 <= len(transitions) <= 2 ** (dimension + 1), "walk length")
    require(all(type(j) is int and 0 <= j < dimension for j in transitions), "label")
    vertices = [0]
    for j in transitions:
        vertices.append(vertices[-1] ^ (1 << j))
    require(vertices[-1] == 0, "walk is not closed")
    require(len(set(vertices)) == 1 << dimension, "walk does not cover the cube")
    counts = Counter(transitions)
    require(all(counts[j] % 2 == 0 for j in range(dimension)), "odd closed count")
    require(max(counts.values()) >= threshold(dimension), "closed-walk lower bound")
    return tuple(vertices)


@dataclass(frozen=True)
class Block:
    dimension: int
    characteristic: int
    sources: tuple[int, ...]
    reads: tuple[tuple[int, ...], ...]


def compile_block(dimension: int, characteristic: int,
                  transitions: tuple[int, ...]) -> Block:
    require(type(characteristic) is int and 2 <= characteristic <= MAX_CHARACTERISTIC,
            "characteristic")
    vertices = closed_walk(dimension, transitions)
    counts = Counter(transitions)
    require(max(counts.values()) <= characteristic, "insufficient characteristic")
    upward: list[int] = []
    downward: list[int] = []
    first = {0: (0, 0)}
    for index, j in enumerate(transitions):
        if vertices[index] & (1 << j):
            downward.append(j)
        else:
            upward.append(j)
        first.setdefault(vertices[index + 1], (len(upward), len(downward)))
    middle = tuple(j for j in range(dimension)
                   for _ in range(characteristic - counts[j]))
    sources = tuple(upward) + middle + tuple(reversed(downward))
    total = dimension * characteristic
    require(len(sources) == total, "source count")
    reads = [()]
    for mask in range(1, 1 << dimension):
        a, down = first[mask]
        reads.append((a, total - down))
    return Block(dimension, characteristic, sources, tuple(reads))


def complete_events(block: Block) -> tuple[tuple[str, int], ...]:
    """Materialize every positive call, including all dirty-cancelling padding."""
    total = len(block.sources)
    buckets: list[list[int]] = [[] for _ in range(total + 1)]
    for mask in range(1, 1 << block.dimension):
        for boundary in block.reads[mask]:
            buckets[boundary].append(mask)
        buckets[0].extend([mask] * (block.characteristic - 2))
    events: list[tuple[str, int]] = []
    for boundary in range(total + 1):
        events.extend(("A", mask) for mask in buckets[boundary])
        if boundary < total:
            events.append(("B", block.sources[boundary]))
    expected = block.characteristic * (block.dimension + (1 << block.dimension) - 1)
    require(len(events) == expected, "complete call count")
    return tuple(events)
