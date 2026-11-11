"""Produce CRT entry streams from declared padded axis records.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
"""


def canonical_end(target, words, records):
    """Remove high zero bits by local moves. Keep one bit for zero."""
    target.step(-1)
    while target.read() == words.ZERO:
        target.write(words.BLANK)
        target.step(-1)
    if target.read() in (records.ROOT, records.WORD_END):
        target.step(1)
        target.append(words.ZERO)
    else:
        words.need(target.read() == words.ONE, 'last nonzero bit')
        target.step(1)
    target.append(records.WORD_END)


class RowEntry:
    """The topology is compile-time data. Axis fields stay on tapes."""

    def __init__(self, words, records, entry, producer, source, dirty,
                 widths, ell, level, start, global_row):
        w, r = words, records
        d = len(widths)
        w.need(d >= 2 and d & (d - 1) == 0, 'power-of-two axis count')
        w.need(type(ell) is int and ell >= 2, 'compiled ell')
        w.need(all(type(h) is int and h in (ell - 1, ell) for h in widths),
               'compiled width family')
        w.need(type(level) is int and 1 <= level < d.bit_length(), 'compiled level')
        size = 1 << level
        w.need(type(start) is int and 0 <= start <= d - size and start % size == 0,
               'compiled tree node')
        w.need(type(global_row) is int and 0 <= global_row < 2 * ell - 1,
               'compiled global row')
        middle, stop = start + size // 2, start + size
        self.active = tuple(i for i in range(middle, stop)
                            if widths[i] == ell or global_row not in (ell - 1, ell))
        w.need(len(dirty) == 8 and len({id(x) for x in (source, *dirty)}) == 9,
               'distinct source and dirty roles')
        self.w, self.r = w, r
        self.context, self.result, self.inputs = None, None, ()
        if not self.active:
            return
        self.guide, self.left, self.right = (entry.Port(w) for _ in range(3))
        self.inputs = (self.guide, self.left, self.right)
        for axis, h in enumerate(widths):
            selected = start <= axis < stop
            target = self.left if axis < middle else self.right
            w.need(source.read() == r.ROOT, 'axis record tag')
            source.step(1)
            if selected:
                target.append(r.ROOT)
            for _ in range(h):
                w.need(source.read() == w.ONE, 'declared unary width')
                source.step(1)
                if selected:
                    self.guide.append(w.ONE)
            w.need(source.read() == r.WORD_END, 'width delimiter')
            source.step(1)
            for delimiter in (r.WORD_END, r.RECORD_END):
                for _ in range(h):
                    bit = source.read()
                    w.need(bit in (w.ZERO, w.ONE), 'declared padded field')
                    source.step(1)
                    if selected:
                        target.append(bit)
                w.need(source.read() == delimiter, 'axis field delimiter')
                source.step(1)
                if selected:
                    canonical_end(target, w, r)
            if selected:
                target.append(r.RECORD_END)
        w.need(source.read() == w.RIGHT, 'complete axis stream')
        source.rewind()
        self.guide.append(w.ONE)
        self.guide.rewind()
        for target in (self.left, self.right):
            target.append(w.RIGHT)
            target.rewind()
        self.context = entry.Entry(w, r, self.guide, dirty)
        self.result = self.context.invoke(producer, self.left, self.right)

    def close(self):
        if self.context is None:
            return
        self.context.consume(self.result)
        self.context.close()
        for port in self.inputs:
            port.retire()
