"""A gate-valid, unitary-premise packed comparator. No new Lean proof."""
from pathlib import Path
import copy
import hashlib
import importlib.util
import json
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
N=512


def need(ok,message):
    if not ok:raise ValueError(message)


def rotate(z,p):
    a,b=z
    return ((a,b),(-b,a),(-a,-b),(b,-a))[p%4]


def mv(rows,x):
    return sum(((r&x).bit_count()%2)<<j for j,r in enumerate(rows))


def compile_gates(gates):
    out=[]
    for g in gates:
        tag=g[0]
        if tag=='pm':
            need(len(g[1])==len(g[2])==9 and all(type(r)is int and 0<=r<N for r in g[1]+g[2]),'permutation domain')
            forward=[mv(g[1],x) for x in range(N)];backward=[mv(g[2],x) for x in range(N)]
            need(all(forward[backward[x]]==x and backward[forward[x]]==x for x in range(N)),'unitary permutation inverse')
            out.append(('pull',backward))
        elif tag=='dg':
            q,alpha=g[1:]
            need(len(q)==len(alpha)==9 and all(type(v)is int and v>=0 for v in q+alpha),'diagonal domain')
            phases=[]
            for x in range(N):
                bits=[i for i in range(9) if x>>i&1]
                phases.append((sum(alpha[i] for i in bits)+2*sum((q[i]>>j)&1 for i in bits for j in bits if i<j))%4)
            out.append(('phase',phases))
        elif tag in ('xg','cg'):
            need(type(g[1])is int and 0<=g[1]<N,'involutive XOR mask')
            if tag=='xg':out.append(('pull',[x^g[1] for x in range(N)]))
            else:
                need(type(g[2])is bool,'C sign')
                out.append(('C',(g[1],1 if g[2] else -1)))
        elif tag=='ph':
            need(type(g[1])is int and g[1]>=0,'phase domain')
            out.append(('phase',[g[1]%4]*N))
        else:raise ValueError('unknown gate')
    return out


def execute(compiled,values):
    values=list(values)
    for tag,data in compiled:
        if tag=='pull':values=[values[x] for x in data]
        elif tag=='phase':values=[rotate(v,p) for v,p in zip(values,data)]
        else:
            mask,s=data
            result=[]
            for x,(a,b) in enumerate(values):
                c,d=values[x^mask]
                result.append((a-s*b+c+s*d,b+s*a+d-s*c))
            values=result
    return values


def count_c(compiled):return sum(tag=='C' for tag,_ in compiled)


def packed(left,right,bits=None,strict=True):
    kl,kr=count_c(left),count_c(right);k=max(kl,kr)
    bits=k+2 if bits is None else bits
    if strict:need(bits>=k+2,'strict unitary radix bound')
    initial=[(1<<(bits*j),0) for j in range(N)]
    a,b=execute(left,initial),execute(right,initial)
    return all((x[0]<<(k-kl),x[1]<<(k-kl))==(y[0]<<(k-kr),y[1]<<(k-kr)) for x,y in zip(a,b))


def run():
    for row in json.loads((HERE/'SOURCES.json').read_text(encoding='utf-8'))['files']:
        if row['usage']=='input':need(hashlib.sha256((ROOT/row['path']).read_bytes()).hexdigest()==row['sha256'],'source '+row['path'])
    # Reuse only the predecessor's closed Lean-literal grammar, not its compiler,
    # executor, independent operator kernels, or any packed comparator.
    path=ROOT/'research/hpe-lean-semantic-binding/verify.py'
    spec=importlib.util.spec_from_file_location('retained_literal_parser',path)
    parser=importlib.util.module_from_spec(spec);spec.loader.exec_module(parser)
    _,circuits=parser.literal_data((ROOT/'research/hyperplane-end-lean/HyperplaneEnd/Exact.lean').read_text(encoding='utf-8'))
    rows=[];controls=[];columns=0
    for i in (1,2,3):
        lhs,rhs=circuits['lhsLit'+str(i)],circuits['rhsLit'+str(i)]
        left,right=compile_gates(lhs),compile_gates(rhs)
        kl,kr=count_c(left),count_c(right);k=max(kl,kr)
        need(kl>=kr,'retained Lean direction')
        need(packed(left,right,2*k+2) and packed(left,right,k+2),'old and new exact decisions')
        peak=0
        for j in range(N):
            initial=[(0,0)]*N;initial[j]=(1,0)
            a,b=execute(left,initial),execute(right,initial)
            need(sum(x*x+y*y for x,y in a)==4**kl,'left column unitary energy')
            need(sum(x*x+y*y for x,y in b)==4**kr,'right column unitary energy')
            need(all((x[0]<<(k-kl),x[1]<<(k-kl))==(y[0]<<(k-kr),y[1]<<(k-kr)) for x,y in zip(a,b)),'unpacked exact columns')
            peak=max(peak,max(abs(v) for z in a for v in z),max(abs(v)<<(k-kr) for z in b for v in z));columns+=2
        need(peak<=2**k,'unitary component bound')
        phase=compile_gates(rhs+[['ph',1]])
        need(not packed(left,phase) and not packed(left,phase,2*k+2),'phase mutant')
        controls.append('pair'+str(i)+'_phase')
        character=[['dg',[0]*9,[2]+[0]*8]]+rhs
        character_circuit=compile_gates(character)
        need(not packed(left,character_circuit) and not packed(left,character_circuit,2*k+2),'input character mutant')
        controls.append('pair'+str(i)+'_input_character')
        initial=[(1<<((k+2)*j),0) for j in range(N)]
        need(execute(left,initial)!=execute(right,initial),'omitted scale control')
        controls.append('pair'+str(i)+'_omitted_scale')
        rows.append({'pair':i,'C_left':kl,'C_right':kr,'old_radix_bits':2*k+2,'new_radix_bits':k+2,
                     'old_max_input_integer_bits':(2*k+2)*(N-1)+1,'new_max_input_integer_bits':(k+2)*(N-1)+1,
                     'unpacked_scaled_component_peak':peak,'unitary_bound':2**k,'normalized_column_energy':'1'})
    broken=copy.deepcopy(circuits['lhsLit1'])
    gate=next(g for g in broken if g[0]=='pm');gate[2]=[0]*9
    try:compile_gates(broken)
    except ValueError:controls.append('nonunitary_permutation')
    else:raise ValueError('nonunitary gate admitted')
    try:packed([],[],0)
    except ValueError:controls.append('undersized_radix')
    else:raise ValueError('undersized radix admitted')
    swap=compile_gates([['xg',1]])
    need(packed([],swap,0,strict=False),'radix-one collision control')
    initial=[(0,0)]*N;initial[0]=(1,0)
    need(execute([],initial)!=execute(swap,initial),'radix-one collision is a false equality')
    controls.append('radix_one_valid_unitary_collision')
    return {'status':'PASS_HPE_UNITARY_PACKED_RADIX','pairs':rows,'unpacked_columns':columns,
            'controls':controls,'new_lean_proof':False,'selected_checker_changed':False,'new_kappa':False}


if __name__=='__main__':
    result=run()
    if '--write' in sys.argv:(HERE/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    else:need(result==json.loads((HERE/'RESULT.json').read_text(encoding='utf-8')),'receipt')
    print(result['status'],'pairs=3 columns=3072 controls='+str(len(result['controls'])))
