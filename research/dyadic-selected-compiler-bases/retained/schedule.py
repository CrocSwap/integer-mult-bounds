"""Expand a normalized native word to rank-one requests on a fixed ambient space."""

from dataclasses import dataclass
from functools import cache
from fractions import Fraction


@dataclass(frozen=True)
class Word:
    ambient: int
    grade: int
    roles: int
    paid: tuple[int, ...]

    def __post_init__(self):
        if not 2 <= self.grade <= self.ambient or self.roles < 1:
            raise ValueError("invalid productive interface")
        if any(not 1 <= rank < self.grade for rank in self.paid):
            raise ValueError("a paid rank does not decrease")

    def depth(self, rank):
        height = 0
        largest = max(self.paid, default=0)
        while rank >= self.grade:
            rank = largest * (rank // self.grade)
            height += 1
        return height

    def tile_size(self, ambient):
        if ambient < 1:
            raise ValueError("a root must have a positive rank")
        capacity = self.grade * (ambient // self.ambient)
        return capacity or ambient

    def tiles(self, ambient):
        size = self.tile_size(ambient)
        for start in range(0, ambient, size):
            yield range(start, min(start + size, ambient))

    def root_width(self, ambient):
        if ambient < self.ambient:
            return 1
        first = self.grade * (ambient // self.ambient)
        return self.roles ** self.depth(first)

    def leaves_per_array(self, ambient):
        """Count leaf requests independently of the choice of storage."""
        size = self.tile_size(ambient)
        if ambient < self.ambient:
            return Fraction(ambient)

        @cache
        def inside(rank):
            columns, tail = divmod(rank, self.grade)
            if not columns:
                return Fraction(rank)
            children = sum((inside(child * columns) for child in self.paid), Fraction())
            return tail + children / self.roles

        count, last = divmod(ambient, size)
        return count * inside(size) + inside(last)


def complete_order(active, ambient):
    used = set(active)
    if len(used) != len(active) or any(i < 0 or i >= ambient for i in used):
        raise ValueError("the requested coordinates must be distinct ambient axes")
    return tuple(active) + tuple(i for i in range(ambient) if i not in used)


def expand(word, ambient, owners, machine):
    """Call machine.native on whole owners. It yields each normalized paid request.

    A native instance takes distinct fields in its declared role order. It performs
    its local instructions and yields (owner, axes) at each paid position. It keeps
    its own adapters and scratch until control returns. The machine implements
    move(owner, order, inverse), leaf(owner, axis) and native(owners, columns).
    """
    width = word.root_width(ambient)
    if len(owners) != width or len(set(owners)) != width:
        raise ValueError("the root needs its full batch of distinct owners")

    def satisfy(jobs):
        rank = len(jobs[0][1])
        if any(len(axes) != rank for _, axes in jobs):
            raise ValueError("a chronological batch must have one rank")
        if len({owner for owner, _ in jobs}) != len(jobs):
            raise ValueError("a chronological batch reused an owner")
        placements = [(owner, complete_order(axes, ambient)) for owner, axes in jobs]
        for owner, order in placements:
            machine.move(owner, order, False)
        columns, tail = divmod(rank, word.grade)
        if columns:
            if columns * word.ambient > ambient or len(jobs) % word.roles:
                raise ValueError("the native instance lacks axes or independent rows")
            paths = []
            for start in range(0, len(jobs), word.roles):
                group = [owner for owner, _ in jobs[start:start + word.roles]]
                paths.append(iter(machine.native(group, columns)))
            for paid in word.paid:
                requests = [next(path) for path in paths]
                if any(len(axes) != paid * columns for _, axes in requests):
                    raise ValueError("native chronology disagrees with the paid rank")
                satisfy(requests)
            sentinel = object()
            if any(next(path, sentinel) is not sentinel for path in paths):
                raise ValueError("a native paid position was omitted")
        for owner, order in placements:
            for axis in range(rank - tail, rank):
                machine.leaf(owner, axis)
            machine.move(owner, order, True)

    if ambient < word.ambient:
        for axis in range(ambient):
            machine.leaf(owners[0], axis)
        return
    for tile in word.tiles(ambient):
        satisfy([(owner, tile) for owner in owners])
