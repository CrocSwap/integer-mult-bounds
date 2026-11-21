"""Bind a powered chronological word to the strict-rule compiler."""

from dataclasses import dataclass
from itertools import product
from math import prod

from periodic import Rule


@dataclass(frozen=True)
class Port:
    tag: tuple
    rank: int


@dataclass(frozen=True)
class Block:
    tags: tuple
    first: int
    rank: int


@dataclass(frozen=True)
class PoweredWord:
    ambient: int
    targets: tuple
    paid: tuple
    power: int
    floor: int
    low_cut: int
    high_cut: int

    def target(self, indices):
        return Port(tuple(self.targets[i].tag for i in indices),
                    prod(self.targets[i].rank for i in indices))

    def target_paths(self):
        for indices in product(range(len(self.targets)), repeat=self.power):
            port = self.target(indices)
            yield port, port.rank >= self.floor ** self.power

    def blocks(self, indices):
        rank = prod(self.paid[i].rank for i in indices)
        cap = (self.low_cut if self.paid[indices[0]].rank <= 4 else self.high_cut) ** self.power
        tags = tuple(self.paid[i].tag for i in indices)
        for first in range(0, rank, cap):
            yield Block(tags, first, min(cap, rank - first))

    def paid_paths(self):
        for indices in product(range(len(self.paid)), repeat=self.power):
            yield from self.blocks(indices)

    def tables(self, target_sink, paid_sink):
        """Write original labels, zero assignments, true split offsets and ranks."""
        for port, keep in self.target_paths():
            target_sink(port, keep)
        for child in self.paid_paths():
            paid_sink(child)

    def rule(self):
        """Use resident tables where available. The tape output follows tables()."""
        return Rule(self.ambient ** self.power,
                    tuple(p.rank for p, keep in self.target_paths() if keep),
                    tuple(p.rank for p in self.paid_paths()))

    def native(self, productive, columns, physical):
        """Run each raw occurrence and yield the actual owner's split job in turn.

        raw receives (raw port tag, full job) pairs. It applies complete native
        entry/exit charts and local instructions, yielding (paid tag, full job).
        fresh receives a full ambient exemplar, active extent and zero port path.
        """
        live = iter(productive)
        if not productive:
            raise ValueError("At least one retained productive field is required")
        exemplar = productive[0]
        fields, owned = {}, []
        for indices in product(range(len(self.targets)), repeat=self.power):
            port = self.target(indices)
            if port.rank >= self.floor ** self.power:
                job = next(live)
            else:
                job = physical.fresh(exemplar, port.rank * columns, port.tag)
                owned.append(job)
            if len(job.axes) != port.rank * columns:
                raise ValueError("Wrong extent at original productive location")
            fields[indices] = job
        sentinel = object()
        if next(live, sentinel) is not sentinel:
            raise ValueError("Unbound productive owner")

        def tensor(depth, ports, factor, prefix):
            frames = {}
            for suffix in product(range(len(self.targets)), repeat=depth - 1):
                axes = prod(self.targets[i].rank for i in suffix)
                inputs = tuple((port.tag, ports[(i,) + suffix])
                               for i, port in enumerate(self.targets))
                frames[suffix] = iter(physical.raw(inputs, factor * axes))
            for j, cut in enumerate(self.paid):
                requests = {}
                for suffix, frame in frames.items():
                    tag, job = next(frame)
                    axes = prod(self.targets[i].rank for i in suffix)
                    if tag != cut.tag or len(job.axes) != cut.rank * factor * axes:
                        raise ValueError("Wrong chronological raw request or extent")
                    requests[suffix] = job
                full = prefix + (j,)
                if depth > 1:
                    yield from tensor(depth - 1, requests, factor * cut.rank, full)
                else:
                    native_job = requests[()]
                    for block in self.blocks(full):
                        first = block.first * columns
                        yield native_job.select(range(first, first + block.rank * columns))
            for frame in frames.values():
                if next(frame, sentinel) is not sentinel:
                    raise ValueError("Pending raw request after its final slot")
        yield from tensor(self.power, fields, columns, ())
        for job in reversed(owned):
            physical.retire(job)


def bit_word(targets, paid):
    return PoweredWord(134, tuple(targets), tuple(paid), 480, 16, 10, 11)


def complex_word(targets, paid):
    return PoweredWord(153, tuple(targets), tuple(paid), 264, 17, 10, 10)
