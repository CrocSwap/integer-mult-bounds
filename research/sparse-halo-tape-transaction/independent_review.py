"""Independent modular-membership and stable-radix oracle.

Prepared for @CubeJerry by a separately assigned source-aware AI reviewer,
with substantial OpenAI Codex assistance. Apache-2.0. Imports the author
program, but no author geometry oracle or fixture builder.
"""
from pathlib import Path
from hashlib import sha256
import importlib.util
import itertools
import json

SOURCE=Path(__file__).with_name('tapes.py')
spec=importlib.util.spec_from_file_location('reviewed_halo_tapes',SOURCE)
p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)

def bitword(n,width):
    if not 0<=n<2**width: raise ValueError('word range')
    return bin(n)[2:].rjust(width,'0')

def rows(text):
    words=text.split('#')
    if words[-1]!='' or len(words)%2!=1: raise ValueError('record grammar')
    return list(zip(words[:-1:2],words[1:-1:2]))

def check_point(ks,ell,a,b,cores,locals_,z=0,zwidth=0):
    L=2**ell;g=len(ks);W=ell+2
    prefix=bitword(z,zwidth) if zwidth else ''
    coordinate=prefix+'&'+''.join('@'+bitword(q,k)+'#'+bitword(r,ell)+';' for q,r,k in zip(cores,locals_,ks))
    machine=p.Program('1010#',coordinate,bitword(L,W),bitword(a,W),bitword(b,W))
    machine.setup();p.home(machine.source);machine.load_payload(machine.source,machine.payload)
    p.end(machine.saved);machine.build_descriptor();p.home(machine.faces)
    while machine.faces.read()!='!':
        machine.prepare_face();machine.emit()
        while machine.next_choice(): machine.emit()
    actual=rows(machine.saved.inspect())
    point=tuple(q*L+r for q,r in zip(cores,locals_))
    sourcekey=prefix+''.join(bitword(x,k+ell) for x,k in zip(point,ks))
    expected=[]
    # Scan all destination core faces and test direct modular interval membership.
    # No source predicates, prefix eligibility, or suffix-choice formula is used.
    for target in itertools.product(*(range(2**k) for k in ks)):
        for face in range(g):
            for side in (0,1):
                offsets=[]
                for axis,(x,q,k) in enumerate(zip(point,target,ks)):
                    lo,hi=((a,L-a) if axis<face else
                           ((0,a) if side==0 else (L-a,L)) if axis==face else (0,L))
                    offset=(x-(q*L+lo-b))%(2**k*L)
                    if offset>=hi-lo+2*b: break
                    offsets.append(offset)
                if len(offsets)==g:
                    key=prefix+''.join(bitword(q,k) for q,k in zip(target,ks))
                    key+=''.join('1' if axis==face else '0' for axis in range(g))+str(side)
                    key+=''.join(bitword(x,W) for x in offsets)+sourcekey
                    expected.append((key,'1010'))
    if sorted(actual)!=sorted(expected):
        raise ValueError(('geometric mismatch',ks,ell,a,b,cores,locals_,actual,expected))
    return len(actual)

checked=0;copies=0
for ks,ell,a,b in [((1,),4,2,1),((1,2),4,2,1),((2,1,1),4,2,1),((1,1,1,1),3,1,0)]:
    L=2**ell;g=len(ks)
    boundary=sorted({r for r in (0,b-1,b,a-b-1,a-b,a+b-1,a+b,L-a-b-1,L-a-b,L-a+b-1,L-a+b,L-b-1,L-b,L-1) if 0<=r<L})
    points=list(itertools.product(boundary,repeat=g))
    if g>=3: points=[point for i,point in enumerate(points) if i%7==0]
    for core in [tuple(0 for _ in ks),tuple(2**k-1 for k in ks)]:
        for point in points:
            copies+=check_point(ks,ell,a,b,core,point,z=1,zwidth=1)
            checked+=1

sort_cases=[]
for width in range(1,6):
    data=[(bitword((i*5+3)%(2**width),width),bitword(i,8)) for i in range(3*2**width)]
    text=''.join(key+'#'+value+'#' for key,value in data)
    machine=p.Program('','&@0#0000;','010000','000010','000001')
    machine.saved=p.Tape('independent_sort_input',text)
    machine.sort(machine.saved)
    actual=rows(machine.saved.inspect())
    expected=sorted(data,key=lambda row:row[0])
    if actual!=expected: raise ValueError(('radix mismatch',width))
    machine.sort(machine.saved)
    if rows(machine.saved.inspect())!=expected: raise ValueError(('radix idempotence',width))
    sort_cases.append({'width':width,'records':len(data)})
print('PASS_INDEPENDENT_HALO_GEOMETRY_AND_RADIX')
print(json.dumps({'source_sha256':sha256(SOURCE.read_bytes()).hexdigest(),'local_geometry_cases':checked,'copies':copies,'stable_radix_cases':sort_cases},sort_keys=True))
