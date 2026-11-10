"""Sequential original-coordinate tensor-image extraction.
Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
"""
from cardinal_counts import Count, positive
from encoded import compare, subtract
from gaussian_rationals import read_count, write_count
from records import Tape
from ring_words import power_two
from router_metadata import indices, owned
from scratch_pool import ScratchPool
from session import OuterScope, borrowed_count, borrowed_tape, erase_marker, initialize_marker, sealed_constructors
from stream import Counter
from words import BLANK, RIGHT, ZERO, ONE, need


def copy_stream(source, target):
    source.rewind()
    while source.read() != BLANK:
        target.append(source.read()); source.step(1)
    source.rewind()


def next_axis(ell, s, j, r, coordinate):
    """One mixed-radix successor; only encoded arithmetic observes sizes."""
    new_j = Count(j); new_j.increment()
    if compare(new_j, s) == 0:
        new_j.close()
        return Count.literal(0), Count(s), Count.literal(0), True
    new_r, new_coordinate = Count(r), Count(coordinate)
    with owned(power_two(ell), Count(s)) as (t, twice_s):
        twice_s.multiply_small(2)
        with owned(subtract(t, s)) as (twice_e,):
            twice_e.multiply_small(2); new_r.add(twice_e)
        new_coordinate.increment()
        if compare(new_r, twice_s) >= 0:
            reduced = subtract(new_r, twice_s); new_r.close(); new_r = reduced
            new_coordinate.increment()
    return new_j, new_r, new_coordinate, False


class Extract:
    """Fixed tape inventory; borrowed prepared Count packet D,(ell,s)^D and q.

    Axis zero is fastest. External B records have two q+3-bit components and
    one '#' separator. Payload and descriptor arrays are never host-decoded.
    """
    def __init__(self, B, descriptors, q):
        self.B = B
        descriptors, q = borrowed_tape(descriptors), borrowed_count(q)
        need(descriptors is not q.tape, 'distinct prepared descriptor ports')
        self.borrowed = (descriptors, q.tape)
        self.pool = ScratchPool(160); self.scope = OuterScope(self.pool)
        self.meta, self.initial, self.first, self.second = (Tape() for _ in range(4))
        self.native = (*self.pool.tapes, self.meta, self.initial, self.first, self.second)
        need(all(t not in self.native for t in self.borrowed), 'external prepared descriptors')
        self.output = B.Tape('original-q-extraction-output')
        self.pending = self.finished = False
        self.closed = True
        for t in self.native: erase_marker(t); initialize_marker(t)
        prepared = False
        try:
            with sealed_constructors(), self.scope.installed():
                try:
                    descriptors.rewind(); positive(q)
                    with owned(read_count(descriptors), Count.literal(0), Count.literal(1), Count(q)) as (D, n, S, bits):
                        positive(D); bits.increment(); bits.increment(); bits.increment(); bits.multiply_small(2)
                        for _ in indices(D):
                            with owned(read_count(descriptors)) as (ell,):
                                with owned(read_count(descriptors)) as (s,):
                                    positive(ell); positive(s)
                                    with owned(power_two(ell), Count(s)) as (t, twice_s):
                                        twice_s.multiply_small(2)
                                        need(compare(s, t) < 0 and compare(t, twice_s) < 0, 'strict original dyadic axis admission')
                                    n.add(ell)
                                    product = Count.product(S, s)
                                    borrowed_tape(S.tape).clear(); copy_stream(product.tape, S.tape); S.rewind(); product.close()
                                    with owned(Count.literal(0)) as (zero,):
                                        for value in (ell, s, zero, s, zero): write_count(value, self.initial)
                        need(descriptors.read() == BLANK, 'complete prepared axis packet')
                        with owned(power_two(n)) as (T,):
                            for value in (D, bits, T, S, n): write_count(value, self.meta)
                    prepared = True
                finally:
                    descriptors.rewind(); q.rewind(); self.pool.empty()
        finally:
            for t in self.pool.tapes: erase_marker(t)
            for t in (self.meta, self.initial, self.first, self.second):
                if not prepared: t.clear(); erase_marker(t)
                else: t.rewind()

    def advance(self, D):
        """Rewrite one packed axis state and concatenate original target bits."""
        self.first.rewind(); self.second.clear()
        address = Count.literal(0); borrowed_tape(address.tape).clear()
        carry = True
        try:
            for _ in indices(D):
                with owned(read_count(self.first), read_count(self.first), read_count(self.first),
                           read_count(self.first), read_count(self.first)) as (ell, s, j, r, coordinate):
                    if carry:
                        a, b, c, carry = next_axis(ell, s, j, r, coordinate)
                    else:
                        a, b, c = Count(j), Count(r), Count(coordinate)
                    with owned(a, b, c):
                        for value in (ell, s, a, b, c): write_count(value, self.second)
                        c.rewind()
                        for _ in indices(ell):
                            bit = c.read()
                            if bit == RIGHT: bit = ZERO
                            else: c.step(1)
                            need(bit in (ZERO, ONE), 'original target coordinate digit')
                            address.tape.append(bit)
                        need(c.read() == RIGHT, 'coordinate fits original dyadic axis')
                        c.rewind()
            need(not carry and self.first.read() == BLANK, 'nonterminal complete tensor successor')
            address.tape.append(RIGHT); address.normalize()
            self.first, self.second = self.second, self.first
            self.first.rewind(); self.second.clear()
            return address
        except BaseException:
            address.close(); raise

    def run(self, source):
        B = self.B
        need(type(source) is B.Tape and source is not self.output, 'distinct external framed field')
        need(self.closed and not self.pending and not self.finished, 'consume protected extraction return')
        for t in self.pool.tapes: initialize_marker(t)
        self.closed = False; succeeded = False
        try:
            with sealed_constructors(), self.scope.installed():
                try:
                    self.meta.rewind(); self.first.clear(); self.second.clear()
                    copy_stream(self.initial, self.first); self.first.rewind()
                    B.clear(self.output); B.home(source)
                    with owned(read_count(self.meta), read_count(self.meta), read_count(self.meta),
                               read_count(self.meta), read_count(self.meta)) as (D, bits, T, S, n):
                        need(self.meta.read() == BLANK, 'complete prepared extraction metadata')
                        address = Count.literal(0)
                        try:
                            with owned(Counter(S)) as (remaining,):
                                for index in indices(T):
                                    keep = not remaining.finished and compare(index, address) == 0
                                    for _ in indices(bits):
                                        symbol = source.read(); need(symbol in ('0', '1'), 'complete framed payload bits')
                                        if keep: B.append(self.output, symbol)
                                        source.move(1)
                                    need(source.read() == '#', 'complete framed record separator')
                                    if keep: B.append(self.output, '#')
                                    source.move(1)
                                    if keep:
                                        remaining.decrement()
                                        if not remaining.finished:
                                            replacement = self.advance(D); address.close(); address = replacement
                                            need(compare(address, index) > 0 and compare(address, T) < 0,
                                                 'strict next original image address')
                                need(remaining.finished and source.read() == '!', 'complete full padded input and compact output')
                        finally: address.close()
                    self.pending = succeeded = True
                finally:
                    B.home(source); B.home(self.output)
                    self.meta.rewind(); self.initial.rewind()
                    self.first.clear(); self.second.clear(); self.pool.empty()
        finally:
            for t in self.pool.tapes: erase_marker(t)
            if not succeeded: B.clear(self.output)
            self.closed = True
        return self.output

    def consume(self):
        need(self.closed and self.pending and not self.finished, 'one protected extraction output')
        self.B.clear(self.output); self.pending = False

    def close(self):
        need(self.closed and not self.pending and not self.finished, 'quiescent extraction owner')
        self.finished = True
        for t in (self.meta, self.initial, self.first, self.second): t.clear(); erase_marker(t)
