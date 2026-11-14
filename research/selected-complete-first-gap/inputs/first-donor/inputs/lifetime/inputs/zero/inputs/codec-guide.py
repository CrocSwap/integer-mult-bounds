"""Input-independent literal tape bridge. Prepared for @CubeJerry with OpenAI assistance. Apache-2.0."""
from dataclasses import dataclass
from hashlib import sha256
import json

BLANK, LEFT = 2, 3
SCHEMA = ('outer','rows','stock','row_bits','within_bits','record_bits','p','d',
          'K','G','H','q0','qF','qB','D','f','rho','active_start','back_start',
          'selected_axes','entry_start','remainder','cutoff')
NAMES = ('OLD','CONTEXT','PACK','GAMMA','OUT','ZERO','ONE','STAGE','COMP','BIN',
         'LEN','TMP','TMP2','CUTOFF','OUTER','ROWS','ROWCLAIM','A','REC','F','K',
         'RHO','U','W','DEN','R','R2','G','GK','END','KM1','CROWS','N','L',
         'ROWEXPECTED','BASEP','S','EXP','HALF','RUN','CHUNKS','PREFIX','ONECOUNT')
PORT = {name:i for i,name in enumerate(NAMES)}


class Builder:
    def __init__(self):
        self.code=[]; self.labels={}; self.serial=0
    def fresh(self,stem='q'):
        self.serial+=1; return stem+str(self.serial)
    def label(self,name):
        if name in self.labels: raise ValueError('duplicate label')
        self.labels[name]=len(self.code)
    def r(self,t,branches): self.code.append(('R',PORT[t],branches))
    def w(self,t,v): self.code.append(('W',PORT[t],v))
    def m(self,t,d): self.code.append(('M',PORT[t],d))
    def j(self,q): self.code.append(('J',q))
    def halt(self,status): self.code.append(('H',status))
    def expect(self,t,v):
        q=self.fresh(); self.r(t,{v:q}); self.label(q)
    def rewind(self,t):
        q=self.fresh(); done=self.fresh(); step=self.fresh()
        self.m(t,-1); self.label(q); self.r(t,{LEFT:done,BLANK:step,0:step,1:step})
        self.label(step); self.m(t,-1); self.j(q); self.label(done); self.m(t,1)
    def end(self,t):
        q=self.fresh(); step=self.fresh(); done=self.fresh()
        self.label(q); self.r(t,{0:step,1:step,BLANK:done})
        self.label(step); self.m(t,1); self.j(q); self.label(done)
    def clear(self,t):
        self.rewind(t); q=self.fresh(); step=self.fresh(); done=self.fresh()
        self.label(q); self.r(t,{0:step,1:step,BLANK:done})
        self.label(step); self.w(t,BLANK); self.m(t,1); self.j(q)
        self.label(done); self.rewind(t)
    def append_one(self,t):
        self.end(t); self.w(t,1); self.m(t,1); self.rewind(t)
    def positive(self,t): self.expect(t,1)
    def copy(self,src,dst,erase=False):
        q=self.fresh(); done=self.fresh(); z=self.fresh(); o=self.fresh()
        self.label(q); self.r(src,{0:z,1:o,BLANK:done})
        for bit,target in ((0,z),(1,o)):
            self.label(target); self.w(dst,bit)
            if erase:self.w(src,BLANK)
            self.m(src,1); self.m(dst,1); self.j(q)
        self.label(done)
    def copy_reset(self,src,dst):
        self.copy(src,dst); self.rewind(src)
    def equal(self,x,y):
        q=self.fresh(); step=self.fresh(); done=self.fresh()
        self.label(q); self.r(x,{1:step,BLANK:done})
        self.label(step); self.expect(y,1); self.m(x,1); self.m(y,1); self.j(q)
        self.label(done); self.expect(y,BLANK); self.rewind(x); self.rewind(y)
    def less(self,x,y,strict=False):
        q=self.fresh(); step=self.fresh(); done=self.fresh()
        self.label(q); self.r(x,{1:step,BLANK:done})
        self.label(step); self.expect(y,1); self.m(x,1); self.m(y,1); self.j(q)
        self.label(done)
        if strict:self.expect(y,1)
        self.rewind(x); self.rewind(y)
    def sub(self,x,y,z):
        q=self.fresh(); step=self.fresh(); done=self.fresh()
        self.label(q); self.r(y,{1:step,BLANK:done})
        self.label(step); self.expect(x,1); self.m(x,1); self.m(y,1); self.j(q)
        self.label(done); self.copy(x,z); self.rewind(x); self.rewind(y); self.rewind(z)
    def sum(self,x,y,z):
        self.copy_reset(x,z); self.copy_reset(y,z); self.rewind(z)
    def multiply(self,x,y,z):
        q=self.fresh(); step=self.fresh(); done=self.fresh()
        self.label(q); self.r(y,{1:step,BLANK:done})
        self.label(step); self.copy_reset(x,z); self.m(y,1); self.j(q)
        self.label(done); self.rewind(y); self.rewind(z)
    def scale(self,x,k,z):
        for _ in range(k):self.copy_reset(x,z)
        self.rewind(z)
    def double(self,x):
        self.copy_reset(x,'TMP'); self.rewind('TMP'); self.end(x)
        self.copy_reset('TMP',x); self.clear('TMP'); self.rewind(x)
    def halve(self,x):
        q=self.fresh(); step=self.fresh(); done=self.fresh()
        self.label(q); self.r(x,{1:step,BLANK:done})
        self.label(step); self.m(x,1); self.expect(x,1); self.m(x,1)
        self.w('TMP',1); self.m('TMP',1); self.j(q)
        self.label(done); self.clear(x); self.rewind('TMP')
        self.copy('TMP',x,erase=True); self.rewind('TMP'); self.rewind(x)
    def repeat_shift(self,x,n,up=True):
        q=self.fresh(); step=self.fresh(); done=self.fresh()
        self.label(q); self.r(n,{1:step,BLANK:done}); self.label(step)
        (self.double if up else self.halve)(x)
        self.m(n,1); self.j(q); self.label(done); self.rewind(n)
    def unary(self,binary,target):
        self.end(binary); self.m(binary,-1)
        q=self.fresh(); z=self.fresh(); o=self.fresh(); done=self.fresh(); common=self.fresh()
        self.label(q); self.r(binary,{0:z,1:o,LEFT:done})
        self.label(z); self.double(target); self.j(common)
        self.label(o); self.double(target); self.append_one(target)
        self.label(common); self.m(binary,-1); self.j(q)
        self.label(done); self.m(binary,1)
    def binary(self,unary,target='BIN'):
        q=self.fresh(); step=self.fresh(); done=self.fresh()
        carry=self.fresh(); zero=self.fresh(); one=self.fresh(); incremented=self.fresh()
        self.label(q); self.r(unary,{1:step,BLANK:done}); self.label(step)
        self.label(carry); self.r(target,{0:zero,BLANK:zero,1:one})
        self.label(one); self.w(target,0); self.m(target,1); self.j(carry)
        self.label(zero); self.w(target,1); self.j(incremented)
        self.label(incremented); self.rewind(target); self.m(unary,1); self.j(q)
        self.label(done); self.rewind(unary)
    def positive_binary(self,t):
        self.end(t); self.m(t,-1); self.expect(t,1); self.rewind(t)
    def gamma_binary(self,binary):
        self.positive_binary(binary)
        q=self.fresh(); step=self.fresh(); done=self.fresh()
        self.label(q); self.r(binary,{0:step,1:step,BLANK:done})
        self.label(step); self.w('LEN',1); self.m('LEN',1); self.m(binary,1); self.j(q)
        self.label(done); self.rewind('LEN'); self.m('LEN',1)
        q=self.fresh(); step=self.fresh(); done=self.fresh()
        self.label(q); self.r('LEN',{1:step,BLANK:done})
        self.label(step); self.w('GAMMA',0); self.m('GAMMA',1); self.m('LEN',1); self.j(q)
        self.label(done); self.m(binary,-1)
        q=self.fresh(); z=self.fresh(); o=self.fresh(); done=self.fresh()
        self.label(q); self.r(binary,{0:z,1:o,LEFT:done})
        for bit,label in ((0,z),(1,o)):
            self.label(label); self.w('GAMMA',bit); self.m('GAMMA',1); self.m(binary,-1); self.j(q)
        self.label(done); self.m(binary,1); self.clear('LEN')
    def gamma(self,unary):
        self.binary(unary); self.gamma_binary('BIN'); self.clear('BIN')
    def take(self,src,dst,guide,erase=False):
        q=self.fresh(); step=self.fresh(); done=self.fresh(); z=self.fresh(); o=self.fresh()
        self.label(q); self.r(guide,{1:step,BLANK:done}); self.label(step); self.r(src,{0:z,1:o})
        for bit,label in ((0,z),(1,o)):
            self.label(label); self.w(dst,bit)
            if erase:self.w(src,BLANK)
            self.m(src,1); self.m(dst,1); self.m(guide,1); self.j(q)
        self.label(done); self.rewind(guide)
    def parse(self,target):
        q=self.fresh(); step=self.fresh(); done=self.fresh()
        self.label(q); self.r('CONTEXT',{1:step,0:done})
        self.label(step); self.w('LEN',1); self.m('LEN',1); self.m('CONTEXT',1); self.j(q)
        self.label(done); self.m('CONTEXT',1); self.rewind('LEN'); self.positive('LEN')
        self.take('CONTEXT','BIN','LEN'); self.m('BIN',-1)
        good=self.fresh(); lastzero=self.fresh()
        self.r('BIN',{1:good,0:lastzero}); self.label(lastzero)
        self.m('BIN',-1); self.expect('BIN',LEFT); self.m('BIN',1); self.j(good)
        self.label(good); self.rewind('BIN'); self.clear('LEN')
        if target=='CUTOFF':
            self.positive_binary('BIN'); self.copy_reset('BIN','CUTOFF'); self.rewind('CUTOFF')
        elif target is not None:self.unary('BIN',target)
        self.clear('BIN')
    def codeword(self,zero,one,delimiter):
        self.expect('OLD',0); self.m('OLD',1)
        q0=self.fresh(); q1=self.fresh(); self.r('OLD',{0:q0,1:q1})
        self.label(q0); self.m('OLD',1)
        z=self.fresh(); o=self.fresh(); self.r('OLD',{0:z,1:o})
        self.label(z); self.m('OLD',1); self.j(zero)
        self.label(o); self.m('OLD',1); self.j(one)
        self.label(q1); self.m('OLD',1); self.expect('OLD',0); self.m('OLD',1); self.j(delimiter)
    def infer_width(self):
        q=self.fresh(); bit=self.fresh(); done=self.fresh()
        self.label(q); self.codeword(bit,bit,done)
        self.label(bit); self.w('W',1); self.m('W',1); self.j(q)
        self.label(done); self.rewind('W'); self.positive('W'); self.m('W',1)
        self.positive('W'); self.rewind('W'); self.rewind('OLD')
    def quotient(self,x,y,z):
        q=self.fresh(); step=self.fresh(); inner=self.fresh(); take=self.fresh(); complete=self.fresh(); done=self.fresh()
        self.label(q); self.r(x,{1:step,BLANK:done}); self.label(step)
        self.label(inner); self.r(y,{1:take,BLANK:complete})
        self.label(take); self.expect(x,1); self.m(x,1); self.m(y,1); self.j(inner)
        self.label(complete); self.w(z,1); self.m(z,1); self.rewind(y); self.j(q)
        self.label(done); self.rewind(x); self.rewind(z); self.positive(z)
    def decode(self):
        outer=self.fresh(); record=self.fresh(); end=self.fresh(); comps=self.fresh(); component=self.fresh(); next_record=self.fresh()
        self.label(outer); self.r('N',{1:record,BLANK:end}); self.label(record)
        self.label(comps); self.r('R2',{1:component,BLANK:next_record}); self.label(component)
        bits=self.fresh(); take=self.fresh(); delimiter=self.fresh(); z=self.fresh(); o=self.fresh(); wrong=self.fresh(); decoded=self.fresh()
        self.label(bits); self.r('W',{1:take,BLANK:delimiter}); self.label(take)
        self.codeword(z,o,wrong)
        for bit,label in ((0,z),(1,o)):
            self.label(label); self.w('COMP',bit); self.m('COMP',1); self.m('W',1); self.j(bits)
        self.label(wrong); self.halt('REJECT')
        self.label(delimiter); self.codeword(wrong,wrong,decoded); self.label(decoded)
        self.reverse_component('COMP','PACK'); self.rewind('W'); self.m('R2',1); self.j(comps)
        self.label(next_record); self.rewind('R2'); self.m('N',1); self.j(outer)
        self.label(end); self.expect('OLD',BLANK); self.rewind('OLD'); self.rewind('N'); self.rewind('PACK')
    def reverse_component(self,src,dst,coded=False):
        self.m(src,-1); q=self.fresh(); z=self.fresh(); o=self.fresh(); done=self.fresh()
        self.label(q); self.r(src,{0:z,1:o,LEFT:done})
        for bit,label in ((0,z),(1,o)):
            self.label(label)
            if coded:
                self.w(dst,0); self.m(dst,1); self.w(dst,0); self.m(dst,1)
            self.w(dst,bit); self.m(dst,1); self.w(src,BLANK); self.m(src,-1); self.j(q)
        self.label(done); self.m(src,1)
        if coded:
            for bit in (0,1,0):self.w(dst,bit); self.m(dst,1)
    def encode(self):
        outer=self.fresh(); record=self.fresh(); end=self.fresh(); comps=self.fresh(); component=self.fresh(); next_record=self.fresh()
        self.label(outer); self.r('N',{1:record,BLANK:end}); self.label(record)
        self.label(comps); self.r('R2',{1:component,BLANK:next_record}); self.label(component)
        self.take('PACK','COMP','W'); self.reverse_component('COMP','STAGE',coded=True)
        self.m('R2',1); self.j(comps)
        self.label(next_record); self.rewind('R2'); self.m('N',1); self.j(outer)
        self.label(end); self.expect('PACK',BLANK); self.rewind('PACK'); self.rewind('N'); self.rewind('STAGE')
    def partition(self,inverse=False):
        outer=self.fresh(); block=self.fresh(); end=self.fresh(); inner=self.fresh(); run=self.fresh(); block_done=self.fresh()
        self.label(outer); self.r('PREFIX',{1:block,BLANK:end}); self.label(block)
        if inverse:
            self.take('PACK','ZERO','HALF'); self.take('PACK','ONE','HALF'); self.rewind('ZERO'); self.rewind('ONE')
        self.label(inner); self.r('CHUNKS',{1:run,BLANK:block_done}); self.label(run)
        if inverse:
            self.take('ZERO','OUT','RUN',erase=True); self.take('ONE','OUT','RUN',erase=True)
        else:
            self.take('PACK','ZERO','RUN'); self.take('PACK','ONE','RUN')
        self.m('CHUNKS',1); self.j(inner); self.label(block_done); self.rewind('CHUNKS')
        if not inverse:
            self.rewind('ZERO'); self.rewind('ONE'); self.copy('ZERO','OUT',erase=True); self.copy('ONE','OUT',erase=True)
        self.rewind('ZERO'); self.rewind('ONE'); self.m('PREFIX',1); self.j(outer)
        self.label(end); self.expect('PACK',BLANK); self.clear('PACK'); self.rewind('OUT')
        self.copy('OUT','PACK',erase=True); self.rewind('OUT'); self.rewind('PACK'); self.rewind('PREFIX')
    def shuffle(self,inverse=False):
        q=self.fresh(); step=self.fresh(); update=self.fresh(); done=self.fresh()
        self.label(q); self.r('G',{1:step,BLANK:done}); self.label(step); self.partition(inverse)
        self.m('G',1); self.r('G',{1:update,BLANK:done}); self.label(update)
        if inverse:
            self.halve('PREFIX'); self.double('HALF'); self.repeat_shift('RUN','K',True); self.repeat_shift('CHUNKS','KM1',False)
        else:
            self.double('PREFIX'); self.halve('HALF'); self.repeat_shift('RUN','K',False); self.repeat_shift('CHUNKS','KM1',True)
        self.j(q); self.label(done); self.rewind('G')
    def finish(self):
        out=[]
        for ins in self.code:
            if ins[0]=='R':out.append(('R',ins[1],{s:self.labels[q] for s,q in ins[2].items()}))
            elif ins[0]=='J':out.append(('J',self.labels[ins[1]]))
            else:out.append(ins)
        return tuple(out),dict(self.labels)


def compile_bridge():
    b=Builder(); b.label('ENTER')
    kept={'outer':'OUTER','rows':'ROWS','row_bits':'ROWCLAIM','within_bits':'A',
          'record_bits':'REC','f':'F','K':'K','rho':'RHO','active_start':'U','cutoff':'CUTOFF'}
    for name in SCHEMA:b.parse(kept.get(name))
    b.expect('CONTEXT',BLANK); b.rewind('CONTEXT')
    for t in ('OUTER','ROWS','ROWCLAIM','REC','F','K'):b.positive(t)
    b.w('ONECOUNT',1); b.scale('F',9,'G'); b.multiply('G','K','GK'); b.sum('U','GK','END'); b.less('END','A'); b.less('RHO','K',True)
    b.sub('K','ONECOUNT','KM1'); b.infer_width()
    b.sum('W','ONECOUNT','TMP2'); b.scale('TMP2',6,'DEN'); b.clear('TMP2'); b.quotient('REC','DEN','R'); b.scale('R',2,'R2')
    b.copy_reset('REC','ROWEXPECTED'); b.rewind('ROWEXPECTED'); b.repeat_shift('ROWEXPECTED','A'); b.equal('ROWEXPECTED','ROWCLAIM')
    b.multiply('OUTER','ROWS','CROWS'); b.copy_reset('CROWS','N'); b.rewind('N'); b.repeat_shift('N','A')
    b.multiply('W','R2','L'); b.copy_reset('CROWS','BASEP'); b.rewind('BASEP'); b.repeat_shift('BASEP','U')
    b.sub('A','U','TMP2'); b.sub('TMP2','G','EXP'); b.clear('TMP2'); b.w('S',1); b.repeat_shift('S','EXP'); b.clear('EXP')
    b.copy_reset('BASEP','PREFIX'); b.rewind('PREFIX')
    b.sub('A','U','TMP2'); b.sub('TMP2','ONECOUNT','EXP'); b.clear('TMP2')
    b.copy_reset('L','HALF'); b.rewind('HALF'); b.repeat_shift('HALF','EXP'); b.clear('EXP')
    b.copy_reset('HALF','RUN'); b.rewind('RUN'); b.repeat_shift('RUN','RHO',False)
    b.w('CHUNKS',1); b.repeat_shift('CHUNKS','RHO')
    for t in ('F','R','BASEP','S','W'):b.gamma(t)
    b.gamma_binary('CUTOFF'); b.rewind('GAMMA')
    b.decode(); b.shuffle(); b.halt('PACKED')
    b.label('EXIT'); b.shuffle(inverse=True); b.encode()
    q=b.fresh(); z=b.fresh(); o=b.fresh(); done=b.fresh()
    b.label(q); b.r('STAGE',{0:z,1:o,BLANK:done})
    for bit,label in ((0,z),(1,o)):
        b.label(label); valid=b.fresh(); b.r('OLD',{0:valid,1:valid}); b.label(valid)
        b.w('OLD',bit); b.m('OLD',1); b.m('STAGE',1); b.j(q)
    b.label(done); b.expect('OLD',BLANK); b.rewind('OLD'); b.rewind('STAGE')
    for t in NAMES[2:]:b.clear(t)
    b.halt('DONE'); return b.finish()


@dataclass
class Tape:
    """Checker hardware; runtime only receives read/write/unit move."""
    cells:list
    head:int=1
    high:int=1
    low:int=0
    reads:int=0
    writes:int=0
    moves:int=0
    @classmethod
    def supplied(cls,bits=(),origin=1):
        if origin<1:raise ValueError('fixture origin')
        values=[BLANK]*(origin-1)+[LEFT]+list(bits)
        return cls(values,origin,len(values),origin-1)
    def read(self):
        self.reads+=1
        return self.cells[self.head] if self.head<len(self.cells) else BLANK
    def write(self,v):
        self.writes+=1
        if self.head>=len(self.cells):self.cells.extend([BLANK]*(self.head+1-len(self.cells)))
        self.cells[self.head]=v; self.high=max(self.high,self.head+1)
    def move(self,d):
        if d not in (-1,1):raise ValueError('nonunit move')
        self.moves+=1; self.head+=d; self.low=min(self.low,self.head)
        if self.head<0:raise ValueError('crossed physical boundary')


class CPU:
    def __init__(self,program,tapes):
        if len(tapes)!=len(NAMES) or len({id(t) for t in tapes})!=len(tapes):
            raise ValueError('genuinely distinct physical owners required')
        self.program=program; self.tapes=tuple(tapes); self.steps=0
    def run(self,entry=0,limit=100_000_000):
        pc=entry; code=self.program; tapes=self.tapes
        while self.steps<limit:
            ins=code[pc]; self.steps+=1; op=ins[0]
            if op=='R':
                pc=ins[2].get(tapes[ins[1]].read(),-1)
                if pc<0:return 'REJECT'
            elif op=='W':tapes[ins[1]].write(ins[2]); pc+=1
            elif op=='M':tapes[ins[1]].move(ins[2]); pc+=1
            elif op=='J':pc=ins[1]
            elif op=='H':return ins[1]
            else:raise ValueError('nonliteral instruction')
        raise TimeoutError('bounded interpreter step cap')


def table_digest(program):
    return sha256(json.dumps(program,separators=(',',':'),sort_keys=True).encode()).hexdigest()
