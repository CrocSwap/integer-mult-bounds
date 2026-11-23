#!/usr/bin/env python3
"""Independent arithmetic and caller review; imports no author checker."""
import argparse, ast, hashlib, importlib.util, itertools, json, math, operator, random, sys
from fractions import Fraction
from pathlib import Path

def need(value, why):
    if not value: raise ValueError(why)

def load(path, name):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module);return module

def certificate(numerators, values, P):
    q=1<<P
    for n,z in zip(numerators,values,strict=True):
        need(-q<=2*(n-q*z)<q,'unique half-open nearest-grid interval')

def direct(u,v,P):
    a,b=u;c,d=v;q=1<<P
    nums=(a*c-b*d,a*d+b*c)
    ans=tuple(math.ceil(Fraction(2*n-q+1,2*q)) for n in nums)
    certificate(nums,ans,P);return ans

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--source',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args();root=args.source
    source_rows=json.loads((root/'SOURCES.json').read_text())['files']
    for row in source_rows:
        raw=(root/row['local']).read_bytes();need(hashlib.sha256(raw).hexdigest()==row['sha256'],'source SHA256')
        if row.get('git_blob'):need(hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==row['git_blob'],'source Git blob')
    subject=load(root/'grid_arithmetic.py','review_subject')
    tensor=ast.parse((root/'retained/direct/tensor_word.py').read_text())
    selected=[n for n in tensor.body if isinstance(n,(ast.ClassDef,ast.FunctionDef)) and n.name in {'Grid','product_diagonal'}]
    need(len(selected)==2,'literal selected definitions')
    ns={'Fraction':Fraction,'prod':math.prod,'word_product':operator.mul}
    exec(compile(ast.Module(body=selected,type_ignores=[]),'<pinned caller>','exec'),ns)
    Grid=ns['Grid'];prod_diag=ns['product_diagonal']
    counts={'arithmetic_cases':0,'zero_multiplier_cases':0,'halfway_components':0,'source_odometer_scans':0,'source_odometer_calls':0,'parameter_bindings':0}
    maximum=0
    def check(B,P,v):
        nonlocal maximum
        u=tuple(v[:2]);w=tuple(v[2:]);a,b=u;c,d=w
        result,frame=subject.multiply_grid(u,w,P,B)
        certificate((a*c-b*d,a*d+b*c),result,P)
        need(result==Grid(P).multiply(u,w),'literal Grid expression')
        need(result==direct(u,w,P),'independent rational ceiling oracle')
        need(len(frame.registers)==7 and frame.registers[2:]==[0]*5,'fixed seven-register frame and reset')
        need(frame.iterations<=4*B and frame.peak<=2*B+1,'written width/iteration envelope')
        maximum=max(maximum,frame.peak);counts['arithmetic_cases']+=1
        counts['zero_multiplier_cases']+=int(c==0 or d==0)
        q=1<<P;counts['halfway_components']+=sum(int((2*n)% (2*q)==q) for n in (a*c-b*d,a*d+b*c))
    for B in (2,3):
        for P in range(1,B+1):
            for v in itertools.product(range(-(1<<(B-1)),1<<(B-1)),repeat=4):check(B,P,v)
    values=(-8,-7,-3,-1,0,1,3,6,7)
    for P in (1,2,3,4):
        for v in itertools.product(values,repeat=4):check(4,P,v)
    rng=random.Random(52408093)
    for B in (9,31,257,4096):
        M=1<<(B-1)
        for P in (1,B//2,B):
            for _ in range(12):check(B,P,tuple(rng.randrange(-M,M) for _ in range(4)))
    for B in (2,17,1024,4924):
        M=1<<(B-1)
        for P in (1,B):
            for v in ((-M,)*4,(-M,0,0,0),(0,-M,0,0),(-M,M-1,M-1,-M)):check(B,P,v)
    for P in (1,3,7):
        q=1<<P;factors=((0,0),(q,0),(-q,0),(0,q),(q//2,-q//2));sides=(2,2,3,2)
        for offset in range(5):
            tables=[tuple(factors[(offset+axis+j)%len(factors)] for j in range(side)) for axis,side in enumerate(sides)]
            data=[(q//2,-q//2) for _ in range(math.prod(sides))];expected=[]
            for index,x in enumerate(data):
                position=[];remaining=index
                for side in sides:remaining,digit=divmod(remaining,side);position.append(digit)
                acc=(q,0)
                for axis in reversed(range(len(sides))):acc=direct(tables[axis][position[axis]],acc,P)
                expected.append(direct(acc,x,P))
            class Checked(Grid):
                def multiply(self,u,v):
                    counts['source_odometer_calls']+=1
                    r,frame=subject.multiply_grid(u,v,self.bits,self.bits+16)
                    certificate((u[0]*v[0]-u[1]*v[1],u[0]*v[1]+u[1]*v[0]),r,self.bits)
                    return r
            prod_diag(data,tables,Checked(P));need(data==expected,'current-coordinate right-fold odometer oracle');counts['source_odometer_scans']+=1
    precision=load(root/'retained/precision.py','review_precision')
    for widths in ((1,),(2,),(4,5),(1,1,1),(32,)*4,(128,)*16,(17,)*129):
        for public in (1,5,30,72):
            d=len(widths);L=sum(widths);E=(257*L+1)//2+1354*d;A=20*L+303*d;J=20000*(d+1)*(max(widths)+2)**6;C=4*J*(d+1)**2+d+1;P=4*public+A+2*E+C.bit_length();B=P+max(A,E)+3
            got=precision.precision_budget(public,widths)
            need((got.fractional_bits,got.local_error_exponent,got.interval_exponent)==(P,A,E),'frozen API input-bound binding')
            need(4*J*(d+1)**2<C and P>=1 and P<=B-3,'strict bootstrap numerator and coefficient denominator height')
            need(A+1<B-1-P and E<B-1-P,'both signed input magnitude margins')
            counts['parameter_bindings']+=1
    kernel=load(root/'retained/kernel.py','review_retained_kernel')
    tree=ast.parse((root/'retained/direct/product.py').read_text());owner=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='Multiplier');operand=next(n for n in owner.body if isinstance(n,ast.FunctionDef) and n.name=='operand');helpers=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in {'digits','ordinal'}];on={'prod':math.prod};exec(compile(ast.Module(body=helpers+[operand],type_ignores=[]),'<pinned operand>','exec'),on)
    class Caller:pass
    caller=Caller();caller.sides=(2,);caller.widths=(2,);caller.size=2;caller.base=32;caller.grid=Grid(3438);caller.crt=lambda field:field
    field,used=on['operand'](caller,1);need(field[0]==(1<<3431,0) and used==1,'actual pre-CRT input height');state=[field[0][0],0,0,0];saved=state[:];identity=tuple(tuple((int(i==j),1) for j in range(4)) for i in range(4))
    rejected=False
    try:kernel.apply_gate(identity,state,3433,1)
    except ValueError as e:rejected=str(e)=='data width'
    need(rejected and state==saved,'unmodified finite predecessor guard')
    controls={}
    for label,nums,z,P in [('negative_tie_away',(-1,0),(-1,0),1),('imaginary_difference',(0,2),(0,0),1),('per_product_round',(0,2),(0,2),1),('coefficient_ties_even',(2,0),(0,0),2)]:
        try:certificate(nums,z,P)
        except ValueError:controls[label]=True
        else:raise ValueError('adverse rounding mutation survived '+label)
    for B in (2,7,128):
        M=1<<(B-1)
        try:subject.multiply_grid((-M,-M),(-M,-M),B,B,diagnostic_width=2*B)
        except OverflowError:pass
        else:raise ValueError('underallocated sum passed')
    report={'marker':'PASS_INDEPENDENT_GRID_CALLER_REVIEW','source_count':len(source_rows),'proof_sha256':hashlib.sha256((root/'PROOF.md').read_bytes()).hexdigest(),'program_sha256':hashlib.sha256((root/'grid_arithmetic.py').read_bytes()).hexdigest(),'counts':counts,'maximum_observed_word_bits':maximum,'rejected_controls':controls,'finite_guard_preserved':True,'scope':'local supplied arithmetic and literal expressions; exact helper adapter, no encoded tape execution'}
    args.output.write_text(json.dumps(report,sort_keys=True,indent=2)+'\n');print(json.dumps(report,sort_keys=True))
if __name__=='__main__':main()
