"""Binary-register arithmetic witness with every local head move charged.

A small reference witness for the register-lowering lemma. Integer load/value
are boundary encoders for the checker; arithmetic uses only finite bits and
explicit Tape moves. This is not a simulator of Python or native callbacks.
"""
from tapes import Meter,Tape,need


class Registers:
    def __init__(self,width,count=8):
        self.width=width;self.meter=Meter(width)
        self.tapes=[Tape(self.meter) for _ in range(count)]
        for tape in self.tapes:tape.put_bits([0]*width);tape.at(0)
    def bit(self,r,j):
        need(0<=j<self.width,'register bit index');t=self.tapes[r];t.at(j);return t.read()
    def setbit(self,r,j,b):
        need(0<=j<self.width,'register bit index');t=self.tapes[r];t.at(j);t.write(b)
    def zero(self,r):
        t=self.tapes[r];t.at(0)
        for _ in range(self.width):t.write(0)
    def load(self,r,value):
        need(0<=value<1<<self.width,'register input overflow')
        t=self.tapes[r];t.at(0)
        for j in range(self.width-1,-1,-1):t.write((value>>j)&1)
    def value(self,r):
        t=self.tapes[r];t.at(0);value=0
        for _ in range(self.width):value=2*value+t.read()
        return value
    def copy(self,a,b):
        for j in range(self.width):self.setbit(b,j,self.bit(a,j))
    def compare(self,a,b):
        for j in range(self.width):
            x,y=self.bit(a,j),self.bit(b,j)
            if x!=y:return 1 if x else -1
        return 0
    def add(self,a,b,out):
        carry=0
        for j in range(self.width-1,-1,-1):
            total=self.bit(a,j)+self.bit(b,j)+carry
            self.setbit(out,j,total&1);carry=total>>1
        need(not carry,'register sum overflow')
    def sub(self,a,b,out):
        borrow=0
        for j in range(self.width-1,-1,-1):
            total=self.bit(a,j)-self.bit(b,j)-borrow
            self.setbit(out,j,total&1);borrow=int(total<0)
        need(not borrow,'negative register difference')
    def mul(self,a,b,out):
        need(out not in (a,b),'product output aliases an input');self.zero(out)
        for i in range(self.width):
            if not self.bit(a,self.width-1-i):continue
            for j in range(self.width):
                if not self.bit(b,self.width-1-j):continue
                k=self.width-1-i-j;need(k>=0,'register product overflow');carry=1
                while carry and k>=0:
                    total=self.bit(out,k)+carry;self.setbit(out,k,total&1);carry=total>>1;k-=1
                need(not carry,'register product overflow')
    def divide(self,a,b,quotient,remainder):
        need(len({a,b,quotient,remainder})==4,'division register alias')
        need(any(self.bit(b,j) for j in range(self.width)),'zero divisor')
        self.zero(quotient);self.zero(remainder)
        for j in range(self.width):
            need(not self.bit(remainder,0),'remainder shift overflow')
            for k in range(self.width-1):self.setbit(remainder,k,self.bit(remainder,k+1))
            self.setbit(remainder,self.width-1,self.bit(a,j))
            if self.compare(remainder,b)>=0:
                self.sub(remainder,b,remainder);self.setbit(quotient,j,1)
