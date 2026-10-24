"""Literal binary lowering of the retained finite key program.

JoyboyBrian, with substantial OpenAI Codex assistance. Apache-2.0.
Assembly/packet construction is outside runtime; Machine only executes bit ops.
"""
from collections import Counter

WIDTH = 13
REGISTER_WIDTH = 14
CODES = {'_':0, 'L':1, '0':2, '1':3, 'R':4, '<':5, '>':6, '=':7}


def code(symbol):
    if type(symbol) is tuple and symbol[0] == 'R' and 0 <= symbol[1] < 4096:
        return 4096 + symbol[1]
    return CODES[symbol]


def bits(symbol):
    n = code(symbol)
    return tuple((n >> j) & 1 for j in range(WIDTH))


def word(value):
    if type(value) is bool: return (int(value),) + (0,)*12 + (1,)
    return bits(value) + (0,)


def compile_program(source, fault=None, lifecycle=False):
    """Finite static compilation; no packet/address/ROM is an argument."""
    out=[];starts=[];registers={}
    def emit(*instruction): out.append(instruction)
    def reg(name, bit):
        key=(name,bit)
        if key not in registers: registers[key]=len(registers)
        return registers[key]
    def set_word(name,value):
        for j,bit in enumerate(word(value)):emit('set',reg(name,j),bit)
    for instruction in source:
        starts.append(len(out));op,*a=instruction
        if op in ('read','write','write_reg'):
            for j in range(WIDTH):
                if op=='read':emit('read',a[0],reg(a[1],j))
                elif op=='write':emit('write',a[0],bits(a[1])[j])
                else:emit('write_reg',a[0],reg(a[1],j))
                if j != WIDTH-1:emit('move',a[0],1)
            for _ in range(WIDTH-1):emit('move',a[0],-1)
            if op=='read':emit('set',reg(a[1],13),0)
        elif op=='move':
            for _ in range(WIDTH if fault!='short_move' else WIDTH-1):emit('move',a[0],a[1])
        elif op=='set':set_word(a[0],a[1])
        elif op=='copy':
            for j in range(REGISTER_WIDTH):emit('copy',reg(a[0],j),reg(a[1],j))
        elif op in ('eq','eq_reg'):
            emit('set',reg('$different',0),0)
            for j in range(13 if fault=='drop_tag' else REGISTER_WIDTH):
                if op=='eq':emit('xor_const',reg(a[0],j),word(a[1])[j],reg('$xor',0))
                else:emit('xor',reg(a[0],j),reg(a[1],j),reg('$xor',0))
                emit('or',reg('$different',0),reg('$xor',0),reg('$different',0))
            for j in range(1,REGISTER_WIDTH):emit('set',reg(a[2],j),int(j==13))
            emit('not',reg('$different',0),reg(a[2],0))
        elif op in ('xorbit','andbit','orbit'):
            emit({'xorbit':'xor','andbit':'and','orbit':'or'}[op],reg(a[0],0),reg(a[1],0),reg(a[2],0))
            for j in range(1,REGISTER_WIDTH):emit('set',reg(a[2],j),int(j==1))
        elif op=='branch':emit('branch',reg(a[0],0),('label',a[1]),('label',a[2]))
        elif op=='jump':emit('jump',('label',a[0]))
        elif op=='halt':
            if fault=='dirty_head':emit('move','rom',1)
            if lifecycle and fault!='keep_control':emit('clear_control')
            emit('halt',a[0])
        else:raise ValueError('unknown source operation')
    starts.append(len(out))
    # Initialize and erase each physical finite-control bit explicitly when
    # composing a complete service, rather than relying on host allocation.
    offsets=[];at=len(registers) if lifecycle else 0
    for instruction in out:
        offsets.append(at);at+=len(registers) if instruction[0]=='clear_control' else 1
    offsets.append(at);starts=[offsets[start] for start in starts]
    program=[('set',j,0) for j in range(len(registers))] if lifecycle else []
    for instruction in out:
        if instruction[0]=='clear_control':program.extend(('set',j,0) for j in range(len(registers)))
        else:program.append(tuple(starts[x[1]] if type(x) is tuple and x[0]=='label' else x for x in instruction))
    return program,starts,registers


class BitTape:
    """Physical binary cells; head coordinates exist only in this emulator."""
    def __init__(self,initial=(),head=0):
        self.cells={i:b for i,b in enumerate(initial) if b};self.head=head;self.actions=Counter()
    def read(self):self.actions['read']+=1;return self.cells.get(self.head,0)
    def write(self,bit):
        if bit not in (0,1):raise ValueError('nonbinary write')
        self.actions['write']+=1
        if bit:self.cells[self.head]=1
        else:self.cells.pop(self.head,None)
    def move(self,direction):
        if direction not in (-1,1) or self.head+direction<0:raise ValueError('invalid physical move')
        self.actions['move']+=1;self.head+=direction


class Machine:
    def __init__(self,program,register_count,tapes):
        self.program=program;self.registers=[0]*register_count;self.tapes=tapes
        self.pc=0;self.census=Counter();self.status=None
    def step(self):
        op,*a=self.program[self.pc];self.pc+=1;self.census[op]+=1;r=self.registers;t=self.tapes
        if op=='read':r[a[1]]=t[a[0]].read()
        elif op=='write':t[a[0]].write(a[1])
        elif op=='write_reg':t[a[0]].write(r[a[1]])
        elif op=='move':t[a[0]].move(a[1])
        elif op=='set':r[a[0]]=a[1]
        elif op=='copy':r[a[1]]=r[a[0]]
        elif op in ('xor','xor_const'):r[a[2]]=r[a[0]]^(a[1] if op=='xor_const' else r[a[1]])
        elif op=='and':r[a[2]]=r[a[0]]&r[a[1]]
        elif op=='or':r[a[2]]=r[a[0]]|r[a[1]]
        elif op=='not':r[a[1]]=r[a[0]]^1
        elif op=='branch':self.pc=a[1] if r[a[0]] else a[2]
        elif op=='jump':self.pc=a[0]
        elif op=='halt':self.status=a[0]
        else:raise ValueError('unknown binary operation')
    def run(self):
        while self.status is None:self.step()
        return self.status
