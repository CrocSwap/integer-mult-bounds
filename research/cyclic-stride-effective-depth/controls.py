"""Admission, rounding, mutation and traffic checks for effective depth."""
from pathlib import Path
from fractions import Fraction as F
import importlib.util
import tempfile
from common import P,need,original as st
from early import solve
from uniform import admission,error_bound,ceil_log2


def main():
    controls=[]
    calls=[('zero margin',lambda:admission(F(0),16)),
           ('unit margin',lambda:admission(F(1),16)),
           ('floating margin',lambda:admission(0.25,16)),
           ('boolean margin',lambda:admission(True,16)),
           ('width below uniform admission',lambda:admission(F(1,16),15)),
           ('boolean width',lambda:admission(F(1,2),True)),
           ('negative width',lambda:admission(F(1,2),-1)),
           ('negative source bound',lambda:error_bound(F(-1),F(1,2),10)),
           ('zero logarithm',lambda:ceil_log2(F(0)))]
    for name,call in calls:
        try:
            call()
        except ValueError as error:
            controls.append(dict(name=name,rejected=str(error)))
        else:
            raise ValueError('admission accepted '+name)

    source=(P/'early.py').read_text()
    mutations={
        'any zero used as all zero':('all(bi == st.ZERO for bi in b)','any(bi == st.ZERO for bi in b)'),
        'coarse product destroys coupling':('p[i] = st.rounded(st.mul(b[i], prev[1]), bits)',
                                           'p[i] = st.rounded(st.mul(b[i], prev[1]), 0)'),
    }
    length,stride,bits,beta=7,3,16,F(1,4)
    x=[st.ONE]*length
    b=[st.ZERO]+[(F(3,4),F(0))]*(length-1)
    exact=st.exact_cycle_solve(x,b,stride)
    bound=error_bound(F(1),beta,bits)
    baseline=solve(x,b,stride,bits,st.Tape())
    need(all(st.norm2(st.sub(a,e))<=bound*bound for a,e in zip(baseline,exact)),'mutation baseline')
    with tempfile.TemporaryDirectory(prefix='stride math controls ') as directory:
        for index,(name,(before,after)) in enumerate(mutations.items()):
            need(source.count(before)==1,'unique mutation target')
            path=Path(directory)/(str(index)+'.py')
            path.write_text(source.replace(before,after))
            spec=importlib.util.spec_from_file_location('stride_mutation_'+str(index),path)
            mutant=importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mutant)
            bad=mutant.solve(x,b,stride,bits,st.Tape())
            need(any(st.norm2(st.sub(a,e))>bound*bound for a,e in zip(bad,exact)),
                 'defect not detected: '+name)
            controls.append(dict(name=name,detected=True))

    u=F(1,1<<16)
    need(st.rounded((u/2,F(0)),16)!=st.ZERO,'positive half-grid tie is not zero')
    need(st.rounded((u/4,-u/4),16)==st.ZERO,'strict zero threshold')
    controls.append(dict(name='strict threshold distinguishes half-grid tie',detected=True))
    zeros=[]
    for length in [1,2,7,19]:
        for stride in [-1,0,length//2]:
            x=[(F(1,3),F(-2,7))]*length
            b=[st.ZERO]*length
            trace=[]
            tape=st.Tape()
            short=solve(x,b,stride,10,tape,trace)
            full=st.solve(x,b,stride,10,st.Tape())
            need(short==full and len(trace)==1,'zero subtree rounds once')
            zeros.append(dict(length=length,stride=stride,records=tape.records))

    traffic=[]
    for length in [1,2,7,64,1000,4096,65536,131072]:
        for stride in sorted({0,1,length//2,length-1,97%length}):
            full_tape,short_tape=st.Tape(),st.Tape()
            st.solve([None]*length,[None]*length,stride,None,full_tape)
            solve([None]*length,[None]*length,stride,None,short_tape)
            need(full_tape.records<=40*length and short_tape.records<=44*length,'traffic with head returns')
            traffic.append(dict(length=length,stride=stride,original_records=full_tape.records,
                                truncated_records=short_tape.records))
    logarithms=[]
    for exponent in range(-257,258):
        power=F(2)**exponent
        for value,expected in [(power*(1-F(1,1<<20)),exponent),(power,exponent),
                               (power*(1+F(1,1<<20)),exponent+1)]:
            answer=ceil_log2(value)
            need(answer==expected and F(2)**(answer-1)<value<=F(2)**answer,'exact logarithm boundary')
            logarithms.append(dict(exponent=exponent,answer=answer))
    admissions=[]
    for g in [1,2,3,4,8,16,64,256,1024]:
        for extra in [0,1,2,16,128,1024]:
            admissions.append(admission(F(1,1<<g),2*g+8+extra))
    u0=F(1,1024)
    q1=F(1,4)+2*u0
    q2=q1*q1+2*u0
    need(F(23,16)**2>2 and q1<F(1,2) and q2<F(1,4) and 36*u0*u0<u0/2,
         'rational decay constants')
    identities=dict(growth_square_gap=F(23,16)**2-2,first_half_step=q1,second_half_step=q2,
                    strict_zero_gap=u0/2-36*u0*u0)
    print('PASS depth controls',len(controls),'log boundaries',len(logarithms),flush=True)
    return dict(controls=controls,zero_bases=zeros,traffic=traffic,log_boundaries=logarithms,
                admissions=admissions,decay_constants=identities)
