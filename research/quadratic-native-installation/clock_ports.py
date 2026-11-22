"""Generate every positive raw label from its real chronological epoch and shared role."""

from bisect import bisect_right
from collections.abc import Sequence
from itertools import accumulate

from powered import Port, PoweredWord


class Ports(Sequence):
    """A segment owns literal ports or a prefix and a shared tuple of role/rank pairs."""

    def __init__(self, segments):
        self.segments = tuple(
            (prefix, entries) for prefix, entries in segments if entries
        )
        self.ends = tuple(accumulate(len(entries) for _, entries in self.segments))

    def __len__(self):
        return self.ends[-1] if self.ends else 0

    def __iter__(self):
        for prefix, entries in self.segments:
            if prefix is None:
                yield from entries
            else:
                for role, rank in entries:
                    yield Port((*prefix, role), rank)

    def __getitem__(self, index):
        if isinstance(index, slice):
            return tuple(self[i] for i in range(*index.indices(len(self))))
        if index < 0:
            index += len(self)
        if index < 0 or index >= len(self):
            raise IndexError(index)
        segment = bisect_right(self.ends, index)
        prefix, entries = self.segments[segment]
        offset = index - (self.ends[segment - 1] if segment else 0)
        if prefix is None:
            return entries[offset]
        role, rank = entries[offset]
        return Port((*prefix, role), rank)

    def ranks(self):
        for prefix, entries in self.segments:
            if prefix is None:
                yield from (p.rank for p in entries)
            else:
                yield from (r for _, r in entries)


def clock_word(atlas):
    graph, layout = atlas.graph, atlas.layout
    dims = tuple(map(len, graph["frames"]))
    helpers = tuple(
        (layout["source_labels"][i], dims[b] - dims[a])
        for i, (a, b) in enumerate(zip(graph["initial"], graph["final"], strict=True))
        if i not in atlas.main
    )
    returns = tuple(
        (node, abs(dims[atlas.moves[node][1]] - dims[atlas.moves[node][0]]))
        for node in graph["schedule"]
        if node in atlas.moves
    )
    roots = []
    for kind, root in atlas.roots:
        for i, (sign, entries) in enumerate(atlas.words[kind][1]):
            tag = ("root", kind, root, atlas.offsets[kind, root] + i, sign)
            roots.append(Port(tag, 1 + 8 * len(entries)))
    targets = [(None, tuple(roots))]
    paid = []
    ordinary = []
    for clock, row in enumerate(atlas.instructions()):
        op = row[0]
        if op == "NATIVE":
            if ordinary:
                paid.append((None, tuple(ordinary)))
                ordinary.clear()
            targets.append((("helper", clock, row[1]), helpers))
            paid.append((("return", clock, row[1]), returns))
        elif op == "QUERY" or op.startswith("IDLE_"):
            rank = 1 if op == "QUERY" else 8 * len(row[2]) + int(op == "IDLE_ODD")
            ordinary.append(Port((op, clock, row[1]), rank))
    if ordinary:
        paid.append((None, tuple(ordinary)))
    return PoweredWord(153, Ports(targets), Ports(paid), 128, 16, 12, 12)
