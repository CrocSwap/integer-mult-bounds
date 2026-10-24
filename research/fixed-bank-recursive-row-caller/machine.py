"""Fixed-bank recursive refinement of the retained complete-row programs.
JoyboyBrian, substantial OpenAI Codex assistance; Apache-2.0.
Only local tape symbols and a finite phase control execution.
"""
from pathlib import Path
import importlib.util,sys
SOURCE,OUTPUT,GUIDE,ROLE0,ROLE1,IO,PARK,TEMP,CONT=range(9)
B,Z,O,L='_','0','1','|'
def need(ok,msg):
    if not ok:raise ValueError(msg)
def load(root):
    path=root/'research/literal-complete-row-parking-caller/caller.py'
    spec=importlib.util.spec_from_file_location('retained_row_caller',path)
    c=importlib.util.module_from_spec(spec);sys.modules[spec.name]=c
    exec(compile(path.read_bytes(),str(path),'exec'),c.__dict__)
    m,rows,push,pop=c.dependencies(root)
    return c,m,rows,push,pop

def leaf_program(Builder):
    a=Builder();a.mark('loop');a.read(SOURCE,{Z:'zero',O:'one',B:'end'})
    for bit,name in ((O,'zero'),(Z,'one')):
        a.mark(name);a.read(OUTPUT,{B:name+'empty'});a.mark(name+'empty')
        a.write(OUTPUT,bit);a.move(SOURCE,1);a.move(OUTPUT,1);a.go('loop')
    a.mark('end');a.rewind(SOURCE);a.rewind(OUTPUT);a.code.append(('done',))
    a.mark('reject');a.code.append(('reject',));a.mark('quarantine');a.code.append(('reject',))
    return a.finish()

class Machine:
    def __init__(self,root,tapes,leaf=None):
        need(len(tapes)==9 and len(set(map(id,tapes)))==9,'nine distinct fixed ports')
        self.c,self.m,self.rows,self.push,self.pop=load(root)
        self.t=tuple(tapes);self.split=self.c.compile_router(self.rows.Builder)
        self.merge=self.c.compile_router(self.rows.Builder,True)
        self.leaf=leaf if leaf is not None else leaf_program(self.rows.Builder)
        self.boundaries=tuple(self.m.boundary_program(2,a) for a in (0,1))
        self.steps=0;self.nodes=0;self.leaves=0;self.used=False
    def read(self,i):self.steps+=1;return self.t[i].read()
    def act(self,i,s=None,d=0):self.steps+=1;self.t[i].perform((s,d))
    def rewind(self,i):
        self.act(i,d=-1)
        while self.read(i)!=L:self.act(i,d=-1)
        self.act(i,d=1)
    def classify(self):
        need(self.read(GUIDE)==O,'positive unary guide')
        while self.read(GUIDE)==O:
            need(self.read(SOURCE) in (Z,O),'complete nonempty leaf row')
            self.act(GUIDE,d=1);self.act(SOURCE,d=1)
        need(self.read(GUIDE)==B,'unary guide')
        leaf=self.read(SOURCE)==B
        self.rewind(SOURCE);self.rewind(GUIDE)
        return leaf
    def erase(self,i):
        while self.read(i) in (Z,O):self.act(i,B,1)
        need(self.read(i)==B,'bit-stream erase');self.rewind(i)
    def primitive(self,phase,role):
        t=self.t;m=self.m
        if phase=='push':self.steps+=m.run_table(self.push,'copy',[t[ROLE0+role],t[PARK]],(0,))
        elif phase=='move_in':self.steps+=m.run_move(t[ROLE0+role],t[IO])
        elif phase=='move_out':self.steps+=m.run_move(t[IO],t[ROLE0+role])
        elif phase=='pop':self.steps+=m.run_table(self.pop,'enterDelimiter',[t[PARK],t[TEMP],t[ROLE0+role]],(0,1,2))
        else:raise ValueError('boundary phase')
    def run(self):
        need(not self.used,'single invocation');self.used=True
        # q/active/pc range over a fixed finite set. Saved return information is
        # one actual bit per active ancestor on CONT, not a Python frame/list.
        q='enter';active=pc=0
        while True:
            self.steps+=1 # stationary finite dispatch
            if q=='enter':
                self.nodes+=1
                if self.classify():
                    self.leaves+=1;self.steps+=self.c.run_router(self.leaf,self.t);q='return'
                else:
                    self.steps+=self.c.run_router(self.split,self.t);active=pc=0;q='boundary'
            elif q=='boundary':
                if pc==5:
                    if active==0:active=1;pc=0
                    else:self.steps+=self.c.run_router(self.merge,self.t);q='return'
                    continue
                phase,role=self.boundaries[active][pc]
                if phase!='child':self.primitive(phase,role);pc+=1;continue
                # Boundary has already parked the inactive role. Push parent's
                # borrowed SOURCE above it, then reuse its physical port.
                self.steps+=self.m.run_table(self.push,'copy',[self.t[SOURCE],self.t[PARK]],(0,))
                need(self.read(CONT)==B,'empty continuation top')
                self.act(CONT,Z if active==0 else O,1)
                self.steps+=self.m.run_move(self.t[IO],self.t[SOURCE]);q='enter'
            elif q=='return':
                self.act(CONT,d=-1);saved=self.read(CONT)
                if saved==L:
                    self.act(CONT,d=1)
                    return {'steps':self.steps,'nodes':self.nodes,'leaves':self.leaves}
                need(saved in (Z,O),'return continuation')
                self.act(CONT,B)
                active=0 if saved==Z else 1
                # Child SOURCE is an owned transferred copy, unlike the root.
                self.erase(SOURCE)
                self.steps+=self.m.run_move(self.t[OUTPUT],self.t[IO])
                self.steps+=self.m.run_table(self.pop,'enterDelimiter',[self.t[PARK],self.t[TEMP],self.t[SOURCE]],(0,1,2))
                pc=3;q='boundary'
            else:raise ValueError('phase')
