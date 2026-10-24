"""Complete private query stream, on the retained records.Tape symbol ABI.

JoyboyBrian with OpenAI Codex assistance. Apache-2.0.
Finite counter and assembler macros retain David Arias / PR2776 credit.
"""
import importlib.util
from pathlib import Path
import sys

X,Y,Z,WD,MD,W,M,T = range(8)
# Actual retained records/words alphabet: binary0/1, LEFT2, RIGHT3, BLANK4.
ZERO,ONE,LEFT,RIGHT,BLANK,UNIT,MARK = range(7)

def need(ok, message):
    if not ok:
        raise ValueError(message)

def macros(root):
    folder = Path(root)/'research/fixed-tape-ordered-shear'
    saved = {name:sys.modules.get(name) for name in ('machine','counters')}
    loaded = []
    try:
        for name in ('machine','counters'):
            spec=importlib.util.spec_from_file_location(name,folder/(name+'.py'))
            module=importlib.util.module_from_spec(spec)
            sys.modules[name]=module
            spec.loader.exec_module(module)
            loaded.append(module)
        return tuple(loaded)
    finally:
        for name,value in saved.items():
            if value is None:sys.modules.pop(name,None)
            else:sys.modules[name]=value

def build(root):
    machine,counters=macros(root)
    # Compile in the credited macro alphabet, then rename symbols bijectively.
    B,L,R,ZERO_,ONE_,U,_=range(7)
    symbol_map={B:BLANK,L:LEFT,R:RIGHT,ZERO_:ZERO,ONE_:ONE,U:UNIT,6:MARK}
    def finish(a):
        rows=[]
        for row in a.finish().instructions:
            if row[0]=='branch':
                row=(row[0],row[1],tuple((symbol_map[s],p) for s,p in row[2]),row[3])
            elif row[0]=='write':row=(row[0],row[1],symbol_map[row[2]])
            rows.append(row)
        return tuple(rows)
    def rewind(a,t):counters.emit_rewind(a,t)
    def check(a,t,s):
        good=a.fresh('check');a.branch(t,{s:good},'reject');a.label(good)
    def component(a,mode):
        loop=a.fresh('bits');done=a.fresh('bits_done')
        a.label(loop);a.branch(W,{U:loop+'body',R:done},'reject');a.label(loop+'body')
        if mode=='clear':
            good=a.fresh('old');a.branch(Z,{ZERO_:good,ONE_:good,B:good},'reject')
            a.label(good);a.write(Z,ZERO_);a.move(Z,1)
        else:
            join=a.fresh('copied')
            a.branch(X,{ZERO_:join+'0',ONE_:join+'1'},'reject')
            for bit in (ZERO_,ONE_):
                a.label(join+str(bit-ZERO_));a.write(Z,bit);a.goto(join)
            a.label(join);a.move(X,1);a.move(Z,1)
        a.move(W,1);a.goto(loop);a.label(done);rewind(a,W)
    def entry(a):
        for tape in range(8):
            a.move(tape,-1);check(a,tape,L);a.move(tape,1)
    a=machine.Assembler(8)
    entry(a)
    for tape in (W,M,T):check(a,tape,B)
    counters.emit_binary_to_unary(a,WD,T,W)
    counters.emit_binary_to_unary(a,MD,T,M)
    for mode in ('clear','copy'):
        loop=a.fresh(mode);done=a.fresh(mode+'_done')
        a.label(loop);a.branch(M,{U:loop+'body',R:done},'reject');a.label(loop+'body')
        component(a,mode);component(a,mode)
        a.move(M,1);a.goto(loop);a.label(done)
        check(a,Z,B);rewind(a,Z);rewind(a,M)
        if mode=='copy':check(a,X,B);rewind(a,X)
    a.halt();a.label('reject');a.reject('prepare field/descriptor shape')
    prepare=finish(a)
    a=machine.Assembler(8)
    entry(a)
    def add_component():
        tag=a.fresh('add');done=tag+'done';a.goto(tag+'c0')
        for carry in (0,1):
            a.label(tag+'c'+str(carry))
            for av in (0,1):
                label=tag+str(carry)+str(av)
                if av==0:a.branch(Z,{ZERO_:label,ONE_:tag+str(carry)+'1'},'reject')
                a.label(label)
                a.branch(Y,{ZERO_:label+'0',ONE_:label+'1'},'reject')
                for bv in (0,1):
                    sub=label+str(bv);value=av+bv+carry;out=value%2
                    a.label(sub);a.move(W,1)
                    a.branch(W,{U:sub+'more',R:sub+'last'},'reject')
                    a.label(sub+'more');a.write(Y,ZERO_+out);a.move(Y,1);a.move(Z,1)
                    a.goto(tag+'c'+str(value//2))
                    a.label(sub+'last')
                    if av==bv and out!=av:a.goto('overflow')
                    else:
                        a.write(Y,ZERO_+out);a.move(Y,1);a.move(Z,1);a.goto(done)
        a.label(done);rewind(a,W)
    loop=a.fresh('records');done=a.fresh('added')
    a.label(loop);a.branch(M,{U:loop+'body',R:done},'reject');a.label(loop+'body')
    add_component();add_component();a.move(M,1);a.goto(loop);a.label(done)
    check(a,Y,B);check(a,Z,B);rewind(a,Y);rewind(a,Z);rewind(a,M)
    for tape,end in ((Z,B),(W,R),(M,R)):
        loop=a.fresh('erase');done=a.fresh('erased')
        a.label(loop);a.branch(tape,{end:done},loop+'body');a.label(loop+'body')
        a.write(tape,B);a.move(tape,1);a.goto(loop);a.label(done)
        if end==R:a.write(tape,B)
        rewind(a,tape)
    a.halt();a.label('reject');a.reject('return field shape')
    a.label('overflow');a.reject('signed addition overflow')
    return prepare,finish(a)

class Invocation:
    """One pre-reserved eight-port invocation; child work is an external contract."""
    def __init__(self,ports,tables):
        need(len(ports)==8 and len({id(t) for t in ports})==8,'distinct invocation ports')
        self.ports=ports;self.tables=tables;self.state='new';self.steps=0
        self.identities=tuple(id(t) for t in ports)
    def execute(self,table):
        need(tuple(id(t) for t in self.ports)==self.identities,'fixed physical ports across child')
        pc=0
        while True:
            row=table[pc];op=row[0];self.steps+=1
            if op=='halt':return
            if op=='reject':raise ValueError(row[1])
            if op=='goto':pc=row[1];continue
            tape=self.ports[row[1]]
            if op=='branch':pc=dict(row[2]).get(tape.read(),row[3]);continue
            if op=='write':tape.write(row[2])
            elif op=='move':tape.step(row[2])
            else:raise ValueError('unknown finite opcode')
            pc+=1
    def prepare(self):
        need(self.state=='new','prepare once')
        self.state='preparing'
        self.execute(self.tables[0]);self.state='waiting'
    def finish(self):
        need(self.state=='waiting','complete outstanding child first')
        self.state='resuming'
        self.execute(self.tables[1]);self.state='done'


class SuspendedPair:
    """Two independent parent slots; their private and borrowed ports cannot alias."""
    def __init__(self,first,second,tables):
        need(len(first)==len(second)==8,'two fixed parent slots')
        need(len({id(t) for t in (*first,*second)})==16,'distinct suspended parent slots')
        self.first=Invocation(first,tables)
        self.second=Invocation(second,tables)
