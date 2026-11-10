"""Counted native alphabet adapter on current A CodedPort objects.

Every old symbol0..13 is four virtual binary digits, hence twelve physical
bits. No physical address or backing length selects a runtime instruction.
The dense hardware below is checker-only; production receives caller ports.
Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
"""
from contextlib import contextmanager
from binding_sources import activate,need

S=activate();A=S.abi

class SymbolPort:
    def __init__(self,physical):
        self.raw=physical;self.port=A.CodedPort(physical)

    def read(self):
        first=self.port.read()
        if first==4:return 4
        value=0
        for i in range(4):
            bit=first if i==0 else self.port.read()
            need(bit in (0,1),'complete binary native symbol')
            value=2*value+bit;self.port.move(1)
        for _ in range(4):self.port.move(-1)
        need(value<14,'native alphabet code')
        return value

    def write(self,value):
        need(type(value) is int and 0<=value<14,'native alphabet')
        for shift in (3,2,1,0):
            self.port.write((value>>shift)&1);self.port.move(1)
        for _ in range(4):self.port.move(-1)

    def step(self,direction):
        need(direction in (-1,1),'unit old-symbol move')
        if direction==1 and self.port.read()==4:self.write(4)
        for _ in range(4):self.port.move(direction)

    def rewind(self):
        self.step(-1)
        while self.read()!=2:self.step(-1)
        self.step(1)

    def initialize(self,marker=2,body=(),head=1):
        # marker/body/head are fixed compilation data, never decoded input.
        need(self.raw.read()==6,'fresh blank native current segment')
        self.write(marker)
        for value in body:self.step(1);self.write(value)
        for _ in body:self.step(-1)
        for _ in range(head):self.step(1)


_original={name:getattr(S.records.Tape,name) for name in ('__init__','read','write','step')}
_executing=False
_patched=False

class OriginHead:
    """Refine retained completed-head guards by local marker observations.

    The only computational head comparisons in the retained closure are a
    chained equality of returned heads ending in1. Equal nonorigin positions
    cannot satisfy that complete guard. No numerical head address is exposed.
    """
    def __init__(self,tape):self.tape=tape
    def restored(self):
        port=self.tape.native_port
        port.step(-1);ok=port.read()==2;port.step(1)
        return ok
    def __eq__(self,other):
        if isinstance(other,OriginHead):return self.restored() and other.restored()
        need(type(other) is int and other==1,'only retained origin-head comparisons')
        return self.restored()

def install_tape_methods():
    global _patched
    if _patched:return
    def read(tape):
        if not hasattr(tape,'native_port'):
            need(not _executing,'unbound native tape during execution')
            return _original['read'](tape)
        tape.meter.reads+=1
        return tape.native_port.read()
    def write(tape,value):
        if not hasattr(tape,'native_port'):
            need(not _executing,'unbound native tape during execution')
            return _original['write'](tape,value)
        tape.meter.writes+=1;tape.native_port.write(value)
    def step(tape,direction):
        if not hasattr(tape,'native_port'):
            need(not _executing,'unbound native tape during execution')
            return _original['step'](tape,direction)
        tape.native_port.step(direction)
        tape._observed_head=tape.__dict__.get('_observed_head',tape.__dict__.get('head',1))+direction
        tape.meter.moves+=1
    def head(tape):
        if _executing:
            need(hasattr(tape,'native_port'),'bound head guard')
            return OriginHead(tape)
        return tape.__dict__.get('_observed_head',tape.__dict__.get('head',1))
    def set_head(tape,value):tape._observed_head=value
    def cells(tape):
        need(not _executing and not hasattr(tape,'native_port'),
             'obsolete host backing is construction-only; inspect supplied physical ports')
        return tape.__dict__.get('_observer_cells',tape.__dict__.get('cells'))
    def set_cells(tape,value):tape._observer_cells=value
    S.records.Tape.read=read;S.records.Tape.write=write;S.records.Tape.step=step
    S.records.Tape.head=property(head,set_head)
    S.records.Tape.cells=property(cells,set_cells)
    _patched=True

@contextmanager
def collect_tapes():
    """Record finite allocation sites during template construction only."""
    tapes=[];old=S.records.Tape.__init__
    def initialize(tape):
        _original['__init__'](tape);tapes.append(tape)
    S.records.Tape.__init__=initialize
    try:yield tapes
    finally:S.records.Tape.__init__=old

@contextmanager
def execution():
    global _executing
    need(not _executing,'one active native cohort')
    _executing=True
    try:yield
    finally:_executing=False

class ParkingView:
    """Only the predecessor's finite completed-baseline guard is exposed."""
    def __init__(self,owner,index):self.owner=owner;self.index=index
    def __eq__(self,expected):
        need(expected in ({},{0:'^'}),'fixed parking baseline comparison')
        p=self.owner.ports[self.index]
        if self.index==0:
            need(expected=={},'empty stack baseline')
            blank=p.read()==4
            p.step(-1);at_origin=p.read()==2;p.step(1)
            return blank and at_origin
        p.step(-1)
        marker=p.read();p.step(-1);at_origin=p.read()==2
        p.step(1);p.step(1)
        return at_origin and marker==(5 if expected else 4) and p.read()==4

class ParkingAdapter:
    """The unchanged seven-symbol parking table on two coded local ports.

BankParking's cell accessors are rebound to unit physical operations. Its
mathematical register and frame algorithms and finite table stay unchanged.
"""
    chars=('_','0','1','^','$','F','R')
    codes=(4,0,1,5,6,7,8)
    def __init__(self,owner,ports):
        from types import MethodType
        self.owner=owner;self.ports=tuple(ports)
        owner.machine.tapes=[ParkingView(self,0),ParkingView(self,1)]
        def read(o,k):
            o.codec_counts['reads']+=1
            value=self.ports[k].read();need(value in self.codes,'parking alphabet')
            return self.chars[self.codes.index(value)]
        def write(o,k,value):
            need(value in self.chars,'parking write alphabet');o.codec_counts['writes']+=1
            self.ports[k].write(self.codes[self.chars.index(value)])
        def move(o,k,direction):
            need(direction in (-1,1),'parking unit move');o.codec_counts['moves']+=1
            self.ports[k].step(direction)
        def command(o,entry):
            need(o.machine.state=='done','completed parking boundary')
            o.codec_counts['commands']+=1;o.machine.state=entry
            while o.machine.state not in ('done','reject'):
                nxt,writes,moves=o.machine.table[(o.machine.state,read(o,0),read(o,1))]
                for k in (0,1):
                    if writes[k] is not None:write(o,k,writes[k])
                    if moves[k]:move(o,k,moves[k])
                o.machine.state=nxt
            need(o.machine.state=='done','matched parking command')
        for name,fn in (('_read',read),('_write',write),('_move',move),('_command',command)):
            setattr(owner,name,MethodType(fn,owner))

    def initialize(self):
        self.ports[0].initialize(2,(),1)
        self.ports[1].initialize(2,(4,),2)

class Cohort:
    def __init__(self,tapes,native):
        install_tape_methods()
        self.tapes=tuple(tapes);self.native=native
        self.markers=[]
        for tape in self.tapes:
            need(tape.head==1 and tape.cells[0] in (2,4)
                 and all(x==4 for x in tape.cells[1:]),'compiled blank native baseline')
            self.markers.append(tape.cells[0])
        need(native.runtime.numerical.machine.tapes==[{},{}],'closed native parking baseline')
        self.ports=None

    @property
    def port_count(self):return len(self.tapes)+2

    def bind(self,ports):
        need(len(ports)==self.port_count and len(set(map(id,ports)))==len(ports),'exact fixed native inventory')
        self.ports=tuple(ports)
        for tape,port in zip(self.tapes,ports):tape.native_port=SymbolPort(port)
        self.parking=ParkingAdapter(self.native.runtime.numerical,
                                    tuple(SymbolPort(p) for p in ports[-2:]))

    def start(self):
        need(self.ports is not None,'native physical ports bound before input')
        for tape,marker in zip(self.tapes,self.markers):
            tape.native_port.initialize(marker);tape.head=1
        self.parking.initialize()

    def finish(self):
        # Raw A retirement erases every encoded blank and the current-call
        # high-water body. It stops at fresh physical BLANK, not backing length.
        for port in self.ports:A.retire(port)


class DenseTape:
    """Independent checker hardware; no runtime routine reads these arrays."""
    def __init__(self,origin=1):
        self.cells=bytearray([6]*(origin+1));self.cells[origin-1]=2
        self.head=origin;self.origin=origin;self.reads=self.writes=self.moves=0
        self.high=origin
    def read(self):
        self.reads+=1
        return self.cells[self.head] if self.head<len(self.cells) else 6
    def write(self,value):
        need(value in range(7),'physical alphabet');self.writes+=1
        if self.head>=len(self.cells):self.cells.extend([6]*(self.head+1-len(self.cells)))
        self.cells[self.head]=value;self.high=max(self.high,self.head+1)
    def move(self,direction):
        need(direction in (-1,1),'physical unit move')
        self.head+=direction;self.moves+=1;need(self.head>=0,'physical boundary')
    def actions(self):return self.reads+self.writes+self.moves
