"""Borrow immutable Gamma6 HEADER; DATA-only B1 HOME. Offline constructors.
Apache-2.0; prepared with substantial OpenAI Codex assistance.
"""
from pathlib import Path
from hashlib import sha256
from functools import cache
import atexit
import importlib.util
import json
import sys
import tempfile

HERE = Path(__file__).resolve().parent
_cache = tempfile.TemporaryDirectory(prefix='borrowed-header-import-')
atexit.register(_cache.cleanup)
sys.dont_write_bytecode = True
sys.pycache_prefix = str(Path(_cache.name)/'required-absent')
if Path(sys.pycache_prefix).exists():
    raise ValueError('cache isolation prefix must be absent')
CORE = HERE/'inputs/core'
freeze = (CORE/'FREEZE.json').read_bytes()
if sha256(freeze).hexdigest() != '5735c401ba981a7af4d3a146eb047d04fa0c87dbf7ed49bd82dc57df8d6cb2ef':
    raise ValueError('generic positive freeze drift')
for pin in json.loads(freeze)['files']:
    raw = (CORE/pin['path']).read_bytes()
    if len(raw) != pin['bytes'] or sha256(raw).hexdigest() != pin['sha256']:
        raise ValueError('frozen generic source drift: '+pin['path'])

def load(name,path):
    spec = importlib.util.spec_from_file_location(name,path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module

C = load('borrowed_positive_core',CORE/'join.py')
D = C.load('borrowed_home_dispatch',CORE/'reference/rank2/reference/home/tape_graph.py')
DATA, LAST, TAPES = 4,33,34
OWNERS = (('parked-productive',0),('supplied-native-data',0))

@cache
def core(rank):
    code, alphabet, entries = C.compile_join(rank)
    pin = next(x for x in json.loads((CORE/'SOURCE-BINDING.json').read_text())['core_tables'] if x['rank'] == rank)
    if alphabet != ('_','0','1','|') or len(code) != pin['locations'] or sha256(repr(code).encode()).hexdigest() != pin['sha256']:
        raise ValueError('actual generic native table drift')
    if any(op == 'write' and args[0] == 0 for op,*args in code):
        raise ValueError('borrowed HEADER must be immutable')
    return code

def step(g,tape,count,target):
    for _ in range(abs(count)):
        target = g.jump(target,((tape,1 if count>0 else -1),))
    return target

def embed(g,code,after,header_tape):
    labels = [g.state('POSITIVE') for _ in code]
    port = lambda t: header_tape if t == 0 else 3+t
    for pc,(op,*args) in enumerate(code):
        state = labels[pc]
        g.rules.setdefault(state,[])
        nxt = labels[pc+1] if pc+1<len(code) else after
        if op == 'read':
            for symbol,destination in args[1].items():
                g.add(state,labels[destination],tests=((port(args[0]),symbol),))
        elif op == 'write':
            g.add(state,nxt,writes=((port(args[0]),args[1]),))
        elif op == 'move':
            if args[1] not in (-1,1):
                raise ValueError('nonlocal native move')
            g.add(state,nxt,moves=((port(args[0]),args[1]),))
        elif op == 'goto':
            g.add(state,labels[args[0]])
        elif op == 'halt':
            g.add(state,after)
        else:
            raise ValueError('nonliteral native operation')
    return labels[0]

def primitive(g,name,arity,after,*,rank,header_tape=3,mutation=None,stages=None):
    C.fixed_rank(rank)
    if arity != 1 or type(header_tape) is not int or header_tape < 3 or DATA<=header_tape<=LAST:
        raise ValueError('distinct borrowed header and fixed native owners')
    stages = {} if stages is None else stages
    stages['primitive_return'] = after
    offset = 1 if mutation == 'guard_offset' else 2
    cleanup = after
    cleanup = step(g,header_tape,-1,cleanup)
    for t in range(LAST,DATA,-1):
        cleanup = step(g,t,-offset,cleanup)
    cleanup = g.rewind(DATA,cleanup)
    cleanup = g.rewind(1,cleanup)
    out = g.state('DATA-only-return')
    g.add(out,cleanup,tests=((1,'|'),(DATA,'_')))
    for old in '01':
        for new in '01':
            g.add(out,out,tests=((1,old),(DATA,new)),writes=((1,new),(DATA,'_')),
                  moves=((1,1),(DATA,1)))
    post = g.jump(out,((1,1),)+(((DATA,1),) if mutation == 'drop_return_bit' else ()))
    if mutation == 'skip_return':
        post = g.jump(after)
    stages['core_return'] = post
    native = embed(g,core(rank),post,header_tape)
    stages['core_entry'] = native
    ready = g.rewind(1,native)
    ready = g.rewind(DATA,step(g,DATA,offset,ready))
    incoming = g.state('DATA-only-clone')
    g.add(incoming,ready,tests=((1,'|'),(DATA,'_')))
    for bit in '01':
        g.add(incoming,incoming,tests=((1,bit),),writes=((DATA,bit),),moves=((1,1),(DATA,1)))
    start = g.jump(incoming,((1,1),(header_tape,1)))
    for t in range(LAST,DATA-1,-1):
        start = step(g,t,offset,start)
    stages['adapter_entry'] = start
    return start

def compile_home(rank,*,header_tapes=(3,),selected=1,mutation=None):
    from collections import namedtuple
    if not header_tapes or selected not in (0,1):
        raise ValueError('nonempty fixed service list and actual HOME index')
    Event = namedtuple('Event','service owners')
    choices = {str(i):t for i,t in enumerate(header_tapes)}
    stages = {i:{} for i in range(len(header_tapes))}
    def install(g,n,a,k):
        return primitive(g,n,a,k,rank=rank,header_tape=choices[n],mutation=mutation,stages=stages[int(n)])
    events = tuple(Event(str(i),(OWNERS[selected],)) for i in range(len(header_tapes)))
    graph = D.compile_graph(events,OWNERS,primitive=install,productive_count=1)
    graph.start = graph.execution_start
    # The supplied entry is already reserved, as in the frozen parent's HOME
    # fixture. Its unreachable reservation prefix is not executed on HEADER3.
    pending=[graph.start];seen=set()
    while pending:
        state=pending.pop()
        if state in seen or state=='HALT':continue
        seen.add(state)
        for rule in graph.rules[state]:
            if any(t in header_tapes for t,_ in rule.writes):
                raise ValueError('reachable borrowed HEADER write')
            pending.append(rule.target)
    return graph,stages
