"""Paid finite-control key at the retained twelve-bit repair port.

JoyboyBrian, with substantial OpenAI Codex assistance. Apache-2.0.
The source query builder and program are supplied from authenticated PR4752 bytes.
"""
from collections import Counter

OWNED_WIDTHS = {'h': 3, 's': 2, 'offset': 1, 'target': 4, 'out': 1,
                'count': 3, 'col': 4, 'row': 2, 'limit': 5, 'u': 2, 't': 2, 'y': 8}
ROLES = ('counter', 'stream', 'rom', *OWNED_WIDTHS)


def assemble(query, target, fault='correct'):
    if target not in (0, 1, 2): raise ValueError('retained three-target geometry only')
    if fault not in ('correct', 'stale', 'drop_high', 'omit_clear', 'omit_rom_return'):
        raise ValueError('unknown verifier mutation')
    b = query.Builder(); e = b.emit
    returns = []; entries = []

    def rewind_counter():
        loop, back, done = (b.new(s) for s in ('counter_home', 'counter_back', 'counter_done'))
        b.mark(loop); e('read', 'counter', 'scan'); b.branch('scan', '<', done, back)
        b.mark(back); e('move', 'counter', -1); e('jump', loop); b.mark(done)

    def at(role, position):
        # All arguments and loop bounds in this assembler are finite constants.
        b.rewind(role)
        for _ in range(position): e('move', role, 1)

    def read_bit(role, bit, reg):
        at(role, bit+1); e('read', role, reg); b.rewind(role)

    def clear_fixed(role):
        # Each private head is at zero here, even after query rejection.
        for _ in range(OWNED_WIDTHS[role]+2):
            e('write', role, '_'); e('move', role, 1)
        for _ in range(OWNED_WIDTHS[role]+2): e('move', role, -1)

    def constant_word(role, word):
        e('write', role, 'L')
        for bit in word: e('move', role, 1); e('write', role, bit)
        e('move', role, 1); e('write', role, 'R'); b.rewind(role)

    def add_constant(role, width, value, condition):
        done, active = b.new('add_done'), b.new('add_active')
        b.branch(condition, '1', active, done); b.mark(active)
        e('set', 'key_carry', '0'); e('move', role, 1)
        for bit in range(width):
            e('read', role, 'key_a'); e('set', 'key_b', '1' if (value >> bit) & 1 else '0')
            e('xorbit', 'key_a', 'key_b', 'key_ab')
            e('xorbit', 'key_ab', 'key_carry', 'key_sum')
            e('andbit', 'key_a', 'key_b', 'key_abcarry')
            e('andbit', 'key_ab', 'key_carry', 'key_acarry')
            e('orbit', 'key_abcarry', 'key_acarry', 'key_carry')
            e('write_reg', role, 'key_sum'); e('move', role, 1)
        b.rewind(role); b.mark(done)

    def descriptor():
        clear_fixed('offset'); clear_fixed('target')
        read_bit('y', 4, 'key_descriptor'); e('write', 'offset', 'L'); e('move', 'offset', 1)
        e('write_reg', 'offset', 'key_descriptor'); e('move', 'offset', 1); e('write', 'offset', 'R'); b.rewind('offset')
        done = b.new('canonical_done'); labels = [b.new('canonical_width') for _ in range(4)]
        for bit in (3, 2, 1):
            more = b.new('canonical_smaller'); read_bit('y', bit, 'key_descriptor')
            b.branch('key_descriptor', '1', labels[bit], more); b.mark(more)
        e('jump', labels[0])
        for width in (1, 2, 3, 4):
            b.mark(labels[width-1]); e('write', 'target', 'L'); e('move', 'target', 1)
            for bit in range(width):
                read_bit('y', bit, 'key_descriptor'); e('write_reg', 'target', 'key_descriptor'); e('move', 'target', 1)
            e('write', 'target', 'R'); b.rewind('target'); e('jump', done)
        b.mark(done)

    def source(epoch):
        if fault != 'stale' or epoch == 1: descriptor()
        prefix = b.new('query'); entries.append(prefix+'_entry'); returns.append(prefix+'_return')
        b.mark(prefix+'_entry')
        for pc, instruction in enumerate(query.PROGRAM):
            b.mark(prefix+str(pc)); op, *args = instruction
            if op == 'jump': args[0] = prefix+str(args[0])
            elif op == 'branch': args[1], args[2] = prefix+str(args[1]), prefix+str(args[2])
            elif op == 'halt':
                e('jump', prefix+'_return' if args[0] == 'accept' else 'service_reject'); continue
            e(op, *args)
        b.mark(prefix+'_return'); read_bit('out', 0, 'key_source'); clear_fixed('out')

    e('jump', 'service_start'); b.mark('service_start')
    constant_word('h', '001'); constant_word('s', '01')
    for role, width in (('u', 2), ('t', 2), ('y', 8)): constant_word(role, '0'*width)
    e('move', 'counter', 1)
    for role, bit in [('u', 1), ('u', 0), ('t', 1), ('t', 0), *[('y', j) for j in range(7, -1, -1)]]:
        valid, one = b.new('input_bit'), b.new('input_one')
        e('read', 'counter', 'key_input'); b.branch('key_input', '0', valid, one)
        b.mark(one); b.branch('key_input', '1', valid, 'service_reject'); b.mark(valid)
        at(role, bit+1); e('write_reg', role, 'key_input'); b.rewind(role); e('move', 'counter', 1)
    e('read', 'counter', 'key_input'); b.branch('key_input', '>', 'input_done', 'service_reject')
    b.mark('input_done'); rewind_counter()
    epoch = 0
    for step in range(9, -1, -1):
        if step in (9, 4):
            epoch += 1; source(epoch)
            add_constant('u', 2, 1 if step == 9 else -1, 'key_source')
            continue
        shear = step if step < 4 else step - 5
        read_bit('u', 0, 'key_z'); read_bit('t', 0, 'key_t0'); read_bit('t', 1, 'key_t1')
        read_bit('y', target, 'key_bit')
        e('andbit', 'key_z', 'key_t0', 'key_zt0'); e('andbit', 'key_z', 'key_t1', 'key_zt1')
        ywidth = target+3 if fault == 'drop_high' else 8
        if shear == 0:
            add_constant('y', ywidth, -(1 << (target+1)), 'key_zt0')
            add_constant('y', ywidth, -(1 << (target+2)), 'key_zt1')
        elif shear == 1: add_constant('t', 2, -1, 'key_bit')
        elif shear == 2:
            add_constant('y', ywidth, -(1 << target), 'key_z')
            add_constant('y', ywidth, 1 << (target+1), 'key_zt0')
            add_constant('y', ywidth, 1 << (target+2), 'key_zt1')
        else:
            e('xorbit', 'key_bit', 'key_z', 'key_digit'); add_constant('t', 2, 1, 'key_digit')
    source(3); read_bit('y', target, 'key_bit'); e('xorbit', 'key_bit', 'key_source', 'key_bit')
    at('y', target+1); e('write_reg', 'y', 'key_bit'); b.rewind('y')
    # The actual bad-stream head advances; no host key string is formed.
    for role, bit in [('u', 1), ('u', 0), ('t', 1), ('t', 0), *[('y', j) for j in range(7, -1, -1)]]:
        read_bit(role, bit, 'key_output'); e('write_reg', 'stream', 'key_output'); e('move', 'stream', 1)
    e('set', 'key_status', '1'); e('jump', 'service_cleanup')
    b.mark('service_reject'); e('set', 'key_status', '0')
    b.mark('service_cleanup'); rewind_counter()
    for role in OWNED_WIDTHS:
        if fault != 'omit_clear' or role != 'y': clear_fixed(role)
    if fault == 'omit_rom_return': e('move', 'rom', 1)
    b.branch('key_status', '1', 'service_accept', 'service_failed')
    b.mark('service_accept'); e('halt', 'accept'); b.mark('service_failed'); e('halt', 'reject')
    program = b.finish()
    return program, {'entries': [b.labels[x] for x in entries], 'returns': [b.labels[x] for x in returns]}


class PrivateTape:
    """Sparse initially blank tape; integer head is emulator metadata only."""
    def __init__(self): self.cells = {}; self.head = 0
    def read(self): return self.cells.get(self.head, '_')
    def write(self, value): self.cells[self.head] = value
    def move(self, direction): self.head += direction


class Service:
    def __init__(self, query, target, rom, fault='correct'):
        self.program, self.marks = assemble(query, target, fault)
        self.rom = rom
        self.private = {name: PrivateTape() for name in OWNED_WIDTHS}
        self.calls = 0; self.totals = Counter(); self.last = None

    def evaluate_key(self, counter, stream, meter=None, trace=False):
        tapes = dict(self.private, counter=counter, stream=stream, rom=self.rom)
        regs = {}; pc = 0; census = Counter(); events = [] if trace else None; interface = 0
        # Fixed finite-control dispatch. No tape lengths, head coordinates, or
        # decoded address/descriptor integers are inspected by this executor.
        while True:
            current = pc; op, *a = self.program[pc]; pc += 1; census[op] += 1; value = None
            if op == 'read': value = tapes[a[0]].read(); regs[a[1]] = value
            elif op in ('write', 'write_reg'):
                value = a[1] if op == 'write' else regs[a[1]]; tapes[a[0]].write(value)
            elif op == 'move': tapes[a[0]].move(a[1])
            elif op == 'set': regs[a[0]] = a[1]
            elif op == 'copy': regs[a[1]] = regs[a[0]]
            elif op == 'eq': regs[a[2]] = regs[a[0]] == a[1]
            elif op == 'eq_reg': regs[a[2]] = regs[a[0]] == regs[a[1]]
            elif op == 'xorbit': regs[a[2]] = '1' if (regs[a[0]] == '1') != (regs[a[1]] == '1') else '0'
            elif op == 'andbit': regs[a[2]] = '1' if regs[a[0]] == '1' and regs[a[1]] == '1' else '0'
            elif op == 'orbit': regs[a[2]] = '1' if regs[a[0]] == '1' or regs[a[1]] == '1' else '0'
            elif op == 'branch': pc = a[1] if regs[a[0]] else a[2]
            elif op == 'jump': pc = a[0]
            elif op != 'halt': raise ValueError('unknown opcode')
            if op in ('read', 'write', 'write_reg', 'move') and a[0] in ('counter', 'stream'): interface += 1
            if events is not None: events.append((current, value))
            if op == 'halt': status = a[0]; break
        self.calls += 1; self.totals.update(census)
        self.last = dict(events=events, census=census, registers=regs, status=status, pc=pc, tapes=tapes)
        if meter is not None:
            meter['calls'] += 1
            # Retain the caller's interface invoice as a subset, never add twice.
            meter['interface_actions'] += interface
        if status != 'accept': raise ValueError('key-service input rejected after cleanup')
        return census
