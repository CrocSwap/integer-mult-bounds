"""Check exact conserved rounding and complete retained ports."""
import ast
from fractions import Fraction as F
import itertools
import json
from pathlib import Path
import random
import sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from kernel import pair,layer,call,center,need
from sources import authenticate,original,check
from ports import port


def add(a,b):return a[0]+b[0],a[1]+b[1]
def sub(a,b):return a[0]-b[0],a[1]-b[1]
def mul(a,b):return a[0]*b[0]-a[1]*b[1],a[0]*b[1]+a[1]*b[0]
def rotate(a,q):
    for _ in range(q%4):a=(-a[1],a[0])
    return a

def ideal_pair(x,y,sign):
    s,d=add(x,y),sub(x,y);r=rotate(d,sign)
    return tuple(F(v,2) for v in add(s,r)),tuple(F(v,2) for v in sub(s,r))

def norm2(z):return z[0]*z[0]+z[1]*z[1]

def fiber_sums(values,f,axis):
    active=sum(1 << (3*j+axis) for j in range(f));out={}
    for index,value in enumerate(values):
        key=index & ~active;out[key]=add(out.get(key,(0,0)),value)
    return out

def ideal_call(values,f,axis,adjoint=False):
    sign=-1 if adjoint else 1
    a,b=(F(1,2),F(sign,2)),(F(1,2),F(-sign,2))
    terms=[]
    for mask in range(1<<f):
        index=0;coefficient=(F(1),F(0))
        for j in range(f):
            bit=(mask>>j)&1;index|=bit<<(3*j+axis)
            coefficient=mul(coefficient,b if bit else a)
        terms.append((index,coefficient))
    return [tuple(sum(mul(c,values[k^shift])[part] for shift,c in terms) for part in (0,1))
            for k in range(len(values))]

def base_map(name,x):
    # Evaluate the literal three-bit monomials as separate constituent maps.
    bits=[(x>>j)&1 for j in range(3)]
    if name=='P':
        phase=sum(bits);bits[2]^=bits[0];phase+=sum(bits)
    elif name=='Q':
        phase=sum(bits);bits[0],bits[1]=bits[1],bits[0];phase+=sum(bits)
    elif name=='W':phase=2*(bits[0]+bits[2])
    elif name=='M':bits[0],bits[1]=bits[1],bits[0];phase=2*bits[1]
    else:raise ValueError('Oracle monomial')
    return sum(b<<j for j,b in enumerate(bits)),phase%4

def ideal_monomial(values,name,f,inverse=False):
    out=[None]*len(values)
    for x in range(len(values)):
        y=phase=0
        for j in range(f):
            digit,q=base_map(name,(x>>(3*j))&7);y|=digit<<(3*j);phase+=q
        if inverse:out[x]=rotate(values[y],-phase)
        else:out[y]=rotate(values[x],phase)
    return out

def ideal_port(x,y,f,kind,reverse):
    x=list(x);y=list(y)
    def mix(sign):
        nonlocal y
        p=ideal_monomial(x,'P',f);q=ideal_monomial(x,'Q',f)
        y=[add(v,(sign*(a[0]+2*b[0]),sign*(a[1]+2*b[1]))) for v,a,b in zip(y,p,q)]
    if reverse:
        if kind==3:
            y=ideal_monomial(y,'M',f,True);y=ideal_call(y,f,2,True);y=ideal_monomial(y,'W',f,True)
        y=ideal_call(y,f,0,True);mix(-1);x=ideal_call(x,f,0,True)
    else:
        x=ideal_call(x,f,0);mix(1);y=ideal_call(y,f,0)
        if kind==3:y=ideal_monomial(ideal_call(ideal_monomial(y,'W',f),f,2),'M',f)
    return x,y

def refusal(fn):
    try:fn()
    except ValueError:return
    raise ValueError('A negative control was accepted')

def port_binding():
    source=(HERE/'inputs/rounded.py').read_text()
    source=source[source.index('def port('):source.index('\ndef request_bits')]
    edits=[('def port(x,y,f,kind,reverse,width,capture=False):','def port(x,y,f,kind,reverse,width,backend,source,capture=False):'),
           ('    need(kind',"    monomial,mix=source.monomial,source.mix\n    need(x is not y, 'Distinct dirty banks')\n    need(kind"),
           ('        call(v,f,axis,width,adj,trace)','        backend(v,f,axis,width,adj,trace)')]
    for before,after in edits:
        need(source.count(before)==1,'One explicit port interface edit');source=source.replace(before,after)
    actual=next(n for n in ast.parse((HERE/'ports.py').read_text()).body if isinstance(n,ast.FunctionDef))
    need(ast.dump(actual)==ast.dump(ast.parse(source).body[0]),'Complete retained port order')

def main():
    pins=authenticate();old=original();port_binding()
    pair_cases=phase_cases=0;trace={}
    for coordinates in itertools.product(range(-4,5),repeat=4):
        x,y=coordinates[:2],coordinates[2:]
        for sign in (-1,1):
            actual=pair(x,y,16,sign,trace);ideal=ideal_pair(x,y,sign)
            need(add(*actual)==add(x,y),'Exact pair sum')
            need(pair(*actual,16,-sign)==(x,y),'Exact inverse')
            fourth=(x,y)
            for _ in range(4):fourth=pair(*fourth,16,sign)
            need(fourth==(x,y),'Exact fourth power')
            error=sum(norm2(sub(a,b)) for a,b in zip(actual,ideal))
            parity=(sum(coordinates)&1)
            need(error==parity,'Pointwise least lattice error')
            for q in range(4):
                transformed=pair(rotate(x,q),rotate(y,q),16,sign)
                need(transformed==tuple(rotate(a,q) for a in actual),'Global Gaussian phase covariance')
                phase_cases+=1
            conjugate=lambda z:(z[0],-z[1])
            need(pair(conjugate(x),conjugate(y),16,sign)==tuple(conjugate(a) for a in pair(x,y,16,-sign)), 'Conjugate inverse covariance')
            pair_cases+=1
    centers=0
    for sr,si in itertools.product(range(-3,4),repeat=2):
        legal=[]
        for cr,ci in itertools.product(range(-3,4),repeat=2):
            if ((cr+ci-sr-si)&1)==0:legal.append((cr*cr+ci*ci,(cr,ci)))
        minimum=min(k for k,c in legal);winners={c for k,c in legal if k==minimum}
        expected={(0,0)} if ((sr+si)&1)==0 else {(1,0),(-1,0),(0,1),(0,-1)}
        need(winners==expected and center(sr,si) in winners,'All optimum centers in the finite corroboration box')
        centers+=1
    rng=random.Random(350104);call_cases=port_cases=roundtrips=aligned_cases=fibers=0;port_trace={};largest_error=F(0)
    for f in (1,2,3):
        for axis in (0,2):
            for adjoint in (False,True):
                for trial in range(3):
                    values=[(rng.randrange(-13,14),rng.randrange(-13,14)) for _ in range(8**f)]
                    actual=list(values);call(actual,f,axis,32,adjoint)
                    expected=ideal_call(values,f,axis,adjoint)
                    maximum=max(norm2(sub(a,b)) for a,b in zip(actual,expected))
                    need(maximum<4*(2**f),'Inherited completed-call coordinate bound')
                    need(tuple(map(sum,zip(*actual)))==tuple(map(sum,zip(*values))),'Exact call sum')
                    need(fiber_sums(actual,f,axis)==fiber_sums(values,f,axis)==fiber_sums(expected,f,axis),'Every spectator-fiber observable is exact')
                    fibers+=4**f
                    call(actual,f,axis,32,not adjoint);need(actual==values,'Complete call round trip')
                    call_cases+=1
        for kind in (2,3):
            for reverse in (False,True):
                P,H=4,4;g=old.request_bits(P,f,kind,reverse);width=old.signed_width(H,P,f,kind,reverse)
                for trial in range(2):
                    x=[(rng.randrange(-11,12),rng.randrange(-11,12)) for _ in range(8**f)]
                    y=[(rng.randrange(-11,12),rng.randrange(-11,12)) for _ in range(8**f)]
                    expected=ideal_port(x,y,f,kind,reverse)
                    xx,yy=list(x),list(y)
                    ax,ay,t,cuts=port(xx,yy,f,kind,reverse,width,call,old,capture=True)
                    need(len(cuts)==kind,'Every paid call captured')
                    for axis,adj,before,after in cuts:
                        exact=ideal_call(before,f,axis,adj)
                        need(max(norm2(sub(a,b)) for a,b in zip(after,exact))<4*(2**f),'Actual-input paid tolerance')
                    error=max(norm2(sub(a,b)) for v,w in zip((ax,ay),expected) for a,b in zip(v,w))
                    largest_error=max(largest_error,error)
                    need(error <= 1 << (2*(g-P)),'Full source port error budget')
                    bx,by,t2,c2=port(xx,yy,f,kind,reverse,width,call,old)
                    need(bx is xx and by is yy and (bx,by)==(ax,ay) and c2==[],'In-place port and no capture arrays')
                    rx,ry,_,_=port(bx,by,f,kind,not reverse,width,call,old)
                    need((rx,ry)==(x,y),'Exact complete dirty-bank return')
                    for key in ('butterflies','data_additions','data_half_shifts','checked_values'):
                        port_trace[key]=port_trace.get(key,0)+t[key]
                    need(t['butterflies']==kind*f*(8**f)//2,'All direct calls charged')
                    need(t['checked_values']==16*t['butterflies'],'All numerical width checks charged')
                    if trial==0:
                        px,py,_,_=port([rotate(a,1) for a in x],[rotate(a,1) for a in y],f,kind,reverse,width,call,old)
                        need((px,py)==([rotate(a,1) for a in ax],[rotate(a,1) for a in ay]),'Complete port phase covariance')
                    port_cases+=1;roundtrips+=1
                scale=1 << (kind*f)
                xx=[(scale*rng.randrange(-3,4),scale*rng.randrange(-3,4)) for _ in range(8**f)]
                yy=[(scale*rng.randrange(-3,4),scale*rng.randrange(-3,4)) for _ in range(8**f)]
                expected=ideal_port(xx,yy,f,kind,reverse)
                before=old.port(list(xx),list(yy),f,kind,reverse,width)
                after=port(list(xx),list(yy),f,kind,reverse,width,call,old)
                need(before[:2]==after[:2]==expected,'Aligned exact predecessor port')
                aligned_cases+=1
    x=[(0,0)]*8;x[0]=(1,0);y=[(0,0)]*8
    bx,by,_,_=old.port(list(x),list(y),1,2,False,32)
    bx,by,_,_=old.port(bx,by,1,2,True,32)
    need((bx,by)!=(x,y),'Retained nearest-even loss control')
    witness=[(0,0)]*4;witness[3]=(1,0)
    left=list(witness);right=list(witness)
    layer(left,0,16);layer(left,1,16);layer(right,1,16);layer(right,0,16)
    need(left!=right,'Different rounded axes need not commute')
    a,b=(1,0),(0,0)
    need(pair(b,a,16)!=tuple(reversed(pair(a,b,16))),'Pair-swap covariance is not promised')
    need(pair((2,0),(0,0),16)!=tuple((2*z[0],2*z[1]) for z in pair(a,b,16)), 'Nonadditivity control')
    shifted=pair((0,0),(-1,0),16)
    need(shifted!=tuple(sub(z,(1,0)) for z in pair(a,b,16)),'Common translation covariance is not promised')
    wrong=[(0,0)]*64;wrong[9]=(1,0);initial=list(wrong);call(wrong,2,0,24)
    layer(wrong,0,24,-1);layer(wrong,3,24,-1)
    need(wrong!=initial,'Wrong inverse stage order fails')
    refusal(lambda:pair((1,0),(0,0),2))
    refusal(lambda:pair((F(1,2),0),(0,0),16))
    refusal(lambda:call([(0,0)]*8,1,1,16))
    refusal(lambda:call([(0,0)]*7,1,0,16))
    same=[(0,0)]*8
    refusal(lambda:port(same,same,1,2,False,16,call,old))
    for pin in pins:
        raw=(HERE/pin['path']).read_bytes();refusal(lambda:check(bytes([raw[0]^1])+raw[1:],pin))
    result=dict(status='PASS_CONSERVATIVE_GAUSSIAN_ROUNDING',pair_cases=pair_cases,phase_cases=phase_cases,
                center_cases=centers,completed_call_cases=call_cases,exact_fiber_observables=fibers,complete_port_cases=port_cases,
                exact_dirty_roundtrips=roundtrips,aligned_predecessor_ports=aligned_cases,paid_port_work=port_trace,pair_work=trace,
                largest_port_error_squared=str(largest_error),noncommuting_witness=dict(input=list(map(list,witness)),first=list(map(list,left)),second=list(map(list,right))),
                source_pins=len(pins),scope='Sharp sum/phase-preserving local rounding and direct complete ports; no native admission or kappa')
    if '--write' in sys.argv:(HERE/'RESULT.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    else:need(result==json.loads((HERE/'RESULT.json').read_text()),'Exact mathematical receipt')
    print(json.dumps(result,sort_keys=True))

if __name__=='__main__':main()
