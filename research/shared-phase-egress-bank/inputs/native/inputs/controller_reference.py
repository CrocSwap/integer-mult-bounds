"""Finite three-tape online rank-recursion control; Apache-2.0.
Only PC and local symbols affect execution. Metrics/event logs are observers.
"""
from dataclasses import dataclass, field
BLANK, ONE, MARK = '_', '1', '|'
WIDTH, CHILD, STACK = range(3)

class Builder:
    def __init__(self): self.code, self.labels, self.serial = [], {}, 0
    def mark(self,n):
        if n in self.labels: raise ValueError('duplicate label')
        self.labels[n]=len(self.code)
    def op(self,*x): self.code.append(x)
    def rewind(self,t,symbols):
        self.serial+=1; loop=f'rw{self.serial}'; done=loop+'done'
        self.op('move',t,-1); self.mark(loop)
        self.op('read',t,{s:loop+'step' for s in symbols}|{MARK:done})
        self.mark(loop+'step'); self.op('move',t,-1); self.op('goto',loop)
        self.mark(done); self.op('move',t,1)
    def finish(self,alphabet):
        result=[]
        for op,*a in self.code:
            if op=='goto': a[0]=self.labels[a[0]]
            elif op=='read': a[1]={s:self.labels[n] for s,n in a[1].items()}
            result.append((op,*a))
        return tuple(result),tuple(alphabet)

def compile_controller(m,ranks):
    """Parameters are compile-time constants, absent from run-time state."""
    if type(m) is not int or m<2 or not ranks: raise ValueError('bad fixed profile')
    if any(type(r) is not int or not 1<=r<m for r in ranks): raise ValueError('rank range')
    ranks=tuple(ranks); tags=tuple(f't{i}' for i in range(len(ranks)))
    a=Builder(); a.mark('enter'); a.op('read',WIDTH,{ONE:'probe0'})
    for k in range(m):
        a.mark(f'probe{k}'); a.op('read',WIDTH,{ONE:f'advance{k}',BLANK:f'leaf{k}'})
        a.mark(f'advance{k}'); a.op('move',WIDTH,1)
        a.op('goto',f'probe{k+1}' if k+1<m else 'internal_rewind')
        a.mark(f'leaf{k}'); a.rewind(WIDTH,(ONE,)); a.op('emit','L'); a.op('goto','complete')
    a.mark('internal_rewind'); a.rewind(WIDTH,(ONE,)); a.op('emit','E'); a.op('goto','child0')
    for i,r in enumerate(ranks):
        a.mark(f'child{i}'); a.op('goto',f'build{i}_0')
        for rem in range(m):
            a.mark(f'build{i}_{rem}')
            a.op('read',WIDTH,{ONE:f'build{i}_{rem}bit',BLANK:f'built{i}'})
            a.mark(f'build{i}_{rem}bit'); quotient,nxt=divmod(rem+r,m)
            if quotient: a.op('write',CHILD,ONE); a.op('move',CHILD,1)
            a.op('move',WIDTH,1); a.op('goto',f'build{i}_{nxt}')
        a.mark(f'built{i}'); a.rewind(WIDTH,(ONE,)); a.rewind(CHILD,(ONE,))
        a.mark(f'push{i}'); a.op('read',WIDTH,{ONE:f'push{i}bit',BLANK:f'pushed{i}'})
        a.mark(f'push{i}bit'); a.op('write',STACK,ONE); a.op('write',WIDTH,BLANK)
        a.op('move',WIDTH,1); a.op('move',STACK,1); a.op('goto',f'push{i}')
        a.mark(f'pushed{i}'); a.op('write',STACK,tags[i]); a.op('move',STACK,1); a.rewind(WIDTH,(BLANK,))
        a.mark(f'transfer{i}'); a.op('read',CHILD,{ONE:f'transfer{i}bit',BLANK:f'transferred{i}'})
        a.mark(f'transfer{i}bit'); a.op('write',WIDTH,ONE); a.op('write',CHILD,BLANK)
        a.op('move',WIDTH,1); a.op('move',CHILD,1); a.op('goto',f'transfer{i}')
        a.mark(f'transferred{i}'); a.rewind(WIDTH,(ONE,)); a.rewind(CHILD,(BLANK,))
        a.op('emit',f'D{i}'); a.op('goto','enter')
    a.mark('complete'); a.op('emit','X'); a.op('move',STACK,-1)
    a.op('read',STACK,{MARK:'root_done',**{t:f'return{i}' for i,t in enumerate(tags)}})
    a.mark('root_done'); a.op('move',STACK,1); a.op('halt')
    for i in range(len(ranks)):
        a.mark(f'return{i}'); a.op('write',STACK,BLANK); a.op('move',STACK,-1)
        a.mark(f'erase{i}'); a.op('read',WIDTH,{ONE:f'erase{i}bit',BLANK:f'erased{i}'})
        a.mark(f'erase{i}bit'); a.op('write',WIDTH,BLANK); a.op('move',WIDTH,1); a.op('goto',f'erase{i}')
        a.mark(f'erased{i}'); a.rewind(WIDTH,(BLANK,))
        a.mark(f'pop{i}'); a.op('read',STACK,{ONE:f'pop{i}bit',MARK:f'popped{i}',**{t:f'popped{i}' for t in tags}})
        a.mark(f'pop{i}bit'); a.op('write',WIDTH,ONE); a.op('write',STACK,BLANK)
        a.op('move',WIDTH,1); a.op('move',STACK,-1); a.op('goto',f'pop{i}')
        a.mark(f'popped{i}'); a.op('move',STACK,1); a.rewind(WIDTH,(ONE,)); a.op('emit',f'U{i}')
        a.op('goto',f'child{i+1}' if i+1<len(ranks) else 'complete')
    return a.finish((BLANK,'0',ONE,MARK,*tags))

@dataclass
class Tape:
    cells:dict
    head:int
    low:int=field(init=False)
    high:int=field(init=False)
    def __post_init__(self): self.low=self.high=self.head
    def read(self): return self.cells.get(self.head,BLANK)
    def write(self,s):
        if s==BLANK: self.cells.pop(self.head,None)
        else: self.cells[self.head]=s
    def move(self,d):
        self.head+=d; self.low=min(self.low,self.head); self.high=max(self.high,self.head)

class Machine:
    def __init__(self,code,tapes):
        self.code,self.tapes=code,tapes; self.pc=self.steps=0; self.events=[]; self.halted=False
    def step(self):
        op,*a=self.code[self.pc]; self.steps+=1; self.pc+=1
        if op=='read':
            s=self.tapes[a[0]].read()
            if s not in a[1]: raise ValueError('invalid scanned symbol')
            self.pc=a[1][s]
        elif op=='write': self.tapes[a[0]].write(a[1])
        elif op=='move': self.tapes[a[0]].move(a[1])
        elif op=='goto': self.pc=a[0]
        elif op=='emit': self.events.append(a[0])
        elif op=='halt': self.halted=True
        else: raise ValueError('invalid opcode')
    def run(self,budget=10_000_000):
        while not self.halted:
            if self.steps>=budget: raise ValueError('finite verifier budget')
            self.step()
        return self

def initial_tapes(width,origins=(0,0,0),ancestor=('0','1','t0','_','|','0')):
    if width<1: raise ValueError('positive width')
    u,c,p=origins
    return [Tape({u-1:MARK,**{u+i:ONE for i in range(width)}},u),Tape({c-1:MARK},c),
            Tape({p-1:MARK,**{p-2-i:s for i,s in enumerate(ancestor) if s!=BLANK}},p)]
