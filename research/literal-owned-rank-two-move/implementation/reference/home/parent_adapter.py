"""Paid six-Gamma||DATA ABI for actual MOVE24472. Apache-2.0; Codex-assisted.

Python constructors run only offline. Runtime is local Graph transitions.
"""
from functools import cache
from hashlib import sha256
import importlib.util
from pathlib import Path
import sys
import json

HERE=Path(__file__).resolve().parent
sys.dont_write_bytecode=True
sys.pycache_prefix=str(HERE/'_unwritten_bytecode_cache')
if Path(sys.pycache_prefix).exists():
    raise ValueError('bytecode isolation path must remain absent')
NATIVE=HERE/'inputs/native'
B1=HERE/'inputs/dispatch/tape_graph.py'
for pin in json.loads((HERE/'SOURCES.json').read_text())['files']:
    raw=(HERE/pin['local']).read_bytes()
    if len(raw)!=pin['bytes'] or sha256(raw).hexdigest()!=pin['sha256']:
        raise ValueError('frozen source drift: '+pin['local'])


def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);sys.modules[name]=module
    spec.loader.exec_module(module)
    return module


if sha256(B1.read_bytes()).hexdigest()!='7d3cee3e79ba5fe410e1a6b5f4cf6a2fbe5e274f838b798cd8860344ff258b54':
    raise ValueError('B1 graph source drift')
D=load('home_move_dispatch',B1)
C=load('home_move_native',NATIVE/'move.py')
CORE_BASE,GUIDE,TAPES=3,34,35
HOME_OWNERS=(('native-occurrence',24472,415),('parked-source',0))


@cache
def core():
    code,alphabet=C.compile_move()
    if len(code)!=82813 or alphabet!=('_','0','1','|'):
        raise ValueError('changed actual selected table')
    return code


def steps(g,tape,count,target):
    for _ in range(abs(count)):
        target=g.jump(target,((tape,1 if count>0 else -1),))
    return target


def copy_out(g,source,target,after):
    state=g.state('repack')
    g.add(state,after,tests=((source,'_'),))
    for bit in '01':
        g.add(state,state,tests=((source,bit),),writes=((target,bit),(source,'_')),
              moves=((source,1),(target,1)))
    return state


def embed(g,code,after):
    labels=[g.state('MOVE24472') for _ in code]
    for pc,(op,*args) in enumerate(code):
        state=labels[pc];g.rules.setdefault(state,[])
        nxt=labels[pc+1] if pc+1<len(code) else after
        if op=='read':
            for symbol,destination in args[1].items():
                g.add(state,labels[destination],tests=((CORE_BASE+args[0],symbol),))
        elif op=='write':
            g.add(state,nxt,writes=((CORE_BASE+args[0],args[1]),))
        elif op=='move':
            if args[1] not in (-1,1):raise ValueError('nonlocal core instruction')
            g.add(state,nxt,moves=((CORE_BASE+args[0],args[1]),))
        elif op=='goto':g.add(state,labels[args[0]])
        elif op=='halt':g.add(state,after)
        else:raise ValueError('nonliteral retained operation')
    return labels[0]


def primitive(g,name,arity,after,*,mutation=None,parser_only=False,stages=None):
    if name!='MOVE24472' or arity!=1:raise ValueError('only unary actual MOVE24472')
    stages={} if stages is None else stages
    h,data=CORE_BASE,CORE_BASE+1
    offset=1 if mutation=='guard_offset' else 2
    stages['primitive_return']=after
    cleanup=after
    for tape in range(CORE_BASE+30,CORE_BASE+1,-1):
        cleanup=steps(g,tape,-offset,cleanup)
    cleanup=g.rewind(data,cleanup);cleanup=g.rewind(h,cleanup);cleanup=g.rewind(1,cleanup)
    check=g.state('outside-delimiter')
    g.add(check,cleanup,tests=((1,'|'),))
    out_data=copy_out(g,data,1,check)
    out_header=out_data if mutation=='drop_header_return' else copy_out(g,h,1,out_data)
    post=g.jump(out_header,((1,1),))
    stages['core_return']=post
    entry=post if parser_only else embed(g,core(),post)
    stages['core_entry']=entry
    ready=g.rewind(1,entry);ready=g.rewind(GUIDE,ready)
    for tape in (data,h):
        ready=g.rewind(tape,steps(g,tape,offset,ready))
    incoming=g.state('complete-DATA')
    g.add(incoming,ready,tests=((1,'|'),))
    for bit in '01':
        g.add(incoming,incoming,tests=((1,bit),),writes=((data,bit),),moves=((1,1),(data,1)))
    nxt=incoming
    # GUIDE counts prefix zeros, never Gamma numerical values.
    for field in range(5,-1,-1):
        prefix=g.state('gamma-prefix');pop=g.state('gamma-pop');suffix=g.state('gamma-suffix')
        g.add(prefix,prefix,tests=((1,'0'),),writes=((h,'0'),(GUIDE,'1')),
              moves=((1,1),(h,1),(GUIDE,1)))
        g.add(prefix,pop,tests=((1,'1'),),writes=((h,'1'),),moves=((1,1),(h,1),(GUIDE,-1)))
        g.add(pop,nxt,tests=((GUIDE,'^'),),moves=((GUIDE,1),))
        g.add(pop,suffix,tests=((GUIDE,'1'),),writes=((GUIDE,'_'),),moves=((GUIDE,-1),))
        for bit in '01':
            g.add(suffix,pop,tests=((1,bit),),writes=((h,bit),),moves=((1,1),(h,1)))
        nxt=prefix
    start=g.jump(nxt,((1,1),(GUIDE,1)))
    for tape in range(CORE_BASE+30,CORE_BASE-1,-1):start=steps(g,tape,offset,start)
    stages['adapter_entry']=start
    return start


def compile_home(*,selected=0,mutation=None,parser_only=False):
    from collections import namedtuple
    Event=namedtuple('Event','service owners');stages={}
    install=lambda g,n,a,k:primitive(g,n,a,k,mutation=mutation,parser_only=parser_only,stages=stages)
    graph=D.compile_graph((Event('MOVE24472',(HOME_OWNERS[selected],)),),HOME_OWNERS,
                          primitive=install,productive_count=2)
    return graph,stages
