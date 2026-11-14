"""A fixed finite-control, ten-tape ROM query machine; no decoded parameters.

JoyboyBrian with substantial OpenAI Codex assistance. Apache-2.0.
The assembler depends only on static role names, never on a query instance.
"""
from collections import Counter

ROLES = ('h', 's', 'offset', 'target', 'rom', 'out', 'count', 'col', 'row', 'limit')
PRIVATE = ('count', 'col', 'row', 'limit')
BORROWED = ('h', 's', 'offset', 'target', 'rom')

class Builder:
    def __init__(self):
        self.code = []
        self.labels = {}
        self.serial = 0
    def new(self, prefix):
        self.serial += 1
        return f'{prefix}_{self.serial}'
    def mark(self, label):
        self.labels[label] = len(self.code)
    def emit(self, *instruction):
        self.code.append(instruction)
    def branch(self, reg, symbol, yes, no):
        # One finite-alphabet equality and one Boolean branch, separately paid.
        self.emit('eq', reg, symbol, 'test')
        self.emit('branch', 'test', yes, no)
    def rewind(self, tape):
        loop, done, back = (self.new(x) for x in ('rewind', 'home', 'back'))
        self.mark(loop); self.emit('read', tape, 'scan')
        self.branch('scan', 'L', done, back)
        self.mark(back); self.emit('move', tape, -1); self.emit('jump', loop)
        self.mark(done)
    def init(self, tape):
        self.emit('write', tape, 'L'); self.emit('move', tape, 1)
        self.emit('write', tape, 'R'); self.emit('move', tape, -1)
    def clear(self, tape):
        loop, end, more = (self.new(x) for x in ('erase', 'erase_end', 'erase_more'))
        self.emit('move', tape, 1)
        self.mark(loop); self.emit('read', tape, 'scan')
        self.branch('scan', 'R', end, more)
        self.mark(more); self.emit('write', tape, '_'); self.emit('move', tape, 1)
        self.emit('jump', loop)
        self.mark(end); self.emit('write', tape, '_')
        self.rewind(tape); self.emit('write', tape, '_')
    def canonical(self, tape, reject):
        loop, digit, more, done, one, zero = (self.new(x) for x in ('canon', 'digit', 'more', 'done', 'one', 'zero'))
        self.emit('set', 'many', '0'); self.emit('move', tape, 1)
        self.emit('read', tape, 'digit')
        self.mark(loop)
        self.branch('digit', '0', digit, one)
        self.mark(one); self.branch('digit', '1', digit, reject)
        self.mark(digit); self.emit('copy', 'digit', 'last')
        self.emit('move', tape, 1); self.emit('read', tape, 'digit')
        self.branch('digit', 'R', done, more)
        self.mark(more); self.emit('set', 'many', '1'); self.emit('jump', loop)
        self.mark(done); self.branch('last', '1', zero, one + '_last')
        self.mark(one + '_last'); self.branch('many', '0', zero, reject)
        self.mark(zero); self.rewind(tape)
    def copy_word(self, src, dst, zeros=False):
        loop, more, end = (self.new(x) for x in ('copy', 'copy_more', 'copy_end'))
        self.emit('move', src, 1); self.emit('move', dst, 1)
        self.mark(loop); self.emit('read', src, 'scan')
        self.branch('scan', 'R', end, more)
        self.mark(more)
        if zeros: self.emit('write', dst, '0')
        else: self.emit('write_reg', dst, 'scan')
        self.emit('move', src, 1); self.emit('move', dst, 1); self.emit('jump', loop)
        self.mark(end); self.emit('write', dst, 'R'); self.rewind(src); self.rewind(dst)
    def is_zero(self, tape):
        loop, more, end, bitzero = (self.new(x) for x in ('zero', 'zero_more', 'zero_end', 'bitzero'))
        self.emit('set', 'zero', '1'); self.emit('move', tape, 1)
        self.mark(loop); self.emit('read', tape, 'scan')
        self.branch('scan', 'R', end, more)
        self.mark(more); self.branch('scan', '0', bitzero, bitzero + '_no')
        self.mark(bitzero + '_no'); self.emit('set', 'zero', '0')
        self.mark(bitzero); self.emit('move', tape, 1); self.emit('jump', loop)
        self.mark(end); self.rewind(tape)
    def decrement(self, tape):
        loop, zero, one = (self.new(x) for x in ('dec', 'dec_zero', 'dec_one'))
        self.emit('move', tape, 1)
        self.mark(loop); self.emit('read', tape, 'scan')
        self.branch('scan', '0', zero, one)
        self.mark(zero); self.emit('write', tape, '1'); self.emit('move', tape, 1); self.emit('jump', loop)
        self.mark(one); self.emit('write', tape, '0'); self.rewind(tape)
    def increment(self, tape):
        loop, notend, zero, one, overflow, end = (self.new(x) for x in ('inc', 'inc_bit', 'inc_zero', 'inc_one', 'inc_overflow', 'inc_end'))
        self.emit('set', 'carry', '0'); self.emit('move', tape, 1)
        self.mark(loop); self.emit('read', tape, 'scan')
        self.branch('scan', 'R', overflow, notend)
        self.mark(notend); self.branch('scan', '0', zero, one)
        self.mark(zero); self.emit('write', tape, '1'); self.emit('jump', end)
        self.mark(one); self.emit('write', tape, '0'); self.emit('move', tape, 1); self.emit('jump', loop)
        self.mark(overflow); self.emit('set', 'carry', '1')
        self.mark(end); self.rewind(tape)
    def compare(self, left, right):
        # LSB-first comparison, with zero padding after either R. No length word.
        loop, leftend, leftbit, rightcheck, rightend, rightbit, compare, equal, less, greater, advance, moveleft, moveright, end = (self.new(x) for x in ('cmp', 'leftend', 'leftbit', 'rightcheck', 'rightend', 'rightbit', 'compare', 'equal', 'less', 'greater', 'advance', 'moveleft', 'moveright', 'cmp_end'))
        self.emit('set', 'cmp', '='); self.emit('move', left, 1); self.emit('move', right, 1)
        self.mark(loop); self.emit('read', left, 'a'); self.emit('read', right, 'b')
        self.branch('a', 'R', leftend, leftbit)
        self.mark(leftend); self.branch('b', 'R', end, rightcheck)
        self.mark(leftbit); self.emit('jump', rightcheck)
        self.mark(rightcheck); self.emit('copy', 'a', 'av'); self.emit('copy', 'b', 'bv')
        self.branch('a', 'R', rightend, rightbit)
        self.mark(rightend); self.emit('set', 'av', '0')
        self.mark(rightbit); self.branch('b', 'R', compare + '_pad', compare)
        self.mark(compare + '_pad'); self.emit('set', 'bv', '0')
        self.mark(compare); self.emit('eq_reg', 'av', 'bv', 'test'); self.emit('branch', 'test', equal, less)
        self.mark(less); self.branch('av', '0', less + '_set', greater)
        self.mark(less + '_set'); self.emit('set', 'cmp', '<'); self.emit('jump', equal)
        self.mark(greater); self.emit('set', 'cmp', '>')
        self.mark(equal); self.branch('a', 'R', advance, moveleft)
        self.mark(moveleft); self.emit('move', left, 1)
        self.mark(advance); self.branch('b', 'R', loop, moveright)
        self.mark(moveright); self.emit('move', right, 1); self.emit('jump', loop)
        self.mark(end); self.rewind(left); self.rewind(right)
    def finish(self):
        resolved = []
        for op, *args in self.code:
            if op == 'jump': args[0] = self.labels[args[0]]
            if op == 'branch': args[1], args[2] = self.labels[args[1]], self.labels[args[2]]
            resolved.append((op, *args))
        return tuple(resolved)

def assemble():
    b = Builder(); e = b.emit
    reject, cleanup, accept = 'reject', 'cleanup', 'accept'
    for tape in PRIVATE: b.init(tape)
    b.init('out'); e('move', 'out', 1); e('write', 'out', '0')
    e('move', 'out', 1); e('write', 'out', 'R'); b.rewind('out')
    for tape in ('h', 's', 'offset', 'target'): b.canonical(tape, reject)
    b.is_zero('h'); b.branch('zero', '1', reject, 'h_positive'); b.mark('h_positive')
    # Canonical s has at least two digits iff s >= 2.
    e('move', 's', 1); e('move', 's', 1); e('read', 's', 'scan')
    b.branch('scan', 'R', reject, 's_at_least_two'); b.mark('s_at_least_two'); b.rewind('s')
    b.copy_word('h', 'count'); e('move', 'col', 1); e('move', 'limit', 1)
    b.mark('width_loop'); b.is_zero('count'); b.branch('zero', '1', 'width_done', 'width_more')
    b.mark('width_more')
    for tape in ('col', 'limit'):
        e('write', tape, '0'); e('move', tape, 1); e('write', tape, 'R')
    b.decrement('count'); e('jump', 'width_loop')
    b.mark('width_done'); e('write', 'limit', '1'); e('move', 'limit', 1); e('write', 'limit', 'R')
    b.rewind('limit'); b.rewind('col')
    b.compare('s', 'limit'); b.branch('cmp', '>', reject, 's_fits'); b.mark('s_fits')
    b.compare('offset', 's'); b.branch('cmp', '<', 'offset_fits', reject); b.mark('offset_fits')
    b.compare('target', 'limit'); b.branch('cmp', '<', 'target_fits', reject); b.mark('target_fits')
    b.copy_word('s', 'row', zeros=True)
    e('set', 'found', '0'); e('move', 'rom', 1)
    b.mark('scan_loop'); e('read', 'rom', 'rombit')
    b.branch('rombit', 'R', 'scan_done', 'rom_not_end')
    b.mark('rom_not_end'); b.branch('rombit', '0', 'rom_bit', 'rom_maybe_one')
    b.mark('rom_maybe_one'); b.branch('rombit', '1', 'rom_bit', reject)
    b.mark('rom_bit'); b.compare('row', 's'); b.branch('cmp', '=', reject, 'row_room'); b.mark('row_room')
    b.compare('row', 'offset'); e('copy', 'cmp', 'rowmatch'); b.compare('col', 'target')
    b.branch('rowmatch', '=', 'maybe_hit', 'after_hit'); b.mark('maybe_hit')
    b.branch('cmp', '=', 'hit', 'after_hit'); b.mark('hit')
    b.branch('found', '1', reject, 'first_hit'); b.mark('first_hit')
    e('set', 'found', '1'); e('move', 'out', 1); e('write_reg', 'out', 'rombit'); e('move', 'out', -1)
    b.mark('after_hit'); b.increment('col'); b.branch('carry', '1', 'next_row', 'next_bit')
    b.mark('next_row'); b.increment('row'); b.branch('carry', '1', reject, 'next_bit')
    b.mark('next_bit'); e('move', 'rom', 1); e('jump', 'scan_loop')
    b.mark('scan_done'); b.is_zero('col'); b.branch('zero', '1', 'col_done', reject); b.mark('col_done')
    b.compare('row', 's'); b.branch('cmp', '=', 'row_done', reject); b.mark('row_done')
    b.branch('found', '1', accept, reject)
    b.mark(accept); e('set', 'status', '1'); e('jump', cleanup)
    b.mark(reject); e('set', 'status', '0')
    b.mark(cleanup)
    for tape in PRIVATE:
        b.rewind(tape); b.clear(tape)
    for tape in BORROWED: b.rewind(tape)
    b.branch('status', '1', 'halt_accept', 'clean_reject_output')
    b.mark('clean_reject_output'); b.rewind('out'); b.clear('out'); e('halt', 'reject')
    b.mark('halt_accept'); e('halt', 'accept')
    return b.finish()

PROGRAM = assemble()

class Machine:
    """Host interpreter: position/PC/census integers are machine metadata only.

    The fixed program can access only alphabet registers and current cells.
    Python dictionary addressing implements a tape head, never a data lookup.
    """
    def __init__(self, records, trace=False, program=PROGRAM):
        self.tapes = {role: {} for role in ROLES}
        for role, payload in records.items():
            self.tapes[role] = dict(enumerate('L' + payload + 'R'))
        self.heads = dict.fromkeys(ROLES, 0)
        self.registers = {}; self.pc = 0; self.census = Counter()
        self.trace = [] if trace else None
        self.program = program
    def run(self, limit=20_000_000):
        # limit is an observer watchdog; an overrun fails, never returns a bit.
        for _ in range(limit):
            pc = self.pc; instruction = self.program[pc]; op, *a = instruction
            self.pc += 1; self.census[op] += 1
            observed = None
            if op == 'read':
                observed = self.tapes[a[0]].get(self.heads[a[0]], '_')
                self.registers[a[1]] = observed
            elif op in ('write', 'write_reg'):
                observed = a[1] if op == 'write' else self.registers[a[1]]
                self.tapes[a[0]][self.heads[a[0]]] = observed
            elif op == 'move': self.heads[a[0]] += a[1]
            elif op == 'set': self.registers[a[0]] = a[1]
            elif op == 'copy': self.registers[a[1]] = self.registers[a[0]]
            elif op == 'eq': self.registers[a[2]] = self.registers[a[0]] == a[1]
            elif op == 'eq_reg': self.registers[a[2]] = self.registers[a[0]] == self.registers[a[1]]
            elif op == 'branch': self.pc = a[1] if self.registers[a[0]] else a[2]
            elif op == 'jump': self.pc = a[0]
            elif op != 'halt': raise ValueError(op)
            if self.trace is not None: self.trace.append((pc, observed))
            if op == 'halt': return a[0]
        raise RuntimeError('observer watchdog exceeded: not an accepted execution')
