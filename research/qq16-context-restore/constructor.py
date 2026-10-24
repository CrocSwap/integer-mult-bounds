"""Finite-handle lowering of the retained Machine.restore_context only.

Mihir Srivastava, with substantial OpenAI Codex assistance. Apache-2.0.
Numerical words and the fixed boundary graph are borrowed, never decoded.
"""
from kernel import Store, access_cost, need

UNSIGNED, RING, COUNT, CONTEXT, PROGRAM = range(2, 7)
ARITY = {UNSIGNED: 1, RING: 4, COUNT: 1, CONTEXT: 8, PROGRAM: 4}
FIELDS = {
    UNSIGNED: ('arena',),
    RING: ('arena', 'raw', 'modulus', 'one'),
    COUNT: ('tape',),
    CONTEXT: ('ring', 'arena', 'raw', 'codes', 'q', 'dimension', 'cap', 'highs'),
    PROGRAM: ('index_arena', 'residue_arena', 'code_bits', 'tape'),
}


class Constructor:
    """F fixed boundary handles; 15 reusable records; at most one held pair.

    The five fixed configuration handles are arena, indices, vocabulary,
    highs Tape, program Tape. Word tables contain the supplied arenas' stable
    slot handles. They are fixed input data, not an object-id/adjacency oracle.
    """
    stride = 9

    def __init__(self, fixed_count, configuration, residue_words, index_words):
        need(type(fixed_count) is int and fixed_count >= 5, 'fixed boundary size')
        need(len(configuration) == 5 and residue_words and index_words,
             'complete fixed constructor interface')
        need(len(residue_words) <= fixed_count and len(index_words) <= fixed_count,
             'bounded word-slot tables')
        values = [*configuration, *residue_words, *index_words]
        need(all(type(x) is int and 1 <= x <= fixed_count for x in values),
             'fixed boundary handles')
        self.fixed = fixed_count
        self.limit = fixed_count + 16  # zero leaf, F fixed, 15 dynamic
        self.extent = fixed_count + len(residue_words) + len(index_words) + 16
        self.store = Store(8*self.extent)
        self.records, _ = self.store.allocate([0]*(self.limit*self.stride))
        for node in range(1, fixed_count+1):
            self.write(node, 0, 1)
        self.config, _ = self.store.allocate(configuration)
        self.residue, self.residue_count = self.store.allocate(residue_words)
        self.index, self.index_count = self.store.allocate(index_words)
        # current context/program/size/depth, held context/program
        self.roots, _ = self.store.allocate([0]*6)
        self.marks, _ = self.store.allocate([0]*15)
        self.stack, _ = self.store.allocate([0]*128)
        self.peak = 0
        self.calls = self.collections = self.holds = self.releases = 0
        self.disposed = False
        # Input range, shape, uniqueness-of-slot position and address arithmetic
        # are bounded scans; source handle aliasing itself is allowed.
        self.store.accesses += 32*self.extent
        self.store.tick(128*self.extent)

    def location(self, node, slot):
        need(type(node) is int and 0 <= node < self.limit and 0 <= slot < self.stride,
             'finite record address')
        self.store.tick(8)
        return self.records + self.stride*node + slot

    def read(self, node, slot):
        return self.store.read(self.location(node, slot))

    def write(self, node, slot, value):
        self.store.write(self.location(node, slot), value)

    def field(self, node, index):
        tag = self.read(node, 0)
        need(tag in ARITY and 0 <= index < ARITY[tag], 'live typed field')
        return self.read(node, 1+index)

    def put(self, node, index, child):
        tag = self.read(node, 0)
        need(tag in ARITY and 0 <= index < ARITY[tag], 'live typed field')
        need(type(child) is int and 0 <= child < self.limit and
             (child == 0 or self.read(child, 0) != 0), 'live child handle')
        self.write(node, 1+index, child)

    def fresh(self, tag):
        need(tag in ARITY, 'fixed constructor tag')
        for node in range(self.fixed+1, self.limit):
            if self.read(node, 0) == 0:
                for slot in range(self.stride):
                    self.write(node, slot, 0)
                self.write(node, 0, tag)
                live = sum(self.read(x, 0) != 0 for x in range(self.fixed+1, self.limit))
                self.peak = max(self.peak, live)
                self.store.tick(64)
                return node
        raise ValueError('constructor transient capacity exhausted')

    def word(self, table, count, slot):
        need(type(slot) is int and 0 <= slot < count, 'declared word slot')
        self.store.tick(8)
        return self.store.read(table+slot)

    def restore(self, labels):
        need(not self.disposed and len(labels) == 5, 'live five-label restoration')
        modulus, one, cap, size, depth = labels
        m = self.word(self.residue, self.residue_count, modulus)
        o = self.word(self.residue, self.residue_count, one)
        c = self.word(self.residue, self.residue_count, cap)
        s = self.word(self.index, self.index_count, size)
        d = self.word(self.index, self.index_count, depth)
        need(sum(self.read(x, 0) == 0 for x in range(self.fixed+1, self.limit)) >= 5,
             'five fresh records before replacement')
        arena, indices, codes, highs, tape = [self.store.read(self.config+i) for i in range(5)]
        ring = self.fresh(RING)
        raw = self.fresh(UNSIGNED)
        self.put(raw, 0, arena)
        for i, child in enumerate((arena, raw, m, o)):
            self.put(ring, i, child)
        context = self.fresh(CONTEXT)
        for i, child in enumerate((ring, arena, raw, codes, 0, 0)):
            self.put(context, i, child)
        count = self.fresh(COUNT)
        self.put(count, 0, highs)
        self.put(context, 6, c)
        self.put(context, 7, count)
        self.store.write(self.roots, context)
        self.store.write(self.roots+2, s)
        self.store.write(self.roots+3, d)
        program = self.fresh(PROGRAM)
        for i, child in enumerate((indices, arena, 0, tape)):
            self.put(program, i, child)
        self.store.write(self.roots+1, program)
        self.store.tick(256)  # fixed source dispatch/tuple-unpack bookkeeping
        self.calls += 1
        self.collect()

    def hold(self):
        need(not self.disposed and self.store.read(self.roots+4) == 0 and
             self.store.read(self.roots+5) == 0, 'one borrowed prior pair')
        need(self.store.read(self.roots) != 0, 'hold an initialized pair')
        for i in range(2):
            self.store.write(self.roots+4+i, self.store.read(self.roots+i))
        self.store.tick(32)
        self.holds += 1

    def release(self):
        need(not self.disposed, 'live release')
        self.store.write(self.roots+4, 0)
        self.store.write(self.roots+5, 0)
        self.store.tick(32)
        self.releases += 1
        self.collect()

    def collect(self):
        """Finite mark/sweep follows all stored references, including codes."""
        self.collections += 1
        for i in range(15):
            self.store.write(self.marks+i, 0)
        top = 0
        for i in (0, 1, 4, 5):
            self.store.write(self.stack+top, self.store.read(self.roots+i))
            top += 1
        while top:
            self.store.tick(32)
            top -= 1
            node = self.store.read(self.stack+top)
            if node <= self.fixed:
                continue
            need(node < self.limit and self.read(node, 0) in ARITY,
                 'retained reference to a live constructor object')
            mark = self.marks + node-self.fixed-1
            if self.store.read(mark):
                continue
            self.store.write(mark, 1)
            for i in range(ARITY[self.read(node, 0)]):
                need(top < 128, 'finite collector stack')
                self.store.write(self.stack+top, self.field(node, i))
                top += 1
        for node in range(self.fixed+1, self.limit):
            if not self.store.read(self.marks+node-self.fixed-1):
                for slot in range(self.stride):
                    self.write(node, slot, 0)
        self.store.tick(256)

    def meter(self):
        """Read-only simulator receipt; no aggregate one-invocation kernel cap."""
        return dict(accesses=self.store.accesses, scalar=self.store.scalar)

    def dispose(self):
        need(not self.disposed, 'one metadata disposal')
        need(self.store.read(self.roots+4) == 0 and self.store.read(self.roots+5) == 0,
             'release borrowed pair before disposal')
        # Full owned padded-store disposal; borrowed numerical/Tape bodies untouched.
        self.store.accesses += self.store.limit['capacity']
        self.store.cells[:] = [0]*len(self.store.cells)
        self.disposed = True

    def tariff(self):
        """Constructive conservative complete metadata-session upper bound."""
        q = self.store.limit['capacity']
        w = self.store.width
        accesses = 2*q + 128*self.extent + 4096*self.calls + 4096*self.collections
        accesses += 64*(self.holds+self.releases)
        scalar = 512*self.extent + 65536*(self.calls+self.collections)
        scalar += 1024*(self.holds+self.releases)
        return dict(capacity=q, width=w, accesses=accesses, scalar=scalar,
                    bits=accesses*access_cost(q, w)+scalar*(16*w+16))
