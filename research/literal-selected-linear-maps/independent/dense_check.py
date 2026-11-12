"""Independent inverse-address oracle, literal CPU and complete cost census.

Prepared for CubeJerry with OpenAI assistance. Apache-2.0.
The author interpreter, test oracle and runtime metrics are not used.
The companion literal_dense_runner.cpp is a separate instruction interpreter.
"""
from pathlib import Path
import hashlib
import importlib.util
import json
import random
import subprocess
import sys
import tempfile

MATRICES = {
    'right': (239,129,130,132,136,16,160,192,256),
    'left': (3,5,9,17,32,65,129,1,256),
}
SYMBOLS = '_01|'

def need(ok, message):
    if not ok:
        raise AssertionError(message)

def gamma(n):
    b=format(n,'b')
    return '0'*(len(b)-1)+b

def gcost(n):
    return 47*n-30*n.bit_count()+33*n.bit_length()-42

def cclear(n):
    return 7*n+4

def ccopy(n):
    return 11*n+7

def cproduct(n,m):
    return 11*n*m+10*n+7

def cmultiply(n,m):
    return 23*n*m+17*n+18

def cdouble(n):
    return 47*n+18

def chalve(n):
    need(n%2==0,'even generated guide')
    return 15*n+14

def cdoublings(n,k,f):
    return 47*(n*(1<<(k*f))-n)+18*k*f+6*f+4

def cvolume(shape):
    f,r,p,s,w=shape
    total=ccopy(p); n=p
    for factor in (r,s,w):
        total+=cmultiply(n,factor); n*=factor
    total+=cdoublings(n,9,f); n<<=9*f
    total+=cdouble(n)
    return total

def geometry(shape,target,control):
    f,r,p,s,w=shape; h,l=sorted((target,control))
    a=p<<(h+1)*f
    cost=ccopy(p)+cdoublings(p,h+1,f)+chalve(a); a//=2
    m=1<<((l-h)*f)
    cost+=1+cdoublings(1,l-h,f)+chalve(m);m//=2
    cost+=cproduct(r,s)+cmultiply(r*s,w)+cdouble(r*s*w)
    b=2*r*s*w
    cost+=cdoublings(b,8-l,f);b<<=(8-l)*f
    return a,m,b,cost

def gate_cost(shape,target,control):
    f,r,p,s,w=shape;v=2*w*p*s*r*(1<<(9*f))
    a,m,b,total=geometry(shape,target,control)
    for j in range(f):
        need(4*a*m*b==v,'complete column geometry')
        # Direct census of prefix loading, four chunks, output merge,
        # whole-array rewind, mode update and the column test.
        total+=58*v+78*a*m+48*a+16
        if j+1<f:
            total+=cdouble(b)+chalve(a)+1
            b*=2;a//=2
    total+=3*f+15+7*(a+m+b)
    return total

def total_cost(shape,word):
    f,r,p,s,w=shape;v=2*w*p*s*r*(1<<(9*f))
    e=sum(2*n.bit_length()-1 for n in shape)
    total=75+sum(map(gcost,shape))+5*e+3+cvolume(shape)+20*v+11+1
    total+=sum(gate_cost(shape,*g) for g in word)
    total+=1+16*v+7+1
    total+=sum(cclear(n) for n in (*shape,v))+cclear(1)+75+1
    return total

def inverse_table(rows):
    inverse=[None]*512
    for source in range(512):
        target=sum(((row&source).bit_count()&1)<<i for i,row in enumerate(rows))
        need(inverse[target] is None,'selected source matrix invertibility')
        inverse[target]=source
    need(all(x is not None for x in inverse),'complete inverse truth table')
    return inverse

def oracle(payload,shape,rows):
    f,r,p,s,w=shape;unit=2*r*s*w;size=1<<(9*f);q=(1<<f)-1
    inverse=inverse_table(rows)
    out=bytearray(len(payload))
    for destination in range(size):
        # Recover one nine-bit native column at a time from the OUTPUT
        # address, invert its complete truth table, then interleave source.
        source=0
        for j in range(f):
            column=sum(((destination>>((8-i)*f+j))&1)<<i for i in range(9))
            old=inverse[column]
            for i in range(9):source|=((old>>i)&1)<<((8-i)*f+j)
        need(source<size and all(((source>>((8-i)*f))&q)<1<<f for i in range(9)),'source range')
        for outer in range(p):
            a=(outer*size+source)*unit;b=(outer*size+destination)*unit
            out[b:b+unit]=payload[a:a+unit]
    return bytes(out)

def encode_program(code):
    result=[]
    for op,*args in code:
        t=v=0;b=[-1]*4
        if op=='read':
            t,branches=args
            for c,p in branches.items():b[SYMBOLS.index(c)]=p
            o=0
        elif op=='write':t,c=args;v=SYMBOLS.index(c);o=1
        elif op=='move':t,v=args;need(v in (-1,1),'unit move');o=2
        elif op=='goto':v=args[0];o=3
        elif op=='halt':o=4
        else:raise AssertionError('nonlocal instruction')
        result.append(' '.join(map(str,(o,t,v,*b))))
    return '\n'.join(result)

def main():
    path=Path(sys.argv[1]).resolve();before=hashlib.sha256(path.read_bytes()).hexdigest()
    spec=importlib.util.spec_from_file_location('linear_subject',path)
    m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m)
    need(m.MATRICES==MATRICES,'actual source matrices')
    cpp=Path(__file__).with_name('literal_dense_runner.cpp')
    receipts=[];mutants=[];rng=random.Random(982713)
    with tempfile.TemporaryDirectory(prefix='independent-linear-') as directory:
        d=Path(directory);exe=d/'cpu'
        subprocess.run(['c++','-std=c++17','-O2','-Wall','-Wextra','-pedantic',str(cpp),'-o',str(exe)],check=True,capture_output=True)
        def execute(code,side,shapes,bad=None,mutant=None):
            cases=[];expected=[]
            for shape in shapes:
                f,r,p,s,w=shape;v=2*w*p*s*r*(1<<(9*f))
                data=bytes(48+(rng.getrandbits(1)) for _ in range(v))
                head=''.join(map(gamma,shape))
                output=oracle(data,shape,MATRICES[side])
                if bad=='short':data=data[:-1]
                elif bad=='extra':data+=b'1'
                elif bad=='header':head='|'+head[1:]
                elif bad=='symbol':data=data[:v//3]+b'|'+data[v//3+1:]
                # The sixth field and following tail are opaque to this graph.
                head+=gamma(33)+'10|'
                cases.append(head+'\n'+data.decode()+'\n'+('REJECT' if bad else output.decode()))
                expected.append(total_cost(shape,m.cnot_word(MATRICES[side])))
            cap=max(2*w*p*s*r*(1<<(9*f)) for f,r,p,s,w in shapes)+4096
            test=d/'case.txt';test.write_text(f'{len(code)} 27 {cap} {len(cases)}\n'+encode_program(code)+'\n'+'\n'.join(cases)+'\n')
            run=subprocess.run([str(exe),str(test)],check=True,capture_output=True,text=True,timeout=120)
            rows=[json.loads(x) for x in run.stdout.splitlines()]
            need(len(rows)==len(shapes),'one receipt per complete packet')
            entry_history=25
            for shape,row,count in zip(shapes,rows,expected):
                f,r,p,s,w=shape;v=2*w*p*s*r*(1<<(9*f));e=sum(2*n.bit_length()-1 for n in shape)
                if bad:need(not row['halt'] and row['failure_public_unchanged'],'malformed public preservation')
                else:
                    need(row['halt'] and row['exact_rows'] and row['heads'],'complete source map, private/exterior restoration and heads')
                    need(row['steps']==count,'independent exact complete helper census')
                    need(row['data_counts']==[v+1,v,4*v],'same-owner data census')
                    need(entry_history<=row['history']<=entry_history+64*(v+e+1),'retained history bound')
                    need(row['steps']<=65536*(f*v+e+1),'full leaf time bound')
                if not mutant:receipts.append({'side':side,'shape':shape,'kind':bad or 'complete actual m9','steps':row['steps'],'history':row['history'],'entry_history':entry_history})
                entry_history=row['history']
            return rows
        tables={side:m.compile_linear(side)[0] for side in MATRICES}
        for side,code in tables.items():
            execute(code,side,[(1,1,1,1,1),(1,1,1,1,5),(1,2,1,2,1),(2,1,1,1,1)])
            execute(code,side,[(1,2,2,1,3),(1,1,1,1,1),(1,1,2,2,4)])
        for bad in ('short','extra','header','symbol'):execute(tables['right'],'right',[(1,1,1,1,1)],bad=bad)
        def detect(code,label,shape=(1,1,1,1,1)):
            try:execute(code,'right',[shape],mutant=label)
            except AssertionError:mutants.append(label)
            else:raise AssertionError('undetected graph mutation: '+label)
        broken=[('write',m.DATA,'0') if ins==('write',m.DATA,'1') else ins for ins in tables['right']]
        detect(broken,'corrupted original-owner commit')
        broken=[]
        for op,*args in tables['right']:
            if op=='goto':args[0]+=1
            elif op=='read':args[1]={s:p+1 for s,p in args[1].items()}
            broken.append((op,*args))
        detect([('goto',1)]+broken,'correct function with incorrect complete cost')
        broken=list(tables['right']);changes=0
        for i,ins in enumerate(broken):
            if i and ins[0]=='read' and ins[1]==m.F and tables['right'][i-1]==('move',m.F,1) and set(ins[2])=={'1','_'}:
                branches=dict(ins[2]);branches['1']=branches['_'];broken[i]=('read',m.F,branches);changes+=1
        need(changes==19,'every actual CNOT column continuation identified')
        detect(broken,'clean first-column-only native map',(2,1,1,1,1))
    need(hashlib.sha256(path.read_bytes()).hexdigest()==before,'science changed during review')
    print(json.dumps({'status':'PASS_INDEPENDENT_SELECTED_LINEAR','program_sha256':before,
        'interpreter_sha256':hashlib.sha256(cpp.read_bytes()).hexdigest(),
        'exact_helper_census':True,'source_matrices':'actual MOVE24472 right and left',
        'complete_actual_f2_sides':2,'seed':982713,'cases':receipts,'mutations':mutants},sort_keys=True))

if __name__=='__main__':main()
