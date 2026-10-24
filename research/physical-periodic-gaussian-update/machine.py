"""Fixed-geometry local binary-tape periodic update. No payload decoding."""
BITS=80
GRID=33
N=385
S=384
OFFSETS=(-4,-3,-2,-1,1,2,3,4)
BLANK,LEFT,RIGHT=2,3,4

def need(x,s):
    if not x:raise ValueError(s)

class Meter:
    def __init__(self):self.reads=self.writes=self.moves=self.control=0
    def record(self):return {k:getattr(self,k) for k in ('reads','writes','moves','control')}
    def tick(self,n=1):self.control+=n
    def repeat(self,n):
        self.tick()
        for i in range(n):
            self.tick(2)
            yield i
        self.tick()

class Tape:
    def __init__(self,m,size):
        self.m=m;self.cells=bytearray([BLANK]*(size+2));self.head=0
        self.write(LEFT);self.step(1)
        for _ in m.repeat(size):self.write(BLANK);self.step(1)
        self.write(RIGHT);self.rewind()
    def read(self):self.m.reads+=1;return self.cells[self.head]
    def write(self,b):
        need(b in (0,1,BLANK,LEFT,RIGHT),'fixed alphabet write');self.m.writes+=1;self.cells[self.head]=b
    def step(self,d):
        need(d in (-1,1),'unit motion');self.m.moves+=1;self.head+=d
        need(0<=self.head<len(self.cells),'tape endpoint')
    def rewind(self):
        self.step(-1)
        while self.read()!=LEFT:self.m.tick();self.step(-1)
        self.m.tick();self.step(1)
    def skip(self,n):
        for _ in self.m.repeat(n):self.step(1)
    def fill(self,n,b):
        self.rewind()
        for _ in self.m.repeat(n):self.write(b);self.step(1)
        need(self.read()==RIGHT,'complete fill');self.rewind()


def transfer(source,target,n):
    for _ in source.m.repeat(n):
        b=source.read();need(b in (0,1),'input bit');target.write(b);source.step(1);target.step(1)


def muladd(c,y,a):
    """a += c*y modulo2^80, c unsigned33 bits; all heads restored."""
    m=c.m
    for k in m.repeat(GRID):
        bit=c.read();need(bit in (0,1),'coefficient bit');m.tick()
        if bit:
            a.skip(k);carry=0;m.tick()
            for _ in m.repeat(BITS-k):
                v=y.read()+a.read()+carry;m.tick();a.write(v&1);carry=v>>1
                y.step(1);a.step(1)
            y.rewind();a.rewind()
        c.step(1)
    c.rewind()


def rounded(a,r):
    """Signed truncation toward zero by2^33, in two's complement."""
    m=a.m;a.skip(BITS-1);negative=a.read();a.rewind();discard=0
    for _ in m.repeat(GRID):discard|=a.read();m.tick();a.step(1)
    transfer(a,r,BITS-GRID)
    for _ in m.repeat(GRID):r.write(negative);r.step(1)
    r.rewind();a.rewind();m.tick()
    if negative and discard:
        carry=1;m.tick()
        for _ in m.repeat(BITS):
            v=r.read()+carry;m.tick();r.write(v&1);carry=v>>1;r.step(1)
        r.rewind()


def subtract_emit(u,r,out):
    m=u.m;carry=1;m.tick()
    for _ in m.repeat(BITS):
        v=u.read()+(1-r.read())+carry;m.tick();out.write(v&1);carry=v>>1
        u.step(1);r.step(1);out.step(1)
    r.rewind()


class Update:
    def __init__(self,m):
        self.m=m
        self.table=Tape(m,S*8*GRID);self.bank=Tape(m,N*2*BITS)
        self.c=Tape(m,GRID);self.y=Tape(m,BITS);self.a=Tape(m,BITS);self.r=Tape(m,BITS)
        self.output=Tape(m,N*2*BITS);self.pending=False
    def private(self):return (self.table,self.bank,self.c,self.y,self.a,self.r)
    def setup(self,coeff):
        # Static order: input[source row][signed offset], output[offset][source row].
        for offset in self.m.repeat(8):
            for _ in self.m.repeat(S):
                for slot in self.m.repeat(8):
                    self.m.tick()
                    if slot==offset:transfer(coeff,self.table,GRID)
                    else:coeff.skip(GRID)
            need(coeff.read()==RIGHT,'coefficient extent');coeff.rewind()
        need(self.table.read()==RIGHT,'table extent');self.table.rewind()
    def run(self,coeff,u,current):
        ports=(coeff,u,current,self.output,*self.private())
        need(len({id(t.cells) for t in ports})==len(ports),'exclusive backing')
        need(all(t.m is self.m for t in ports),'one physical meter')
        need(not self.pending and all(t.head==1 for t in ports),'canonical entry')
        for t in (self.output,*self.private()):
            for _ in self.m.repeat(len(t.cells)-2):
                need(t.read()==BLANK,'empty owner entry');t.step(1)
            t.rewind()
        need(len(coeff.cells)==S*8*GRID+2 and len(u.cells)==len(current.cells)==N*2*BITS+2,'fixed ports')
        self.setup(coeff);self.bank.fill(N*2*BITS,0)
        for offset in self.m.repeat(8):
            h=OFFSETS[offset];j=h%S;self.m.tick(2)
            # Fixed compile-time starting coordinate, not payload-derived addressing.
            start=j+(j>=192);current.skip(start*2*BITS)
            for i in self.m.repeat(S):
                self.m.tick()
                if i==192:self.bank.skip(2*BITS)
                transfer(self.table,self.c,GRID);self.c.rewind()
                for _ in self.m.repeat(2):
                    transfer(current,self.y,BITS);self.y.rewind()
                    transfer(self.bank,self.a,BITS);self.a.rewind()
                    muladd(self.c,self.y,self.a)
                    for _ in self.m.repeat(BITS):self.bank.step(-1)
                    transfer(self.a,self.bank,BITS);self.a.rewind()
                    self.y.fill(BITS,BLANK);self.a.fill(BITS,BLANK)
                self.c.fill(GRID,BLANK)
                self.m.tick(3)
                if j==191:current.skip(2*BITS)
                if j==383:current.rewind()
                j=(j+1)%S
            current.rewind();self.bank.rewind()
        need(self.table.read()==RIGHT,'all coefficients consumed');self.table.rewind()
        for _ in self.m.repeat(N*2):
            transfer(self.bank,self.a,BITS);self.a.rewind();rounded(self.a,self.r)
            subtract_emit(u,self.r,self.output)
            self.a.fill(BITS,BLANK);self.r.fill(BITS,BLANK)
        need(u.read()==self.bank.read()==self.output.read()==RIGHT,'complete output')
        u.rewind();self.output.rewind();self.bank.fill(N*2*BITS,BLANK)
        self.table.fill(S*8*GRID,BLANK);self.pending=True
        return self.output
    def consume(self):
        need(self.pending and self.output.head==1,'canonical owned return');self.output.fill(N*2*BITS,BLANK);self.pending=False
