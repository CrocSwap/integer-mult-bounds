"""Literal R/W/M/J/H interpreter and explicit granted-window adapters.

Apache-2.0; prepared for @CubeJerry with substantial OpenAI assistance.
"""
class NumericPort:
    symbols=('0','1','L','R','_')
    values={s:i for i,s in enumerate(symbols)}
    def __init__(self,word):self.word=word
    @property
    def cells(self):return self.word.cells
    @property
    def head(self):return self.word.head
    def read(self):return self.symbols[self.word.read()]
    def write(self,s):self.word.write(self.values[s])
    def step(self,d):self.word.step(d)

class GrantedSelector:
    """Capability for precisely [origin,origin+7]; grant is external and paid.

    Construction never allocates or clears backing cells.  In particular a
    growable predecessor Tape alone does not establish this capability.
    """
    def __init__(self,tape,origin=0,granted_extent=8):
        if granted_extent<8 or len(tape.cells)<origin+granted_extent or tape.head!=origin:
            raise ValueError('explicit backed eight-cell selector grant')
        self.tape,self.origin,self.extent=tape,origin,granted_extent
    @property
    def cells(self):return self.tape.cells
    @property
    def head(self):return self.tape.head
    def check(self):
        if not self.origin<=self.head<self.origin+8:raise ValueError('selector capability boundary')
    def read(self):self.check();return self.tape.read()
    def write(self,s):self.check();self.tape.write(s)
    def step(self,d):
        if not self.origin<=self.head+d<self.origin+8:raise ValueError('selector capability movement')
        self.tape.step(d)

class Program:
    def __init__(self,code,labels,metadata):
        self.code,self.labels,self.metadata=code,labels,metadata
        self.total=self.numeric_actions=self.selector_actions=self.calls=0
        self.history=[None]*68;self.receipts=[]
        self.logical_pc=set(metadata['logical_to_physical'])
    def run(self,ports,entry='DIVIDE',limit=20000000):
        if len(ports)!=68 or len({id(t.cells) for t in ports})!=68:
            raise ValueError('64 distinct numerical plus four distinct selector owners')
        if isinstance(entry,str):pc=self.metadata['entries'][entry]
        else:pc=entry
        steps=numeric=selector=logical=0;writes=[0]*68;counts={};history=[[t.head,t.head] for t in ports]
        while True:
            op,*a=self.code[pc];steps+=1
            logical+=pc in self.logical_pc
            if steps>limit:raise ValueError('bounded verifier watchdog')
            counts[op]=counts.get(op,0)+1
            if op in('R','W','M'):
                t=ports[a[0]];numeric+=a[0]<64;selector+=a[0]>=64
            if op=='R':
                s=t.read()
                if s not in a[1]:raise ValueError('outside declared alphabet')
                pc=a[1][s]
            elif op=='W':t.write(a[1]);writes[a[0]]+=1;pc+=1
            elif op=='M':
                t.step(a[1]);history[a[0]][0]=min(history[a[0]][0],t.head)
                history[a[0]][1]=max(history[a[0]][1],t.head);pc+=1
            elif op=='J':pc=a[0]
            elif op=='H':
                out={'status':a[0],'instructions':steps,'numeric_actions':numeric,
                     'selector_actions':selector,'logical_instructions':logical,
                     'writes':writes,'history':history,'op_counts':counts}
                self.total+=steps;self.numeric_actions+=numeric;self.selector_actions+=selector;self.calls+=1
                for k,pair in enumerate(history):
                    old=self.history[k];self.history[k]=pair if old is None else[min(old[0],pair[0]),max(old[1],pair[1])]
                self.receipts.append(out);return out
            else:raise ValueError('unknown opcode')

def setters(program,ports,slots):
    if len(slots)!=4:raise ValueError('four fixed-role descriptors')
    for role,slot in enumerate(slots):
        if not isinstance(slot,int) or not 0<=slot<64:raise ValueError('finite slot domain')
        got=program.run(ports,program.metadata['setters'][role][slot])
        if got['status']!='BOUND':raise ValueError('selector binding rejected')
