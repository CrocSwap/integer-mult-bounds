"""Literal raw-field port for the whole-high batch order.

Python loops compile finite tables. Runtime uses only the retained local
instruction interpreter. Prepared for @CubeJerry with substantial OpenAI
Codex assistance, Apache-2.0. Imported arithmetic retains #6719/#2776 credit.
"""
from pathlib import Path
import importlib.util
import sys

HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location('chronological_retained', HERE/'vendor6719/inputs/core/recursive.py')
retained = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = retained
_spec.loader.exec_module(retained)
m, c = retained.m, retained.P.c
BL, LEFT, RIGHT, Z, O, WE, FE = m.BLANK, m.LEFT, m.RIGHT, m.ZERO, m.ONE, m.UNIT, m.MARK
WIDTH, CODES, FIBRE, PAYLOAD = range(4)
W, F, CAP, TEMPLATE, W_GUIDE, WORK, F_GUIDE, STATE, PREFIX = range(4, 13)
TAPES = 13


class Builder:
    def __init__(self, q, dimension, code_bits, oldest_first=True, input_markers=None):
        m.need(type(q) is int and q >= 3 and q % 2, 'compiled odd radix')
        m.need(type(dimension) is int and dimension >= 1, 'compiled dimension')
        m.need(type(code_bits) is int and code_bits >= 1, 'compiled code width')
        self.q, self.dimension, self.code_bits, self.oldest_first = q, dimension, code_bits, oldest_first
        self.input_markers = input_markers or {WIDTH:LEFT,FIBRE:LEFT,PAYLOAD:LEFT}
        self.a = m.Assembler(TAPES); self.fail = self.a.fresh('invalid_port'); self.events = {}

    def labels(self, *names): return tuple(self.a.fresh(n) for n in names)

    def expect(self, tape, symbol):
        yes = self.a.fresh('expected'); self.a.branch(tape, {symbol:yes}, self.fail); self.a.label(yes)

    def emit(self, tape, symbol): self.a.write(tape, symbol); self.a.move(tape, 1)

    def initialize(self, tape): self.expect(tape, BL); self.emit(tape, LEFT)

    def rewind(self, tape): c.emit_rewind(self.a, tape, 'origin')

    def rewind_encoded(self, tape):
        loop,back,done=self.labels('encoded_origin','back','found'); self.a.move(tape,-1)
        self.a.label(loop)
        self.a.branch(tape,{self.input_markers[tape]:done,Z:back,O:back},self.fail)
        self.a.label(back); self.a.move(tape,-1); self.a.goto(loop)
        self.a.label(done); self.a.move(tape,1)
        for _ in range(3): self.a.move(tape, 1)

    def code_branch(self, tape, cases):
        labels = {(n,v):self.a.fresh('code') for n in range(1,4) for v in range(1<<n)}
        self.a.branch(tape, {Z:labels[1,0], O:labels[1,1]}, self.fail)
        for n in (1,2):
            for v in range(1<<n):
                self.a.label(labels[n,v]); self.a.move(tape,1)
                self.a.branch(tape, {Z:labels[n+1,2*v], O:labels[n+1,2*v+1]}, self.fail)
        for v in range(8):
            self.a.label(labels[3,v]); self.a.move(tape,-1); self.a.move(tape,-1)
            self.a.goto(cases.get(v,self.fail))

    def code_move(self, tape):
        for _ in range(3): self.a.move(tape,1)

    def decode(self, source, target):
        self.initialize(target); loop,zero,one,done = self.labels('decode','zero','one','done')
        self.a.label(loop); self.code_branch(source,{Z:zero,O:one,RIGHT:done})
        for label,bit in ((zero,Z),(one,O)):
            self.a.label(label); self.expect(target,BL); self.emit(target,bit)
            self.code_move(source); self.a.goto(loop)
        self.a.label(done); self.expect(target,BL); self.a.write(target,RIGHT)
        self.rewind(target); self.rewind_encoded(source)

    def inline(self, program, ports):
        labels = [self.a.fresh('retained_pc') for _ in program.instructions]; done = self.a.fresh('return')
        self.a.goto(labels[program.entry])
        for pc,row in enumerate(program.instructions):
            self.a.label(labels[pc]); op=row[0]
            if op=='branch': self.a.branch(ports[row[1]],{s:labels[t] for s,t in row[2]},labels[row[3]])
            elif op=='write': self.a.write(ports[row[1]],row[2])
            elif op=='move': self.a.move(ports[row[1]],row[2])
            elif op=='goto': self.a.goto(labels[row[1]])
            elif op=='halt': self.a.goto(done)
            else: self.a.goto(self.fail)
        self.a.label(done)

    def copy_word(self, source, target):
        loop,zero,one,done=self.labels('copy_word','zero','one','done'); self.a.label(loop)
        self.a.branch(source,{Z:zero,O:one,RIGHT:done},self.fail)
        for label,bit in ((zero,Z),(one,O)):
            self.a.label(label); self.expect(target,BL); self.emit(target,bit)
            self.a.move(source,1); self.a.goto(loop)
        self.a.label(done); self.a.write(target,RIGHT); self.rewind(source); self.rewind(target)

    def seek_right(self, tape, delimiter=RIGHT):
        loop,more,done=self.labels('seek','more','found'); self.a.label(loop)
        self.a.branch(tape,{delimiter:done},more); self.a.label(more)
        self.a.move(tape,1); self.a.goto(loop); self.a.label(done)

    def word_origin(self):
        loop,more,done=self.labels('digit_origin','back','found'); self.a.move(STATE,-1)
        self.a.label(loop); self.a.branch(STATE,{WE:done,Z:more,O:more},self.fail)
        self.a.label(more); self.a.move(STATE,-1); self.a.goto(loop)
        self.a.label(done); self.a.move(STATE,1)

    def previous_word(self): self.a.move(STATE,-1); self.expect(STATE,WE); self.word_origin()

    def next_word(self): self.seek_right(STATE,WE); self.a.move(STATE,1)

    def pad_cap(self):
        scanning,padding,finish,more,live=self.labels('pad_cap','padding','finish','bit','live')
        self.a.label(scanning); self.a.branch(TEMPLATE,{Z:more,O:more},self.fail)
        self.a.label(more); self.a.branch(CAP,{Z:live,O:live,RIGHT:padding},self.fail)
        self.a.label(live); self.a.write(TEMPLATE,Z); self.a.move(TEMPLATE,1); self.a.move(CAP,1)
        self.a.goto(scanning); self.a.label(padding); self.a.write(TEMPLATE,Z)
        self.emit(CAP,Z); self.a.move(TEMPLATE,1)
        self.a.branch(TEMPLATE,{Z:padding,O:padding,RIGHT:finish},self.fail)
        self.a.label(finish); self.a.write(CAP,RIGHT); self.rewind(CAP); self.rewind(TEMPLATE)

    def initialize_state(self):
        self.initialize(STATE); field,done=self.labels('initialize_field','initialized')
        self.a.label(field)
        for _ in range(self.code_bits):
            zero,one,after=self.labels('code_zero','code_one','after')
            self.a.branch(CODES,{Z:zero,O:one},self.fail)
            for label,bit in ((zero,Z),(one,O)):
                self.a.label(label); self.emit(STATE,bit); self.a.move(CODES,1); self.a.goto(after)
            self.a.label(after)
        self.expect(CODES,WE); self.a.move(CODES,1); self.emit(STATE,WE)
        for _ in range(self.dimension*self.dimension):
            loop,bit,stop=self.labels('zero_word','bit','done'); self.a.label(loop)
            self.a.branch(TEMPLATE,{Z:bit,RIGHT:stop},self.fail); self.a.label(bit)
            self.emit(STATE,Z); self.a.move(TEMPLATE,1); self.a.goto(loop)
            self.a.label(stop); self.emit(STATE,WE); self.rewind(TEMPLATE)
        self.emit(STATE,FE); self.a.branch(CODES,{Z:field,O:field,RIGHT:done},self.fail)
        self.a.label(done); self.a.write(STATE,RIGHT); self.rewind(STATE); self.rewind(CODES)

    def emit_prefix(self):
        loop,done=self.labels('emit_prefix','copied'); self.a.label(loop)
        cases={v:self.a.fresh('symbol') for v in (Z,O,WE,FE)}
        self.a.branch(STATE,{**cases,RIGHT:done},self.fail)
        for symbol,label in cases.items():
            self.a.label(label); self.expect(PREFIX,BL); self.emit(PREFIX,symbol)
            self.a.move(STATE,1); self.a.goto(loop)
        self.a.label(done); self.rewind(STATE); self.rewind(PREFIX)

    def clear_prefix(self):
        loop,more,done=self.labels('clear_prefix','more','empty'); self.a.label(loop)
        self.a.branch(PREFIX,{Z:more,O:more,WE:more,FE:more,BL:done},self.fail)
        self.a.label(more); self.emit(PREFIX,BL); self.a.goto(loop)
        self.a.label(done); self.rewind(PREFIX)

    def consume_fibre(self):
        loop,read,advance,done=self.labels('fibre','read','advance','done'); self.a.label(loop)
        self.a.branch(F_GUIDE,{WE:read,RIGHT:done},self.fail); self.a.label(read)
        self.code_branch(PAYLOAD,{Z:advance,O:advance}); self.a.label(advance)
        self.events['payload_advance']=len(self.a.instructions)
        self.code_move(PAYLOAD); self.a.move(F_GUIDE,1); self.a.goto(loop)
        self.a.label(done); self.rewind(F_GUIDE)

    def increment_word(self, no_carry):
        ripple,zero,one,inc=self.labels('ripple','zero','one','incremented'); self.a.label(ripple)
        self.a.branch(STATE,{Z:zero,O:one},self.fail); self.a.label(one)
        self.emit(STATE,Z); self.a.goto(ripple); self.a.label(zero)
        self.a.write(STATE,O); self.a.goto(inc); self.a.label(inc); self.word_origin()
        states={v:self.a.fresh('compare') for v in (-1,0,1)}
        ends={v:self.a.fresh('compared') for v in (-1,0,1)}; self.a.goto(states[0])
        for relation in (-1,0,1):
            self.a.label(states[relation]); first={v:self.a.fresh('left_bit') for v in (Z,O)}
            self.a.branch(STATE,{**first,WE:ends[relation]},self.fail)
            for left,label in first.items():
                self.a.label(label); actions={v:self.a.fresh('right_bit') for v in (Z,O)}
                self.a.branch(CAP,actions,self.fail)
                for right,action in actions.items():
                    self.a.label(action); self.a.move(STATE,1); self.a.move(CAP,1)
                    nxt=relation if left==right else 1 if left==O else -1
                    self.a.goto(states[nxt])
        equal=self.a.fresh('equal_cap')
        for relation in (-1,0,1):
            self.a.label(ends[relation]); self.expect(CAP,RIGHT); self.rewind(CAP); self.word_origin()
            self.a.goto(no_carry if relation==-1 else equal if relation==0 else self.fail)
        self.a.label(equal); loop,more,done=self.labels('reset','more','done'); self.a.label(loop)
        self.a.branch(STATE,{Z:more,O:more,WE:done},self.fail); self.a.label(more)
        self.emit(STATE,Z); self.a.goto(loop); self.a.label(done); self.word_origin()

    def previous_field(self, wrapped, next_field):
        for _ in range(self.code_bits+2): self.a.move(STATE,-1)
        scan,loop,back,found=self.labels('previous','scan','back','found')
        self.a.branch(STATE,{LEFT:wrapped,FE:scan},self.fail); self.a.label(scan)
        self.a.move(STATE,-1); self.a.label(loop)
        self.a.branch(STATE,{LEFT:found,FE:found,Z:back,O:back,WE:back},self.fail)
        self.a.label(back); self.a.move(STATE,-1); self.a.goto(loop)
        self.a.label(found); self.a.move(STATE,1); self.a.goto(next_field)

    def advance(self, not_wrapped, wrapped):
        field,no_carry,overflow=self.labels('advance_field','no_carry','overflow')
        if not self.oldest_first:
            self.seek_right(STATE); self.a.move(STATE,-1); self.expect(STATE,FE); self.a.move(STATE,-1)
            loop,back,found=self.labels('last_field','back','found'); self.a.label(loop)
            self.a.branch(STATE,{LEFT:found,FE:found,Z:back,O:back,WE:back},self.fail)
            self.a.label(back); self.a.move(STATE,-1); self.a.goto(loop)
            self.a.label(found); self.a.move(STATE,1)
        self.a.label(field)
        for _ in range(self.code_bits+1): self.a.move(STATE,1)
        for _ in range(self.dimension*self.dimension-1): self.next_word()
        for index in reversed(range(self.dimension*self.dimension)):
            self.increment_word(no_carry)
            if index: self.previous_word()
        if self.oldest_first:
            for _ in range(self.dimension*self.dimension): self.next_word()
            self.expect(STATE,FE); self.a.move(STATE,1)
            self.events['field_carry']=len(self.a.instructions)
            self.a.branch(STATE,{Z:field,O:field,RIGHT:overflow},self.fail)
        else: self.previous_field(overflow,field)
        self.a.label(overflow)
        if not self.oldest_first: self.a.move(STATE,1)
        self.rewind(STATE); self.a.goto(wrapped); self.a.label(no_carry)
        self.rewind(STATE); self.a.goto(not_wrapped)

    def retire(self, tape):
        self.seek_right(tape); loop,more,done=self.labels('retire','more','done'); self.a.label(loop)
        self.a.branch(tape,{LEFT:done},more); self.a.label(more)
        self.a.write(tape,BL); self.a.move(tape,-1); self.a.goto(loop)
        self.a.label(done); self.a.write(tape,BL)

    def compile(self):
        self.decode(WIDTH,W); self.decode(FIBRE,F)
        self.inline(retained.high_program(self.q),{0:W,1:CAP,2:W_GUIDE,3:WORK})
        self.initialize(TEMPLATE); self.copy_word(CAP,TEMPLATE)
        retained.multiply_constant(self.a,TEMPLATE,self.q,self.fail,'word_extent')
        self.seek_right(TEMPLATE); self.emit(TEMPLATE,Z); self.a.write(TEMPLATE,RIGHT)
        self.rewind(TEMPLATE); self.pad_cap()
        self.initialize(F_GUIDE); self.initialize(WORK)
        c.emit_binary_to_unary(self.a,F,WORK,F_GUIDE,'complete_fibre')
        self.initialize_state(); self.initialize(PREFIX)
        nonwrap,wrap,emit,finish=self.labels('nonwrapped','wrapped','emit','finished')
        self.a.goto(nonwrap); self.a.label(nonwrap); self.code_branch(PAYLOAD,{Z:emit,O:emit})
        self.a.label(wrap); self.code_branch(PAYLOAD,{Z:emit,O:emit,RIGHT:finish})
        self.a.label(emit); self.emit_prefix(); self.events['ready']=len(self.a.instructions)
        continuation=self.a.fresh('consumer_return')
        self.a.goto(continuation)  # Precise finite subroutine replacement port.
        self.a.label(continuation); self.events['prefix_clear']=len(self.a.instructions)
        self.clear_prefix(); self.events['fibre_begin']=len(self.a.instructions); self.consume_fibre()
        self.advance(nonwrap,wrap); self.a.label(finish); self.events['cleanup']=len(self.a.instructions)
        self.rewind_encoded(PAYLOAD)
        for tape in (W,F,CAP,TEMPLATE,F_GUIDE,STATE):
            if tape==STATE: self.events['state_retire']=len(self.a.instructions)
            self.retire(tape)
        self.events['state_retired']=len(self.a.instructions)
        self.a.move(WORK,-1); self.expect(WORK,LEFT); self.a.write(WORK,BL)
        self.a.move(PREFIX,-1); self.expect(PREFIX,LEFT); self.a.write(PREFIX,BL)
        self.a.halt(); self.a.label(self.fail); self.a.reject('chronological raw-field producer port')
        return self.a.finish(), {'q':self.q,'dimension':self.dimension,'code_bits':self.code_bits,
                                'tapes':TAPES,'events':self.events,'oldest_first':self.oldest_first}


def build(q=3, dimension=2, code_bits=2, *, oldest_first=True, input_markers=None):
    return Builder(q,dimension,code_bits,oldest_first,input_markers).compile()
