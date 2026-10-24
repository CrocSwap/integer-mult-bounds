"""Fixed-role unit-head source machine for the retained A5 caller.
JoyboyBrian with substantial OpenAI Codex assistance; Apache-2.0.
Runtime widths are tape words, never decoded Python loop bounds.
"""
BLANK, LEFT, END = 2, 3, 4


def need(ok, why):
    if not ok:
        raise ValueError(why)


class Tape:
    def __init__(self, body=(), *, blank=False):
        self.cells = [BLANK] if blank else [LEFT, *body]
        self.head = 0 if blank else 1
        self.steps = 0
        self.visited = {1}

    def read(self):
        self.steps += 1
        self.visited.add(self.head)
        return self.cells[self.head] if self.head < len(self.cells) else BLANK

    def write(self, symbol):
        self.steps += 1
        self.visited.add(self.head)
        while len(self.cells) <= self.head:
            self.cells.append(BLANK)
        self.cells[self.head] = symbol

    def move(self, direction):
        need(direction in (-1, 1), 'unit move')
        self.steps += 1
        self.head += direction
        need(self.head >= 0, 'left boundary')
        self.visited.add(self.head)

    def home(self):
        self.move(-1)
        while self.read() != LEFT:
            self.move(-1)
        self.move(1)

    def clear(self):
        self.home()
        while self.read() != BLANK:
            self.write(BLANK)
            self.move(1)
        self.home()


class Machine:
    """Three data ports, borrowed width; three private roles. Typed success ABI."""
    def __init__(self, data, width):
        need(len(data) == 3 and len({id(t) for t in (*data, width)}) == 4,
             'distinct external ports')
        self.data, self.width = tuple(data), width
        self.guide, self.counter, self.output = (Tape(blank=True) for _ in range(3))
        self.private = (self.guide, self.counter, self.output)
        # The actual private marker initialization is charged explicitly.
        for tape in self.private:
            tape.head = 0
            tape.write(LEFT)
            tape.move(1)
        self.control = 0
        self.ready = False
        self.closed = False

    def tick(self):
        self.control += 1

    def setup(self):
        need(not self.ready and not self.closed, 'one setup')
        w, c, g = self.width, self.counter, self.guide
        # Copy canonical positive LSF binary q; retain no decoded q.
        seen = False
        last = 0
        while w.read() != END:
            self.tick()
            last = w.read()
            need(last in (0, 1), 'width bit')
            c.write(last)
            c.move(1)
            w.move(1)
            seen = True
        need(seen and last == 1, 'positive canonical width')
        c.write(END)
        c.home()
        w.home()
        # Canonical counter representation shrinks at every highest-bit loss.
        while c.read() != END:
            self.tick()
            while c.read() == 0:
                c.write(1)
                c.move(1)
                self.tick()
            need(c.read() == 1, 'positive countdown')
            c.write(0)
            c.move(1)
            if c.read() == END:
                c.write(BLANK)
                c.move(-1)
                c.write(END)
            c.home()
            g.write(1)
            g.move(1)
        g.home()
        c.clear()
        self.ready = True

    def block(self, source, dest=None):
        g = self.guide
        while g.read() == 1:
            self.tick()
            if dest is not None:
                symbol = source.read()
                need(symbol in (0, 1), 'payload bit')
                dest.write(symbol)
                dest.move(1)
            source.move(1)
            g.move(1)
        g.home()

    def permute(self, role, inverse):
        """inverse[j] is a FIXED compiled source row for output row j."""
        source, out = self.data[role], self.output
        need(out.read() == BLANK, 'empty owned output')
        for origin in inverse:
            self.tick()
            source.home()
            for _ in range(origin):  # fixed <=255-state control, never runtime q
                self.block(source)
            self.block(source, out)
        source.home()
        out.home()
        while out.read() != BLANK:
            self.tick()
            source.write(out.read())
            source.move(1)
            out.move(1)
        source.home()
        out.clear()

    def mix(self, word):
        for source_role, target_role in word:  # fixed finite binary role circuit
            self.tick()
            a, b = self.data[source_role], self.data[target_role]
            need(a is not b, 'proper CNOT')
            while a.read() != BLANK:
                self.tick()
                x, y = a.read(), b.read()
                need(x in (0, 1) and y in (0, 1), 'complete binary roles')
                b.write(x ^ y)
                a.move(1)
                b.move(1)
            need(b.read() == BLANK, 'equal role lengths')
            a.home()
            b.home()

    def projector(self, word, inverse):
        need(self.ready and not self.closed, 'live prepared caller')
        self.mix(word)
        self.permute(0, inverse)
        self.mix(tuple(reversed(word)))

    def close(self):
        need(self.ready and not self.closed, 'one close')
        self.guide.clear()
        for tape in self.private:
            need(tape.read() == BLANK, 'empty private body')
            tape.move(-1)
            need(tape.read() == LEFT, 'private marker')
            tape.write(BLANK)
            tape.move(1)
        self.closed = True
