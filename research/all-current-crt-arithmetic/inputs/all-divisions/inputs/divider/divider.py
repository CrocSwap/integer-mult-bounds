"""Fixed64-Word physical divider; constructors run offline. Apache-2.0.
Prepared for @CubeJerry with substantial OpenAI assistance.
"""
import json
from hashlib import sha256
ALPHABET=('0','1','L','R','_','|')
N,D,Q,R=range(4)
TAPES=68

class Builder:
    def __init__(self):self.code,self.labels,self.serial=[],{},0
    def fresh(self,s='q'):
        self.serial+=1;return s+'_'+str(self.serial)
    def mark(self,s):
        if s in self.labels:raise ValueError('duplicate label')
        self.labels[s]=len(self.code)
    def op(self,*row):self.code.append(row)
    def jump(self,s):self.op('J',s)
    def read(self,t,branches):self.op('R',t,{s:branches.get(s,'FAIL') for s in ALPHABET})
    def expect(self,t,s):
        done=self.fresh('expected');self.read(t,{s:done});self.mark(done)
    def rewind(self,t):
        loop,back,done=(self.fresh(s) for s in ('rewind','left','origin'))
        self.mark(loop);self.read(t,{s:done if s=='L' else back for s in ALPHABET})
        self.mark(back);self.op('M',t,-1);self.jump(loop);self.mark(done)
    def native_rewind(self,t):
        self.op('M',t,-1);self.rewind(t);self.op('M',t,1)
    def finish(self):
        out=[]
        for op,*a in self.code:
            if op=='R':out.append((op,a[0],{s:self.labels[t] for s,t in a[1].items()}))
            elif op=='J':out.append((op,self.labels[a[0]]))
            else:out.append((op,*a))
        return tuple(out),dict(self.labels)

def distinct(b,a,c):
    a+=64;c+=64
    for t in(a,c):b.expect(t,'L');b.op('M',t,1)
    prefix=b.fresh('distinct');b.jump(prefix+'_0_0')
    for j in range(6):
        for unequal in(0,1):
            b.mark(prefix+'_'+str(j)+'_'+str(unequal))
            branches={str(x):b.fresh('leftbit') for x in(0,1)};b.read(a,branches)
            for x in(0,1):
                b.mark(branches[str(x)]);other={str(y):b.fresh('pair') for y in(0,1)};b.read(c,other)
                for y in(0,1):
                    b.mark(other[str(y)]);b.op('M',a,1);b.op('M',c,1)
                    b.jump(prefix+'_'+str(j+1)+'_'+str(int(unequal or x!=y)))
    b.mark(prefix+'_6_0');b.jump('FAIL');b.mark(prefix+'_6_1')
    for t in(a,c):
        b.expect(t,'R')
        for _ in range(7):b.op('M',t,-1)

def initialize(b):
    for t in(N,D,Q,R):b.op('M',t,-1);b.expect(t,'L');b.op('M',t,1)
    b.jump('INIT_0_0')
    for stage in range(5):
        for seen in(0,1):
            b.mark('INIT_'+str(stage)+'_'+str(seen));digit=b.fresh('digit')
            b.read(N,{'0':digit,'1':digit,**({'R':'INIT_END_'+str(seen)} if stage==4 else {})})
            b.mark(digit);branches={str(x):b.fresh('divisor') for x in(0,1)};b.read(D,branches)
            for x in(0,1):
                b.mark(branches[str(x)])
                for t in(Q,R):b.expect(t,'_');b.op('W',t,'0')
                for t in(N,D,Q,R):b.op('M',t,1)
                b.jump('INIT_'+str(min(4,stage+1))+'_'+str(int(seen or x)))
    b.mark('INIT_END_0');b.jump('FAIL');b.mark('INIT_END_1');b.expect(D,'R')
    for t in(Q,R):b.expect(t,'_');b.op('W',t,'R')
    b.op('M',D,-1);b.expect(D,'0');b.native_rewind(D)
    b.op('M',N,-1);b.op('M',Q,-1);b.native_rewind(R);b.jump('DIGIT')

def shift(b):
    for carry in(0,1):
        b.mark('SHIFT_'+str(carry));branches={str(x):b.fresh('shiftbit') for x in(0,1)}
        b.read(R,{**branches,**({'R':'SHIFT_END'} if carry==0 else {})})
        for x in(0,1):
            b.mark(branches[str(x)]);b.op('W',R,str(carry));b.op('M',R,1);b.jump('SHIFT_'+str(x))
    b.mark('SHIFT_END');b.native_rewind(R);b.jump('CMP_0')

def compare(b):
    for state in(-1,0,1):
        b.mark('CMP_'+str(state));branches={str(x):b.fresh('cmpbit') for x in(0,1)}
        b.read(R,{**branches,'R':'CMP_END_'+str(state)})
        for x in(0,1):
            b.mark(branches[str(x)]);other={str(y):b.fresh('cmppair') for y in(0,1)};b.read(D,other)
            for y in(0,1):
                b.mark(other[str(y)]);b.op('M',R,1);b.op('M',D,1)
                b.jump('CMP_'+str(state if x==y else 1 if x>y else -1))
        b.mark('CMP_END_'+str(state));b.expect(D,'R');b.native_rewind(R);b.native_rewind(D)
        b.jump('QBIT_0' if state==-1 else 'SUB_0')

def subtract(b):
    for borrow in(0,1):
        b.mark('SUB_'+str(borrow));branches={str(x):b.fresh('subbit') for x in(0,1)}
        b.read(R,{**branches,**({'R':'SUB_END'} if borrow==0 else {})})
        for x in(0,1):
            b.mark(branches[str(x)]);other={str(y):b.fresh('subpair') for y in(0,1)};b.read(D,other)
            for y in(0,1):
                b.mark(other[str(y)]);value=x-y-borrow;b.op('W',R,str(value&1))
                b.op('M',R,1);b.op('M',D,1);b.jump('SUB_'+str(int(value<0)))
    b.mark('SUB_END');b.expect(D,'R');b.native_rewind(R);b.native_rewind(D);b.jump('QBIT_1')

def clear_selectors(b,status='DONE'):
    for t in range(64,68):
        b.expect(t,'L');b.op('W',t,'_');b.op('M',t,1)
        for _ in range(6):
            ok=b.fresh('selector_digit');b.read(t,{'0':ok,'1':ok});b.mark(ok);b.op('W',t,'_');b.op('M',t,1)
        b.expect(t,'R');b.op('W',t,'_')
        for _ in range(7):b.op('M',t,-1)
    b.op('H',status)

def logical_graph():
    b=Builder();b.mark('DIVIDE')
    for a in range(4):
        for c in range(a+1,4):distinct(b,a,c)
    initialize(b);b.mark('DIGIT');b.read(N,{'0':'SHIFT_0','1':'SHIFT_1','L':'DIVISION_END'})
    shift(b);compare(b);subtract(b)
    for x in(0,1):
        b.mark('QBIT_'+str(x));b.op('W',Q,str(x));b.op('M',N,-1);b.op('M',Q,-1);b.jump('DIGIT')
    b.mark('DIVISION_END');b.expect(Q,'L');b.op('M',N,1);b.op('M',Q,1);clear_selectors(b)
    b.mark('RETIRE')
    for t in(Q,R):
        loop,erase,end=(b.fresh(s) for s in('retire','erase','erased'))
        b.mark(loop);b.read(t,{'0':erase,'1':erase,'R':end});b.mark(erase)
        b.op('W',t,'_');b.op('M',t,1);b.jump(loop)
        b.mark(end);b.op('W',t,'_');b.native_rewind(t)
    clear_selectors(b,'RETIRED');b.mark('FAIL');b.op('H','MALFORMED')
    return b.finish()

def dispatch(b,role,row,next_label):
    """Every leaf names a compile-time physical port; no runtime port operand."""
    selector=64+role
    b.expect(selector,'L');b.op('M',selector,1)
    prefix=b.fresh('dispatch');b.jump(prefix+'_0_0')
    for depth in range(6):
        for value in range(1<<depth):
            b.mark(prefix+'_'+str(depth)+'_'+str(value))
            branches={str(bit):b.fresh('selector_move') for bit in(0,1)}
            b.read(selector,branches)
            for bit in(0,1):
                b.mark(branches[str(bit)]);b.op('M',selector,1)
                b.jump(prefix+'_'+str(depth+1)+'_'+str(value+(bit<<depth)))
    for slot in range(64):
        b.mark(prefix+'_6_'+str(slot));b.expect(selector,'R')
        for _ in range(7):b.op('M',selector,-1)
        if row[0]=='R':b.read(slot,{s:'CORE_'+str(pc) for s,pc in row[2].items()})
        else:b.op(row[0],slot,row[2]);b.jump(next_label)

def compile_divider():
    logical,ll=logical_graph();b=Builder();b.mark('ACQUIRE')
    # Exactly eight granted inactive cells per selector, arbitrary prior bits.
    # The external capability/grant is an explicit entry premise.
    for t in range(64,68):
        for k in range(8):
            b.op('W',t,'_')
            if k!=7:b.op('M',t,1)
        for _ in range(7):b.op('M',t,-1)
    b.op('H','READY')
    setter_names=[]
    for role in range(4):
        names=[]
        for slot in range(64):
            name='SET_'+str(role)+'_'+str(slot);names.append(name);b.mark(name)
            t=64+role;b.expect(t,'_');b.op('W',t,'L');b.op('M',t,1)
            for bit in range(6):
                b.expect(t,'_');b.op('W',t,str((slot>>bit)&1));b.op('M',t,1)
            b.expect(t,'_');b.op('W',t,'R')
            for _ in range(7):b.op('M',t,-1)
            b.op('H','BOUND')
        setter_names.append(names)
    for pc,row in enumerate(logical):
        b.mark('CORE_'+str(pc));op=row[0]
        if op in('R','W','M') and row[1]<4:
            dispatch(b,row[1],row,'CORE_'+str(pc+1))
        elif op=='R':b.read(row[1],{s:'CORE_'+str(t) for s,t in row[2].items()})
        elif op=='J':b.jump('CORE_'+str(row[1]))
        else:b.op(*row)
    b.mark('FAIL');b.op('H','MALFORMED')
    code,labels=b.finish()
    metadata={'tapes':TAPES,'logical_locations':len(logical),
              'entries':{'ACQUIRE':labels['ACQUIRE'],**{s:labels['CORE_'+str(ll[s])] for s in('DIVIDE','RETIRE')}},
              'setters':[[labels[s] for s in row] for row in setter_names],
              'logical_labels':ll,'logical_to_physical':[labels['CORE_'+str(i)] for i in range(len(logical))]}
    return code,labels,metadata

def digest(code):
    return sha256(json.dumps(code,separators=(',',':'),sort_keys=True).encode()).hexdigest()

if __name__=='__main__':
    code,labels,metadata=compile_divider()
    print(json.dumps({'locations':len(code),'logical_locations':metadata['logical_locations'],
                      'tapes':TAPES,'sha256':digest(code),'entries':metadata['entries']},sort_keys=True))
