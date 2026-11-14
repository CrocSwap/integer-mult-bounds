"""Tape-driven balanced-node selection into the unchanged CRT numerical entry.

No runtime width, axis count, start, level or precision is decoded. All variable
iteration is driven by local symbols on the supplied source or owned unary
tapes. Numeric arithmetic and its 63-role bank are pinned predecessor code.
Prepared for CubeJerry with substantial OpenAI assistance. Apache-2.0.
"""
from types import SimpleNamespace


COUNTERS = ('axis', 'depth', 'halve_a', 'halve_b', 'half', 'double', 'width')
GUARDS = ('g0', 'g1', 'g2', 'g3', 'g4', 'g5', 'g6', 'g7')


class Iterator:
    """One numerical result at a time; source contents stay read-only.

The supplied source has the #5353 tagged padded-axis encoding and enters at
head one. Construction charges shape manufacture. next() takes no geometry
arguments. The physical interface is linear-use: consume the current lease
once before the next result and relinquish its borrowed aliases. Historical
Python-handle identity checks are interpreter guards, not a tape service.
"""
    def __init__(self, words, records, entry, numeric, owner, canonical, source):
        self.w, self.r, self.e = words, records, entry
        self.numeric, self.canonical, self.source = numeric, canonical, source
        self.bank = owner.Bank(words, entry)
        self.guards = tuple(entry.Port(words) for _ in GUARDS)
        for port in self.guards:
            port.retire()
        self.counters = {name: entry.Port(words) for name in COUNTERS}
        self.live, self.closed = False, False
        try:
            self._shape()
        except ValueError:
            # Source framing errors and nondyadic counts precede numerical entry.
            source.rewind()
            for port in self.counters.values():
                port.retire()
            self.closed = True
            raise

    def _record(self, target=None, guide=None):
        """Read one exact axis record; optionally project its canonical pair."""
        w, r, source = self.w, self.r, self.source
        width = self.counters['width']
        width.clear()
        w.need(source.read() == r.ROOT, 'axis tag')
        source.step(1)
        if target is not None:
            target.append(r.ROOT)
        seen = False
        while source.read() == w.ONE:
            seen = True
            width.append(w.ONE)
            if guide is not None:
                guide.append(w.ONE)
            source.step(1)
        w.need(seen and source.read() == r.WORD_END, 'positive unary width')
        source.step(1)
        width.append(w.RIGHT)
        width.rewind()
        for delimiter in (r.WORD_END, r.RECORD_END):
            while width.read() == w.ONE:
                bit = source.read()
                w.need(bit in (w.ZERO, w.ONE), 'padded source bit')
                if target is not None:
                    target.append(bit)
                source.step(1)
                width.step(1)
            w.need(width.read() == w.RIGHT and source.read() == delimiter,
                   'exact source field extent')
            source.step(1)
            width.rewind()
            if target is not None:
                self.canonical.canonical_end(target, w, r)
        if target is not None:
            target.append(r.RECORD_END)
        width.clear()

    def _many(self, port):
        w = self.w
        w.need(port.read() == w.ONE, 'nonempty reduction count')
        port.step(1)
        symbol = port.read()
        w.need(symbol in (w.ONE, w.RIGHT), 'unary reduction shape')
        port.rewind()
        return symbol == w.ONE

    def _shape(self):
        w, source = self.w, self.source
        axis, depth = self.counters['axis'], self.counters['depth']
        current, spare = self.counters['halve_a'], self.counters['halve_b']
        while source.read() != w.RIGHT:
            self._record()
            axis.append(w.ONE)
            current.append(w.ONE)
        source.rewind()
        axis.append(w.RIGHT)
        axis.rewind()
        current.append(w.RIGHT)
        current.rewind()
        w.need(self._many(current), 'at least two source axes')
        while self._many(current):
            depth.append(w.ONE)
            odd = False
            while current.read() == w.ONE:
                odd = not odd
                if not odd:
                    spare.append(w.ONE)
                current.step(1)
            w.need(current.read() == w.RIGHT and not odd, 'dyadic source axis count')
            spare.append(w.RIGHT)
            spare.rewind()
            current.clear()
            current, spare = spare, current
        current.clear()
        spare.clear()
        depth.append(w.RIGHT)
        depth.rewind()
        half = self.counters['half']
        half.append(w.ONE)
        half.append(w.RIGHT)
        half.rewind()
        w.need(axis.read() == w.ONE, 'first axis')
        axis.write(self.r.STEP)  # Unique current-node marker.

    def _prepare_guards(self, guide):
        w = self.w
        for port in self.guards:
            port.step(-1)
            w.need(port.read() == w.BLANK, 'retired protected marker')
            port.write(w.LEFT)
            port.step(1)
            while guide.read() == w.ONE:
                w.need(port.read() == w.BLANK, 'retired protected body')
                port.write(w.ZERO)
                port.step(1)
                guide.step(1)
            w.need(guide.read() == w.BLANK and port.read() == w.BLANK,
                   'current protected extent')
            port.write(w.RIGHT)
            port.rewind()
            guide.rewind()

    def _entry(self, w, r, adapter, numeric, source, dirty,
               widths, ell, level, start, row):
        # Bank.open's fixed call signature is preserved. Geometry is never supplied.
        w.need(widths is None and ell is None and level is None and
               start is None and row is None, 'no host geometry arguments')
        w.need(source is self.source and dirty is self.guards, 'actual borrowed ports')
        return NodeEntry(self, adapter)

    def next(self):
        self.w.need(not self.live, 'previous node result must close')
        if self.closed:
            return None
        self.w.need(self.counters['depth'].read() == self.w.ONE, 'active encoded level')
        self.live = True
        bridge = SimpleNamespace(RowEntry=self._entry)
        lease = self.bank.open(self.r, self.numeric, bridge, self.source, self.guards,
                               None, None, None, None, None)
        return NodeLease(self, lease)

    def _double_half(self):
        w = self.w
        half, temporary = self.counters['half'], self.counters['double']
        while half.read() == w.ONE:
            temporary.append(w.ONE)
            half.step(1)
        w.need(half.read() == w.RIGHT, 'half-size delimiter')
        half.write(w.BLANK)
        temporary.append(w.RIGHT)
        temporary.rewind()
        while temporary.read() == w.ONE:
            half.append(w.ONE)
            temporary.step(1)
        w.need(temporary.read() == w.RIGHT, 'copied half size')
        half.append(w.RIGHT)
        half.rewind()
        temporary.clear()

    def _advance(self, last):
        w, r = self.w, self.r
        axis, depth = self.counters['axis'], self.counters['depth']
        while axis.read() != r.STEP:
            w.need(axis.read() == w.ONE, 'preserved current cursor')
            axis.step(1)
        axis.write(w.ONE)
        if last:
            while axis.read() != w.RIGHT:
                w.need(axis.read() == w.ONE, 'last-node suffix')
                axis.step(1)
            axis.rewind()
            depth.step(1)
            if depth.read() == w.RIGHT:
                self.close()
                return
            w.need(depth.read() == w.ONE, 'next encoded level')
            self._double_half()
            axis.write(r.STEP)
        else:
            while axis.read() != r.VALUE:
                w.need(axis.read() == w.ONE, 'next-node interval')
                axis.step(1)
            axis.write(r.STEP)
            axis.rewind()

    def close(self):
        self.w.need(not self.live and not self.closed, 'retired iterator closes once')
        for port in self.counters.values():
            port.retire()
        self.closed = True


class NodeEntry:
    """Actual canonical streams and precision guide into unchanged Entry."""
    def __init__(self, iterator, adapter):
        self.iterator = iterator
        w, r, source = iterator.w, iterator.r, iterator.source
        self.guide, self.left, self.right = (adapter.Port(w), adapter.Port(w), adapter.Port(w))
        self.inputs = (self.guide, self.left, self.right)
        self.active = True
        axis, half = iterator.counters['axis'], iterator.counters['half']
        while axis.read() != r.STEP:
            w.need(axis.read() == w.ONE, 'prefix cursor')
            iterator._record()
            axis.step(1)
        for target in (self.left, self.right):
            while half.read() == w.ONE:
                w.need(axis.read() in (w.ONE, r.STEP), 'complete selected node')
                iterator._record(target, self.guide)
                axis.step(1)
                half.step(1)
            w.need(half.read() == w.RIGHT, 'encoded half extent')
            half.rewind()
            target.append(w.RIGHT)
            target.rewind()
        self.last = axis.read() == w.RIGHT
        if not self.last:
            w.need(axis.read() == w.ONE, 'following source axis')
            axis.write(r.VALUE)  # Pending next cursor; current cursor survives handoff.
        axis.rewind()
        source.rewind()
        self.guide.append(w.ONE)
        self.guide.rewind()
        iterator._prepare_guards(self.guide)
        self.context = adapter.Entry(w, r, self.guide, iterator.guards)
        self.result = self.context.invoke(iterator.numeric, self.left, self.right)

    def close(self):
        self.context.consume(self.result)
        self.context.close()
        for port in self.inputs:
            port.retire()
        for port in self.iterator.guards:
            port.retire()


class NodeLease:
    """Interpreter wrapper for the single current linear-use continuation.

The closed flag also guards stale Python references, but the fixed-role
physical theorem does not implement an unbounded stale-handle history.
"""
    def __init__(self, iterator, lease):
        self.iterator, self.lease = iterator, lease
        self.actual = lease.actual
        self.closed = False

    def close(self):
        self.iterator.w.need(not self.closed, 'node lease closes once')
        last = self.actual.last
        self.lease.close()
        self.closed = True
        self.iterator.live = False
        self.iterator._advance(last)
