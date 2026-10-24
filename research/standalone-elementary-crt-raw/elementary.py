"""Standalone binary elementary interchange, with no selected supplier objects.

The digit body is unchanged retained source. Encoded width replaces the
source's repeated divisions of a power-of-two modulus. See PROOF.md.
"""
from pathlib import Path
from hashlib import sha256
from contextlib import contextmanager
import json,sys,tarfile
HERE=Path(__file__).resolve().parent
inventory=json.loads((HERE/'VENDOR.json').read_text())
archive=HERE.parents[1]/'research/physical-ordinary-interchange/inputs/pr2809.tar'
if sha256(archive.read_bytes()).hexdigest()!=inventory['archive_sha256']:
    raise ValueError('retained archive hash')
with tarfile.open(archive) as retained:
    for row in inventory['files']:
        data=(HERE/row['path']).read_bytes()
        if sha256(data).hexdigest()!=row['sha256'] or data!=retained.extractfile(row['archive_member']).read():
            raise ValueError('retained source hash/member '+row['path'])
if any(n in sys.modules for n in ('words','records','stream','cardinality','bitstream')):
    raise ValueError('standalone cold namespace')
sys.path.insert(0,str(HERE/'vendor'))
import words,records,stream,cardinality,bitstream
from words import ZERO,ONE,LEFT,RIGHT,BLANK,need
Tape=records.Tape

class Physical(Tape):
    def __init__(self):
        self.cells=bytearray([BLANK]);self.head=0;self.meter=words.Meter()
        self.write(LEFT);self.step(1)

class Lease:
    def __init__(self,bank,slot):self.bank,self.slot,self.active=bank,slot,True
    def physical(self):
        need(self.active and self.bank.live[self.slot] is self,'active fixed role')
        return self.bank.tapes[self.slot]
    def read(self):return self.physical().read()
    def write(self,x):return self.physical().write(x)
    def step(self,x):return self.physical().step(x)
    def append(self,x):return self.physical().append(x)
    def rewind(self):return self.physical().rewind()
    def clear(self):
        need(self.active,'one owner closes lease')
        self.physical().clear();self.bank.live[self.slot]=None;self.active=False
        self.bank.control+=1

class Bank:
    def __init__(self):
        self.tapes=tuple(Physical() for _ in range(16))
        self.live=[None]*16;self.control=0;self.peak=0
    def acquire(self):
        for slot,tape in enumerate(self.tapes):
            self.control+=1
            if self.live[slot] is None:
                need(tape.read()==BLANK,'blank role before acquire')
                lease=Lease(self,slot);self.live[slot]=lease
                self.peak=max(self.peak,sum(v is not None for v in self.live))
                return lease
        raise ValueError('fixed bank exhausted')
    def empty(self):
        need(not any(self.live),'all leases returned')
        for tape in self.tapes:
            need(tape.read()==BLANK,'empty private body')
            tape.step(-1);need(tape.read()==LEFT,'private origin');tape.step(1)
    @contextmanager
    def installed(self):
        # These are all reachable constructor globals of unchanged digit_swap,
        # copy_bits, Counter, Natural. No loader/controller namespace exists.
        modules=(stream,cardinality,bitstream)
        old=[m.Tape for m in modules];original=Tape.__init__
        def forbidden(*args,**kwargs):raise ValueError('runtime physical allocation')
        for m in modules:m.Tape=self.acquire
        Tape.__init__=forbidden
        try:yield
        finally:
            Tape.__init__=original
            for m,v in zip(modules,old):m.Tape=v
    def dispose(self):
        self.empty()
        for tape in self.tapes:
            tape.step(-1);tape.write(BLANK);tape.step(1)


def canonical(value,positive=False):
    """Input is LEFT, canonical little-endian bits, RIGHT, blank tail."""
    value.step(-1);need(value.read()==LEFT,'descriptor origin');value.step(1)
    seen=False;last=ZERO;one=False;single=True
    while value.read()!=RIGHT:
        bit=value.read();need(bit in (ZERO,ONE),'descriptor bit')
        if seen:single=False
        seen=True;last=bit;one=one or bit==ONE;value.step(1)
    need(seen and (last==ONE or single),'canonical descriptor')
    need(not positive or one,'positive spectator')
    value.step(1);need(value.read()==BLANK,'descriptor terminator');value.rewind()


def transfer(source,target):
    while source.read()!=BLANK:
        bit=source.read();need(bit in (ZERO,ONE),'binary payload')
        target.append(bit);source.step(1)
    source.rewind();target.rewind()

class Elementary:
    """Fixed16 scratch tapes + owned output. No width-dependent constructor."""
    def __init__(self):self.bank=Bank();self.output=Physical();self.closed=False
    def run(self,payload,width,before,middle,suffix):
        ports=(payload,width,before,middle,suffix,self.output)
        need(len({id(p) for p in ports})==6,'distinct external ports')
        need(not self.closed,'live elementary service')
        need(self.output.read()==BLANK,'consume previous output')
        for v in (width,before,middle,suffix):canonical(v,v is not width)
        with self.bank.installed():
            pre,gap,tail=(cardinality.Natural(v) for v in (before,middle,suffix))
            scan=stream.Counter(width);first=True
            while not scan.finished:
                if first:first=False
                else:gap.multiply_small(2);tail.multiply_small(2)
                scan.decrement()
            scan.close()
            remaining=stream.Counter(width);current=payload;first=True
            while not remaining.finished:
                if not first:
                    pre.multiply_small(2);need(tail.divide_small(2)==0,'exact suffix division')
                following=bitstream.digit_swap(current,2,pre,gap,tail)
                if current is not payload:current.clear()
                current=following;first=False;remaining.decrement()
            transfer(current,self.output)
            if current is not payload:current.clear()
            remaining.close();pre.close();gap.close();tail.close()
        self.bank.empty()
        return self.output
    def close(self):
        need(not self.closed and self.output.read()==BLANK,'consume output before disposal')
        self.bank.dispose();self.output.step(-1);self.output.write(BLANK);self.output.step(1)
        self.closed=True
