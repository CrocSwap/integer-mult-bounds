"""Paid whole-node CRT result projection into the actual encoded source.

Prepared for Jerry Chen / CubeJerry with substantial OpenAI assistance.
Apache-2.0. The fixed predecessor providers are pinned in INPUT-PINS.json.
No coordinate, modulus, width, level or axis count enters host control.
"""


class Endpoint:
    """One encoded forward balanced address-state traversal, 79 owned roles."""

    def __init__(self, frontend, words, records, entry, numeric, owner,
                 canonical, source):
        self.w, self.r, self.source = words, records, source
        self.iterator = frontend.Iterator(words, records, entry, numeric,
                                          owner, canonical, source)
        self.staging = entry.Port(words)
        self.staging.retire()
        self.pending = False

    def _copy(self, expected):
        w = self.w
        w.need(self.source.read() == expected, 'preserved source delimiter')
        self.staging.append(expected)
        self.source.step(1)

    def _field(self, width):
        w = self.w
        while width.read() == w.ONE:
            bit = self.source.read()
            w.need(bit in (w.ZERO, w.ONE), 'source padded bit')
            self.staging.append(bit)
            self.source.step(1)
            width.step(1)
        w.need(width.read() == w.RIGHT, 'source width extent')
        width.rewind()

    def _updated(self, width, result, guide):
        w, r = self.w, self.r
        w.need(result.read() == r.ROOT, 'whole-node result record')
        result.step(1)
        while guide.read() == w.ONE:
            w.need(result.read() in (w.ZERO, w.ONE), 'offset bit')
            result.step(1)
            guide.step(1)
        w.need(guide.read() == w.BLANK and result.read() == r.WORD_END,
               'whole offset consumed')
        result.step(1)
        guide.rewind()
        while width.read() == w.ONE:
            old, new = self.source.read(), result.read()
            w.need(old in (w.ZERO, w.ONE) and new in (w.ZERO, w.ONE),
                   'current and updated coordinate bits')
            w.need(guide.read() == w.ONE, 'updated field covers source width')
            self.staging.append(new)
            self.source.step(1)
            result.step(1)
            width.step(1)
            guide.step(1)
        w.need(width.read() == w.RIGHT, 'updated source width')
        width.rewind()
        while guide.read() == w.ONE:
            w.need(result.read() == w.ZERO, 'updated value fits declared width')
            result.step(1)
            guide.step(1)
        w.need(guide.read() == w.BLANK and result.read() == r.WORD_END,
               'complete updated field')
        result.step(1)
        guide.rewind()
        w.need(result.read() == r.RECORD_END, 'whole-node result end')
        result.step(1)

    def _record(self, result=None, guide=None):
        w, r = self.w, self.r
        width = self.iterator.counters['width']
        self._copy(r.ROOT)
        seen = False
        while self.source.read() == w.ONE:
            seen = True
            self.staging.append(w.ONE)
            width.append(w.ONE)
            self.source.step(1)
        w.need(seen, 'positive source width')
        self._copy(r.WORD_END)
        width.append(w.RIGHT)
        width.rewind()
        self._field(width)
        self._copy(r.WORD_END)
        if result is None:
            self._field(width)
        else:
            self._updated(width, result, guide)
        self._copy(r.RECORD_END)
        width.clear()

    def stage(self, lease):
        """Snapshot the next complete source while its numerical lease is live."""
        w, r, it = self.w, self.r, self.iterator
        w.need(it.live and not self.pending, 'one live unstaged node result')
        self.staging.step(-1)
        w.need(self.staging.read() == w.BLANK, 'retired staging origin')
        self.staging.write(w.LEFT)
        self.staging.step(1)
        axis, half = it.counters['axis'], it.counters['half']
        result, guide = lease.actual.result['stream'], lease.actual.guide
        while axis.read() != r.STEP:
            w.need(axis.read() == w.ONE, 'current node prefix')
            self._record()
            axis.step(1)
        for selected in (False, True):
            while half.read() == w.ONE:
                w.need(axis.read() in (w.ONE, r.STEP), 'complete current node')
                self._record(result if selected else None, guide)
                axis.step(1)
                half.step(1)
            w.need(half.read() == w.RIGHT, 'current node half extent')
            half.rewind()
        w.need(result.read() == w.RIGHT, 'all right-coordinate results consumed')
        while self.source.read() != w.RIGHT:
            w.need(axis.read() in (w.ONE, r.VALUE), 'unchanged source suffix')
            self._record()
            axis.step(1)
        w.need(axis.read() == w.RIGHT, 'complete source and cursor extents')
        self.staging.append(w.RIGHT)
        self.staging.rewind()
        self.source.rewind()
        axis.rewind()
        result.rewind()
        self.pending = True

    def commit(self):
        """After retirement, overwrite equal-length source and erase the copy."""
        w, it = self.w, self.iterator
        w.need(self.pending and not it.live and not it.bank.busy,
               'source update follows numerical retirement')
        while self.staging.read() != w.RIGHT:
            self.source.write(self.staging.read())
            self.source.step(1)
            self.staging.step(1)
        w.need(self.source.read() == w.RIGHT, 'preserved full source extent')
        self.source.rewind()
        self.staging.retire()
        self.pending = False

    def step(self):
        self.w.need(not self.pending, 'previous staged update must commit')
        lease = self.iterator.next()
        if lease is None:
            return False
        self.stage(lease)
        lease.close()
        self.commit()
        return True

    def run(self):
        while self.step():
            pass
