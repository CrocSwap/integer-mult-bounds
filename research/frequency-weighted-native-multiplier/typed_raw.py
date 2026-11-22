"""Generate both raw types from the signed target tags and restore their independent owners."""


class TypedRaw:
    def __init__(self, word, physical):
        self.word, self.physical = word, physical

    def native(self, ports, header):
        kind = header % 2
        columns = header - kind
        if columns <= 0 or len(ports) != len(self.word.targets):
            raise ValueError("Every raw type needs a complete positive even-width job")
        if len({p.owner for p in ports}) != len(ports):
            raise ValueError("Two productive ports share a live field")
        width = columns * (1 + kind)
        bound = []
        for tag, p in zip(self.word.targets, ports, strict=True):
            if len(p.axes) != tag.rank * width:
                raise ValueError("A productive job has the wrong physical rank")
            bound.append((tag.tag, p))
        actual = self.physical.raw(bound, width)
        remaining = 1008 if kind == 0 else 0
        for tag in self.word.paid:
            name, p = next(actual)
            if name != tag.tag or len(p.axes) != tag.rank * width:
                raise ArithmeticError("A raw loan differs from its source")
            if remaining and tag.rank == 1:
                yield p.select(range(width // 2))
                yield p.select(range(width // 2, width))
                remaining -= 1
            else:
                yield p
        if next(actual, None) is not None or remaining:
            raise ArithmeticError("The raw tape did not close")
