"""Fixed three-lane local program; JoyboyBrian with OpenAI assistance, Apache-2.0.
Builder/Tape instruction semantics credited to retained PR5090.
"""
import importlib.util
from pathlib import Path
_spec = importlib.util.spec_from_file_location('reversal_instruction_source', Path(__file__).resolve().parents[1] / 'bit-row-padding-physical/machine.py')
source = importlib.util.module_from_spec(_spec)
import sys
sys.modules[_spec.name] = source
_spec.loader.exec_module(source)
Builder, Tape, BLANK, LEFT, need = source.Builder, source.Tape, source.BLANK, source.LEFT, source.need
SOURCE, BD, B, TEMP = 0, 4, 8, 10
LANES = (5, 6, 7)
S, N, DATA, NEXT, OUTPUT = 9, 11, 12, 13, 14
WORK = (*LANES, B, TEMP, S, N, DATA, NEXT)


class Control(Builder):
    def row(self, src, dst, consume=False):
        loop, bit, zero, one, end = [self.fresh('row') for _ in range(5)]
        self.mark(loop)
        self.read(B, {'1': bit, BLANK: end})
        self.mark(bit)
        self.read(src, {'0': zero, '1': one})
        self.mark(zero)
        self.write(dst, '0')
        self.go(one + 'written')
        self.mark(one)
        self.write(dst, '1')
        self.mark(one + 'written')
        if consume:
            self.write(src, BLANK)
        self.move(src, 1)
        self.move(dst, 1)
        self.move(B, 1)
        self.go(loop)
        self.mark(end)
        self.rewind(B)

    def chunk(self, src, dst):
        loop, available, record, end = [self.fresh('chunk') for _ in range(4)]
        self.mark(loop)
        self.read(S, {'1': available, BLANK: end})
        self.mark(available)
        self.read(src, {'0': record, '1': record, BLANK: end})
        self.mark(record)
        self.row(src, dst, True)
        self.move(S, 1)
        self.go(loop)
        self.mark(end)
        self.rewind(S)

    def transfer(self, src, dst, consume=False):
        loop, zero, one, end = [self.fresh('transfer') for _ in range(4)]
        self.mark(loop)
        self.read(src, {'0': zero, '1': one, BLANK: end})
        self.mark(zero)
        self.write(dst, '0')
        self.go(one + 'written')
        self.mark(one)
        self.write(dst, '1')
        self.mark(one + 'written')
        if consume:
            self.write(src, BLANK)
        self.move(src, 1)
        self.move(dst, 1)
        self.go(loop)
        self.mark(end)
        self.rewind(src)
        self.rewind(dst)


def program():
    global STAGE_PC
    c = Control()
    c.unary(BD, B)
    scan, record, copied = [c.fresh('input') for _ in range(3)]
    c.mark(scan)
    c.read(SOURCE, {'0': record, '1': record, BLANK: copied})
    c.mark(record)
    c.row(SOURCE, DATA)
    c.write(N, '1')
    c.move(N, 1)
    c.go(scan)
    c.mark(copied)
    for t in (SOURCE, DATA, N): c.rewind(t)
    c.write(S, '1')
    test, nmore, pair, covered, route = [c.fresh('cover') for _ in range(5)]
    c.mark(test)
    c.read(N, {'1': nmore, BLANK: covered})
    c.mark(nmore)
    c.read(S, {'1': pair, BLANK: route})
    c.mark(pair)
    c.move(N, 1)
    c.move(S, 1)
    c.go(test)
    c.mark(route)
    c.rewind(N)
    c.rewind(S)
    split, splitmore, splitend = [c.fresh('split') for _ in range(3)]
    c.mark(split)
    c.read(DATA, {'0': splitmore, '1': splitmore, BLANK: splitend})
    c.mark(splitmore)
    for lane in LANES: c.chunk(DATA, lane)
    c.go(split)
    c.mark(splitend)
    for t in (DATA, *LANES): c.rewind(t)
    merge, mergemore, mergeend = [c.fresh('merge') for _ in range(3)]
    c.mark(merge)
    c.read(LANES[0], {'0': mergemore, '1': mergemore, BLANK: mergeend})
    c.mark(mergemore)
    for lane in reversed(LANES): c.chunk(lane, DATA)
    c.go(merge)
    c.mark(mergeend)
    STAGE_PC = len(c.code)
    for t in (DATA, *LANES): c.rewind(t)
    triple, unit, tripled = [c.fresh('triple') for _ in range(3)]
    c.mark(triple)
    c.read(S, {'1': unit, BLANK: tripled})
    c.mark(unit)
    c.write(S, BLANK)
    c.move(S, 1)
    for _ in range(3):
        c.write(NEXT, '1')
        c.move(NEXT, 1)
    c.go(triple)
    c.mark(tripled)
    c.rewind(S)
    c.rewind(NEXT)
    c.transfer(NEXT, S, True)
    c.go(test)
    c.mark(covered)
    c.rewind(N)
    c.rewind(S)
    c.transfer(DATA, OUTPUT, True)
    for t in WORK: c.clear(t)
    c.code.append(('done',))
    c.mark('reject')
    c.code.append(('rejected',))
    c.mark('quarantine')
    c.code.append(('quarantined',))
    return c.finish()


PROGRAM = program()


class Machine:
    def __init__(self, tapes):
        need(len(tapes) == 15 and len({id(t) for t in tapes}) == 15, 'fifteen distinct ports')
        self.tapes, self.pc, self.steps = tapes, 0, 0

    def run(self, budget=10000000):
        while self.steps < budget:
            ins = PROGRAM[self.pc]
            op = ins[0]
            self.steps += 1
            if op == 'done': return
            if op in ('rejected', 'quarantined'): raise ValueError(op)
            if op == 'goto':
                self.pc = ins[1]
                continue
            t = self.tapes[ins[1]]
            if op == 'read':
                symbol = t.read()
                need(symbol in ins[2], 'local symbol')
                self.pc = ins[2][symbol]
                continue
            if op == 'write':
                t.read()
                t.cells[t.head] = ins[2]
            elif op == 'move':
                t.head += ins[2]
                t.read()
            else: raise ValueError('unknown opcode')
            self.pc += 1
        raise ValueError('execution budget')
