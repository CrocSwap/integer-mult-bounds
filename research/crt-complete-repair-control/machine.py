"""Fixed finite-symbol executor and source-bound assembly entry point.

Only configuration heads/PC/census are numerical observer data. Runtime
operands are constants, finite symbol registers or fixed product fields.
Apache-2.0; JoyboyBrian with substantial OpenAI Codex assistance.
"""
from pathlib import Path
import types
from collections import Counter

def load(path):
    m=types.ModuleType(path.stem);m.__file__=str(path)
    exec(compile(path.read_bytes(),str(path),'exec'),m.__dict__);return m

def assemble(root):
    p=Path(__file__).parent;cmod=load(p/'compiler.py')
    source={ns:(root/path).read_text() for ns,path in {
        'producer':'research/crt-unary-stencil-producer/producer.py',
        'scanner':'research/crt-dense-guard-scan/machine.py',
        'bridge':'research/crt-mask-repair-bridge/bridge.py'}.items()}
    query=load(root/'research/crt-uniform-rom-query/machine.py')
    service=load(root/'research/crt-paid-key-service/service.py')
    key,_=service.assemble(query,2)
    c=cmod.Compiler(source,key);C=cmod.C;R=cmod.R;stages={}
    def field(v,i):
        reg=c.fresh();c.emit('field',v,i,reg);return R(reg)
    stages['producer']=len(c.code)
    produced=c.call('producer','produce',[*[C(x) for x in ('G','H','K','Y','J','B')],C('Tape')],{})
    work=field(produced,0);stencil=field(produced,1)
    stages['scanner']=len(c.code)
    scanned=c.call('scanner','transduce',[stencil],{})
    counter=field(scanned,0);mask=field(scanned,1)
    roles=[field(work,i) for i in range(4)]
    stages['repair']=len(c.code)
    c.call('bridge','repair',[stencil,mask,counter,C('data'),*roles,C(None),C('increment'),C(None)],{})
    stages['clear_control']=len(c.code)
    for role in c.roles:c.emit('write',C(role),C('_'))
    regs=registers(c.code)
    for r in sorted(regs):c.emit('copy',C(None),r)
    c.emit('halt','accept')
    # Initialize every finite-control register through charged instructions too.
    prefix=[('copy',C(None),r) for r in sorted(regs)]
    prefix += [('write',C(role),C('<')) for role in c.roles]
    shift=len(prefix)
    lowered=[]
    for op,*a in c.code:
        if op=='jump':a[0]+=shift
        elif op=='branch':a[1]+=shift;a[2]+=shift
        lowered.append((op,*a))
    stages={name:pc+shift for name,pc in stages.items()}
    stages['key_sites']=[(a+shift,b+shift) for a,b in c.key_sites]
    return tuple(prefix+lowered),tuple(c.roles),stages

def registers(code):
    found=set()
    def walk(a):
        if isinstance(a,tuple):
            if len(a)==2 and a[0]=='r':found.add(a[1])
            else:
                for x in a:walk(x)
    for op,*a in code:
        for x in a:walk(x)
        if op in ('read','copy','not','record'):found.add(a[-1])
        elif op in ('field','eq','ne','in','notin','xorbit','andbit','orbit'):found.add(a[-1])
    return found

def execute(code,tapes,max_steps=1000000000,observe=None):
    heads={r:0 for r in tapes};regs={r:None for r in registers(code)};pc=0;steps=0;cell=0
    def val(a):
        if a[0]=='c':return a[1]
        if a[0]=='r':return regs[a[1]]
        if a[0]=='tuple':return tuple(val(x) for x in a[1])
        raise ValueError('invalid operand')
    while steps<max_steps:
        if observe is not None and pc in observe:observe[pc](pc,tapes,heads,regs,steps,cell)
        op,*a=code[pc];steps+=1;pc+=1
        if op=='read':
            role=val(a[0]);regs[a[1]]=tapes[role][heads[role]];cell+=1
        elif op=='write':
            role=val(a[0]);tapes[role][heads[role]]=val(a[1]);cell+=1
        elif op=='move':
            role=val(a[0]);heads[role]+=val(a[1]);cell+=1
            if heads[role]<0:raise ValueError('left-boundary crossing')
            if heads[role]==len(tapes[role]):tapes[role].append('_')
        elif op=='copy':regs[a[1]]=val(a[0])
        elif op=='not':regs[a[1]]=not val(a[0])
        elif op=='field':regs[a[2]]=val(a[0])[a[1]]
        elif op=='record':
            x=val(a[0]);regs[a[1]]=isinstance(x,tuple) and len(x)==2 and x[0]=='R' and isinstance(x[1],int) and 0<=x[1]<4096
        elif op=='eq':regs[a[2]]=val(a[0])==val(a[1])
        elif op=='ne':regs[a[2]]=val(a[0])!=val(a[1])
        elif op=='in':regs[a[2]]=val(a[0]) in val(a[1])
        elif op=='notin':regs[a[2]]=val(a[0]) not in val(a[1])
        elif op=='xorbit':regs[a[2]]='1' if (val(a[0])=='1')!=(val(a[1])=='1') else '0'
        elif op=='andbit':regs[a[2]]='1' if val(a[0])=='1' and val(a[1])=='1' else '0'
        elif op=='orbit':regs[a[2]]='1' if val(a[0])=='1' or val(a[1])=='1' else '0'
        elif op=='branch':pc=a[1] if val(a[0]) else a[2]
        elif op=='jump':pc=a[0]
        elif op=='halt':return dict(status=a[0],steps=steps,cell_actions=cell,heads=heads,registers=regs)
        else:raise ValueError('unknown instruction '+op)
    raise ValueError('observer watchdog exceeded')

def control_bound(code):
    """Longest control-only CFG path, cutting at every charged cell operation.

    Explicit cycle rejection is essential. The bound then holds on every
    executed finite path, not just the observed accepting trace.
    """
    edges=[]
    for pc,(op,*a) in enumerate(code):
        if op in ('read','write','move','halt'):out=[]
        elif op=='jump':out=[a[0]]
        elif op=='branch':out=[a[1],a[2]]
        else:out=[pc+1]
        if any(not isinstance(i,int) or not 0<=i<len(code) for i in out):raise ValueError('static CFG target')
        edges.append(out)
    indegree=[0]*len(code)
    for out in edges:
        for i in out:indegree[i]+=1
    queue=[i for i,n in enumerate(indegree) if n==0];length=[1]*len(code);visited=0
    while queue:
        p=queue.pop();visited+=1
        for q in edges[p]:
            length[q]=max(length[q],length[p]+1);indegree[q]-=1
            if not indegree[q]:queue.append(q)
    if visited!=len(code):raise ValueError('unbounded control-only cycle')
    return max(length)


def prepare(roles,borrowed):
    expected={'G','H','K','Y','J','B','data','rom'}
    if set(borrowed)!=expected or len({id(v) for v in borrowed.values()})!=len(expected):
        raise ValueError('exact distinct borrowed roles required')
    tapes={r:['_'] for r in roles}
    tapes.update({'key_'+r:['_'] for r in ('h','s','offset','target','out','count','col','row','limit','u','t','y')})
    tapes.update(borrowed)
    return tapes
