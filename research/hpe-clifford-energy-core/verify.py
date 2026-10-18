"""Finite external binding to the standalone Lean energy grammar; no Lean build."""
from pathlib import Path
import hashlib, importlib.util, json, sys
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
N=512

def need(ok,msg):
    if not ok: raise ValueError(msg)

def load(path,name):
    spec=importlib.util.spec_from_file_location(name,path)
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    return mod

def groups(p):
    n=len(p)
    need(all(type(x)is int and 0<=x<n for x in p),'index domain')
    need(all(p[p[x]]==x for x in range(n)),'involution')
    seen=set();result=[]
    for x,y in enumerate(p):
        if x not in seen:
            group=[x] if x==y else [x,y]
            seen.update(group);result.append(group)
    cover(result,n)
    return result

def cover(gs,n):
    need(all(len(g) in (1,2) for g in gs),'cycle size')
    need(sorted(x for g in gs for x in g)==list(range(n)),'complete disjoint cover')

def c(a,b,s):
    x,y=a;z,t=b
    return (x-s*y+z+s*t,y+s*x+t-s*z)

def norm(v):return sum(x*x+y*y for x,y in v)

def stage(tag,data,v):
    if tag=='pull':
        need(sorted(data)==list(range(len(v))),'bijection')
        return [v[i] for i in data]
    if tag=='phase':
        need(len(data)==len(v),'phase count')
        out=[]
        for (a,b),p in zip(v,data):
            out.append(((a,b),(-b,a),(-a,-b),(b,-a))[p%4])
        return out
    mask,s=data
    need(s in (-1,1),'sign')
    gs=groups([i^mask for i in range(len(v))]);out=[None]*len(v)
    for g in gs:
        if len(g)==1:
            i=g[0];out[i]=c(v[i],v[i],s)
        else:
            i,j=g;out[i]=c(v[i],v[j],s);out[j]=c(v[j],v[i],s)
    return out

def rejected(fn):
    try:fn()
    except (ValueError,IndexError):return True
    return False

def run():
    for row in json.loads((HERE/'SOURCES.json').read_text())['files']:
        if row['usage']=='input':need(hashlib.sha256((ROOT/row['path']).read_bytes()).hexdigest()==row['sha256'],'source '+row['path'])
    parser=load(ROOT/'research/hpe-lean-semantic-binding/verify.py','parser')
    reference=load(ROOT/'research/hpe-unitary-packed-radix/verify.py','reference')
    _,circuits=parser.literal_data((ROOT/'research/hyperplane-end-lean/HyperplaneEnd/Exact.lean').read_text(encoding='utf-8'))
    rows=[];columns=0
    for name in ('lhsLit1','rhsLit1','lhsLit2','rhsLit2','lhsLit3','rhsLit3'):
        compiled=reference.compile_gates(circuits[name]);k=reference.count_c(compiled)
        for tag,data in compiled:
            for j in range(N):
                v=[(0,0)]*N;v[j]=(1,0)
                actual=stage(tag,data,v)
                need(actual==reference.execute([(tag,data)],v),'all-row external binding')
                need(norm(actual)==(4 if tag=='C' else 1),'basis energy')
                columns+=1
            v=[(i%11-5,i%7-3) for i in range(N)]
            need(stage(tag,data,v)==reference.execute([(tag,data)],v),'mixed-sign binding')
            need(norm(stage(tag,data,v))==norm(v)*(4 if tag=='C' else 1),'dirty energy')
        rows.append({'name':name,'stages':len(compiled),'C_stages':k,'energy_multiplier':4**k})
    controls={
        'noninvolution':lambda:groups([1,2,0]),
        'duplicate':lambda:cover([[0,1],[1,2]],4),
        'omitted':lambda:cover([[0,1]],3),
        'out_of_range':lambda:groups([1,9]),
        'nonbijective':lambda:stage('pull',[0,0],[(1,0),(0,0)]),
        'missing_phase':lambda:stage('phase',[0],[(1,0),(0,0)])}
    for name,fn in controls.items():need(rejected(fn),'accepted '+name)
    a,b=(1,0),(0,1)
    need(norm([c(a,b,1),c(b,a,-1)])!=4*norm([a,b]),'inconsistent pair signs')
    need(norm([a])!=4*norm([a]),'fixed point must double')
    return {'status':'PASS_HPE_ENERGY_EXTERNAL_BINDING','circuits':rows,'basis_columns':columns,
            'controls':list(controls)+['inconsistent_pair_signs','missing_fixed_point_doubling'],
            'independence':'Retained parser/compiler/executor are comparison subjects; pair-cycle lowering is new. This is an external finite binding, not a new independent Clifford executor or kernel proof.'}

if __name__=='__main__':
    result=run()
    if '--emit' in sys.argv:print(json.dumps(result,indent=2))
    else:
        need(result==json.loads((HERE/'RESULT.json').read_text()),'receipt mismatch')
        print(result['status'],result['basis_columns'],'columns; 8 controls')
