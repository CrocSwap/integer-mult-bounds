"""Bounded verifier hardware. No fixture integer reaches a runtime operand.
Prepared for @CubeJerry with OpenAI assistance. Apache-2.0.
"""
B,L,E=2,3,4
class Tape:
    def __init__(self,body=(),origin=3,private=False,capacity=None):
        self.origin=self.head=origin
        span=len(body) if capacity is None else capacity+1
        if span<len(body): raise ValueError('insufficient fixture capacity')
        self.cells=[B]*(origin+span+2)
        self.cells[origin-2]=7
        self.cells[origin-1]=B if private else L
        self.cells[origin:origin+len(body)]=body
        self.cells[origin+span+1]=7
        self.low=self.high=origin
        self.reads=self.writes=self.moves=0
        self.guard_writes=[]
    def read(self):
        self.reads+=1;self.low=min(self.low,self.head);self.high=max(self.high,self.head)
        if not 0<=self.head<len(self.cells): raise ValueError('read outside supplied window')
        return self.cells[self.head]
    def write(self,value):
        self.writes+=1;self.low=min(self.low,self.head);self.high=max(self.high,self.head)
        if not 0<=self.head<len(self.cells): raise ValueError('write outside supplied window')
        self.cells[self.head]=value
        if self.head==self.origin-1: self.guard_writes.append(value)
    def move(self,amount):
        if amount not in (-1,1): raise ValueError('nonunit move')
        self.moves+=1;self.head+=amount;self.low=min(self.low,self.head);self.high=max(self.high,self.head)
        if not 0<=self.head<len(self.cells): raise ValueError('move outside supplied window')

class CPU:
    def __init__(self,code,tapes,labels):
        if len(tapes)!=14 or len({id(t) for t in tapes})!=14: raise ValueError('14 distinct owners required')
        self.code=code;self.tapes=tuple(tapes);self.labels=labels
        self.steps=self.iterations=0
    def run(self,limit):
        pc=0
        while self.steps<limit:
            self.steps+=1
            if pc==self.labels['query_loop']: self.iterations+=1
            op,*a=self.code[pc]
            if op=='R':
                symbol=self.tapes[a[0]].read()
                if symbol not in a[1]: raise ValueError('outside fixed alphabet')
                pc=a[1][symbol]
            elif op=='W': self.tapes[a[0]].write(a[1]);pc+=1
            elif op=='M': self.tapes[a[0]].move(a[1]);pc+=1
            elif op=='J': pc=a[0]
            elif op=='H': return a[0]
            else: raise ValueError('nonliteral opcode')
        raise TimeoutError('bounded fixture cap')

def bits(value,width):
    if value<0 or value>=1<<width: raise ValueError('fixture unsigned width')
    return [(value>>i)&1 for i in range(width)]

def fixture(h,s,a,j,x,overrides=None):
    if h<0: raise ValueError('fixture h domain')
    width=h+1
    bodies=[bits(h,max(1,h.bit_length())),bits(s,width),bits(a,width),bits(j,width),bits(x,width)]
    if overrides:
        for key,value in overrides.items(): bodies[key]=list(value)
    tapes=[Tape(body,origin=3+i%4) for i,body in enumerate(bodies)]
    tapes.append(Tape((),origin=4,capacity=1))
    # Capacity includes current blank frontier and guard retirement.
    tapes.extend(Tape((),origin=3+i%5,private=True,capacity=max(h+2,len(bodies[0])+1)) for i in range(8))
    return tapes

def check_return(tapes,before,outcome,expected=None):
    if any(t.head!=t.origin for t in tapes): raise ValueError('head return')
    for t,old in zip(tapes[:5],before[:5]):
        if t.cells!=old or t.writes: raise ValueError('borrowed descriptor changed')
    if outcome=='DONE':
        old=list(before[5]);old[tapes[5].origin]=expected
        if tapes[5].cells!=old or tapes[5].writes!=1: raise ValueError('owned Boolean output')
    elif outcome=='REJECT':
        if tapes[5].cells!=before[5] or tapes[5].writes: raise ValueError('rejected output modified')
    else: raise ValueError('unknown outcome')
    for t,old in zip(tapes[6:],before[6:]):
        if t.cells!=old: raise ValueError('private capacity or exterior not restored')
        if t.guard_writes!=[L,B]: raise ValueError('private guard lifetime')
    if any(t.low<t.origin-1 for t in tapes): raise ValueError('opaque left exterior accessed')
    if any(t.guard_writes for t in tapes[:6]): raise ValueError('borrowed/output marker changed')
    return sum(t.high-t.low+1 for t in tapes)
