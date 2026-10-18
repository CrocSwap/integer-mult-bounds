"""One-cell sequential machine for five-coordinate padding/restriction.

The cursor reads only marker/bit tapes; it never computes an integer coordinate,
cardinality, address, logarithm or volume. Test harnesses serialize descriptors.
Prepared for ywz65 with OpenAI Codex assistance. Apache-2.0.
"""


class Meter:
    def __init__(self, trace=False):
        self.steps = 0
        self.trace = [] if trace else None

    def tick(self, name, action, head, value=''):
        self.steps += 1
        if self.trace is not None:
            self.trace.append((name, action, head, value))


class Tape:
    """Instrumented ordinary tape; only read/write/one-cell move are exposed."""
    def __init__(self, name, contents, meter, origin=0, writable=True):
        self.name, self.meter, self.origin = name, meter, origin
        self.cells = {origin+i: c for i, c in enumerate(contents)}
        self.head, self.writable = origin+1, writable
        self.low, self.high = self.head, self.head

    def read(self):
        value = self.cells.get(self.head, '_')
        self.meter.tick(self.name, 'read', self.head, value)
        return value

    def write(self, value):
        if not self.writable:
            raise ValueError('immutable descriptor/input write')
        if value not in '01^$_':
            raise ValueError('finite tape alphabet')
        self.cells[self.head] = value
        self.meter.tick(self.name, 'write', self.head, value)

    def move(self, direction):
        if direction not in (-1, 1):
            raise ValueError('one-cell moves only')
        self.meter.tick(self.name, 'move', self.head, direction)
        self.head += direction
        self.low, self.high = min(self.low, self.head), max(self.high, self.head)


def rewind(tape):
    tape.move(-1)
    while tape.read() != '^':
        tape.move(-1)
    tape.move(1)


def decrement(tape):
    """Little-endian subtract one modulo 2^L; return borrow out, head restored."""
    while tape.read() == '0':
        tape.write('1')
        tape.move(1)
    value = tape.read()
    if value == '1':
        tape.write('0')
        underflow = False
    elif value == '$':
        underflow = True
    else:
        raise ValueError('malformed counter')
    rewind(tape)
    return underflow


def copy_template(template, target, ones=False):
    while True:
        value = template.read()
        if value == '$':
            break
        if value not in '01':
            raise ValueError('malformed descriptor')
        target.write('1' if ones else value)
        template.move(1)
        target.move(1)
    if target.read() != '$':
        raise ValueError('counter width mismatch')
    rewind(template)
    rewind(target)


def clear(tape):
    while tape.read() != '$':
        tape.write('0')
        tape.move(1)
    rewind(tape)


class Coordinate:
    def __init__(self, template, padded, genuine):
        self.template, self.padded, self.genuine = template, padded, genuine
        self.active = True
        copy_template(template, padded, ones=True)
        copy_template(template, genuine)

    def tick(self):
        carry = decrement(self.padded)
        if self.active and decrement(self.genuine):
            self.active = False
        if carry:
            copy_template(self.template, self.genuine)
            self.active = True
        return carry

    def finish(self):
        clear(self.padded)
        clear(self.genuine)


def scan(coordinates, source, target, restrict=False):
    """Pad or restrict, then restore all heads and zero owned counter work.

    Five coordinates are a fixed part of the machine, not an input-length list.
    All input tapes have '^'/'$' delimiters; output starts with '^' and blanks.
    A descriptor is q-1 in canonical little-endian binary (empty for q=1).
    Each counter is initially L zeros between markers, with that same width.
    """
    if len(coordinates) != 5:
        raise ValueError('exactly five aggregate coordinates')
    while True:
        source.meter.tick('control', 'emit', 0)
        genuine = all(c.active for c in coordinates)
        if restrict:
            bit = source.read()
            if bit not in '01':
                raise ValueError('short/nonbinary padded payload')
            source.move(1)
            if genuine:
                target.write(bit)
                target.move(1)
        else:
            if genuine:
                bit = source.read()
                if bit not in '01':
                    raise ValueError('short/nonbinary genuine payload')
                source.move(1)
            else:
                bit = '0'
            target.write(bit)
            target.move(1)
        complete = True
        for coordinate in reversed(coordinates):
            source.meter.tick('control', 'advance', 0)
            if not coordinate.tick():
                complete = False
                break
        if complete:
            break
    if source.read() != '$':
        raise ValueError('long payload')
    target.write('$')
    rewind(source)
    rewind(target)
    for coordinate in coordinates:
        coordinate.finish()
