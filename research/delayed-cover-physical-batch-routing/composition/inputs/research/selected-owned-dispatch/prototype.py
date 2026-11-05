"""Exploratory composition, not a selected whole-caller admission.

Runs the unchanged query tables through a constant-size symbol codec and the
unchanged continuation/output-return programs. Algorithmic routines use only
read/write/unit-move on physical tapes. Fixture initialization and assertions
may inspect the simulated hardware; neither supplies runtime dispatch state.
"""
import importlib.util
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SRC = ROOT / 'research'

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module

s = load('stack', SRC / 'delimited-continuation-stack' / 'stack.py')
r = load('return_output', SRC / 'continuation-output-return' / 'return_output.py')
q = load('query_machine', SRC / 'selected-owned-query-private-stream' / 'query_machine.py')
TABLES = q.build(ROOT)

def moves(tape, direction, count=3):
    # Fixed count3 has a finite unrolling; never an input-sized host counter.
    for _ in range(count):
        tape.move(direction)

class CodedQueryTape:
    """Stateless seven-symbol facade; no saved origin, extent or logical head.

    Every logical symbol, including logical BLANK4 and LEFT2, is coded by its
    three binary digits. Physical BLANK6 terminates the binary segment. The
    physical LEFT2 preceding the body is never a query data symbol.
    """
    __slots__ = ('tape',)

    def __init__(self, tape):
        self.tape = tape

    def read(self):
        t = self.tape
        first = t.read()
        if first == s.BLANK:
            return q.BLANK
        value = 0
        for _ in range(3):
            bit = t.read()
            s.need(bit in (0, 1), 'complete three-bit codeword')
            value = 2 * value + bit
            t.move(1)
        moves(t, -1)
        s.need(value < 7, 'unused codeword111')
        return value

    def write(self, value):
        s.need(value in range(7), 'logical query alphabet')
        for shift in (2, 1, 0):
            s.emit(self.tape, (value >> shift) & 1)
        moves(self.tape, -1)

    def step(self, direction):
        s.need(direction in (-1, 1), 'logical unit move')
        if direction == 1 and self.tape.read() == s.BLANK:
            # Moving across an as-yet unwritten logical blank materializes its
            # code so no physical hole can become a false segment delimiter.
            self.write(q.BLANK)
        moves(self.tape, direction)

def execute(table, ports):
    # Same instruction interpreter as the predecessor, without per-invocation
    # Python state. pc has only the fixed table's243/248 possible instruction IDs.
    pc = 0
    while True:
        row = table[pc]
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
            tape.step(row[2])
        else:
            raise ValueError('opcode')
        pc += 1

def at_start(tape, marker=s.LEFT):
    s.rewind(tape, marker)

def clear(tape, marker=s.LEFT):
    at_start(tape, marker)
    while (bit := tape.read()) != s.BLANK:
        s.need(bit in (0, 1), 'binary segment')
        s.emit(tape, s.BLANK)
    at_start(tape, marker)

def copy(source, target, source_marker=s.LEFT, target_marker=s.LEFT):
    at_start(source, source_marker)
    at_start(target, target_marker)
    s.need(target.read() == s.BLANK, 'copy destination empty')
    while (bit := source.read()) != s.BLANK:
        s.need(bit in (0, 1), 'binary copy')
        s.emit(target, bit)
        source.move(1)
    at_start(source, source_marker)
    at_start(target, target_marker)

def initialize_empty_query(tape):
    # New segment has no virtual marker yet. This writes the fixed LEFT code.
    CodedQueryTape(tape).write(q.LEFT)
    moves(tape, 1)

def query_origin(tape):
    at_start(tape)
    moves(tape, 1)

class Dispatcher:
    """A fixed unary-depth test grammar, not the selected production grammar.

    Eight query payloads + reserved return role + three input staging roles;
    sixteen payload roles remain fixed at every depth. Input staging is done
    on four fixed BASE tapes (Z,p,M and output relay). No saved frame list.
    """
    def __init__(self, payloads, control, descriptor, relays, depth):
        self.payloads = payloads
        self.control = control
        self.descriptor = descriptor
        self.relays = relays
        self.depth = depth
        self.ports = tuple(CodedQueryTape(t) for t in payloads[:8])

    def descend(self):
        # Save actual complete encodedZ and descriptors on fixed staging tapes.
        for role, relay in zip((q.Z, q.WD, q.MD), self.relays[:3]):
            copy(self.payloads[role], relay, target_marker=s.BASE)
            query_origin(self.payloads[role])
        self.push_staged()

    def push_staged(self):
        """Park the parent and load an explicit three-tape child input grant.

        Used by descend with complete parentZ/p/M, and by a separate unequal
        subjob fixture with physically supplied child input/p/M descriptors.
        """
        # Constant return phase is physically saved by the retained stack.
        s.emit(self.descriptor, 1)
        at_start(self.descriptor, s.BASE)
        s.Stack(self.payloads, self.control, self.descriptor).push(
            (True,) * 9 + (False,) * 7)
        # ChildX and childY both start at the passed field. Child Y supplies a
        # nonzero summand, making wrong return/phase observable at every level.
        for role in (q.X, q.Y):
            copy(self.relays[0], self.payloads[role], source_marker=s.BASE)
            query_origin(self.payloads[role])
        for role, relay in zip((q.WD, q.MD), self.relays[1:3]):
            copy(relay, self.payloads[role], source_marker=s.BASE)
            query_origin(self.payloads[role])
        for role in (q.Z, q.W, q.M, q.T):
            initialize_empty_query(self.payloads[role])
        for relay in self.relays[:3]:
            clear(relay, s.BASE)

    def has_parent(self):
        self.control.move(-1)
        symbol = self.control.read()
        self.control.move(1)
        s.need(symbol in (s.BASE, s.END), 'control top')
        return symbol == s.END

    def ascend(self):
        # Child output is copied before child retirement and physical pop.
        r.return_output(self.payloads, self.control, self.descriptor,
                        self.relays[3], q.Y, 8)
        s.need(self.descriptor.read() == 1, 'encoded resume phase')
        s.emit(self.descriptor, s.BLANK)
        s.need(self.descriptor.read() == s.BLANK, 'one fixed phase bit')
        at_start(self.descriptor, s.BASE)
        # The query ABI updates an occupied Z. The predecessor's empty output
        # role is a real additional role, not silently aliased with that Z.
        clear(self.payloads[q.Z])
        copy(self.payloads[8], self.payloads[q.Z])
        clear(self.payloads[8])
        query_origin(self.payloads[q.Z])

    def run(self):
        while True:
            execute(TABLES[0], self.ports)
            if self.depth.read() == s.BLANK:
                break
            s.need(self.depth.read() == 1, 'unary child-depth descriptor')
            self.depth.move(1)
            self.descend()
        # Leaf fixture is the complete identity operator on Z. This is not an
        # admitted Gaussian child; its role is to test actual caller mechanics.
        execute(TABLES[1], self.ports)
        while self.has_parent():
            self.ascend()
            execute(TABLES[1], self.ports)
        at_start(self.depth, s.BASE)

def code(symbols):
    return [bit for symbol in symbols for bit in ((symbol >> 2) & 1,
                                                 (symbol >> 1) & 1,
                                                 symbol & 1)]

def bits(values, p):
    return [(value >> i) & 1 for value in values for i in range(p)]

def interior_blank_roundtrip():
    payloads = [s.Tape() for _ in range(16)]
    control = s.Tape(marker=s.BASE)
    descriptor = s.Tape(marker=s.BASE)
    t = payloads[0]
    view = CodedQueryTape(t)
    for symbol in [q.LEFT, q.ONE, q.BLANK, q.ZERO, q.UNIT, q.MARK, q.RIGHT]:
        view.write(symbol)
        view.step(1)
    query_origin(t)
    before, head = list(t.cells), t.head
    s.Stack(payloads, control, descriptor).push((True,) + (False,) * 15)
    # A child really uses its new segment; a false delimiter would overwrite
    # the parent's still-live symbols beyond the logical interior blank.
    for _ in range(30):
        s.emit(t, 1)
    clear(t)
    s.Stack(payloads, control, descriptor).pop()
    s.need(t.cells[:len(before)] == before and t.head == head,
           'interior logical blank truncated a live parent segment')
    return True

def fixture(p, records, depth, prefix, cycles=1):
    counts = s.Counts()
    payloads = [s.Tape([1] * prefix, counts=counts) for _ in range(16)]
    control = s.Tape([0] * prefix, s.BASE, counts)
    descriptor = s.Tape([], s.BASE, counts)
    relays = [s.Tape([], s.BASE, counts) for _ in range(4)]
    depth_tape = s.Tape([], s.BASE, counts)
    values = [(-1 if i % 2 else 2) for i in range(2 * records)]
    yvalues = [(1 if i % 2 else -2) for i in range(2 * records)]
    words = [bits(values, p), bits(yvalues, p), [],
             [int(c) for c in bin(p)[2:][::-1]] + [q.RIGHT],
             [int(c) for c in bin(records)[2:][::-1]] + [q.RIGHT], [], [], []]
    for tape, word in zip(payloads, words):
        for bit in code([q.LEFT] + word):
            s.emit(tape, bit)
        query_origin(tape)
    for _ in range(depth):
        s.emit(depth_tape, 1)
    at_start(depth_tape, s.BASE)
    saved = [(list(t.cells), t.head) for t in payloads]
    before = counts.total
    identities = tuple(id(t) for t in payloads + relays + [control, descriptor, depth_tape])
    sizes = []
    dispatcher = Dispatcher(payloads, control, descriptor, relays, depth_tape)
    for _ in range(cycles):
        dispatcher.run()
        sizes.append(sum(len(t.cells) for t in payloads + relays + [control, descriptor, depth_tape]))
    s.need(identities == tuple(id(t) for t in payloads + relays + [control, descriptor, depth_tape]),
           'fixed physical tape identities')
    expected = [a + cycles * (depth + 1) * b for a, b in zip(yvalues, values)]
    result = payloads[q.Y].cells[prefix + 1:prefix + 1 + 3 * (1 + 2 * records * p)]
    s.need(result == code([q.LEFT] + bits(expected, p)),
           'complete root arithmetic endpoint ' + str((p, records, depth, prefix)))
    for role in (q.X, q.WD, q.MD):
        old, head = saved[role]
        s.need(payloads[role].cells[:len(old)] == old, 'borrowed payload/descriptor bytes')
        s.need(payloads[role].head == head, 'borrowed payload/descriptor head')
    for role in (q.Z, q.W, q.M, q.T):
        tape = payloads[role]
        raw = tape.cells[prefix + 1:]
        while raw and raw[-1] == s.BLANK:
            raw.pop()
        s.need(raw[:3] == code([q.LEFT]), 'private logical LEFT preserved')
        s.need(raw[3:] == code([q.BLANK] * ((len(raw) - 3) // 3)), 'private logical bodies erased')
        s.need(tape.head == prefix + 4, 'private logical heads restored')
    for tape in payloads:
        s.need(tape.cells[:prefix] == [1] * prefix, 'dirty ancestor prefix preserved')
    for tape in payloads[8:]:
        s.need(all(x == s.BLANK for x in tape.cells[prefix + 1:]), 'reserved payload role retired')
    s.need(all(x == s.BLANK for x in control.cells[prefix + 1:]), 'control frames erased')
    s.need(all(x == s.BLANK for x in descriptor.cells[1:]), 'resume descriptor erased')
    s.need(all(all(x == s.BLANK for x in tape.cells[1:]) for tape in relays), 'all relay bodies erased')
    s.need(len(set(sizes)) == 1, 'completed sibling invocations grew retained backing')
    return {'p': p, 'records': records, 'nested_edges': depth, 'ancestor_prefix': prefix,
            'sequential_reuses': cycles, 'per_reuse_retained_cells': sizes,
            'physical_actions': counts.total - before,
            'retained_cells': sum(len(t.cells) for t in payloads + relays + [control, descriptor, depth_tape]),
            'physical_tapes': len(identities)}

def unequal_boundary(parent_p, parent_m, child_p, child_m, prefix):
    """A real unequal subjob boundary, not a whole-parent child substitution.

    Its delivered result stays in role8 while the parked parentZ is preserved.
    This checks the boundary that a production row-splitting implementation
    could call; it does not claim to implement that splitter or assembly.
    """
    counts = s.Counts()
    payloads = [s.Tape([1] * prefix, counts=counts) for _ in range(16)]
    control = s.Tape([0] * prefix, s.BASE, counts)
    descriptor = s.Tape([], s.BASE, counts)
    relays = [s.Tape([], s.BASE, counts) for _ in range(4)]
    depth_tape = s.Tape([], s.BASE, counts)
    parent_x = [2, -1] * parent_m
    parent_y = [-2, 1] * parent_m
    child_x = [1, -2] * child_m
    words = [bits(parent_x, parent_p), bits(parent_y, parent_p), [],
             [int(c) for c in bin(parent_p)[2:][::-1]] + [q.RIGHT],
             [int(c) for c in bin(parent_m)[2:][::-1]] + [q.RIGHT], [], [], []]
    for tape, word in zip(payloads, words):
        for bit in code([q.LEFT] + word):
            s.emit(tape, bit)
        query_origin(tape)
    child_words = [bits(child_x, child_p),
                   [int(c) for c in bin(child_p)[2:][::-1]] + [q.RIGHT],
                   [int(c) for c in bin(child_m)[2:][::-1]] + [q.RIGHT]]
    for tape, word in zip(relays, child_words):
        for bit in code([q.LEFT] + word):
            s.emit(tape, bit)
        at_start(tape, s.BASE)
    dispatcher = Dispatcher(payloads, control, descriptor, relays, depth_tape)
    execute(TABLES[0], dispatcher.ports)
    parent = [(list(t.cells), t.head) for t in payloads[:8]]
    before = counts.total
    dispatcher.push_staged()
    execute(TABLES[0], dispatcher.ports)
    execute(TABLES[1], dispatcher.ports)
    r.return_output(payloads, control, descriptor, relays[3], q.Y, 8)
    s.need(descriptor.read() == 1, 'unequal subjob resume phase')
    s.emit(descriptor, s.BLANK)
    s.need(descriptor.read() == s.BLANK, 'unequal subjob phase end')
    at_start(descriptor, s.BASE)
    for tape, (old, head) in zip(payloads[:8], parent):
        s.need(tape.cells[:len(old)] == old and tape.head == head,
               'unequal subjob disturbed parked parent')
    expected = code([q.LEFT] + bits([2 * x for x in child_x], child_p))
    s.need(payloads[8].cells[prefix + 1:prefix + 1 + len(expected)] == expected,
           'unequal subjob complete output delivery')
    # Parent retains its original full-size Z. An independent subjob result
    # cannot be silently substituted for a different-size complete query result.
    execute(TABLES[1], dispatcher.ports)
    wanted = code([q.LEFT] + bits([x + y for x, y in zip(parent_x, parent_y)], parent_p))
    s.need(payloads[q.Y].cells[prefix + 1:prefix + 1 + len(wanted)] == wanted,
           'parent full-size query failed after unequal subjob')
    clear(payloads[8])
    s.need(all(all(v == s.BLANK for v in t.cells[1:]) for t in relays),
           'unequal subjob relay cleanup')
    return {'parent_p': parent_p, 'parent_records': parent_m,
            'child_p': child_p, 'child_records': child_m,
            'ancestor_prefix': prefix, 'physical_actions': counts.total - before,
            'physical_tapes': 23}

def run_checks():
    interior_blank_roundtrip()
    results = [fixture(p, m, d, prefix)
               for p in (5, 9, 17) for m in (1, 2, 4)
               for d in (0, 1, 2, 4) for prefix in (0, 17, 257)]
    results += [fixture(9, 4, 4, prefix, cycles=15) for prefix in (0, 17, 257)]
    results += [fixture(9, 4, 31, prefix) for prefix in (0, 17, 257)]
    unequal = [unequal_boundary(pp, pm, cp, cm, prefix)
               for pp, pm, cp, cm in ((17, 4, 5, 1), (5, 4, 17, 2), (9, 4, 9, 1))
               for prefix in (0, 17, 257)]
    return {
        'status': 'prototype-cases-pass', 'query_table_lengths': list(map(len, TABLES)),
        'cases': results,
        'unequal_subjob_cases': unequal,
        'scope': 'Finite-symbol codec and unary-depth nested query boundary; leaf identity is a named semantic fixture, not native admission; no selected production grammar or global reserve claimed.'
    }

if __name__ == '__main__':
    print(json.dumps(run_checks(), indent=2))
