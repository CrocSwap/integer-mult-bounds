"""Static local-symbol program for encoded binary elementary interchange.
JoyboyBrian, with substantial OpenAI Codex assistance. Apache-2.0.
Assembly helpers run only before execution; no helper survives as an opcode.
"""
ZERO,ONE,LEFT,RIGHT,BLANK=range(5)
BORROWED=('SOURCE','H','A','G','S')
PRIVATE=('PRE','GAP','TAIL','SCAN','REMAIN','OUTER','BETWEEN','BITS','Q00','Q01','Q10','Q11','B0','B1','OUTPUT')
ROLES=BORROWED+PRIVATE

class Builder:
    def __init__(self):self.code=[];self.labels={};self.serial=0
    def fresh(self):self.serial+=1;return 'L'+str(self.serial)
    def mark(self,label):self.labels[label]=len(self.code)
    def emit(self,*x):self.code.append(x)
    def jump(self,label):self.emit('jump',label)
    def test(self,role,symbol,yes,no):self.emit('test',role,symbol,yes,no)
    def write(self,role,symbol):self.emit('write',role,symbol)
    def move(self,role,d):self.emit('move',role,d)
    def require(self,role,symbol):
        ok=self.fresh();self.test(role,symbol,ok,'reject');self.mark(ok)
    def rewind(self,role):
        loop,end=self.fresh(),self.fresh();self.move(role,-1);self.mark(loop)
        more=self.fresh();self.test(role,LEFT,end,more);self.mark(more);self.move(role,-1);self.jump(loop);self.mark(end);self.move(role,1)
    def clear(self,role):
        self.rewind(role);loop,end,body=self.fresh(),self.fresh(),self.fresh();self.mark(loop)
        self.test(role,BLANK,end,body);self.mark(body);self.write(role,BLANK);self.move(role,1);self.jump(loop);self.mark(end);self.rewind(role)
    def copy(self,source,target,end_symbol):
        loop,end,z,o=self.fresh(),self.fresh(),self.fresh(),self.fresh();self.mark(loop)
        bit=self.fresh();self.test(source,end_symbol,end,bit);self.mark(bit)
        self.test(source,ZERO,z,o);self.mark(z);self.require(target,BLANK);self.write(target,ZERO);next_=self.fresh();self.jump(next_)
        self.mark(o);self.require(source,ONE);self.require(target,BLANK);self.write(target,ONE);self.mark(next_)
        self.move(source,1);self.move(target,1);self.jump(loop);self.mark(end)
        self.rewind(source)
        if end_symbol==RIGHT:self.write(target,RIGHT)
        self.rewind(target)
    def zero(self,role,yes,no):
        # Canonical number: only the word 0 RIGHT denotes zero.
        z=self.fresh();self.test(role,ZERO,z,no);self.mark(z);self.move(role,1)
        restore_y,restore_n=self.fresh(),self.fresh();self.test(role,RIGHT,restore_y,restore_n)
        self.mark(restore_y);self.move(role,-1);self.jump(yes)
        self.mark(restore_n);self.move(role,-1);self.jump(no)
    def normalize(self,role):
        self.rewind(role);loop,end,body=self.fresh(),self.fresh(),self.fresh();self.mark(loop)
        self.test(role,RIGHT,end,body);self.mark(body);self.move(role,1);self.jump(loop);self.mark(end);self.move(role,-1)
        trim,stop,erase=self.fresh(),self.fresh(),self.fresh();self.mark(trim);self.test(role,ZERO,erase,stop)
        self.mark(erase);self.write(role,RIGHT);self.move(role,1);self.write(role,BLANK);self.move(role,-1);self.move(role,-1);self.jump(trim)
        self.mark(stop);empty,done=self.fresh(),self.fresh();self.test(role,LEFT,empty,done)
        self.mark(empty);self.move(role,1);self.write(role,ZERO);self.move(role,1);self.write(role,RIGHT);self.mark(done);self.rewind(role)
    def dec(self,role):
        loop,one,zero=self.fresh(),self.fresh(),self.fresh();self.mark(loop);self.test(role,ZERO,zero,one)
        self.mark(zero);self.write(role,ONE);self.move(role,1);self.jump(loop)
        self.mark(one);self.require(role,ONE);self.write(role,ZERO);self.normalize(role)
    def double(self,role):
        # Shift a canonical LE positive word right using finite carry in PC.
        self.rewind(role)
        states=[self.fresh(),self.fresh()];done=self.fresh();self.jump(states[0])
        for carry in (0,1):
            self.mark(states[carry]);end,z,o=self.fresh(),self.fresh(),self.fresh();bit=self.fresh()
            self.test(role,RIGHT,end,bit);self.mark(bit);self.test(role,ZERO,z,o)
            self.mark(z);self.write(role,carry);self.move(role,1);self.jump(states[0])
            self.mark(o);self.require(role,ONE);self.write(role,carry);self.move(role,1);self.jump(states[1])
            self.mark(end)
            if carry:self.write(role,ONE);self.move(role,1);self.write(role,RIGHT)
            self.jump(done)
        self.mark(done);self.rewind(role)
    def half(self,role):
        self.require(role,ZERO);self.move(role,1);loop=self.fresh();self.mark(loop)
        end,z,o=self.fresh(),self.fresh(),self.fresh();bit=self.fresh();self.test(role,RIGHT,end,bit);self.mark(bit);self.test(role,ZERO,z,o)
        nxt=self.fresh()
        for label,symbol in ((z,ZERO),(o,ONE)):
            self.mark(label);self.require(role,symbol);self.move(role,-1);self.write(role,symbol);self.move(role,1);self.move(role,1);self.jump(nxt)
        self.mark(nxt);self.jump(loop);self.mark(end);self.write(role,BLANK);self.move(role,-1);self.write(role,RIGHT);self.rewind(role)
    def counted(self,number,counter,body):
        self.copy(number,counter,RIGHT);loop,end,work=self.fresh(),self.fresh(),self.fresh();self.mark(loop);self.zero(counter,end,work)
        self.mark(work);body();self.dec(counter);self.jump(loop);self.mark(end);self.clear(counter)
    def block(self,source,target):
        def bit():
            z,o,nxt=self.fresh(),self.fresh(),self.fresh();self.test(source,ZERO,z,o)
            for label,symbol in ((z,ZERO),(o,ONE)):
                self.mark(label);self.require(source,symbol);self.require(target,BLANK);self.write(target,symbol);self.jump(nxt)
            self.mark(nxt);self.move(source,1);self.move(target,1)
        self.counted('TAIL','BITS',bit)
    def digit(self,source,target):
        def outer_in():
            for a in range(2):self.counted('GAP','BETWEEN',lambda a=a:[self.block(source,'Q'+str(a)+str(b)) for b in range(2)])
        self.counted('PRE','OUTER',outer_in);self.require(source,BLANK);self.rewind(source)
        for q in ('Q00','Q01','Q10','Q11'):self.rewind(q)
        def outer_out():
            for a in range(2):self.counted('GAP','BETWEEN',lambda a=a:[self.block('Q'+str(b)+str(a),target) for b in range(2)])
        self.counted('PRE','OUTER',outer_out)
        for q in ('Q00','Q01','Q10','Q11'):self.require(q,BLANK);self.clear(q)
        self.rewind(target)
    def finish(self):
        code=[]
        for op,*a in self.code:
            if op=='jump':a=[self.labels[a[0]]]
            elif op=='test':a[-2:]=[self.labels[x] for x in a[-2:]]
            code.append((op,*a))
        return tuple(code)

def assemble():
    b=Builder();entries={}
    entries['init']=len(b.code)
    for r in PRIVATE:b.require(r,BLANK);b.write(r,LEFT);b.move(r,1)
    b.emit('halt','initialized');entries['run']=len(b.code)
    for r in PRIVATE:b.require(r,BLANK)
    for src,dst in (('A','PRE'),('G','GAP'),('S','TAIL'),('H','SCAN')):b.copy(src,dst,RIGHT)
    # SCAN decremented once before each doubling, yielding max(H-1,0).
    scan,end,work,again=b.fresh(),b.fresh(),b.fresh(),b.fresh();b.mark(scan);b.zero('SCAN',end,work)
    b.mark(work);b.dec('SCAN');b.zero('SCAN',end,again);b.mark(again);b.double('GAP');b.double('TAIL');b.jump(scan);b.mark(end);b.clear('SCAN')
    b.copy('H','REMAIN',RIGHT)
    loops=[b.fresh() for _ in range(3)];ends=[b.fresh() for _ in range(3)]
    b.jump(loops[0])
    for i,(src,dst,next_i) in enumerate((('SOURCE','B0',1),('B0','B1',2),('B1','B0',1))):
        b.mark(loops[i]);work=b.fresh();b.zero('REMAIN',ends[i],work);b.mark(work)
        if i:b.double('PRE');b.half('TAIL')
        b.digit(src,dst)
        if i:b.clear(src)
        b.dec('REMAIN');b.jump(loops[next_i])
    done=b.fresh()
    for i,src in enumerate(('SOURCE','B0','B1')):
        b.mark(ends[i]);b.copy(src,'OUTPUT',BLANK)
        if i:b.clear(src)
        b.jump(done)
    b.mark(done)
    for r in ('PRE','GAP','TAIL','REMAIN'):b.clear(r)
    b.emit('halt','returned');entries['consume']=len(b.code);b.clear('OUTPUT');b.emit('halt','consumed')
    entries['install']=len(b.code);b.clear('SOURCE');b.copy('OUTPUT','SOURCE',BLANK);b.clear('OUTPUT');b.emit('halt','installed')
    entries['close']=len(b.code)
    for r in PRIVATE:b.require(r,BLANK);b.move(r,-1);b.require(r,LEFT);b.write(r,BLANK);b.move(r,1)
    b.emit('halt','closed');b.mark('reject');b.emit('halt','rejected')
    return b.finish(),entries
