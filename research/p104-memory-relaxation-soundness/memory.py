# SPDX-License-Identifier: Apache-2.0
"""Literal-subspace implementation of the proved necessary relaxation."""

from dataclasses import dataclass

Frame = frozenset[int]
Bounds = tuple[Frame, Frame]
ZERO = frozenset({0})
MAX_MEMORIES = 16


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def span(basis):
    require(len(basis) <= 9, "basis capacity")
    result = {0}
    for vector in basis:
        require(type(vector) is int and 0 < vector < 512, "binary vector")
        require(vector not in result, "independent basis")
        result |= {point ^ vector for point in result}
    return frozenset(result)


def join(*frames):
    result = {0}
    for frame in frames:
        for vector in sorted(frame):
            if vector not in result:
                result |= {point ^ vector for point in result}
    return frozenset(result)


def bitmap(frame):
    return sum(1 << point for point in frame)


def fits(bounds, dimension, frame):
    low, high = bounds
    return len(frame) == 1 << dimension and low <= frame <= high


def contact(left, right, dimension):
    low = join(left[0], right[0])
    high = left[1] & right[1]
    return low <= high and len(low) <= 1 << dimension <= len(high)


@dataclass(frozen=True)
class Model:
    bounds: tuple[tuple[Bounds, ...], ...]
    sources: tuple[tuple[Frame, ...], ...]
    targets: tuple[tuple[Frame, ...], ...]

    def __post_init__(self):
        require(1 <= len(self.bounds) <= 8, "layer capacity")
        require(1 <= len(self.bounds[0]) <= 208, "helper capacity")
        require(len(self.sources) <= 104 and len(self.targets) <= 104, "data capacity")
        for dimension, layer in enumerate(self.bounds, 1):
            require(len(layer) == len(self.bounds[0]), "rectangular layers")
            for low, high in layer:
                require(
                    low <= high and len(low) <= 1 << dimension <= len(high),
                    "nonempty interval",
                )
        for chain in self.sources + self.targets:
            require(len(chain) <= 10, "snapshot capacity")


def layer_relations(model, dimension):
    bounds = model.bounds[dimension - 1]
    adjacency, reads, writes = [], [], []
    for left in bounds:
        adjacency.append(
            [w for w, right in enumerate(bounds) if contact(left, right, dimension)]
        )
        reads.append(
            [
                s
                for s, chain in enumerate(model.sources)
                if any(fits(left, dimension, frame) for frame in chain)
            ]
        )
        writes.append(
            [
                t
                for t, chain in enumerate(model.targets)
                if any(fits(left, dimension, frame) for frame in chain)
            ]
        )
    return adjacency, reads, writes


def insert(memories, candidate):
    if any(old <= candidate for old in memories):
        return
    memories[:] = [old for old in memories if not candidate < old]
    require(len(memories) < MAX_MEMORIES, "memory antichain capacity")
    memories.append(candidate)


def acquire(next_state, model, bounds, reads, dimension, full_memory):
    for helper, sources in enumerate(reads):
        for source in sources:
            for frame in model.sources[source]:
                if fits(bounds[helper], dimension, frame):
                    memory = frame if full_memory else bounds[helper][0]
                    insert(next_state[helper].setdefault(source, []), memory)


def relay(state, next_state, bounds, adjacency, dimension, full_memory):
    for helper, neighbors in enumerate(adjacency):
        low_h, high_h = bounds[helper]
        for writer in neighbors:
            if writer == helper:
                continue
            low_w, high_w = bounds[writer]
            high = high_h & high_w
            for source, memories in state[helper].items():
                for memory in memories:
                    needed = join(memory, low_h, low_w)
                    if needed <= high and len(needed) <= 1 << dimension <= len(high):
                        kept = needed if full_memory else join(low_h, low_w)
                        insert(next_state[writer].setdefault(source, []), kept)


def deliver(outputs, state, model, bounds, writes, dimension):
    for helper, targets in enumerate(writes):
        for target in targets:
            for frame in model.targets[target]:
                if fits(bounds[helper], dimension, frame):
                    for source, memories in state[helper].items():
                        if any(memory <= frame for memory in memories):
                            outputs[target] |= 1 << source


def propagate(model, full_memory):
    """Retain all source bits. No predecessor implementation is executed here."""
    state = [{} for _ in model.bounds[0]]
    outputs = [
        sum(
            1 << s for s, chain in enumerate(model.sources) if set(chain) & set(targets)
        )
        for targets in model.targets
    ]
    high_water = 0
    for dimension, bounds in enumerate(model.bounds, 1):
        adjacency, reads, writes = layer_relations(model, dimension)
        next_state = [
            {s: list(memories) for s, memories in row.items()} for row in state
        ]
        acquire(next_state, model, bounds, reads, dimension, full_memory)
        relay(state, next_state, bounds, adjacency, dimension, full_memory)
        state = next_state
        deliver(outputs, state, model, bounds, writes, dimension)
        high_water = max(
            high_water,
            max(
                (len(memories) for row in state for memories in row.values()), default=0
            ),
        )
    return outputs, high_water
