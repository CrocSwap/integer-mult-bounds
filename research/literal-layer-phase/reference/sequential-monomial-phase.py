"""Sequential counter production of source Gaussian monomial phases.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
The tensor phase follows Jose Manuel's retained monomial implementation.
Counter amortization retains Cinna Davis and the PR4325 audit's credit.
"""
ZERO,ONE,LEFT,END,BLANK=range(5)


def need(ok,message):
    if not ok:raise ValueError(message)


class Meter:
    def __init__(self):self.reads=self.writes=self.moves=0
    @property
    def total(self):return self.reads+self.writes+self.moves


class Tape:
    """Hardware model; only current-symbol operations are algorithm inputs."""
    def __init__(self,prefix=(),meter=None):
        self.cells=list(prefix)+[LEFT];self.head=len(self.cells);self.floor=self.head-1
        self.meter=meter if meter is not None else Meter()
    def read(self):
        need(self.head>=self.floor,'ancestor read');self.meter.reads+=1
        return self.cells[self.head] if self.head<len(self.cells) else BLANK
    def write(self,value):
        need(value in range(5) and self.head>=self.floor,'owned finite-symbol write');self.meter.writes+=1
        while len(self.cells)<=self.head:self.cells.append(BLANK)
        self.cells[self.head]=value
    def move(self,direction):
        need(direction in (-1,1),'unit move');self.head+=direction;self.meter.moves+=1
        need(self.head>=self.floor,'ancestor crossed')


def emit(tape,value):tape.write(value);tape.move(1)


def rewind(tape):
    tape.move(-1)
    while tape.read()!=LEFT:tape.move(-1)
    tape.move(1)


class Phases:
    """The recipe is compiled data; mask length and addresses stay on tapes."""
    def __init__(self,recipe,mask,counters):
        self.alpha=tuple(recipe['linear_Z4']);self.quadratic=tuple(recipe['quadratic_rows'])
        self.counters=tuple(counters);self.mask=mask;self.phase=0;self.done=False
        m=len(self.alpha)
        need(m>=1 and len(self.quadratic)==len(self.counters)==m,'compiled recipe extent')
        need(all(type(a) is int and 0<=a<4 for a in self.alpha),'compiled linear phases')
        need(all(type(a) is int and 0<=a<1<<m for a in self.quadratic),'compiled quadratic rows')
        need(type(recipe['phase']) is int and 0<=recipe['phase']<4,'compiled absolute phase')
        for tape in self.counters:need(tape.read()==BLANK,'empty counter owner')
        nonempty=False
        while (active:=mask.read())!=END:
            need(active in (ZERO,ONE),'binary active mask');nonempty=True
            if active:self.phase=(self.phase+recipe['phase'])%4
            for tape in self.counters:emit(tape,ZERO)
            mask.move(1)
        need(nonempty,'positive counter width')
        for tape in self.counters:emit(tape,END);rewind(tape)
        rewind(mask)
    def restore_heads(self):
        for tape in self.counters:rewind(tape)
        rewind(self.mask)
    def advance(self):
        need(not self.done,'live complete phase domain')
        for i in range(len(self.counters)-1,-1,-1):
            while (active:=self.mask.read())!=END:
                need(active in (ZERO,ONE),'binary active mask')
                bit=self.counters[i].read();need(bit in (ZERO,ONE),'binary counter')
                if active:
                    delta=self.alpha[i] if bit==0 else -self.alpha[i]
                    for j,tape in enumerate(self.counters):
                        if j!=i and (self.quadratic[min(i,j)]>>max(i,j))&1:
                            other=tape.read();need(other in (ZERO,ONE),'aligned binary counter')
                            delta+=2*other
                    self.phase=(self.phase+delta)%4
                self.counters[i].write(1-bit)
                if bit==0:self.restore_heads();return True
                for tape in self.counters:tape.move(1)
                self.mask.move(1)
            for tape in self.counters:need(tape.read()==END,'equal counter extents')
            self.restore_heads()
        self.done=True
        return False
    def close(self):
        need(self.done,'complete phase consumption')
        for tape in self.counters:
            while (symbol:=tape.read())!=END:
                need(symbol in (ZERO,ONE),'counter cleanup');emit(tape,BLANK)
            emit(tape,BLANK);need(tape.read()==BLANK,'counter end');rewind(tape)


def apply_phase(source,producer,coefficient_bits,TapeClass,copy,inverse=False):
    """Retained Gaussian coefficient loop, driven by physical phase overflow.

    This is adapted from the pinned monomial.phase_pass. Sequential coefficient
    primitives and their precision contract remain inherited.
    """
    need(coefficient_bits>=2,'Gaussian coefficient extent')
    source.rewind();out=TapeClass(source.meter);real=TapeClass(source.meter);imag=TapeClass(source.meter)
    def coefficient(tape,negative):
        if negative:
            carry=1
            for _ in range(coefficient_bits):
                value=(1-tape.read(1)[0])+carry
                out.write(bytes((value&1,)));carry=value>>1
        else:copy(tape,out,coefficient_bits)
        tape.finish()
    while True:
        phase=(-producer.phase if inverse else producer.phase)%4
        source.meter.control_evaluations+=1
        copy(source,real,coefficient_bits);copy(source,imag,coefficient_bits)
        real.rewind();imag.rewind()
        if phase==0:coefficient(real,False);coefficient(imag,False)
        elif phase==1:coefficient(imag,True);coefficient(real,False)
        elif phase==2:coefficient(real,True);coefficient(imag,True)
        else:coefficient(imag,False);coefficient(real,True)
        real.erase();imag.erase()
        if not producer.advance():break
    source.finish();source.erase();out.rewind();producer.close();return out
