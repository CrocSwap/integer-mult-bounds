"""Sequential binary-cell tables with explicit movement and bounded registers.

The reference interpreter counts physical tape-cell actions. Host integer
registers are charged separately by the universal binary-register lowering
bound in COST-PROOF.md; they are not claimed to be unit-cost tape operations.
"""
from dataclasses import dataclass


def need(ok,message):
    if not ok:raise ValueError(message)


@dataclass
class Meter:
    width:int
    cells:int=0
    registers:int=0
    sweeps:int=0
    max_live_bits:int=0
    def word(self,n=1):self.registers+=n
    def total_upper(self):return (self.cells+self.registers)*2**20*(2*self.width+1)**4


class Tape:
    def __init__(self,meter):self.m=meter;self.cells=[];self.head=0;self.peak=0
    def move(self,delta):
        need(delta in (-1,1),'one-cell move');self.head+=delta
        need(self.head>=0,'left boundary');self.m.cells+=1
    def at(self,position):
        need(position>=0,'negative local position');self.m.word()
        while self.head<position:self.move(1)
        while self.head>position:self.move(-1)
    def read(self):
        need(self.head<len(self.cells),'read beyond initialized binary tape')
        value=self.cells[self.head];self.m.cells+=1;self.move(1);return value
    def write(self,value):
        need(value in (0,1),'binary alphabet')
        if self.head==len(self.cells):self.cells.append(value)
        else:
            need(self.head<len(self.cells),'uninitialized gap');self.cells[self.head]=value
        self.m.cells+=1;self.move(1);self.peak=max(self.peak,self.head)
    def clear(self):
        self.at(0)
        for _ in range(len(self.cells)):self.write(0)
        self.at(0);self.cells=[]
    def put_u(self,value):
        w=self.m.width;need(0<=value<1<<w,'register overflow');self.m.word()
        for j in range(w-1,-1,-1):self.write((value>>j)&1)
    def get_u(self):
        value=0;self.m.word()
        for _ in range(self.m.width):value=(value<<1)|self.read()
        return value
    def put_bits(self,bits):
        for bit in bits:self.write(bit)
    def get_bits(self,size):
        self.m.word();return [self.read() for _ in range(size)]


def bit_image(image):
    data,length=image
    return [(data[i//8]>>(7-i%8))&1 for i in range(length)]


def byte_image(bits):
    data=bytearray((len(bits)+7)//8)
    for i,b in enumerate(bits):
        need(b in (0,1),'binary payload');data[i//8]|=b<<(7-i%8)
    return bytes(data),len(bits)


class Table:
    """Sorted (key, bit-length, payload) records; every operation scans tapes."""
    def __init__(self,meter,records=()):
        self.m=meter;self.a=Tape(meter);self.b=Tape(meter)
        self.reset(records)
    def reset(self,records=(),count=None):
        if count is None:
            need(hasattr(records,'__len__'),'streaming initialization requires record count')
            count=len(records)
        self.a.clear();self.b.clear();self.a.put_u(count);last=-1;seen=0
        for key,payload in records:
            need(key>last,'initial key order');self.a.put_u(key);self.a.put_u(len(payload));self.a.put_bits(payload);last=key;seen+=1
        need(seen==count,'initial record count');self.a.at(0)
    def walk(self):
        self.m.sweeps+=1;self.a.at(0);count=self.a.get_u();last=-1
        for _ in range(count):
            key=self.a.get_u();length=self.a.get_u();need(key>last,'stored key order')
            payload=self.a.get_bits(length);last=key;self.m.word()
            yield key,payload
    def get(self,key):
        result=None
        for current,payload in self.walk():
            self.m.word()
            if current==key:result=payload
        if result is None:raise KeyError(key)
        return result
    def rewrite(self,key,payload=None,*,remove=False):
        self.b.clear();self.b.put_u(0);count=0;found=False;written=False
        for current,old in self.walk():
            self.m.word(3)
            if not written and key<current and not remove:
                self.b.put_u(key);self.b.put_u(len(payload));self.b.put_bits(payload);count+=1;written=True
            if current==key:
                found=True
                if not remove:
                    self.b.put_u(key);self.b.put_u(len(payload));self.b.put_bits(payload);count+=1;written=True
            else:
                self.b.put_u(current);self.b.put_u(len(old));self.b.put_bits(old);count+=1
        if remove:need(found,'remove missing key')
        elif not written:
            self.b.put_u(key);self.b.put_u(len(payload));self.b.put_bits(payload);count+=1
        end=self.b.head;self.b.at(0);self.b.put_u(count);self.b.at(end)
        self.a.clear();self.a,self.b=self.b,self.a
        self.m.max_live_bits=max(self.m.max_live_bits,len(self.a.cells)+len(self.b.cells))
    def pop(self,key):
        payload=self.get(key);self.rewrite(key,remove=True);return payload
    def empty(self):self.a.at(0);return self.a.get_u()==0
    def close(self):self.a.clear();self.b.clear()
    def historical_bits(self):return self.a.peak+self.b.peak
