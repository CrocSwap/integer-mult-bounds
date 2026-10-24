"""Static four-column ABI bridge; all data operations execute source opcodes.
JoyboyBrian with substantial OpenAI Codex assistance; Apache-2.0.
"""
import ast
import copy
import hashlib
import json
import types
from pathlib import Path

C=lambda x:('c',x)
R=lambda x:('r',x)

class Builder:
    def __init__(self):self.code=[];self.labels={};self.pending=[]
    def emit(self,*op):self.code.append(op)
    def label(self,name):
        if name in self.labels:raise ValueError('duplicate label')
        self.labels[name]=len(self.code)
    def jump(self,name):self.pending.append((len(self.code),1,name));self.emit('jump',None)
    def branch(self,arg,yes,no):
        self.pending.extend(((len(self.code),2,yes),(len(self.code),3,no)))
        self.emit('branch',arg,None,None)
    def finish(self):
        for pc,field,name in self.pending:
            row=list(self.code[pc]);row[field]=self.labels[name];self.code[pc]=tuple(row)
        return tuple(self.code)
    def eq(self,a,b):self.emit('eq',a,C(b),'test')
    def rewind(self,role,marker,name):
        self.label(name);self.emit('read',C(role),'symbol');self.eq(R('symbol'),marker)
        self.branch(R('test'),name+'_done',name+'_step')
        self.label(name+'_step');self.emit('move',C(role),C(-1));self.jump(name)
        self.label(name+'_done')

def load(path):
    m=types.ModuleType(path.stem);m.__file__=str(path)
    exec(compile(path.read_bytes(),str(path),'exec'),m.__dict__);return m

def source_machine(root):return load(root/'research/crt-complete-repair-control/machine.py')

def assemble(root,repair=True):
    """Compile finite tables and four copies of the unchanged source program."""
    m=source_machine(root);service,roles,source_stages=m.assemble(root)
    b=Builder();stages={};columns=tuple('column'+str(i) for i in range(4))
    for r in ('symbol','test','column','payload'):b.emit('copy',C(None),r)
    b.emit('move',C('raw'),C(-1));b.emit('read',C('raw'),'symbol')
    b.eq(R('symbol'),2);b.branch(R('test'),'input_ok','reject');b.label('input_ok')
    b.emit('move',C('raw'),C(1))
    for col in columns:b.emit('write',C(col),C('<'));b.emit('move',C(col),C(1))
    b.emit('copy',C(columns[0]),'column');b.label('fiber')
    b.emit('read',C('raw'),'symbol');b.eq(R('symbol'),4)
    b.branch(R('test'),'demux_done','pack_0_0')
    # Prefix is encoded in the static PC. No runtime integer accumulation.
    for depth in range(12):
        for prefix in range(1<<depth):
            b.label(f'pack_{depth}_{prefix}');b.emit('read',C('raw'),'symbol')
            b.eq(R('symbol'),0);b.branch(R('test'),f'zero_{depth}_{prefix}',f'check_{depth}_{prefix}')
            b.label(f'check_{depth}_{prefix}');b.eq(R('symbol'),1)
            b.branch(R('test'),f'one_{depth}_{prefix}','reject')
            for bit,tag in ((0,'zero'),(1,'one')):
                b.label(f'{tag}_{depth}_{prefix}');b.emit('write',C('raw'),C(4));b.emit('move',C('raw'),C(1))
                value=prefix*2+bit
                if depth==11:
                    b.emit('write',R('column'),C(('R',value)));b.emit('move',R('column'),C(1));b.jump('next_column')
                else:b.jump(f'pack_{depth+1}_{value}')
    b.label('next_column')
    for i in range(3):
        b.eq(R('column'),columns[i]);b.branch(R('test'),f'column_to_{i+1}',f'column_test_{i+1}')
        b.label(f'column_to_{i+1}');b.emit('copy',C(columns[i+1]),'column');b.jump('pack_0_0')
        b.label(f'column_test_{i+1}')
    b.emit('copy',C(columns[0]),'column');b.jump('fiber')
    b.label('demux_done');stages['demux_done']=len(b.code)
    for col in columns:
        b.emit('write',C(col),C('>'));b.rewind(col,'<','rewind_'+col)
    b.rewind('raw',2,'raw_return');b.emit('write',C('raw'),C(4));b.emit('move',C('raw'),C(1))
    stages['calls']=[]
    if repair:
        for col in columns:
            start=len(b.code);stages['calls'].append({'column':col,'start':start,'end':start+len(service),'source_key_sites':source_stages['key_sites']})
            def operand(a):
                if a==C('data'):return C(col)
                return tuple(operand(x) for x in a) if isinstance(a,tuple) else a
            for op,*args in service:
                args=[operand(a) for a in args]
                if op=='jump':args[0]+=start
                elif op=='branch':args[1]+=start;args[2]+=start
                elif op=='halt' and args[0]=='accept':op='jump';args=[start+len(service)]
                b.emit(op,*args)
    stages['rejoin']=len(b.code)
    b.emit('write',C('output'),C(2));b.emit('move',C('output'),C(1))
    for col in columns:b.emit('move',C(col),C(1))
    b.label('rejoin_fiber');b.emit('read',C(columns[0]),'symbol');b.eq(R('symbol'),'>')
    b.branch(R('test'),'rejoin_done','rejoin_records');b.label('rejoin_records')
    for i,col in enumerate(columns):
        b.emit('read',C(col),'symbol');b.emit('record',R('symbol'),'test')
        b.branch(R('test'),f'emit_record_{i}','reject');b.label(f'emit_record_{i}')
        b.emit('field',R('symbol'),1,'payload')
        for bit in range(11,-1,-1):
            alphabet=frozenset(v for v in range(4096) if v&(1<<bit))
            b.emit('in',R('payload'),C(alphabet),'test')
            b.branch(R('test'),f'emit_one_{i}_{bit}',f'emit_zero_{i}_{bit}')
            b.label(f'emit_one_{i}_{bit}');b.emit('write',C('output'),C(1));b.jump(f'emitted_{i}_{bit}')
            b.label(f'emit_zero_{i}_{bit}');b.emit('write',C('output'),C(0))
            b.label(f'emitted_{i}_{bit}');b.emit('move',C('output'),C(1))
        b.emit('write',C(col),C('_'));b.emit('move',C(col),C(1))
    b.jump('rejoin_fiber');b.label('rejoin_done')
    for i,col in enumerate(columns):
        b.emit('read',C(col),'symbol');b.eq(R('symbol'),'>');b.branch(R('test'),f'clear_end_{i}','reject');b.label(f'clear_end_{i}')
        b.emit('write',C(col),C('_'));b.rewind(col,'<','clear_return_'+col);b.emit('write',C(col),C('_'))
    b.emit('write',C('output'),C(4));b.rewind('output',2,'output_return');b.emit('move',C('output'),C(1))
    for r in ('symbol','test','column','payload'):b.emit('copy',C(None),r)
    b.emit('halt','accept');b.label('reject');b.emit('halt','reject')
    return b.finish(),roles,stages

class NumericPort:
    """Identity-preserving numeric backing; emulator blank extension means4."""
    def __init__(self,tape):self.tape=tape
    def __getitem__(self,i):return self.tape.cells[i]
    def __setitem__(self,i,v):self.tape.cells[i]=v
    def __len__(self):return len(self.tape.cells)
    def append(self,v):
        if v!='_':raise ValueError('numeric blank extension')
        self.tape.cells.append(4)

class Heads(dict):
    def __init__(self,tapes,numeric):
        super().__init__((r,numeric[r].head if r in numeric else 0) for r in tapes);self.numeric=numeric
    def __setitem__(self,r,v):
        super().__setitem__(r,v)
        if r in self.numeric:self.numeric[r].head=v

def prepare(roles,raw,output,borrowed):
    expected={'G','H','K','Y','J','B','rom'}
    if set(borrowed)!=expected:raise ValueError('exact borrowed roles')
    ports=[raw.cells,output.cells,*borrowed.values()]
    if len({id(x) for x in ports})!=len(ports):raise ValueError('external backing alias')
    if raw is output or raw.head!=1 or output.head!=0 or len(output.cells)!=1 or output.cells[0]!=4:raise ValueError('numeric entry ownership')
    tapes={r:['_'] for r in roles}
    tapes.update({'key_'+r:['_'] for r in ('h','s','offset','target','out','count','col','row','limit','u','t','y')})
    tapes.update({'column'+str(i):['_'] for i in range(4)});tapes.update(borrowed)
    tapes.update(raw=NumericPort(raw),output=NumericPort(output))
    return tapes,Heads(tapes,{'raw':raw,'output':output})

def executor(root):
    """Change only source executor entry heads, retaining its instruction body."""
    path=root/'research/crt-complete-repair-control/machine.py';tree=ast.parse(path.read_text())
    fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='execute')
    expected=ast.parse('heads={r:0 for r in tapes}').body[0]
    if ast.dump(fn.body[0])!=ast.dump(expected):raise ValueError('executor entry drift')
    fn=copy.deepcopy(fn);fn.name='persistent_execute'
    fn.args.args.append(ast.arg(arg='initial_heads'));fn.args.defaults.append(ast.Constant(value=None))
    fn.body[0]=ast.parse('heads=initial_heads').body[0]
    env=source_machine(root).__dict__.copy()
    exec(compile(ast.fix_missing_locations(ast.Module(body=[fn],type_ignores=[])),str(path),'exec'),env)
    return env['persistent_execute']

def encoding(code):
    def norm(x):
        if isinstance(x,frozenset):return {'finite_set':sorted(x)}
        if isinstance(x,(tuple,list)):return [norm(v) for v in x]
        return x
    return json.dumps(norm(code),separators=(',',':')).encode()


def digest(code):return hashlib.sha256(encoding(code)).hexdigest()

def static_stats(root,code):
    widths={r:0 for r in source_machine(root).registers(code)}
    def width(x):
        if x[0]=='r':return widths[x[1]]
        if x[0]=='tuple':return 4+sum(1+width(v) for v in x[1])
        if isinstance(x[1],frozenset):return 16+13*len(x[1])
        return 13
    for iteration in range(len(widths)+1):
        old=dict(widths)
        for op,*v in code:
            if op=='read':n=13
            elif op in ('copy','field'):n=width(v[0])
            elif op in ('not','record','eq','ne','in','notin','xorbit','andbit','orbit'):n=13
            else:continue
            widths[v[-1]]=max(widths[v[-1]],n)
        if widths==old:break
    else:raise ValueError('unbounded register shape')
    return dict(description_bytes=len(encoding(code)),registers=len(widths),register_bits=sum(widths.values()),maximum_register_bits=max(widths.values()),
        prefix_internal_states=4095,record_leaves=4096,bit_table_members=48*2048,assembly_table_tests=48*4096,
        copied_service_instructions=4*8242,private_roles=27,private_cell_cap=4096*13+64,private_backing_bits=13*27*(4096*13+64))
