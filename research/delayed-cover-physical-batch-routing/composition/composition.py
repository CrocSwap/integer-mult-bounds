"""Physical router/codec/continuation composition on K+7 fixed tapes.

The runtime below observes only scanned symbols and uses read/write/unit-move.
Its router PC ranges over a fixed finite microtable. No runtime algorithm reads
hardware heads, cell arrays, action counts, coordinates or a recursive list.
The fixed test grammar has one unequal child edge and two sequential siblings.
It is not a production supplier or a general recursive grammar lowering.

thu-nmrc with substantial OpenAI Codex assistance, Apache-2.0.
Retained sources: David Arias router-machine/counter lineage; Ali Romman stack
and output bridge; Mason Hale selected-owned-dispatch codec/composition.
"""
from pathlib import Path
import importlib.util
import sys

HERE = Path(__file__).resolve().parent


def load(name, relative):
    spec = importlib.util.spec_from_file_location(name, HERE / relative)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


s = load('stack', 'inputs/research/delimited-continuation-stack/stack.py')
returned = load('return_output', 'inputs/research/continuation-output-return/return_output.py')
m = load('machine', 'inputs/root-router/machine.py')
load('counters', 'inputs/root-router/counters.py')
router = load('router', 'inputs/root-router/router.py')


def three_moves(tape, direction):
    # Constant finite unrolling; no extent, address, or runtime counter.
    tape.move(direction)
    tape.move(direction)
    tape.move(direction)


class CodedTape:
    """Stateless 3-bit facade for all seven router symbols.

    Physical BLANK terminates a stack segment. Logical router BLANK is the
    code000 inside that segment. No origin or logical-head coordinate is kept.
    """
    __slots__ = ('tape',)

    def __init__(self, tape):
        self.tape = tape

    def read(self):
        t = self.tape
        if t.read() == s.BLANK:
            return m.BLANK
        value = 0
        for _ in (0, 1, 2):
            bit = t.read()
            s.need(bit in (0, 1), 'complete binary codeword')
            value = 2 * value + bit
            t.move(1)
        three_moves(t, -1)
        s.need(value < 7, 'unused code111')
        return value

    def write(self, symbol):
        s.need(symbol in range(7), 'logical router alphabet')
        for shift in (2, 1, 0):
            s.emit(self.tape, (symbol >> shift) & 1)
        three_moves(self.tape, -1)

    def move(self, direction):
        s.need(direction in (-1, 1), 'logical unit step')
        if direction == 1 and self.tape.read() == s.BLANK:
            # Materialize crossed logical blanks: no hole may impersonate the
            # physical segment delimiter when the stack later parks the tape.
            self.write(m.BLANK)
        three_moves(self.tape, direction)


def execute(program, ports):
    """Literal router microtable execution; PC is finite control only."""
    pc = program.entry
    while True:
        row = program.instructions[pc]
        op = row[0]
        if op == 'halt':
            return
        if op == 'reject':
            raise ValueError(row[1])
        if op == 'goto':
            pc = row[1]
            continue
        tape = ports[row[1]]
        if op == 'branch':
            pc = dict(row[2]).get(tape.read(), row[3])
            continue
        if op == 'write':
            tape.write(row[2])
        elif op == 'move':
            tape.move(row[2])
        else:
            raise ValueError('unsupported literal instruction')
        pc += 1


def origin(tape, marker=s.LEFT):
    s.rewind(tape, marker)


def copy_binary(source, target, source_marker=s.LEFT, target_marker=s.LEFT):
    origin(source, source_marker)
    origin(target, target_marker)
    s.need(target.read() == s.BLANK, 'owned target empty')
    while (bit := source.read()) != s.BLANK:
        s.need(bit in (0, 1), 'binary body')
        s.emit(target, bit)
        source.move(1)
    origin(source, source_marker)
    origin(target, target_marker)


def coded_input_origin(tape):
    origin(tape)
    three_moves(tape, 1)


def clear_base(tape):
    origin(tape, s.BASE)
    while (bit := tape.read()) != s.BLANK:
        s.need(bit in (0, 1), 'binary relay')
        s.emit(tape, s.BLANK)
    origin(tape, s.BASE)


def complement_bank(tape):
    """Actual complete bit-string leaf; it is not an admitted native child."""
    origin(tape)
    three_moves(tape, 1)
    view = CodedTape(tape)
    while True:
        symbol = view.read()
        if symbol == m.RIGHT:
            break
        s.need(symbol in (m.ZERO, m.ONE), 'complete leaf bit alphabet')
        view.write(m.ONE if symbol == m.ZERO else m.ZERO)
        view.move(1)
    coded_input_origin(tape)


class Pipeline:
    """Fixed one-edge grammar with two child calls and physical grant tapes.

    K=max(16,L+8) payload tapes, one control tape, one resume-descriptor tape,
    four BASE tapes (input relay, child-A grant, child-R grant, output relay),
    and one unary-depth input. The child grant descriptors are read-only inputs.
    L is a compile-time constant. No tape is allocated during an invocation.
    """
    def __init__(self, low_types, payloads, control, descriptor, relays, depth):
        self.p = router.ports(low_types)
        s.need(len(payloads) == max(16,low_types+8), 'fixed compiled payload ABI')
        self.return_slot = len(payloads)-1
        s.need(self.return_slot >= self.p['count'], 'distinct empty return role')
        s.need(len(relays) == 4, 'fixed relay and grant ABI')
        self.payloads, self.control = tuple(payloads), control
        self.descriptor, self.relays, self.depth = descriptor, tuple(relays), depth
        self.views = tuple(CodedTape(t) for t in payloads[:self.p['count']])
        self.split = router.build(low_types)
        self.merge = router.build(low_types, merge=True)
        self.present = (True,) * self.p['count'] + (False,) * (len(payloads)-self.p['count'])

    def child(self, bank):
        """bank is one of two statically compiled call sites, not an address."""
        p = self.p
        copy_binary(self.payloads[bank], self.relays[0], target_marker=s.BASE)
        coded_input_origin(self.payloads[bank])
        # Resume phase is written on a physical descriptor, consumed by push,
        # and restored by pop. No host parent pointer is saved.
        s.need(self.descriptor.read() == s.BLANK, 'empty resume descriptor')
        s.emit(self.descriptor, 1)
        origin(self.descriptor, s.BASE)
        s.Stack(self.payloads, self.control, self.descriptor).push(self.present)
        copy_binary(self.relays[0], self.payloads[p['source']], source_marker=s.BASE)
        coded_input_origin(self.payloads[p['source']])
        for role, grant in ((p['repeats_input'], self.relays[1]),
                            (p['block_input'], self.relays[2])):
            copy_binary(grant, self.payloads[role], source_marker=s.BASE)
            coded_input_origin(self.payloads[role])
        clear_base(self.relays[0])
        s.need(self.depth.read() == s.BLANK, 'this grammar has one child edge')
        execute(self.split, self.views)
        complement_bank(self.payloads[0])
        execute(self.merge, self.views)
        # The original bridge saves all child output before retire/pop. The
        # target return role was really empty in the parked parent.
        returned.return_output(self.payloads, self.control, self.descriptor,
                               self.relays[3], p['output'], self.return_slot)
        s.need(self.descriptor.read() == 1, 'physical resume phase')
        s.emit(self.descriptor, s.BLANK)
        s.need(self.descriptor.read() == s.BLANK, 'one-bit resume phase')
        origin(self.descriptor, s.BASE)
        # The occupied parent bank is replaced only after its child result is
        # protected and the parent segment has been physically restored.
        returned.retire(self.payloads[bank])
        copy_binary(self.payloads[self.return_slot], self.payloads[bank])
        returned.retire(self.payloads[self.return_slot])
        coded_input_origin(self.payloads[bank])

    def run(self):
        execute(self.split, self.views)
        if self.depth.read() != s.BLANK:
            s.need(self.depth.read() == 1, 'unary physical depth input')
            self.depth.move(1)
            self.child(0)
            self.depth.move(-1)
            self.depth.move(1)
            self.child(1)
            self.depth.move(-1)
        execute(self.merge, self.views)
        # Copy banks and encoded logical-blank scratch receive no output credit.
        for role in self.p['banks'] + (self.p['repeats'], self.p['block'],
                                      self.p['binary_work']):
            returned.retire(self.payloads[role])
        origin(self.depth, s.BASE)

    def consume_output(self):
        """Explicit fixture consumer retires the delivered owned packet."""
        returned.retire(self.payloads[self.p['output']])
