"""Literal lifecycle control on fixed sequential tapes.

Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
Stack is the authenticated #5356 implementation supplied by the loader.
Algorithms never read tape addresses, extents, hardware arrays or a host stack.
Instruction and primitive tables are fixed before runtime inputs vary.
"""
from dataclasses import dataclass

ZERO, ONE, LEFT, SEP, END, BASE, BLANK = range(7)
COMPONENT = 2


def need(condition, message):
    if not condition:
        raise ValueError(message)


def emit(tape, symbol):
    tape.write(symbol)
    tape.move(1)


def origin(tape, marker=LEFT):
    tape.move(-1)
    while tape.read() != marker:
        tape.move(-1)
    tape.move(1)


def retire(tape, marker=LEFT):
    """Erase all coded bytes, including encoded logical blanks."""
    origin(tape, marker)
    while (symbol := tape.read()) != BLANK:
        need(symbol in (ZERO, ONE), "contiguous binary body")
        emit(tape, BLANK)
    origin(tape, marker)


def transfer(source, target, source_marker=LEFT, target_marker=LEFT):
    """Administrative actual-byte copy; never an arithmetic COPY."""
    origin(source, source_marker)
    origin(target, target_marker)
    need(target.read() == BLANK, "administrative transfer needs empty target")
    while (symbol := source.read()) != BLANK:
        need(symbol in (ZERO, ONE), "binary transfer")
        emit(target, symbol)
        source.move(1)
    origin(source, source_marker)
    origin(target, target_marker)


class CodedPort:
    """Seven virtual symbols encoded as three nonblank physical bits.

    The physical LEFT before the current body is never exposed as data.
    A left step at its local origin rejects. Two-sided routines first use
    the standard translation to two one-sided ports.
    """
    __slots__ = ("tape",)

    def __init__(self, tape):
        self.tape = tape

    def read(self):
        t = self.tape
        if t.read() == BLANK:
            return 4
        value = 0
        for _ in range(3):
            bit = t.read()
            need(bit in (ZERO, ONE), "whole virtual codeword")
            value = 2 * value + bit
            t.move(1)
        for _ in range(3):
            t.move(-1)
        need(value < 7, "unused virtual codeword")
        return value

    def write(self, value):
        need(type(value) is int and 0 <= value < 7, "virtual alphabet")
        for shift in (2, 1, 0):
            emit(self.tape, (value >> shift) & 1)
        for _ in range(3):
            self.tape.move(-1)

    def move(self, direction):
        need(direction in (-1, 1), "virtual unit move")
        t = self.tape
        if direction == 1:
            if t.read() == BLANK:
                self.write(4)
            for _ in range(3):
                t.move(1)
        else:
            t.move(-1)
            if t.read() == LEFT:
                t.move(1)
                raise ValueError("native routine crossed its local origin")
            t.move(-1)
            t.move(-1)


class BinaryContextPort:
    """Read-only raw binary descriptor, with its own physical alphabet.

    Unlike CodedPort, read returns physical BLANK=6 at the frontier. A table
    may inspect that frontier but cannot pass it or the current LEFT marker.
    This supplies runtime e/f/K/rho data through counted local operations.
    """
    __slots__ = ("tape",)

    def __init__(self, tape):
        self.tape = tape

    def read(self):
        symbol = self.tape.read()
        need(symbol in (ZERO, ONE, BLANK), "binary context alphabet")
        return symbol

    def write(self, value):
        raise ValueError("native context is read-only")

    def move(self, direction):
        need(direction in (-1, 1), "binary context unit move")
        t = self.tape
        if direction == 1:
            need(t.read() in (ZERO, ONE), "context frontier cannot be crossed")
            t.move(1)
        else:
            t.move(-1)
            if t.read() == LEFT:
                t.move(1)
                raise ValueError("native context crossed its local origin")


def read_code(tape):
    """Consume a numeric-format code; physical frontier returns None."""
    if tape.read() == BLANK:
        return None
    value = 0
    for _ in range(3):
        bit = tape.read()
        need(bit in (ZERO, ONE), "numeric codeword")
        value = 2 * value + bit
        tape.move(1)
    need(value < 7, "unused numeric codeword")
    return value


def write_code(tape, value):
    for shift in (2, 1, 0):
        emit(tape, (value >> shift) & 1)


def initialize(target, shape):
    """Dispose of arbitrary old bytes, then zero the complete common format."""
    need(target is not shape, "private initialization cannot destroy its guide")
    retire(target)
    origin(shape)
    in_component = False
    while (symbol := read_code(shape)) is not None:
        need(symbol in (ZERO, ONE, COMPONENT), "canonical signed components")
        if symbol == COMPONENT:
            need(in_component, "positive component width")
            write_code(target, COMPONENT)
            in_component = False
        else:
            write_code(target, ZERO)
            in_component = True
    need(not in_component, "component terminator")
    origin(shape)
    origin(target)


def copy_as_add(target, source):
    """Signed addition into the actual destination, including any residue.

    Components are little-endian two's complement followed by COMPONENT.
    Carries reset at delimiters; equal-sign signed overflow rejects.
    No ideal-zero test or exact-value overwrite substitutes for addition.
    """
    need(target is not source, "distinct COPY/ADD ports")
    origin(source)
    origin(target)
    carry = 0
    last_a = last_b = last_out = 0
    in_component = False
    while True:
        a = read_code(source)
        b = read_code(target)
        need((a is None) == (b is None), "same complete numerical extent")
        if a is None:
            need(not in_component, "complete signed component")
            break
        need(a in (ZERO, ONE, COMPONENT) and b in (ZERO, ONE, COMPONENT),
             "canonical signed addition operands")
        need((a == COMPONENT) == (b == COMPONENT), "same component boundaries")
        if a == COMPONENT:
            need(in_component, "positive signed component width")
            need(last_a != last_b or last_out == last_a, "signed addition overflow")
            carry = 0
            in_component = False
            continue
        value = a + b + carry
        last_a, last_b, last_out = a, b, value & 1
        carry = value >> 1
        for _ in range(3):
            target.move(-1)
        write_code(target, last_out)
        in_component = True
    origin(source)
    origin(target)


def execute_table(table, ports, readonly_context=()):
    """Run a supplied finite native table with every port confined.

    These tables retain explicit semantics/time/space premises. Fixture
    tables are not advertised as Gaussian implementations.
    """
    views = (tuple(CodedPort(t) for t in ports)
             + tuple(BinaryContextPort(t) for t in readonly_context))
    pc = 0
    while True:
        row = table[pc]
        op = row[0]
        if op == "halt":
            break
        if op == "reject":
            raise ValueError(row[1])
        if op == "goto":
            pc = row[1]
            continue
        view = views[row[1]]
        if op == "branch":
            pc = dict(row[2]).get(view.read(), row[3])
            continue
        if op == "write":
            view.write(row[2])
        elif op == "move":
            view.move(row[2])
        else:
            raise ValueError("native table opcode")
        pc += 1
    for tape in tuple(ports)+tuple(readonly_context):
        origin(tape)


@dataclass(frozen=True)
class Instruction:
    op: str
    ports: tuple = ()
    token: tuple = ()


class Controller:
    """Fixed finite controller of a fixed flat compiled template.

    rows implements the separately priced row/shape interface; all its
    dynamic state belongs on the supplied tapes. services contains fixed
    finite transition tables. Payload ports include metadata and all scratch.
    The only runtime continuation is the physical Stack.
    """
    def __init__(self, program, public_count, payloads, control, descriptor,
                 bridge, child_header, rows, services, stack_class, protected_ports=(),
                 primitive_work=(), primitive_context=()):
        self.program = tuple(program)
        self.public_count = public_count
        self.payloads = tuple(payloads)
        self.control = control
        self.descriptor = descriptor
        self.bridge = bridge
        self.child_header = child_header
        self.rows = rows
        self.services = services
        need(len({id(t) for t in self.payloads+(control,descriptor,bridge,child_header)})
             == len(self.payloads)+4, "all physical ports distinct")
        self.stack = stack_class(self.payloads, control, descriptor)
        self.protected_ports = tuple(protected_ports)
        owned = {e.ports[0] for e in self.program if e.op == "INIT"}
        need(all(public_count <= i < len(self.payloads) for i in owned), "INIT only private physical slots")
        need(owned.isdisjoint(self.protected_ports), "owned fields cannot be borrowed descriptors")
        self.root_cleanup = tuple(i for i in range(public_count,len(self.payloads))
                                  if i not in self.protected_ports)
        self.primitive_work = tuple(primitive_work)
        self.primitive_context = tuple(primitive_context)
        data_ports = {i for e in self.program for i in e.ports}
        need(all(0 <= i < len(self.payloads) for i in data_ports), "compiled port range")
        need(all(i >= public_count and i < len(self.payloads) and i not in data_ports
                 and i not in self.protected_ports for i in self.primitive_work), "separate primitive scratch")
        need(len(set(self.primitive_work)) == len(self.primitive_work), "distinct primitive work ports")
        need(len(set(self.primitive_context)) == len(self.primitive_context)
             and all(i in self.protected_ports and 0 <= i < len(self.payloads)
                     and i not in data_ports for i in self.primitive_context), "borrowed binary context ports")
        self.pc_bits = max(1, (len(self.program) - 1).bit_length())
        self.pc_words = tuple(tuple((pc >> j) & 1 for j in range(self.pc_bits))
                              for pc in range(len(self.program)))
        need(self.program and self.program[-1].op == "RET", "finite completed program")

    def save_pc(self, pc):
        need(self.descriptor.read() == BLANK, "empty active PC descriptor")
        for bit in self.pc_words[pc]:
            emit(self.descriptor, bit)
        origin(self.descriptor, BASE)

    def consume_pc(self):
        pc = 0
        for shift in range(self.pc_bits):
            bit = self.descriptor.read()
            need(bit in (ZERO, ONE), "binary return PC")
            pc |= bit << shift
            emit(self.descriptor, BLANK)
        need(self.descriptor.read() == BLANK, "exact fixed return PC width")
        origin(self.descriptor, BASE)
        need(pc < len(self.program) and pc > 0 and self.program[pc-1].op == "PAID",
             "return PC designates a paid continuation")
        return pc

    def has_parent(self):
        self.control.move(-1)
        symbol = self.control.read()
        self.control.move(1)
        need(symbol in (BASE, END), "complete continuation top")
        return symbol == END

    def descend(self, pc):
        event = self.program[pc]
        source = self.payloads[event.ports[0]]
        transfer(source, self.bridge, target_marker=BASE)
        self.rows.prepare(event.token, self.child_header)
        self.save_pc(pc + 1)
        self.stack.push((True,) * len(self.payloads))
        self.rows.install(self.bridge, self.child_header,
                          self.payloads[:self.public_count])
        retire(self.bridge, BASE)
        retire(self.child_header, BASE)

    def primitive(self, token, fields):
        for i in self.primitive_work:
            retire(self.payloads[i])
        execute_table(self.services[token],
                      tuple(self.payloads[i] for i in fields+self.primitive_work),
                      tuple(self.payloads[i] for i in self.primitive_context))
        for i in self.primitive_work:
            retire(self.payloads[i])

    def ascend(self):
        self.rows.collect(self.payloads[:self.public_count], self.bridge)
        for tape in self.payloads:
            retire(tape)
        self.stack.pop()                   # ignore observer sizes and heads
        pc = self.consume_pc()
        target = self.payloads[self.program[pc-1].ports[0]]
        retire(target)
        transfer(self.bridge, target, source_marker=BASE)
        retire(self.bridge, BASE)
        return pc

    def run(self, observe=None):
        pc = 0
        while True:
            event = self.program[pc]
            if observe is not None:
                observe("before", pc, event)  # checker only; ignores return value
            if event.op == "INIT":
                initialize(self.payloads[event.ports[0]], self.payloads[0])
                pc += 1
            elif event.op == "CLEAR":
                retire(self.payloads[event.ports[0]])
                pc += 1
            elif event.op == "COPY":
                copy_as_add(self.payloads[event.ports[0]], self.payloads[event.ports[1]])
                pc += 1
            elif event.op == "SERVICE":
                self.primitive(event.token,event.ports)
                pc += 1
            elif event.op == "PAID":
                if self.rows.is_leaf(event.token):
                    self.primitive(("leaf",)+event.token,event.ports)
                    pc += 1
                else:
                    self.descend(pc)
                    pc = 0
            elif event.op == "RET":
                if not self.has_parent():
                    for i in self.root_cleanup:
                        retire(self.payloads[i])
                    break
                pc = self.ascend()
            else:
                raise ValueError("compiled opcode")
            if observe is not None:
                observe("after", pc, event)


def boundary_actions(q, b, parent_total, child_total, input_length,
                     output_length, staged_header_length):
    """Exact descend+ascend actions, excluding the three row-service calls.

    Also excludes caller leaf/top tests. All heads are at local origins.
    Includes PC, all retirement, occupied-target replacement and both relays.
    """
    return (4 * parent_total + 5 * child_total + 18 * input_length
            + 13 * output_length + 5 * staged_header_length
            + 38 * q + 27 * b + 103)
