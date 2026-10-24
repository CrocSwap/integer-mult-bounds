# SPDX-License-Identifier: Apache-2.0
"""Separate table interpreter and coordinate gather oracle; no producer imports.

Dense tape mechanics follow David Arias's PR2776 independent checker.
The runtime affine contract, fixtures and validation are new.
"""
import itertools

BLANK, LEFT, RIGHT, ZERO, ONE, UNIT, MARK = range(7)
TAPES = 19
INPUTS = (0, 4, 5, 6, 7, 14, 16)
WORK = (2, 3, 8, 9, 10, 11, 12, 13, 15, 17, 18)


def need(ok, message):
    if not ok:
        raise ValueError(message)


def validate(program):
    need(set(program) == {'tapes', 'entry', 'instructions'} and program['tapes'] == TAPES,
         'fixed nineteen-tape program schema')
    code = program['instructions']
    target = lambda x: type(x) is int and 0 <= x < len(code)
    tape = lambda x: type(x) is int and 0 <= x < TAPES
    need(target(program['entry']), 'finite entry')
    for pc, row in enumerate(code):
        op = row[0]
        if op == 'branch':
            need(len(row) == 4 and tape(row[1]) and target(row[3]), 'local branch')
            need(len(set(x[0] for x in row[2])) == len(row[2]), 'unique branches')
            need(all(type(s) is int and 0 <= s < 7 and target(p) for s, p in row[2]), 'finite branches')
        elif op == 'move':
            need(len(row) == 3 and tape(row[1]) and type(row[2]) is int and row[2] in (-1, 1),
                 'literal unit motion')
        elif op == 'write':
            need(len(row) == 3 and tape(row[1]) and type(row[2]) is int and 0 <= row[2] < 7,
                 'local alphabet write')
        elif op == 'goto':
            need(len(row) == 2 and target(row[1]), 'finite jump')
        elif op in ('halt', 'reject'):
            need(len(row) == (1 if op == 'halt' else 2), 'terminal schema')
        else:
            raise ValueError('unsupported instruction')
        if op in ('move', 'write'):
            need(target(pc + 1), 'finite successor')


class DenseTape:
    def __init__(self, cells, head):
        self.base = min(cells, default=head)
        end = max(cells, default=head)
        self.cells = [BLANK] * (end - self.base + 1)
        for k, v in cells.items():
            self.cells[k - self.base] = v
        self.head = self.low = self.high = head

    def read(self):
        k = self.head - self.base
        return self.cells[k] if 0 <= k < len(self.cells) else BLANK

    def write(self, value):
        k = self.head - self.base
        if k < 0:
            self.cells[:0] = [BLANK] * -k
            self.base = self.head
            k = 0
        if k >= len(self.cells):
            self.cells.extend([BLANK] * (k - len(self.cells) + 1))
        self.cells[k] = value

    def move(self, delta):
        self.head += delta
        self.low = min(self.low, self.head)
        self.high = max(self.high, self.head)

    def snapshot(self):
        return {self.base + k: v for k, v in enumerate(self.cells) if v != BLANK}


def execute(program, bank, cap):
    validate(program)
    tapes = [DenseTape(*row) for row in bank]
    code, pc, steps = program['instructions'], program['entry'], 0
    while True:
        need(steps < cap, 'experimental execution cap')
        steps += 1
        row = code[pc]
        op = row[0]
        if op == 'halt':
            return tapes, steps
        if op == 'reject':
            raise ValueError('machine rejected: ' + row[1])
        if op == 'goto':
            pc = row[1]
        elif op == 'branch':
            symbol = tapes[row[1]].read()
            pc = next((p for s, p in row[2] if s == symbol), row[3])
        else:
            if op == 'move':
                tapes[row[1]].move(row[2])
            else:
                tapes[row[1]].write(row[2])
            pc += 1


def marked(bits, origin):
    return ({origin: LEFT, **{origin + k + 1: v for k, v in enumerate(bits)},
             origin + len(bits) + 1: RIGHT}, origin + 1)


def binary(n, origin):
    return marked([ONE if n >> j & 1 else ZERO for j in range(n.bit_length())], origin)


def fixtures(shape, coefficient, offset, payload, translated=False):
    p, q, g, s = shape
    need(all(type(n) is int and n > 0 for n in shape), 'positive extents')
    need(len(payload) == p * q * q * g * s and all(type(b) is int and b in (0, 1) for b in payload),
         'complete Boolean stream')
    origins = [i * 3 - 23 if translated else 0 for i in range(TAPES)]
    bank = [({}, k) for k in origins]
    bank[0] = marked([ONE if b else ZERO for b in payload], origins[0])
    for t, value in zip((4, 5, 6, 7, 14, 16), (*shape, coefficient + 1, offset + 1)):
        bank[t] = binary(value, origins[t])
    return bank


def oracle(shape, coefficient, offset, payload, inverse=False):
    p, q, g, s = shape
    sign = -1 if inverse else 1
    out = []
    # Gather by output coordinate, with a direct flat-address formula.
    for a, x, b, y, z in itertools.product(range(p), range(q), range(g), range(q), range(s)):
        original_y = (y - sign * (coefficient * x + offset)) % q
        index = ((((a * q + x) * g + b) * q + original_y) * s + z)
        out.append(payload[index])
    return out


def check_result(tapes, steps, bank, shape, coefficient, offset, payload, inverse=False):
    expected = oracle(shape, coefficient, offset, payload, inverse)
    for t in INPUTS:
        need(tapes[t].snapshot() == bank[t][0], 'input preservation ' + str(t))
        need(tapes[t].head == bank[t][1], 'input head return ' + str(t))
    for t in WORK:
        need(not tapes[t].snapshot(), 'whole scratch erasure ' + str(t))
        need(tapes[t].head == bank[t][1], 'scratch head return ' + str(t))
    cells, head = marked([ONE if b else ZERO for b in expected], bank[1][1])
    need(tapes[1].snapshot() == cells and tapes[1].head == head, 'affine output and head')
    volume = len(payload)
    need(steps <= 1024 * volume, 'proved conservative physical transition bill')
    span = sum(t.high - t.low + 1 for t in tapes)
    need(span <= 64 * volume, 'proved visited-cell bill')
    return span
