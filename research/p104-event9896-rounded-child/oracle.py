#!/usr/bin/env python3
"""Independent physical XOR-pair oracle for one selected width-one child.

No author kernel, Clifford compiler, records executor or primary is imported.
Existing pair theorems retain Ali Romman/6509 and predecessor credit.
New consumer checking: ToikY with OpenAI Codex assistance, Apache-2.0.
"""
import argparse
from fractions import Fraction as F
import gzip
import hashlib
import json
import math
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parent
MANIFEST_SHA='c9847104b61030a74b416a550f72dfa24a3fda660fa7d21fef4593e7fb307936'
N=512
PINS={
 'inputs/kernel.py':(2464,'fc3e2bf828fa547bee5710f9d5502b7c8c4dcb4cab7536ff73e3dbff54960f1b','b00bbbc7655121232a46101962c48e71cee98a39'),
 'inputs/PROOF-6509.md':(11768,'122eff335674d8de1bcba47d28feb0c420be62b2b6d4e84f91c4292383753380','b7047476aaa5e2bb149c92a8a40a9b2ab444ef73'),
 'inputs/PROOF-6499.md':(3945,'7e8802411729e42dc202f6be4d837d25d0d8ee753b32e2c8702a97d847e6b9bf','c1882238c57ae7d21505359577cee01c50573ff8'),
 'inputs/records-6499.py':(1450,'dff32a6cdc94434e1586418d7c1f66915afb161e47687cd336fbc9a9d73a7b6a','62b4a1ef5192664334bf1d5b7480fe6963bb8edd'),
 'inputs/WORD.json.gz':(119880,'7834725d9e34ee846a9ccc615221ea81e0201613938afa185d2eda0c9a6c232f','22f9ab02d1b73ea0aa4b07ce445a14cc2602c760'),
 'inputs/clifford_exact.py':(6824,'2982ead07721e83358dc67c6f49c2b4c16a236a6bebdfd72f58221be1f5d0962','166841a037f069249f6f7f6dedb89248812f59e2'),
}


def require(ok,message):
    if not ok:raise ValueError(message)


def canonical(value):
    return json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False)


def digest(value):
    return hashlib.sha256((canonical(value)+'\n').encode()).hexdigest()


def decode(raw):
    def unique(items):
        result={}
        for key,value in items:
            require(key not in result,'duplicate JSON key');result[key]=value
        return result
    def bad(value):raise ValueError('nonfinite JSON: '+value)
    def floating(value):
        result=float(value);require(math.isfinite(result),'nonfinite JSON number');return result
    return json.loads(raw,object_pairs_hook=unique,parse_constant=bad,parse_float=floating)


def read(path):
    with path.open('rb') as handle:raw=handle.read(8*1024*1024+1)
    require(len(raw)<=8*1024*1024,'input capacity');return raw


def authenticate(raw,manifest):
    require(hashlib.sha256(manifest).hexdigest()==MANIFEST_SHA,'source manifest SHA256')
    require(set(raw)==set(PINS),'exact six-source closure')
    for path,(size,sha,blob) in PINS.items():
        value=raw[path];require(len(value)==size,'source byte length: '+path)
        require(hashlib.sha256(value).hexdigest()==sha,'source SHA256: '+path)
        frame=b'blob '+str(len(value)).encode()+b'\0'+value
        require(hashlib.sha1(frame).hexdigest()==blob,'source Git blob: '+path)


def rotate(value,power):
    a,b=value
    return ((a,b),(-b,a),(-a,-b),(b,-a))[power%4]


def validate_word(word):
    require(type(word['public']) is int and word['public']==770,'770 arbitrary public roles')
    require(type(word['owned_fields']) is int and word['owned_fields']==29,'29 owned roles')
    require(len(word['program'])==22803,'complete source event count')
    writes={236:[],720:[]};prefix_ops=set()
    for index,event in enumerate(word['program']):
        require(type(event) is list and type(event[0]) is str,'event grammar')
        op=event[0]
        if op in ('ADD','COPY'):
            require(len(event)==5 and type(event[2]) is int and 0<=event[2]<799,'binary scalar grammar')
            require(type(event[3]) is str and F(event[3])!=0 and type(event[4]) is int,'scalar coefficient/frame')
        elif op=='SCALE':
            require(len(event)==4 and type(event[2]) is str and F(event[2])!=0 and type(event[3]) is int,'SCALE grammar')
        elif op=='MOVE':
            require(len(event)==5 and all(type(x) is int for x in event[2:4]) and type(event[4]) is bool,'MOVE grammar')
        elif op in ('INIT','CLEAR'):
            require(len(event)==3 and type(event[2]) is int,'owned grammar')
        else:raise ValueError('unknown destination semantics')
        require(type(event[1]) is int and 0<=event[1]<799,'typed destination role')
        if index<9896:
            prefix_ops.add(op)
            if event[1] in writes:writes[event[1]].append([index,event])
    require(prefix_ops=={'ADD','INIT','SCALE'},'complete prefix operation alphabet')
    require(writes=={236:[[8203,['ADD',236,720,'-2',3]]],720:[]},'literal entrance write history')
    require(word['initial'][236]==word['initial'][720]==3 and word['frames'][3]==[],'arbitrary coarse public entrance')
    require(word['program'][9896]==['MOVE',236,3,7,False] and word['frames'][7]==[21],'actual selected call')
    return {'event9896':word['program'][9896],'public_roles':[236,720],
            'initial_frames':[3,3],'prefix_writes':{str(k):v for k,v in writes.items()},
            'entrance_formula':'initial236 - 2*initial720','coarse_grid_entrance':True}


def source_monomial():
    columns=[];span={0}
    for value in [21]+[1<<i for i in range(9)]:
        if value not in span:
            columns.append(value);span|={x^value for x in tuple(span)}
    require(len(columns)==9 and len(span)==512,'source basis extension')
    permutation=[]
    for value in range(N):
        out=0
        for bit,column in enumerate(columns):
            if value>>bit&1:out^=column
        permutation.append(out)
    inverse=[0]*N
    for x,y in enumerate(permutation):inverse[y]=x
    inverse_columns=[inverse[1<<i] for i in range(9)]
    Q=[(1<<i)^sum(((a&b).bit_count()%2)<<j for j,b in enumerate(inverse_columns)) for i,a in enumerate(inverse_columns)]
    G=[sum(((column>>i)&1)<<j for j,column in enumerate(columns)) for i in range(9)]
    alpha=[Q[i]>>i&1 for i in range(9)]
    phases=[]
    for x in range(N):
        diagonal=sum(alpha[i] for i in range(9) if x>>i&1)
        cross=sum(((Q[i]>>(i+1))&(x>>(i+1))).bit_count()%2 for i in range(9) if x>>i&1)
        phases.append((diagonal+2*cross)%4)
    require(all((inverse[x]&1)==bool(x&16) for x in range(N)),'source pair orientation')
    require(all(phases[x]==0 for x in range(N) if not x&16),'absolute left chart phase for nonlinear pair equivalence')
    return {'G':G,'Q':Q,'alpha':alpha},permutation,phases


def monomial(values,permutation,phases,adjoint=False):
    out=[(0,0)]*N
    for x,y in enumerate(permutation):
        if adjoint:out[x]=rotate(values[y],-phases[y])
        else:out[y]=rotate(values[x],phases[y])
    return out


def ideal_columns(permutation,phases):
    columns=[];a=(F(1,2),F(1,2));b=(F(1,2),F(-1,2))
    inverse=[0]*N
    for x,y in enumerate(permutation):inverse[y]=x
    for source in range(N):
        target=source^21
        actual_phase=(phases[target]-phases[source])%4
        require(permutation[inverse[source]^1]==target,'source XOR displacement')
        phase=1 if (source&5).bit_count()%2==0 else -1
        require(actual_phase==(0 if phase==1 else 2),'source signed Pauli phase')
        direct={source:a,target:(phase*b[0],phase*b[1])}
        column=[[row,list(map(str,value))] for row,value in sorted(direct.items())]
        columns.append(column)
    return columns


def pair_difference(x,y,sign):
    require(type(sign) is int and sign in (-1,1),'pair sign')
    require(len(x)==len(y)==2 and all(type(v) is int for v in (*x,*y)),'integer Gaussian inputs')
    s=(x[0]+y[0],x[1]+y[1]);d=(x[0]-y[0],x[1]-y[1])
    if s[0]%2==s[1]%2:c=(0,0)
    elif s[0]%2:c=(1 if s[0]>0 else -1,0)
    else:c=(0,1 if s[1]>0 else -1)
    shifted=rotate((d[0]-c[0],d[1]-c[1]),sign)
    difference=(shifted[0]+c[0],shifted[1]+c[1])
    first=tuple(F(s[j]+difference[j],2) for j in range(2))
    second=tuple(F(s[j]-difference[j],2) for j in range(2))
    require(all(value.denominator==1 for value in (*first,*second)),'exact coarse pair parity')
    return tuple(value.numerator for value in first),tuple(value.numerator for value in second)


def direct(values,sign=1):
    require(type(values) is list and len(values)==N,'512-coordinate field')
    out=[None]*N
    for left in range(N):
        if left&16:continue
        right=left^21;phase=1 if (left&5).bit_count()%2==0 else -1
        x=values[left];y=tuple(phase*v for v in values[right])
        first,second=pair_difference(x,y,sign)
        out[left]=first;out[right]=tuple(phase*v for v in second)
    return out


def layer(values,sign):
    out=list(values)
    for left in range(0,N,2):out[left],out[left+1]=pair_difference(out[left],out[left+1],sign)
    return out


def cycle_monomial(values,permutation,phases,adjoint=False):
    inverse=[0]*N
    for x,y in enumerate(permutation):inverse[y]=x
    route=inverse if adjoint else permutation
    seen=set();temporary=(0,0);cycles=0
    for start in range(N):
        if start in seen:continue
        require(temporary==(0,0),'clean swap temporary before cycle')
        temporary,values[start]=values[start],temporary
        current=start
        while True:
            seen.add(current);target=route[current]
            phase=-phases[current] if adjoint else phases[target]
            shifted=rotate(temporary,phase)
            temporary,values[target]=values[target],shifted
            current=target
            if current==start:break
            require(current not in seen,'closed permutation cycle')
        require(temporary==(0,0),'swap temporary clean after literal cycle')
        cycles+=1
    return temporary,cycles


def inplace_reference(fine,p,permutation,phases):
    require(type(p) is int and p>=14,'p=t+14 domain')
    require(len(fine)==N and all(type(v) is int and v%32==0 for z in fine for v in z),'coarse entrance required')
    bank=fine;identity=id(bank)
    coarse=[tuple(v//32 for v in z) for z in bank]
    values=list(coarse)
    first,cycles1=cycle_monomial(values,permutation,phases,True)
    values[:]=layer(values,1)
    second,cycles2=cycle_monomial(values,permutation,phases)
    require(values==direct(coarse),'independent direct physical-pair and literal-cycle agreement')
    bank[:]=[tuple(32*v for v in z) for z in values]
    require(id(bank)==identity,'inplace destination object')
    require(first==second==(0,0),'both swap returns zero')
    limit=1<<(p+15)
    require(all(-limit<=v<limit for z in bank for v in z),'caller signed record width')
    return bank,second,[cycles1,cycles2]


def error_squared(coarse,rounded):
    result=F(0)
    for row in range(N):
        phase=1 if (row&5).bit_count()%2==0 else -1
        x=coarse[row];y=coarse[row^21]
        exact=(F(x[0]-x[1]+phase*(y[0]+y[1]),2),F(x[0]+x[1]+phase*(-y[0]+y[1]),2))
        result+=sum((F(rounded[row][j])-exact[j])**2 for j in range(2))
    return result


def fixture(name,p,coarse,permutation,phases):
    require(sum(v*v for z in coarse for v in z)<=1<<(2*p),'source-compatible initial norm')
    fine=[tuple(32*v for v in z) for z in coarse]
    original=[list(z) for z in fine]
    output,scratch,cycles=inplace_reference(fine,p,permutation,phases)
    rounded=[tuple(v//32 for v in z) for z in output]
    require(direct(rounded,-1)==coarse,'actual rounded inverse')
    error=error_squared(coarse,rounded)
    require(error<=256,'width-one completed absolute field error')
    return {'name':name,'p':p,'fine_input':original,'fine_output':[list(z) for z in output],
            'swap_scratch':list(scratch),'inplace_object_preserved':'yes','monomial_cycle_counts':cycles,
            'error_squared':{'numerator':error.numerator,'denominator':error.denominator}}


def reject(callback,fragment):
    try:callback()
    except ValueError as error:
        require(fragment in str(error),'unexpected negative-control reason');return str(error)
    raise ValueError('negative control accepted')


def controls(raw,manifest,permutation,phases):
    bad=[(0,0)]*N;bad[0]=(1,0)
    offgrid=reject(lambda:inplace_reference(bad,14,permutation,phases),'coarse entrance')
    altered=dict(raw);altered['inputs/kernel.py']=b'X'+altered['inputs/kernel.py'][1:]
    source=reject(lambda:authenticate(altered,manifest),'source SHA256')
    trials=0
    for a in (-1,0,1):
        for b in (-1,0,1):
            for c in (-1,0,1):
                for d in (-1,0,1):
                    x,y=pair_difference((a,b),(c,d),1)
                    require(pair_difference(x,y,-1)==((a,b),(c,d)),'independent pair inverse')
                    require((x[0]+y[0],x[1]+y[1])==(a+c,b+d),'independent pair sum')
                    trials+=1
    odd=[((37*j+11)%31-15,(23*j+7)%29-14) for j in range(N)]
    nonlinear=fixture('odd-phase-control',14,odd,permutation,phases)
    return {'off_coarse_entry_rejected':offgrid,'source_byte_mutation_rejected':source,'pair_formula_inverse_sum_cases':trials,
            'odd_field_error_squared':nonlinear['error_squared'],'odd_field_output_sha256':digest(nonlinear['fine_output'])}


def compute():
    manifest=read(ROOT/'SOURCE-PINS.json');raw={path:read(ROOT/path) for path in PINS}
    authenticate(raw,manifest)
    unpacked=gzip.decompress(raw['inputs/WORD.json.gz']);require(len(unpacked)<=8*1024*1024,'decoded word capacity')
    binding=validate_word(decode(unpacked));operator,permutation,phases=source_monomial()
    columns=ideal_columns(permutation,phases)
    binding.update(operator,ideal_columns_sha256=digest(columns))
    zero=[(0,0)]*N;internal=[(1,0) if x%2==0 else (0,0) for x in range(N)]
    sharp=monomial(internal,permutation,phases)
    cases=[fixture('zero',14,zero,permutation,phases),fixture('sharp',14,sharp,permutation,phases)]
    for p in (14,15,31,127):
        scale=1<<(p-10)
        values=[(((37*j+11)%31-15)*scale,((23*j+7)%29-14)*scale) for j in range(N)]
        cases.append(fixture('signed-'+str(p),p,values,permutation,phases))
    require(cases[1]['error_squared']=={'numerator':256,'denominator':1},'attaining sixteen-h source-compatible witness')
    return {'schema_version':1,'source_manifest_sha256':MANIFEST_SHA,
            'method':'Independent signed-XOR21 physical pairs, Fraction difference-center formula, own binary monomial/source-history parser; no author or primary executable imports',
            'source_binding':binding,'ideal_columns_checked':N,'fixtures':cases,
            'logical_invoice':{'monomial_cycle_passes':2,'monomial_coordinate_updates':1024,'input_conversion_components':1024,
                               'output_conversion_components':1024,'pair_calls':256,'credited_kernel_data_additions':2560,
                               'credited_kernel_half_shifts':512,'credited_kernel_range_checks':4096},
            'controls':controls(raw,manifest,permutation,phases),
            'limits':['One actual source9896 occurrence,tensor width1,512coordinates only; not an arbitrary fine-grid child.',
                      'Generic pair nearest/inverse/sum theorem is credited6509 work; new independent evidence binds its actual selected coarse entrance and consumer.',
                      'Inplace destination and clean monomial swap word are logical finite-record properties; pair arithmetic physical cleanup,tape,bit circuits,accelerated tariff,global stock,wholecaller and higherwidth remain open.']}


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--emit',action='store_true');args=parser.parse_args()
    result=compute()
    if args.emit:print(canonical(result))
    else:
        require(canonical(decode(read(ROOT/'ORACLE.json')))==canonical(result),'strict oracle receipt drift')
        primary=decode(read(ROOT/'RESULT.json'))
        require(primary['source_binding']['ideal_columns_sha256']==result['source_binding']['ideal_columns_sha256'],'primary ideal matrix digest')
        expected={record['name']:record for record in result['fixtures']}
        seen=set()
        for record in primary['fixtures']:
            require(record['name'] in expected and record['name'] not in seen,'distinct primary fixture domain')
            seen.add(record['name'])
            for key in ('p','fine_input','fine_output','swap_scratch','inplace_object_preserved','error_squared'):
                require(canonical(record[key])==canonical(expected[record['name']][key]),'primary fixture '+key)
        require(seen==expected.keys(),'complete primary fixture coverage')
        print('PASS_INDEPENDENT_SELECTED_EVENT9896_CHILD')


if __name__=='__main__':
    try:main()
    except (ValueError,KeyError,TypeError,OSError) as error:
        print('FAIL: '+str(error),file=sys.stderr);sys.exit(1)
