"""Bounded-word RamStd-fragment packed-tape kernels. Apache-2.0; OpenAI assistance.
This is a microinstruction interpreter/checker, not an implementation of fast multiplication.
"""
from collections import defaultdict
from random import Random
import json

class VM:
    def __init__(self,w):
        if w<10:raise ValueError('Use at least 10 word bits')
        self.w=w;self.mask=(1<<w)-1;self.mem=defaultdict(int);self.steps=0;self.high=0
    def put(self,a,v):
        if not 0<=a<=self.mask:raise ValueError('Address overflow')
        if not 0<=v<=self.mask:raise ValueError('Value overflow in checked precondition')
        self.mem[a]=v;self.high=max(self.high,a)
    def run(self,p):
        pc=0;start=self.steps
        while pc<len(p):
            i=p[pc];op,*z=i;pc+=1
            def m(a):return self.mem[a&self.mask]
            if op=='halt':break
            self.steps+=1
            if op=='jump':pc=z[0];continue
            if op=='jzero':
                if m(z[0])==0:pc=z[1]
                continue
            if op=='jlt':
                if m(z[0])<m(z[1]):pc=z[2]
                continue
            if op=='set':a,v=z
            elif op=='load':a,b=z;v=m(m(b))
            elif op=='store':a,b=z;self.mem[m(a)]=m(b);self.high=max(self.high,m(a));continue
            elif op=='not':a,b=z;v=self.mask-m(b)
            else:
                a,b,c=z;x,y=m(b),m(c)
                if op=='add':v=x+y
                elif op=='sub':v=max(0,x-y)
                elif op=='and':v=x&y
                elif op=='or':v=x|y
                elif op=='xor':v=x^y
                elif op=='shiftl':v=(x<<y)if y<self.w else 0
                elif op=='shiftr':v=x>>y
                else:raise ValueError('Forbidden opcode '+op)
            self.mem[a&self.mask]=v&self.mask
        return self.steps-start

# Register 0=input bit length; fixed registers <64; packed data starts at128.
# Metadata 4=log2(B),5=B-1; parameters10=absolute bank index,11=tape/sign tag,
# 12=symbol towrite; result13. Two sign banks encode z>=0 as(z,0), z<0 as(-z-1,1).
# INIT is the SAME finite program for every input and every word length.
def initialize(field_log=1):
    p=[('set',1,1),('set',2,2),('add',3,0,2),('set',6,0),
       ('jlt',3,2,9),('shiftr',3,3,1),('add',6,6,1),('jump',4),('halt',),
       ('set',7,3+field_log),('shiftr',6,6,7),('set',8,1),('set',4,0),
       ('shiftl',9,8,1),('jlt',6,9,19),('add',8,8,8),('add',4,4,1),('jump',13),('halt',),
       ('sub',5,8,1),('halt',)]
    return p

# Two-bit tape alphabet (blank,0,1,marker); stride H=4 supports two tapes.
# B=max(1,largestpower2<=floor(log2(n+2)/16)); 2B<=w under theorem's widthbound.
def address_code(stride_log=2,field_log=1,base=128):
    return [('shiftr',14,10,4),('and',15,10,5),('set',16,field_log),
            ('shiftl',17,15,16),('set',18,stride_log),('shiftl',19,14,18),
            ('add',19,19,11),('set',20,base),('add',19,19,20)]
def get_code(stride_log=2,field_log=1,base=128):
    return address_code(stride_log,field_log,base)+[('load',21,19),('shiftr',22,21,17),('set',23,(1<<(1<<field_log))-1),('and',13,22,23)]
def set_code(stride_log=2,field_log=1,base=128):
    return address_code(stride_log,field_log,base)+[('load',21,19),('set',23,(1<<(1<<field_log))-1),('shiftl',24,23,17),
      ('not',25,24),('and',26,21,25),('shiftl',27,12,17),('or',28,26,27),('store',19,28)]

def need(ok,msg):
    if not ok:raise ValueError(msg)

def check():
    rng=Random(20261022);cases=0;maxget=maxset=0;packed_saved=False
    for field_log in [0,1,2]:
      c=1<<field_log;symbol_mask=(1<<c)-1
      for stride_log in [1,2,3,4]:
       H=1<<stride_log
       for w in [10,16,32,64,128]:
        for n in [0,1,2,15,127,1024,2**32,2**64]:
            if n+2>=(1<<w):continue
            v=VM(w);v.put(0,n);init=v.run(initialize(field_log));B=1<<v.mem[4]
            q=((n+2).bit_length()-1)>>(3+field_log)
            expected=1<<max(0,q.bit_length()-1)
            need(B==expected and v.mem[5]==B-1,'Uniform B initialization')
            need(c*B<=w,'Packed fields fit word')
            reference={};limit=min(300,((1<<w)-128-H)//H*B)
            for _ in range(40):
                tape=rng.randrange(H//2);z=rng.randrange(-limit,limit+1);tag=2*tape+int(z<0);index=z if z>=0 else -z-1
                v.put(10,index);v.put(11,tag);value=rng.randrange(symbol_mask+1);v.put(12,value)
                st=v.run(set_code(stride_log,field_log));reference[tape,z]=value;maxset=max(maxset,st)
                g=v.run(get_code(stride_log,field_log));maxget=max(maxget,g);need(v.mem[13]==value,'Write/read')
                (t2,z2),a2=rng.choice(list(reference.items()));v.put(10,z2 if z2>=0 else -z2-1);v.put(11,2*t2+int(z2<0));v.run(get_code(stride_log,field_log));need(v.mem[13]==a2,'Frame or bank alias')
                cases+=1
            packed_saved|=B>1
    need(packed_saved,'Packed path tested')
    need(maxget==13 and maxset==17,'Fixed macro cost')
    # Semantic rejection control: use an incorrect bank tag, not a self-mirroring oracle.
    v=VM(16);v.put(0,1024);v.run(initialize());v.put(10,0);v.put(11,0);v.put(12,3);v.run(set_code());v.put(11,1);v.run(get_code());need(v.mem[13]!=3,'Wrong-sign control')
    # Exact field overwrite must preserve arbitrary unused high bits and neighbors.
    v=VM(32);v.put(0,2**20);v.run(initialize());v.put(128,v.mask);v.put(10,0);v.put(11,0);v.put(12,0);v.run(set_code());need(v.mem[128]==v.mask-3,'Dirty padding preservation')
    for base in [256,1024,4096]:
        v=VM(32);v.put(0,2**20);v.run(initialize(0));v.put(10,6);v.put(11,255);v.put(12,1);v.run(set_code(8,0,base));v.run(get_code(8,0,base));need(v.mem[13]==1 and v.mem[base+3*256+255]==1,'Machine-dependent packed base')
    return {'machine_dependent_base_cases':3,'status':'PASS_PACKED_TAPE_RAM_KERNELS','operation_traces':cases,'get_instructions':maxget,'set_instructions':maxset,'word_widths':[10,16,32,64,128],'packed_path_tested':packed_saved,'dirty_padding_preserved':True,'checked_tape_counts':[1,2,4,8],'symbol_field_bits':[1,2,4],'wrong_bank_rejected':True,'unit_multiplication':False,'formal_Lean_proof':False}
if __name__=='__main__':print(json.dumps(check(),indent=2))
