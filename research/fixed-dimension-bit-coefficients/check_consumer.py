"""Independent small-block algebra and literal encoded-consumer executions.

Fixture serialization and expected arithmetic are outside the runtime. Runtime
Word.inspect is forbidden, including for N>64. This is not a full B0 dispatcher.
"""
from fractions import Fraction as F
from hashlib import sha256
import json
from itertools import permutations
from math import gcd
from pathlib import Path
import sys
from types import ModuleType

HERE = Path(__file__).resolve().parent


def load(path):
    name = "fixed_dimension_consumer_source"
    old = sys.modules.get(name)
    module = ModuleType(name)
    module.__file__ = str(path)
    sys.modules[name] = module
    try:
        exec(compile(path.read_bytes(),str(path),"exec"),module.__dict__)
    finally:
        if old is None:
            sys.modules.pop(name,None)
        else:
            sys.modules[name]=old
    return module


C = load(HERE/"consumer.py")


def need(condition, label):
    if not condition:
        raise ValueError(label)


def identity(n):
    return [[F(i==j) for j in range(n)] for i in range(n)]


def fixtures(n,rank=1):
    preparation = identity(n)
    preparation[0][n-1] = F(1,2)
    template = C.Template(3,rank,tuple(map(tuple,preparation)))
    specs = {}
    for code,block in enumerate((((1,1),(1,2)),((0,1),(1,1)),((1,2),(1,0)))):
        low=[[int(i==j) for j in range(n)] for i in range(n)]
        for i,x in enumerate((0,n-1)):
            for j,y in enumerate((0,n-1)):
                low[x][y]=block[i][j]
        # The compiled preparation is unit triangular. The first projector
        # pivot is good for the first and third low class, bad for the second.
        specs[code]=C.Specification(code,template,tuple(map(tuple,low)),code!=1)
    return specs


def projector(spec,high,modulus):
    """Closed 2x2 adjugate formula on the nontrivial extreme-coordinate block.

    Other coordinates are identity in the header and zero in the rank-one
    projector. No source matrix preparation or elimination is imported.
    """
    n=len(high)
    if n<=3:
        need(spec.template.rank==1,'dense fixture oracle rank-one domain')
        # The signed-permutation determinant and cofactor inverse are
        # independent of the source's row-reduction algorithm.
        g=[[(spec.low[i][j]+spec.template.q*high[i][j])%modulus for j in range(n)] for i in range(n)]
        s=[[(z.numerator*pow(z.denominator,-1,modulus))%modulus for z in row]
           for row in spec.template.preparation]
        a=[[sum(g[i][k]*s[k][j] for k in range(n))%modulus for j in range(n)] for i in range(n)]
        def det(matrix):
            size=len(matrix); total=0
            for p in permutations(range(size)):
                inversions=sum(p[i]>p[j] for i in range(size) for j in range(i+1,size))
                term=(-1)**inversions
                for i in range(size): term*=matrix[i][p[i]]
                total+=term
            return total%modulus
        invdet=pow(det(a),-1,modulus)
        row=[]
        for j in range(n):
            minor=[[a[x][y] for y in range(1,n)] for x in range(n) if x!=j]
            row.append(((-1)**j*det(minor)*invdet)%modulus)
        return [[a[i][0]*row[j]%modulus for j in range(n)] for i in range(n)]
    axes=(0,n-1)
    g=[[ (spec.low[i][j]+spec.template.q*high[i][j])%modulus for j in axes] for i in axes]
    s=[[ (z.numerator*pow(z.denominator,-1,modulus))%modulus
         for j in axes for z in (spec.template.preparation[i][j],)] for i in axes]
    h=[[sum(g[i][k]*s[k][j] for k in range(2))%modulus for j in range(2)] for i in range(2)]
    a,b=h[0]; c,d=h[1]; det=(a*d-b*c)%modulus
    inv=pow(det,-1,modulus)
    block=[[a*d*inv%modulus,-a*b*inv%modulus],[c*d*inv%modulus,-c*b*inv%modulus]]
    out=[[0]*n for _ in range(n)]
    for k in range(1,spec.template.rank): out[k][k]=1
    for i,x in enumerate(axes):
        for j,y in enumerate(axes): out[x][y]=block[i][j]
    return out


def fallback_diagonal(p,modulus):
    """Separate integer row-operation oracle for the fixed residual matrix."""
    n=len(p); d=2*n
    a=[[0]*d for _ in range(d)]
    for i in range(n):
        for j in range(n):
            z=(int(i==j)-p[i][j])%modulus
            a[i][j]=z; a[d-1-i][d-1-j]=z
            a[i][d-1-j]=p[i][j]; a[d-1-i][j]=p[i][j]
    perm=list(range(d))
    for j in range(d):
        pivot=next(k for k in range(j,d) if gcd(a[k][j],modulus)==1)
        a[j],a[pivot]=a[pivot],a[j]; perm[j],perm[pivot]=perm[pivot],perm[j]
        inv=pow(a[j][j],-1,modulus)
        for i in range(d):
            if i!=j:
                factor=a[i][j]*inv%modulus
                a[i]=[(x-factor*y)%modulus for x,y in zip(a[i],a[j],strict=True)]
    need(all(not a[i][j] for i in range(d) for j in range(d) if i!=j),"oracle residual diagonal")
    return [a[i][i] for i in range(d)],perm


def oracle(n,modulus,root_unit,root_size,events,specs,highs,index,coefficient=False):
    sizes=[root_size]
    for kind,code,rank,field,reverse,half in events:
        f=sizes[-1]//n
        sizes.append(rank*f if kind==0 else f//2 if half else f)
    def weight(level,coordinate):
        if level==0: return root_unit
        kind,code,rank,field,reverse,half=events[level-1]
        if kind==2: return 1
        f=sizes[level-1]//n
        p=projector(specs[code],highs[level-1],modulus)
        if kind==0:
            pivot=coordinate//f
            need(0<=pivot<rank,'independent generated pivot label')
            factor=p[0][0] if pivot==0 else 1
            need(rank==1 or n>3,'sparse higher-rank oracle domain')
            return factor*weight(level-1,coordinate)%modulus
        diagonal,perm=fallback_diagonal(p,modulus)
        column=f-1-coordinate if reverse else coordinate
        def bank(row):
            return weight(level-1,row*f+column) if row<n else 1
        return diagonal[field]*bank(perm[field])*pow(bank(field),-1,modulus)%modulus
    if not coefficient:
        return weight(len(events),index)
    p=projector(specs[2],highs[-1],modulus)
    f=sizes[-1]//n
    ell=-p[n-1][0]*pow(p[0][0],-1,modulus)%modulus
    return ell*weight(len(events),(n-1)*f+index)*pow(weight(len(events),index),-1,modulus)%modulus


def run_case(n,width,kinds,*,repeat=1,coefficient=True,short_capacity=False,
             wrong_field_code=False,truncate_field=False,dense=False,warm_history=False,
             inverse=False,offset=False,leaf=False,rank=1,half_units=False):
    need(not leaf or not coefficient,'leaf has no current coefficient')
    m=C.build(n); q=3; modulus=q**width; h=len(kinds); root_size=n**(h+1)*2
    residue_bits=modulus.bit_length()+1; index_bits=root_size.bit_length()+1; code_bits=2
    bound=C.footprint(n,h,residue_bits,index_bits,code_bits)
    r=m.words.Arena(residue_bits,capacity=bound['residue_pending']+16)
    i=m.words.Arena(index_bits,capacity=bound['index_pending']+16)
    if warm_history:
        for arena,limit in ((r,bound['residue_pending']+8),(i,bound['index_pending']+8)):
            old=[arena.zero() for _ in range(limit)]
            arena.free_many(*old)
    mod=r.input(modulus); ring=m.words.Ring(mod)
    specs=fixtures(n,rank); events=[]; fields=[]; highs=[]
    for level,kind in enumerate(kinds):
        code=0 if kind=='G' else 1
        field=0 if kind!='P' else (n if level%2 else 0)
        events.append(({'G':0,'P':1,'U':2}[kind],code,rank,field,field>=n,
                       bool(half_units and kind=='U')))
    for level,code in enumerate([row[1] for row in events]+([] if leaf else [2])):
        high=[[0]*n for _ in range(n)]
        if width>1:
            if dense:
                need(n<=3,'small exact dense oracle')
                high=[[(2*x+3*y+level+1)%(q**(width-1)) for y in range(n)] for x in range(n)]
            else:
                high[n-1][n-1]=(level+1)%q
                if code==1: high[0][0]=1
        highs.append(high); fields.append((code,high))
    program=m.records.Program.fixture(i,r,root_size,2,events,code_bits)
    raw=m.records.Fields.fixture(i,r,fields,code_bits)
    if wrong_field_code:
        raw.tape.cells[1]=1-raw.tape.cells[1]
    if truncate_field:
        # Remove one complete final digit word before the first RECORD_END.
        end=raw.tape.cells.index(m.records.RECORD_END)
        del raw.tape.cells[end-(residue_bits+1):end]
    before=(bytes(program.tape.cells),program.tape.head,bytes(raw.tape.cells),raw.tape.head)
    position=i.input(0)
    operand=r.input(2) if offset else None
    workspace=C.Workspace(m,ring,i)
    stack_identities=tuple(id(t) for s in workspace.roles for t in (s.tape,s.reverse))
    start_r,start_i=len(r.live),len(i.live)
    entry_r,entry_i=len(r.words),len(i.words)
    pending={id(r):start_r,id(i):start_i}
    original_zero=m.words.Arena.zero
    original_inspect=m.words.Word.inspect
    original_tape_init=m.records.Tape.__init__
    def observed_zero(arena):
        pending[id(arena)]=max(pending.get(id(arena),0),len(arena.live)+1)
        return original_zero(arena)
    def forbidden_inspect(_): raise ValueError('runtime word decoding forbidden')
    def forbidden_tape_init(_): raise ValueError('fresh continuation tape during callback')
    m.words.Arena.zero=observed_zero; m.words.Word.inspect=forbidden_inspect
    m.records.Tape.__init__=forbidden_tape_init
    if short_capacity:
        r.capacity=max(len(r.words),len(r.live))+1
    values=[]; stack_max=[0]*4
    error=None
    try:
        for _ in range(repeat):
            cb=None
            try:
                cb=workspace.open(program,raw,specs,2,leaf=leaf)
                try:
                    workspace.open(program,raw,specs,2)
                except ValueError as exc:
                    need(str(exc)=='exclusive continuation workspace','exact lease guard')
                else:
                    raise ValueError('concurrent callback lease was accepted')
                output=(cb.offset(n-1,position,operand,inverse) if offset else
                        cb.coefficient(n-1,position,inverse) if coefficient else cb.weight(position))
                cb.close()
                value=original_inspect(output); r.free(output); values.append(value)
                for j,tape in enumerate((cb.pending.tape,cb.pending.reverse,cb.values.tape,cb.values.reverse)):
                    stack_max[j]=max(stack_max[j],len(tape.cells)+1)
            except ValueError:
                if cb is not None: cb.abort()
                raise
    except ValueError as exc:
        error=str(exc)
    finally:
        m.words.Arena.zero=original_zero; m.words.Word.inspect=original_inspect
        m.records.Tape.__init__=original_tape_init
    need(pending[id(r)]<=start_r+bound['residue_pending'],'pre-guard residue demand')
    need(pending[id(i)]<=start_i+bound['index_pending'],'pre-guard index demand')
    if short_capacity or wrong_field_code or truncate_field:
        need(error is not None,'invalid runtime control rejected')
        return {'control_error':error,'residue_pending':pending[id(r)],'index_pending':pending[id(i)]}
    need(error is None,'valid encoded run: '+str(error))
    expected=oracle(n,modulus,2,root_size,events,specs,highs,0,coefficient)
    if coefficient and inverse: expected=-expected%modulus
    if offset: expected=2*expected%modulus
    need(values==[expected]*repeat,'independent full-ring coefficient')
    need(before==(bytes(program.tape.cells),program.tape.head,bytes(raw.tape.cells),raw.tape.head),
         'complete borrowed program/field bytes and heads')
    need(len(r.live)==start_r and len(i.live)==start_i,'numerical frame closed')
    need(not workspace.active and stack_identities==tuple(id(t) for s in workspace.roles for t in (s.tape,s.reverse)),
         'exclusive fixed continuation roles reused')
    need(len(program.tape.cells)+1<=bound['program_extent'],'full Program backing')
    need(len(raw.tape.cells)+1<=bound['fields_extent'],'full N-squared Fields backing')
    need(sum(stack_max)<=bound['four_stack_extents'],'four historical stack extents')
    residue_backing=(len(r.words)+1)*(residue_bits+2)
    index_backing=(len(i.words)+1)*(index_bits+2)
    need(len(r.words)<=max(entry_r,start_r+bound['residue_pending']) and
         len(i.words)<=max(entry_i,start_i+bound['index_pending']),
         'allocated slots retain erased history')
    i.free(position)
    if operand is not None: r.free(operand)
    ring.close(); r.free(mod)
    need(not r.live and not i.live,'complete numerical retirement')
    return {'N':n,'w':width,'kinds':kinds,'repetitions':repeat,'value':expected,
            'rank':rank,
            'half_units':half_units,
            'dense_fields':dense,'warm_history':warm_history,'entry_slots':[entry_r,entry_i],
            'inverse':inverse,'offset':offset,'leaf':leaf,
            'residue_pending':pending[id(r)],'index_pending':pending[id(i)],
            'residue_backing':residue_backing,'index_backing':index_backing,
            'four_stack_backing':stack_max,'program_backing':len(program.tape.cells)+1,
            'fields_backing':len(raw.tape.cells)+1,
            'source_changes':m.edit_count}


if __name__=='__main__':
    print(json.dumps(run_case(2,2,'GP'),sort_keys=True))
