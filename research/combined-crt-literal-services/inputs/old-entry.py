"""Guide-driven CRT numerical entry; no host width or bulk word constructor.
JoyboyBrian with substantial OpenAI Codex assistance. Apache-2.0.
"""
from types import SimpleNamespace

class Port:
    def __init__(self,w):
        self.w=w;self.cells=bytearray([w.BLANK]);self.head=0;self.meter=w.Meter()
        self.write(w.LEFT);self.step(1)
    def read(self):
        self.meter.reads+=1
        return self.cells[self.head] if self.head<len(self.cells) else self.w.BLANK
    def write(self,v):
        self.w.need(v in range(14),'finite record symbol');self.meter.writes+=1
        if self.head==len(self.cells):self.cells.append(v)
        else:self.cells[self.head]=v
    def step(self,d):
        self.w.need(d in (-1,1) and self.head+d>=0,'unit local movement')
        self.head+=d;self.meter.moves+=1
    def append(self,v):
        self.w.need(self.read()==self.w.BLANK,'append blank');self.write(v);self.step(1)
    def rewind(self):
        self.step(-1)
        while self.read()!=self.w.LEFT:self.step(-1)
        self.step(1)
    def clear(self):
        self.rewind()
        while self.read()!=self.w.BLANK:self.write(self.w.BLANK);self.step(1)
        self.rewind()
    def retire(self):
        self.clear();self.step(-1);self.write(self.w.BLANK);self.step(1)

class Extent:
    """An encoded width value. Only the source's literal >=4 observation exists."""
    def __init__(self,guide,w):self.guide,self.w=guide,w
    def __ge__(self,constant):
        self.w.need(type(constant) is int and constant==4,'audited width observation')
        good=True;g=self.guide
        for _ in range(4):
            if g.read()!=self.w.ONE:good=False;break
            g.step(1)
        g.rewind();return good
    def __int__(self):raise ValueError('runtime width decode forbidden')

class Entry:
    def __init__(self,w,r,guide,dirty):
        w.need(len(dirty)==8 and len({id(x) for x in [guide,*dirty]})==9,'eight distinct dirty ports')
        self.w,self.r,self.guide,self.dirty=w,r,guide,tuple(dirty);self.owned=[];self.control=0;self.closed=False
        width=Extent(guide,w);w.need(width>=4,'encoded width at least four')
        a=object.__new__(w.Arena);a.bits=width;a.capacity=64;a.meter=w.Meter()
        a.words=[];a.available=list(reversed(range(8,64)));a.live=set(range(8));self.arena=a
        class HostedWord(w.Word):
            @property
            def cells(self):return self.port.cells
            @property
            def head(self):return self.port.head
            @head.setter
            def head(self,value):self.port.head=value
        def wrap(port,slot):
            word=object.__new__(HostedWord);word.arena=a;word.slot=slot;word.port=port;return word
        for slot in range(64):
            self.control+=1
            if slot<8:port=dirty[slot]
            else:port=self.word_storage(False)
            a.words.append(wrap(port,slot))
        a.template=wrap(self.word_storage(True),-1)
        self.left,self.right,self.output=(self.new_port() for _ in range(3));self.output_taken=False
    def new_port(self):
        p=Port(self.w);self.owned.append(p);self.control+=1;return p
    def word_storage(self,template):
        p=self.new_port();g=self.guide;w=self.w
        while g.read()==w.ONE:p.write(w.ZERO if template else w.BLANK);p.step(1);g.step(1)
        w.need(g.read()==w.BLANK,'unary width guide');g.rewind()
        p.write(w.RIGHT if template else w.BLANK);p.rewind();return p
    def pad(self,source,target):
        w,r,g=self.w,self.r,self.guide
        while source.read()!=w.RIGHT:
            w.need(source.read()==r.ROOT,'paired canonical tag');target.append(r.ROOT);source.step(1)
            for _ in range(2):
                seen=False;many=False;last=w.ZERO;ended=False
                while g.read()==w.ONE:
                    if source.read()==r.WORD_END:ended=True
                    if ended:target.append(w.ZERO)
                    else:
                        bit=source.read();w.need(bit in (w.ZERO,w.ONE),'canonical bit')
                        many=seen;seen=True;last=bit;target.append(bit);source.step(1)
                    g.step(1)
                w.need(g.read()==w.BLANK,'unary guide');g.rewind()
                w.need(source.read()==r.WORD_END and seen and (last==w.ONE or not many),'canonical word fits width')
                source.step(1);target.append(r.WORD_END)
            w.need(source.read()==r.RECORD_END,'paired canonical end');source.step(1);target.append(r.RECORD_END)
        target.append(w.RIGHT);target.rewind();source.rewind()
    def output_factory(self):
        self.w.need(not self.output_taken,'one output stream role');self.output_taken=True;return self.output
    def invoke(self,producer,left,right):
        self.w.need(not self.closed,'live context');self.pad(left,self.left);self.pad(right,self.right)
        proxy=SimpleNamespace(**{n:getattr(self.r,n) for n in ('ROOT','RECORD_END','WORD_END','read_word','append_word')},Tape=self.output_factory)
        old=self.w.Word.__init__;old_arena=self.w.Arena.__init__;inspect=self.w.Word.inspect
        def forbidden(*args,**kwargs):raise ValueError('scientific host constructor/decode forbidden')
        self.w.Word.__init__=forbidden;self.w.Arena.__init__=forbidden;self.w.Word.inspect=forbidden
        try:return producer.produce(self.arena,self.left,self.right,self.w,proxy)
        finally:self.w.Word.__init__=old;self.w.Arena.__init__=old_arena;self.w.Word.inspect=inspect
    def consume(self,result):
        self.arena.free_many(result['lower'],result['product']);result['stream'].clear()
        self.left.clear();self.right.clear();self.output_taken=False
    def close(self):
        w=self.w;w.need(not self.closed and self.arena.live==set(range(8)),'terminal numerical owners')
        # Retained private word backing is blank after free; remove its marker.
        for word in self.arena.words[8:]:
            word.rewind();w.need(word.read()==w.BLANK,'retired word body');word.step(-1)
            # Word.write forbids LEFT/marker changes: the owned setup port performs this paid write.
            port=word.port;port.write(w.BLANK);port.step(1)
        self.arena.template.erase()
        template=self.arena.template.port
        template.step(-1);template.write(w.BLANK);template.step(1)
        for p in (self.left,self.right,self.output):p.retire()
        self.closed=True
