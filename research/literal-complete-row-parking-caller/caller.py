"""Eight-port complete-row caller; retained parking and local control primitives.

JoyboyBrian, with substantial OpenAI Codex assistance. Apache-2.0.
Runtime decisions inspect only local symbols. Diagnostics are outside control.
"""
from pathlib import Path
import importlib.util
import sys

SOURCE,OUTPUT,GUIDE,ROLE0,ROLE1,IO,PARK,TEMP=range(8)
PORTS=8
B,Z,O,L='_','0','1','|'

def need(ok,message):
    if not ok:raise ValueError(message)

def source_module(root,relative,name):
    spec=importlib.util.spec_from_file_location(name,root/relative)
    module=importlib.util.module_from_spec(spec)
    sys.modules[name]=module
    # Execute exact source, never a stale bytecode cache.
    exec(compile((root/relative).read_bytes(),str(root/relative),'exec'),module.__dict__)
    return module

def dependencies(root):
    m=source_module(root,'research/recursive-parking-boundary/machine.py','parking_source')
    rows=source_module(root,'research/bit-row-padding-physical/machine.py','row_builder_source')
    path=root/'research/machine-transfer-verification/transfer-proof/tapes'
    push=m.parse_instruction_table((path/'TapeStackPush.lean').read_text(),m.PUSH_MODES,('source',),2)
    pop=m.parse_instruction_table((path/'TapeStack.lean').read_text(),m.POP_MODES,('park','temp','out'),3)
    return m,rows,push,pop

def compile_router(Builder,merge=False):
    a=Builder()
    # Caller-owned markers at -1; guards are literal three-instruction probes.
    for t in (SOURCE,OUTPUT,GUIDE,ROLE0,ROLE1):a.boundary(t)
    a.read(GUIDE,{O:'guide_positive'});a.mark('guide_positive')
    # Positive even number of complete rows is the admitted input domain.
    first=ROLE0 if merge else SOURCE
    a.read(first,{Z:'start',O:'start'});a.mark('start')
    a.go('row0')
    for role in (0,1):
        src=(ROLE0+role) if merge else SOURCE
        dst=OUTPUT if merge else (ROLE0+role)
        a.mark('row'+str(role))
        entries={Z:'payload'+str(role),O:'payload'+str(role)}
        if role==0:entries[B]='end'
        a.read(src,entries)
        a.mark('payload'+str(role))
        loop='loop'+str(role);a.mark(loop)
        a.read(GUIDE,{O:'bit'+str(role),B:'row_done'+str(role)})
        a.mark('bit'+str(role))
        a.read(src,{Z:'zero'+str(role),O:'one'+str(role)})
        for bit,name in ((Z,'zero'),(O,'one')):
            a.mark(name+str(role))
            good=a.fresh('empty')
            a.read(dst,{B:good});a.mark(good)
            a.write(dst,bit)
            if merge:a.write(src,B)
            a.move(src,1);a.move(dst,1);a.move(GUIDE,1);a.go(loop)
        a.mark('row_done'+str(role))
        a.rewind(GUIDE)
        a.go('row'+str(1-role))
    a.mark('end')
    if merge:
        a.read(ROLE1,{B:'equal_end'});a.mark('equal_end')
    for t in ((ROLE0,ROLE1,OUTPUT) if merge else (SOURCE,ROLE0,ROLE1)):a.rewind(t)
    a.code.append(('done',))
    a.mark('reject');a.code.append(('reject',))
    a.mark('quarantine');a.code.append(('reject',))
    return a.finish()

def run_router(code,tapes,budget=None):
    pc=steps=0
    while True:
        need(budget is None or steps<budget,'router budget')
        op,*args=code[pc];steps+=1;pc+=1
        if op=='done':return steps
        if op=='reject':raise ValueError('row interface rejected')
        if op=='goto':pc=args[0]
        elif op=='read':pc=args[1][tapes[args[0]].read()]
        elif op=='write':tapes[args[0]].perform((args[1],0))
        elif op=='move':tapes[args[0]].perform((None,args[1]))
        else:raise ValueError('invalid router opcode')

class Caller:
    def __init__(self,root,tapes):
        need(len(tapes)==PORTS and len(set(map(id,tapes)))==PORTS,'distinct eight physical ports')
        self.m,self.rows,self.push,self.pop=dependencies(root)
        self.tapes=tuple(tapes)
        self.identities=tuple(map(id,tapes))
        self.work=self.m.Workspace([tapes[ROLE0],tapes[ROLE1]],tapes[PARK],tapes[IO],tapes[TEMP])
        self.split=compile_router(self.rows.Builder)
        self.merge=compile_router(self.rows.Builder,True)
        self.phase='new'
    def bindings(self):
        ports=(*self.work.roles,self.work.io,self.work.parking,self.work.temporary)
        expected=(self.tapes[ROLE0],self.tapes[ROLE1],self.tapes[IO],self.tapes[PARK],self.tapes[TEMP])
        need(tuple(map(id,ports))==tuple(map(id,expected)),'workspace port binding')
    def run(self,children):
        need(self.phase=='new','caller single use')
        need(len(set(map(id,self.tapes)))==PORTS,'distinct eight physical ports')
        need(len(children)==2,'two fixed child entries')
        self.bindings()
        self.phase='split';split=run_router(self.split,self.tapes)
        counts=[]
        for active in (0,1): # Fixed compile-time two-boundary program.
            self.phase='child'+str(active)
            def bound_child(work):
                children[active](work)
                self.bindings() # Structural ABI check, not a semantic tape oracle.
            counts.append(self.m.boundary(self.work,active,bound_child,self.push,self.pop,check_contract=False))
        self.phase='merge';merge=run_router(self.merge,self.tapes)
        self.phase='done'
        # Fixed split->boundary0->boundary1->merge->done control edges.
        return {'split':split,'boundary':[x['total'] for x in counts],'merge':merge,'dispatch':4,
                'wrapper':split+sum(x['total'] for x in counts)+merge+4}
