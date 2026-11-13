from pathlib import Path
import hashlib, importlib.util, json, sys
P=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(P))
import move as m
import verify as v

def require(x,s):
    if not x:raise ValueError(s)
code,alphabet,starts=m._compile_move()
r=json.loads((P/'reference/RECIPE.json').read_text())['lowered_recipe']
modules=[('right_phase_',m.PHASE.compile_phase(r['right']['linear_Z4'],r['right']['quadratic_rows'],r['right']['phase'])),('right_linear_',m.LINEAR.compile_linear('right')),('right_offset_',m.TRANSLATION.compile_translation()),('positive_child_',m.LEAF.compile_leaf()),('left_phase_',m.PHASE.compile_phase(r['left']['linear_Z4'],r['left']['quadratic_rows'],r['left']['phase'])),('left_linear_',m.LINEAR.compile_linear('left'))]
checked=0
for k,(name,(old,alph)) in enumerate(modules):
    start=starts[name];end=starts[modules[k+1][0]] if k+1<len(modules) else starts['commit']
    require(end-start==len(old),'component size or order')
    for i,ins in enumerate(old):
        op,*a=ins
        port=lambda t: {0:0,1:2}.get(t,t+2)
        if op=='read':expected=(op,port(a[0]),{s:start+d for s,d in a[1].items()})
        elif op in ('write','move'):expected=(op,port(a[0]),a[1])
        elif op=='goto':expected=(op,start+a[0])
        elif op=='halt':expected=('goto',end)
        else:raise ValueError('uncovered opcode')
        require(code[start+i]==expected,'relocation mismatch')
        require(not(op=='write' and port(a[0])==1),'factor public write')
        checked+=1
for ins in code:
    if ins[0]=='read': require(all(0<=d<len(code) for d in ins[2].values()),'read target')
    if ins[0]=='goto':require(0<=ins[1]<len(code),'jump target')
    if ins[0] in ('read','write','move'):require(0<=ins[1]<31,'port bounds')
# Independent forward-address full f=1 operator. No inverse address map,
# CNOT word, phase counter, butterfly routine or author oracle is used.
def rotate(a,q):
    re,im=a
    return ((re,im),(-im,re),(-re,-im),(im,-re))[q%4]
def transform(x):
    z=[(0,0)]*512
    for idx,a in enumerate(x):
        coords=[(idx>>(8-j))&1 for j in range(9)]
        phase=r['right']['phase']+sum(r['right']['linear_Z4'][j]*coords[j] for j in range(9))
        phase+=2*sum(coords[j]*coords[k] for j in range(9) for k in range(j+1,9) if r['right']['quadratic_rows'][j]>>k&1)
        y=[(sum(coords[k] for k in range(9) if r['right']['matrix_rows'][j]>>k&1)%2)^((r['right']['offset']>>j)&1) for j in range(9)]
        dest=sum(y[j]<<(8-j) for j in range(9))
        z[dest]=rotate(a,phase)
    t=[(0,0)]*512
    for lo in range(256):
        for ob in (0,1):
            re=im=0
            for ib in (0,1):
                ar,ai=z[(ib<<8)|lo];sgn=1 if ob==ib else -1
                re+=ar-sgn*ai;im+=ai+sgn*ar
            require(re%2==0 and im%2==0,'reference integrality')
            t[(ob<<8)|lo]=(re//2,im//2)
    out=[(0,0)]*512
    for idx,a in enumerate(t):
        coords=[(idx>>(8-j))&1 for j in range(9)]
        phase=r['left']['phase']+sum(r['left']['linear_Z4'][j]*coords[j] for j in range(9))
        phase+=2*sum(coords[j]*coords[k] for j in range(9) for k in range(j+1,9) if r['left']['quadratic_rows'][j]>>k&1)
        y=[sum(coords[k] for k in range(9) if r['left']['matrix_rows'][j]>>k&1)%2 for j in range(9)]
        dest=sum(y[j]<<(8-j) for j in range(9));out[dest]=rotate(a,phase)
    return out
values=[(2*((i*7)%3-1),2*((i*11+1)%3-1)) for i in range(512)]
expected_values=transform(values)
# This independent forward oracle uses only exact Python integer arithmetic.
expected=v.encode(expected_values,4)
require(expected==v.oracle(values,(1,1,1,1,4,1)),'forward versus inverse oracle disagreement')
receipt,_=v.run_case('root_independent_forward_address_full_f1',(1,1,1,1,4,1),values,expected=expected)
require(receipt['early']==0 and receipt['writes']==4096,'transactional public writes')
result={'status':'PASS_ROOT_NATIVE_COMPOSITION_REVIEW','relocated_instructions':checked,'total_instructions':len(code),'tapes':31,'graph_sha256':hashlib.sha256(repr(code).encode()).hexdigest(),'fixture':receipt,'oracle_scope':'exact integer Gaussian forward-address oracle; all-f proof remains written factor-composition proof','files':{str(f.relative_to(P)):hashlib.sha256(f.read_bytes()).hexdigest() for f in [P/'move.py',P/'verify.py',P/'SOURCES.json',P/'reference/RECIPE.json']}}
print(json.dumps(result,indent=2))
